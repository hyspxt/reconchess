import asyncio
import json 
import chess
from channels.generic.websocket import AsyncWebsocketConsumer
from reconchess import LocalGame
from reconchess.bots.trout_bot import TroutBot
from .HumanPlayer import HumanPlayer

class GameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.game = None
		self.player = None
		self.bot = None
		await self.accept()

	async def disconnect(self, close_code):
		self.game.end()
		self.player = None
		self.bot = None

	async def receive(self, text_data):
		data = json.loads(text_data)
		asyncio.create_task(self.handle_action(data))
	
	async def handle_action(self, data):
		action = data['action']
		if action == 'start_game':
			seconds = data.get('seconds', None)
			await self.start_game(seconds)
		elif action == 'sense':
			self.player.sense = data['sense']
		elif action == 'move':
			self.player.move = data['move']
		elif action == 'pass':
			self.player.sense = 'pass'
			self.player.move = 'pass'
		elif action == 'resign':
			self.game.resign()
			self.game.end()
			await self.player.handle_game_end(self.game.get_winner_color(), self.game.get_win_reason(), self.game.get_game_history())
			self.bot.handle_game_end(self.game.get_winner_color(), self.game.get_win_reason(), self.game.get_game_history())
			#restart the game if the player wants to rematch
			if data['rematch']: 
				await self.start_game(seconds=self.game.seconds_per_player)
		else:
			print('invalid action')
	
	async def start_game(self, seconds):
		seconds = 30 if seconds is None else seconds
		#initialize the game
		self.game = LocalGame(seconds_per_player=seconds)
		self.player = HumanPlayer(self, self.game)
		self.bot = TroutBot()
		white_name = self.player.__class__.__name__
		black_name = self.bot.__class__.__name__
		self.game.store_players(white_name, black_name)

		await self.player.handle_game_start(chess.WHITE, self.game.board, black_name)
		self.bot.handle_game_start(chess.BLACK, self.game.board.copy(), white_name)

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
					await self.play_human_turn(capture_square=capture_square, move_actions=move_actions, first_ply=first_ply)
					first_ply = False
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

	async def play_human_turn(self, capture_square, move_actions, first_ply):
		player = self.player
		#the human player has started their turn
		player.finished = False

		if not first_ply:
			#update the game for the player	
			await player.handle_opponent_move_result(capture_square is not None, capture_square)

		#let the player choose a sense action
		sense = await player.choose_sense()
		self.game.sense(sense)

		#let the current player choose a move action
		move = await player.choose_move(move_actions)
		_, taken_move, capture_square = self.game.move(move)
		await player.handle_move_result(move, taken_move, capture_square is not None, capture_square)

		self.game.end_turn()
		
		#get the updated time for the player
		time_left = self.game.seconds_left_by_color[not self.game.turn]

		#send the remaining time to the client for syncronization purposes
		#5 seconds are added to the player's time at the end of the turn as per  the rules
		await self.send(text_data=json.dumps({
			'message': 'turn ended',
			'my_time': time_left,
			'opponent_time': self.game.get_seconds_left(),
		}))

	def play_bot_turn(self, capture_square, sense_actions, move_actions):
		#update the game for the bot
		self.bot.handle_opponent_move_result(capture_square is not None, capture_square)

		#let the bot choose a sense action
		sense = self.bot.choose_sense(sense_actions, move_actions, self.game.get_seconds_left())
		self.game.sense(sense)

		#let the bot choose a move action
		move = self.bot.choose_move(move_actions, self.game.get_seconds_left())
		requested_move, taken_move, capture_square = self.game.move(move)
		
		self.bot.handle_move_result(requested_move, taken_move, capture_square is not None, capture_square)

		self.game.end_turn()
