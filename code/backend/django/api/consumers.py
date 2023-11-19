import asyncio
import json 
from channels.generic.websocket import AsyncWebsocketConsumer
import chess
from reconchess import Player, LocalGame, chess, game
from reconchess.bots.attacker_bot import AttackerBot
from reconchess.bots.random_bot import RandomBot
from reconchess.types import Color, List, Optional, Square, WinReason
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
			'message': 'game started',
			'board': board.fen(),
			'color': color_name,
			'opponent_name': opponent_name,
			'time': self.game.get_seconds_left()
		}))
	
	async def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[chess.Square]):
		if(captured_my_piece):
			return await self.consumer.send(text_data=json.dumps({
				'message': 'opponent capture',
				'capture_square': capture_square,
				'board': self.game.board.fen()
			}))
		
		return
	
	async def choose_sense(self) -> chess.Square | None:
		await self.consumer.send(text_data=json.dumps({
			'message': 'your turn to sense',
		}))

		#waits for the client to send a sense action
		while self.sense is None:
			if(self.game.get_seconds_left() <= 0):
				raise TimeoutError('player ran out of time')
			await asyncio.sleep(0.1)

		sense = self.sense
		self.sense = None
		return chess.parse_square(sense)
	
	#the client should already know where the pieces are, so this is just to implement the interface
	def handle_sense_result(self):
		pass

	async def choose_move(self, move_actions: List[chess.Move]) -> chess.Move | None:
		await self.consumer.send(text_data=json.dumps({
			'message': 'your turn to move',
			'move_actions': [str(move) for move in move_actions]
		}))
		
		#waits for the client to send a valid move
		while self.move is None or chess.Move.from_uci(self.move) not in move_actions:
			#if the move is invalid send a message to the client and keep waiting
			if self.move is not None:
				await self.consumer.send(text_data=json.dumps({
					'message': 'invalid move'
				}))
			if(self.game.get_seconds_left() <= 0):
				raise TimeoutError('player ran out of time')
			await asyncio.sleep(0.1)

		move = self.move
		self.move = None
		return chess.Move.from_uci(move)
	
	async def handle_move_result(self, requested_move: chess.Move | None, taken_move: chess.Move | None, captured_opponent_piece: bool, capture_square: Square | None):
		#finish the turn
		self.finished = True
		#send the move results to the client
		return await self.consumer.send(text_data=json.dumps({
			'message': 'move result',
			'requested_move': str(requested_move),
			'taken_move': str(taken_move),
			'captured_opponent_piece': captured_opponent_piece,
			'capture_square': str(capture_square)
		}))
	
	async def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason], game_history: GameHistory):
		self.finished = True
		 win_reason_messages = {
        WinReason.KING_CAPTURE: 'the king was captured',
        WinReason.TIMEOUT: 'timeout',
        WinReason.RESIGN: 'resign',
        WinReason.TURN_LIMIT: 'full turn limit exceeded',
        WinReason.MOVE_LIMIT: 'full move limit exceeded',
        None: 'game over'
    }

    message = f'game over: {win_reason_messages.get(win_reason, "")}'
		
		return await self.consumer.send(text_data=json.dumps({
			'message': 'game over',
			'winner': winner_color,
			'reason': win_reason.name if win_reason else None,
		}))
	
	async def print_time_left(self, color: Optional[Color]):
		await self.consumer.send(text_data=json.dumps({
			'message': 'time left',
			'player color': color,
		}))
		
		while not self.game.is_over():
			return self.game.get_seconds_left()


class GameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.game = LocalGame()
		self.player = HumanPlayer(self, self.game)
		self.bot = AttackerBot()
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
		white_name = self.player.__class__.__name__
		black_name = self.bot.__class__.__name__
		self.game.store_players(white_name, black_name)

		await self.player.handle_game_start(chess.WHITE, self.game.board, black_name)
		self.bot.handle_game_start(chess.BLACK, self.game.board, white_name)

		self.game.start()

		first_ply = True

		while not self.game.is_over():
			#get possible actions on this turn
			sense_actions = self.game.sense_actions()
			move_actions = self.game.move_actions()

			#get the result of the opponent's move, only returns a square if a piece was captured
			capture_square = self.game.opponent_move_results() if not first_ply else None

			if(self.game.turn == chess.WHITE):
				try:
					await self.play_human_turn(capture_square=capture_square, move_actions=move_actions)
					first_turn = False
				except TimeoutError:
					break
			else:
				self.play_bot_turn(capture_square=capture_square, sense_actions=sense_actions, move_actions=move_actions)

		self.game.end()
		winner_color = self.game.get_winner_color()
		win_reason = self.game.get_win_reason()
		game_history = self.game.get_game_history()

		await self.player.handle_game_end(winner_color, win_reason, game_history)
		self.bot.handle_game_end(winner_color, win_reason, game_history)

	async def play_human_turn(self, capture_square, move_actions):
		player = self.player
		#the human player has started their turn
		player.finished = False

		#update the game for the player	
		await player.handle_opponent_move_result(capture_square is not None, capture_square)

		#let the player choose a sense action
		sense = await player.choose_sense()
		self.game.sense(sense)

		#let the current player choose a move action
		move = await player.choose_move(move_actions)
		_, taken_move, capture_square = self.game.move(move)
		await player.handle_move_result(move, taken_move, capture_square is not None, capture_square)

		while(not player.finished):
			await asyncio.sleep(0.1)
			
		self.game.end_turn()

	def play_bot_turn(self, capture_square, sense_actions, move_actions):
		#update the game for the bot
		self.bot.handle_opponent_move_result(capture_square is not None, capture_square)

		#let the bot choose a sense action
		sense = self.bot.choose_sense(sense_actions, move_actions, self.game.get_seconds_left())
		self.game.sense(sense)

		#let the bot choose a move action
		move = self.bot.choose_move(move_actions, self.game.get_seconds_left())
		_, taken_move, capture_square = self.game.move(move)
		self.bot.handle_move_result(move, taken_move, capture_square is not None, capture_square)

		self.game.end_turn()