import asyncio
import json 
import chess
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from reconchess import LocalGame
from reconchess.bots import random_bot, attacker_bot, trout_bot
from strangefish.strangefish_strategy import StrangeFish2
from .HumanPlayer import HumanPlayer
from asgiref.sync import sync_to_async

available_bots = {
	'random': random_bot.RandomBot,
	'attacker': attacker_bot.AttackerBot,
	'trout': trout_bot.TroutBot,
	'strangefish': StrangeFish2
}

class GameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.game = None
		self.player = None
		self.bot = None
		await self.accept()

	async def disconnect(self, close_code):
		self.player = None
		self.bot = None

	async def receive(self, text_data):
		data = json.loads(text_data)
		asyncio.create_task(self.handle_action(data))
	
	async def handle_action(self, data):
		action = data['action']
		print(data)
		if action == 'start_game':
			seconds = int(data.get('seconds', 900) or 900)
			color = data.get('color', 'w')
			bot = available_bots.get(data.get('bot', 'random'))
			await self.start_game(seconds, color, bot)
		elif action == 'sense':
			self.player.sense = data['sense']
		elif action == 'move':
			self.player.move = data['move']
		elif action == 'pass':
			self.player.sense = 'pass'
			self.player.move = 'pass'
		elif action == 'resign':
			if(not self.game.is_over()):
				#only the player can resign through a message
				self.game._resignee = self.player.color == 'w' #chess.COLORS are booleans, returns chess.WHITE if True chess.BLACK if False
				await self.end_game()

			#restart the game if the player wants to rematch
			if data['rematch']: 
				print(data)
				await self.start_game(seconds=self.game.seconds_per_player, color=self.player.color, bot_constructor=type(self.bot))
		elif action == 'get_active_timer':
			color = 'w' if self.game.turn == chess.WHITE else 'b'
			await self.send(text_data=json.dumps({
				'message': 'time left',
				'color': color,
				'time': self.game.get_seconds_left()
			}))

		else:
			print('invalid action')

	async def game_message(self, event):
		#send the messages from the player to the client
		await self.send(text_data=json.dumps(event))

	async def end_game(self):
		self.game.end()
		winner_color = self.game.get_winner_color()
		win_reason = self.game.get_win_reason()
		game_history = self.game.get_game_history()

		await self.player.handle_game_end(winner_color, win_reason, game_history)
		self.bot.handle_game_end(winner_color, win_reason, game_history)

	
	async def start_game(self, seconds, color, bot_constructor):
		#initialize the game
		self.game = LocalGame(seconds_per_player=seconds)
		self.player = HumanPlayer(self.channel_name, self.game)
		self.bot = bot_constructor()

		#get the username if the player is authenticated otherwise use 'guest'
		player_name = self.scope['user'].username if self.scope['user'].is_authenticated else 'guest'
		
		#save the player names in a list
		names = [self.bot.__class__.__name__, player_name]
		#make sure that the list's order follows the order of chess.COLORS
		if	color == 'b':
			names.reverse()
		#save the players in the game
		self.game.store_players(names[chess.WHITE], names[chess.BLACK])
		
		#find the color of the player
		player_color = chess.WHITE if color == 'w' else chess.BLACK

		await self.player.handle_game_start(player_color, self.game.board, names[not player_color])
		self.bot.handle_game_start(not player_color, self.game.board.copy(), names[player_color])

		self.game.start()

		first_ply = True

		while not self.game.is_over():
			#get possible actions on this turn
			sense_actions = self.game.sense_actions()
			move_actions = self.game.move_actions()

			#get the result of the opponent's move, only returns a square if a piece was captured
			capture_square = self.game.opponent_move_results() if not first_ply else None
			if(self.game.turn == player_color):
				try:
					await self.play_human_turn(capture_square=capture_square, move_actions=move_actions, first_ply=first_ply)
					first_ply = False
				except TimeoutError:
					break
			else:
				await sync_to_async(self.play_bot_turn)(capture_square=capture_square, sense_actions=sense_actions, move_actions=move_actions)

		await self.end_game()

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
		print("BOT'S MOVE", taken_move)

		
		self.bot.handle_move_result(requested_move, taken_move, capture_square is not None, capture_square)

		self.game.end_turn()


class MultiplayerGameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = 'game_%s' % self.room_name

		await self.accept()
		if(len(self.channel_layer.groups.get(self.room_group_name, [])) < 2):
			# Join room group
			await self.channel_layer.group_add(
				self.room_group_name,
				self.channel_name
			)
		else:
			await self.send(text_data=json.dumps({
				'message': 'room full'
			}))
		
	async def receive(self, text_data):
		data = json.loads(text_data)
		asyncio.create_task(self.handle_action(data))

	async def handle_action(self, data):
		#get the name of the channel that sent the message if it exists
		sender = data.get('sender', None)

		#ignore messages sent by the same consumer
		if sender == self.channel_name:
			return
		
		action = data['action']
		if action == 'start_game':
			seconds = data.get('seconds', 900)
			await self.start_game(seconds)
		elif action == 'sense':
			#check if the players attribute exists 
			if hasattr(self, 'players'):
				self.players[self.game.turn].sense = data['sense']
			else:		
				#send the message to the other consumer	
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'handle_action',
						'action': 'sense',
						'sense': data['sense'],
						'sender': self.channel_name
					}
				)
		elif action == 'move':
			#check if the players attribute exists 
			if hasattr(self, 'players'):
				self.players[self.game.turn].move = data['move']
			else:			
				#send the message to the other consumer	
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'handle_action',
						'action': 'move',
						'move': data['move'],
						'sender': self.channel_name
					}
				)
		elif action == 'pass':
			#check if the players attribute exists 
			if hasattr(self, 'players'):
				self.players[self.game.turn].sense = 'pass'
				self.players[self.game.turn].move = 'pass'
			else:		
				#send the message to the other consumer		
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'handle_action',
						'action': 'pass',
						'sender': self.channel_name
					}
				)
		elif action == 'resign':
			#check if the players attribute exists 
			if hasattr(self, 'players'):
				self.game.resign()
				self.game.end()
				await self.players[self.game.turn].handle_game_end(self.game.get_winner_color(), self.game.get_win_reason(), self.game.get_game_history())
				await self.players[not self.game.turn].handle_game_end(self.game.get_winner_color(), self.game.get_win_reason(), self.game.get_game_history())
			else:	
				#send the message to the other consumer			
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'handle_action',
						'action': 'resign',
						'sender': self.channel_name
					}
				)
		elif action == 'get_active_timer':
			if hasattr(self, 'players'):
				color = 'w' if self.game.turn == chess.WHITE else 'b'

				#send to the other consumer's channel if it was the one to request the timer
				#otherwise send the data to its own channel
				sender = data.get('sender', self.channel_name)
				await self.channel_layer.send(
					sender,
					{
						'type': 'game_message',
						'message': 'time left',
						'color': color,
						'time': self.game.get_seconds_left()
					}
				)
			else:
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'handle_action',
						'action': 'get_active_timer',
						'sender': self.channel_name
					}
				)
		else:
			print('invalid action')


	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)

	#this method is called only for the consumer instance of the player class sending the message
	async def game_message(self, event):
		#send the messages from the players to the client
		await self.send(text_data=json.dumps(event))

	async def start_game(self, seconds):
		#the first consumer will not directly handle the game
		if len(self.channel_layer.groups.get(self.room_group_name, [])) < 2:
			await self.send(text_data=json.dumps({
				'message': 'waiting for opponent'
			}))
			return

		self.game = LocalGame(seconds_per_player=seconds)
		self.players = []
		self.player_names = []
		#pick a random color for the first player
		color = random.choice([chess.WHITE, chess.BLACK])
		
		for channel in self.channel_layer.groups[self.room_group_name]:
			player = HumanPlayer(channel, self.game)
			self.players.append(player)
			#TODO:find a way to get the player names from the db
			self.player_names.append(player.__class__.__name__)

		#if players[0] is white reverse the players and player_names lists to match the colors
		if color == chess.WHITE:
			self.players.reverse()
			self.player_names.reverse()

		#store the players in the game
		self.game.store_players(self.player_names[chess.WHITE], self.player_names[chess.BLACK])
		
		await self.players[0].handle_game_start(chess.BLACK, self.game.board, self.player_names[1])
		await self.players[1].handle_game_start(chess.WHITE, self.game.board, self.player_names[0])

		self.game.start()

		first_ply = True

		while not self.game.is_over():
			#get possible actions on this turn
			sense_actions = self.game.sense_actions()
			move_actions = self.game.move_actions()

			#get the result of the opponent's move, only returns a square if a piece was captured
			capture_square = self.game.opponent_move_results() if not first_ply else None
	
			try:
				await self.play_human_turn(self.players[self.game.turn], capture_square=capture_square, move_actions=move_actions, first_ply=first_ply)
				first_ply = False
			except TimeoutError:
				break
		
	async def play_human_turn(self, player, capture_square, move_actions, first_ply):
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
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'game_message',
				'message': 'turn ended',
				'color': 'w' if self.game.turn == chess.WHITE else 'b',
				'my_time': time_left,
				'opponent_time': self.game.get_seconds_left(),
			}
		)

	async def game_message(self, event):
		#send the game start message to the players
		await self.send(text_data=json.dumps(event))