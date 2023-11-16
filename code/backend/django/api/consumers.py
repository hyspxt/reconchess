import asyncio
import json 
from channels.generic.websocket import AsyncWebsocketConsumer
import chess
from reconchess import Player, LocalGame, chess
from reconchess.bots.random_bot import RandomBot
from reconchess.types import Color, List, Optional, Square, Tuple, WinReason
from reconchess.history import GameHistory

class HumanPlayer(Player):
	def __init__(self, consumer, game):
		self.consumer = consumer
		self.game = game 
		self.move = None
		self.sense = None
		self.finished = True
	
	async def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
		color_name = 'white' if color == chess.WHITE else 'black'
		return await self.consumer.send(text_data=json.dumps({
			'board': board.fen(),
			'color': color_name
		}))
	
	async def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[chess.Square]):
		return await self.consumer.send(text_data=json.dumps({
				'message': 'opponent_capture',
				'capture_square': capture_square
			}))
	
	async def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square | None:
		await self.consumer.send(text_data=json.dumps({
			'message': 'your turn to sense'
		}))
		while self.sense is None:
			await asyncio.sleep(0.1)

		sense = self.sense
		self.sense = None
		return chess.parse_square(sense)
	
	#the client should already know where the pieces are, so this is just to implement the interface
	def handle_sense_result(self, sense_result: List[Tuple[Square, chess.Piece | None]]):
		pass

	async def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> chess.Move | None:
		await self.consumer.send(text_data=json.dumps({
			'message': 'your turn to move'
		}))
		
		while self.move is None or chess.Move.from_uci(self.move) not in move_actions:
			if self.move is not None:
				await self.consumer.send(text_data=json.dumps({
					'message': 'invalid move'
				}))
			await asyncio.sleep(0.1)

		move = self.move
		self.move = None
		return chess.Move.from_uci(move)
	
	async def handle_move_result(self, requested_move: chess.Move | None, taken_move: chess.Move | None, captured_opponent_piece: bool, capture_square: Square | None):
		return await self.consumer.send(text_data=json.dumps({'test':'test'}))
	

	async def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason], game_history: GameHistory):
		self.finished = True
		switch(WinReason):
		
			case KING_CAPTURE:
				return await self.consumer.send(text_data=json.dumps({
					'message': 'game over: the king was captured',
					'winner': winner_color,
				}))
				break
			case TIMEOUT:
				return await self.consumer.send(text_data=json.dumps({
					'message': 'game over: timeout',
					'winner': winner_color,
				}))
				break
			case RESIGN:
				return await self.consumer.send(text_data=json.dumps({
					'message': 'game over: resign',
					'winner': winner_color,
				}))
				break
			case TURN_LIMIT:
				return await self.consumer.send(text_data=json.dumps({
					'message': 'game over: full turn limit exceeded',
					'winner': winner_color,
				}))
				break
			case MOVE_LIMIT:
				return await self.consumer.send(text_data=json.dumps({
					'message': 'game over: full move limit exceeded',
					'winner': winner_color,
				}))
				break
			case default:
				return await self.consumer.send(text_data=json.dumps({
					'message': 'game over',
					'winner': winner_color,
				}))

	def print_time_left(self, color: Optional[Color]):
		await self.consumer.send(text_data=json.dumps({
			'message': 'time left',
			'player color': color,
		}))
		 while not self.game.is_over():
			return self.game.get_seconds_left()
##


class GameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.game = LocalGame()
		self.player = HumanPlayer(self, self.game)
		self.bot = RandomBot()
		self.lock = asyncio.Lock()
		await self.accept()

	async def disconnect(self, close_code):
		pass

	async def receive(self, text_data):
		data = json.loads(text_data)
		asyncio.create_task(self.handle_action(data))
	
	async def handle_action(self, data):
		action = data['action']
		if action == 'start_game':
			await self.start_game()
		elif action == 'sense':
			self.player.sense = data['sense']
		elif action == 'move':
			self.player.move = data['move']
		elif action == 'resign':
			self.game.resign()
			self.game.end()
			await self.player.handle_game_end(self.game.get_winner_color(), self.game.get_win_reason(), self.game.get_game_history())
			self.bot.handle_game_end(self.game.get_winner_color(), self.game.get_win_reason(), self.game.get_game_history())
		else:
			print('invalid action')
	
	async def start_game(self):
		players = [self.bot, self.player]

		white_name = self.player.__class__.__name__
		black_name = self.bot.__class__.__name__
		self.game.store_players(white_name, black_name)

		await self.player.handle_game_start(chess.WHITE, self.game.board, black_name)
		self.bot.handle_game_start(chess.BLACK, self.game.board, white_name)

		self.game.start()

		while not self.game.is_over():
			#wait for the player to finish their turn before continuing
			while not self.player.finished:
				await asyncio.sleep(0.1)
			
			current_player = players[self.game.turn]
			if current_player == self.player:
				self.player.finished = False

			#get possible actions on this turn
			sense_actions = self.game.sense_actions()
			move_actions = self.game.move_actions()

			#update the game for the current player
			capture_square = self.game.opponent_move_results()
			await current_player.handle_opponent_move_result(capture_square is not None, capture_square)
			#let the current player choose a sense action
			sense = await current_player.choose_sense(sense_actions, move_actions, self.game.get_seconds_left())
			sense_result = self.game.sense(sense)
			current_player.handle_sense_result(sense_result)

			#let the current player choose a move action
			move = await current_player.choose_move(move_actions, self.game.get_seconds_left())
			taken_move, captured_opponent_piece, capture_square = self.game.move(move)
			await current_player.handle_move_result(move, taken_move, captured_opponent_piece, capture_square)

			self.game.end_turn()

		self.game.end()
		winner_color = self.game.get_winner_color()
		win_reason = self.game.get_win_reason()
		game_history = self.game.get_game_history()

		await self.player.handle_game_end(winner_color, win_reason, game_history)
		self.bot.handle_game_end(winner_color, win_reason, game_history)


			