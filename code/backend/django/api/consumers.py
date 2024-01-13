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
from django.contrib.auth.models import AnonymousUser
from .models import Matches
from .tables_interactions import update_loc_stats, save_match_results, update_elo

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
		self.game_task = None
		await self.accept()

	async def disconnect(self, close_code):
		#treat the player as if they resigned if they disconnect
		self.game._resignee = self.player.color
		await self.end_game()
		self.player = None
		self.bot = None

	async def receive(self, text_data):
		data = json.loads(text_data)
		await self.handle_action(data)
	
	async def handle_action(self, data):
		action = data['action']
		if action == 'start_game':
			seconds = int(data.get('seconds', 900))
			#get the correct chess.COLORS value based on the color string
			color = chess.COLOR_NAMES.index(data.get('color', 'white')) 
			bot = available_bots.get(data.get('bot', 'random'))
			#create a separete task for the game loop and keep a refernce to it
			self.game_task = asyncio.create_task(self.start_game(seconds, color, bot))
		elif action == 'sense':
			self.player.sense = data['sense']
		elif action == 'move':
			self.player.move = data['move']
		elif action == 'pass':
			# the player can only pass during their turn
			if self.game.turn == self.player.color:
				self.player.sense = 'pass'
				self.player.move = 'pass'
		elif action == 'resign':
			if(not self.game.is_over()):
				#only the player can resign through a message
				self.game._resignee = self.player.color 
				await self.end_game()

			#restart the game if the player wants to rematch
			if data.get('rematch', False): 
				#start a new game loop task
				self.game_task = asyncio.create_task(self.start_game(seconds=self.game.seconds_per_player, player_color=self.player.color, bot_constructor=type(self.bot)))
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
		event.pop('type')
		#send the messages from the player to the client
		await self.send(text_data=json.dumps(event))

	async def get_username(self):
		user = self.scope['user']
		if(user.is_authenticated):
			return user.username
		else:
			print('not logged in')

	async def end_game(self):
		#avoid trying to end a game that's already over
  
		self.game.end()
		winner_color = self.game.get_winner_color()
		win_reason = self.game.get_win_reason()
		game_history = self.game.get_game_history()
		
		await self.player.handle_game_end(winner_color, win_reason, game_history)
		self.bot.handle_game_end(winner_color, win_reason, game_history)
		
		#stop the game loop task if it exists
		if self.game_task is not None:
			self.game_task.cancel()
			self.game_task = None

	
	async def start_game(self, seconds, player_color: chess.COLORS, bot_constructor):
		#initialize the game
		self.game = LocalGame(seconds_per_player=seconds)
		self.player = HumanPlayer(self.channel_name, self.game)
		self.bot = bot_constructor()

		#get the username if the player is authenticated otherwise use 'guest'
		if self.scope.get('user', AnonymousUser()).is_authenticated:
			player_name = self.scope['user'].username
		else: 
			player_name = 'guest'		
		#save the player names in a list
		names = [self.bot.__class__.__name__, player_name]
		#make sure that the list's order follows the order of chess.COLORS
		if player_color == chess.BLACK:
			names.reverse()
		#save the players in the game
		self.game.store_players(names[chess.WHITE], names[chess.BLACK])
		
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
				except TimeoutError:
					break
			else:
				await sync_to_async(self.play_bot_turn)(capture_square=capture_square, sense_actions=sense_actions, move_actions=move_actions)

			first_ply = False
		
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
		
		self.bot.handle_move_result(requested_move, taken_move, capture_square is not None, capture_square)

		self.game.end_turn()


class MultiplayerGameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = 'game_%s' % self.room_name

		await self.accept()
		#check if the room is full
		if(len(self.channel_layer.groups.get(self.room_group_name, [])) < 2):
			# Join room group
			await self.channel_layer.group_add(
				self.room_group_name,
				self.channel_name
			)
			#the second consumer will start the game
			if(len(self.channel_layer.groups.get(self.room_group_name, [])) == 2):
				self.game = None
		else:
			await self.send(text_data=json.dumps({
				'message': 'room full'
			}))
		
	async def receive(self, text_data):
		data = json.loads(text_data)
		await self.handle_action(data)

	async def handle_action(self, data):
		#get the name of the channel that sent the message if it exists
		sender = data.get('sender', None)

		#ignore messages sent by the same consumer
		if sender == self.channel_name:
			return
		
		action = data['action']

		if action == 'start_game':
			seconds = int(data.get('seconds', 900) or 900)
			self.game_task = asyncio.create_task(self.start_game(seconds))
		elif action == 'sense':
			#check if the players attribute exists 
			if hasattr(self, 'players'):
				self.players[self.game.turn].sense = data['sense']
			#the game has not started yet
			elif hasattr(self, 'game') and self.game is None:
				return
			else:

				#send the message to the other consumer specifying the sender
				data.update({'type': 'handle_action', 'sender': self.channel_name})
				await self.channel_layer.group_send(self.room_group_name, data)
		elif action == 'move':
			#check if the players attribute exists 
			if hasattr(self, 'players'):
				self.players[self.game.turn].move = data['move']
			#the game has not started yet
			elif hasattr(self, 'game') and self.game is None:
				return
			else:			
				#send the message to the other consumer	specifying the sender
				data.update({'type': 'handle_action', 'sender': self.channel_name})
				await self.channel_layer.group_send(self.room_group_name, data)
		elif action == 'pass':
			if hasattr(self, 'players'):
				#get the channel name of the sender
				sender = data.get('sender', self.channel_name)
				sender_color = self.player_colors[sender]
				#only pass the turn if the sender is the one whose turn it is
				if sender_color != self.game.turn:
					return
				
				self.players[self.game.turn].sense = 'pass'
				self.players[self.game.turn].move = 'pass'
			#the game has not started yet
			elif hasattr(self, 'game') and self.game is None:
				return
			#this consumer is not the one handling the game
			else:		
				#send the message to the other consumer	specifying the sender
				data.update({'type': 'handle_action', 'sender': self.channel_name})
				await self.channel_layer.group_send(self.room_group_name, data)
		elif action == 'resign':
			#check if the players attribute exists 
			if hasattr(self, 'players'):
				if (not self.game.is_over()):
					#set the resignee to the appropriate color before ending the game
					self.game._resignee = self.player_colors[data.get('sender', self.channel_name)] 
					await self.end_game()
			#the game has not started yet
			elif hasattr(self, 'game') and self.game is None:
				return
			else:
				#add the sender's channel name to the data
				data.update({'type': 'handle_action', 'sender': self.channel_name})
				#send the message to the other consumer, the game will be stopped		
				await self.channel_layer.group_send(self.room_group_name, data)	

			#both consumers should handle rematch requests the same way after the game has ended
			#the request should be sent to the group only once
			if data.get('rematch', False) and data.get('sender', self.channel_name) == self.channel_name:
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'game_message',
						'message': 'rematch',
						'sender': self.channel_name
					}
				)
		#the game has ended and the players have agreed to a rematch
		elif action == 'rematch':
			if hasattr(self, 'players') and data.get('accept', False):
				current_match = await sync_to_async(Matches.objects.filter)(room_name=self.room_group_name)
				current_match = await sync_to_async(current_match.first)()
				player1 = current_match.player1
				player2 = current_match.player2
				seconds = current_match.seconds
				match = await sync_to_async(Matches.objects.create)(room_name = self.room_group_name, player1=player1, player2=player2, seconds=seconds)
				await sync_to_async(match.save)()
				self.game_task = asyncio.create_task(self.start_game(seconds))
			elif not data.get('accept', False):
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'game_message',
						'message': 'rematch declined',
						'sender': self.channel_name
					}
				)
			else:
				#add the sender's channel name to the data
				data.update({'type': 'handle_action', 'sender': self.channel_name})
				#send the response to the rematch request to the other consumer
				await self.channel_layer.group_send(
					self.room_group_name,
					data
				)
		elif action == 'get_active_timer':
			if hasattr(self, 'players'):
				color = 'w' if self.game.turn == chess.WHITE else 'b'
				#send to the requesting player only
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
			#the game has not started yet
			elif hasattr(self, 'game') and self.game is None:
				return
			else:
				#add the sender's channel name to the data
				data.update({'type': 'handle_action', 'sender': self.channel_name})
				await self.channel_layer.group_send(
					self.room_group_name,
					data
				)
		else:
			print('invalid action')

	async def disconnect(self, close_code):
		#this consumer is not handling the game 
		if (not hasattr(self, 'players')):
			#send a message to the other consumer to inform it that the player has disconnected
			#the other consumer will handle it as if the player resigned
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'handle_action',
					'action': 'resign',
					'sender': self.channel_name
				}
			)
		else: 
			#treat the player as if they resigned if they disconnect
			self.game._resignee = self.player_colors[self.channel_name]
			await self.end_game()
			self.player = None
			self.players = None
			self.player_colors = None
	
		#remove the consumer from the group
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)

	#this method is called only for the consumer instance of the player class sending the message
	async def game_message(self, event):
		#ignore rematch messages sent by the same consumer
		if((event['message'] == 'rematch' or event['message'] == 'rematch declined') and event['sender'] == self.channel_name):
			return
		#remove the sender and type keys from the event
		event.pop('sender', None)
		event.pop('type')
		#send the messages from the players to the client
		await self.send(text_data=json.dumps(event))


	async def end_game(self):
		self.game.end()

		try:
			# Cerca un match con il nome della stanza
			room_name = self.room_group_name
			match = await sync_to_async(Matches.objects.get)(room_name=room_name, finished=False)
		except Matches.DoesNotExist:
			# il match non esiste o è già stato terminato
			return
		
		winner_color = self.game.get_winner_color()
		win_reason = self.game.get_win_reason()
		game_history = self.game.get_game_history()

		for player in self.players:
			await player.handle_game_end(winner_color, win_reason, game_history)

		#insert data in db here
		#save the match results in the database
		#aggiorno dati vincitore e perdente nel db
		winner = self.player_names[winner_color]
		loser = self.player_names[not winner_color]
		
		draw = False
		if winner_color == None and win_reason == None:
			draw = True
		#only update the player's information if they are logged in
		if(winner != 'guest'):
			await update_loc_stats(winner, True, draw)
			await update_elo(winner, loser, True, draw)
		if(loser != 'guest'):
			await update_loc_stats(loser, False, draw)
			await update_elo(loser, winner, False, draw)
		
		await save_match_results(match, winner, loser, draw)

		#stop the game loop task if it exists
		if self.game_task is not None:
			self.game_task.cancel()
			self.game_task = None


	async def start_game(self, seconds):
		#the first consumer will not directly handle the game
		if len(self.channel_layer.groups.get(self.room_group_name, [])) < 2:
			await self.send(text_data=json.dumps({
				'message': 'waiting for opponent'
			}))
			user = 'guest'
			if(self.scope['user'].is_authenticated):
				user = self.scope['user'].username
			match = await sync_to_async(Matches.objects.create)(room_name = self.room_group_name, player1=user, seconds=seconds)
			await sync_to_async(match.save)()
			
			return
		
		match = await sync_to_async(Matches.objects.get)(room_name=self.room_group_name, finished=False)
		if self.scope.get('user', AnonymousUser()).is_authenticated:
			user = self.scope['user'].username
		else:
			user = 'guest'

		match.player2 = user
		await sync_to_async(match.save)()

		seconds = match.seconds

		self.game = LocalGame(seconds_per_player=seconds)
		self.players = []
		self.player_names = [match.player1, match.player2]
		#dictionary using channel names as keys for player colors
		self.player_colors = {}

		selected_color = None

		for channel in self.channel_layer.groups[self.room_group_name]:
			#pick a random color for the first player
			if selected_color is None:
				selected_color = random.choice(chess.COLORS)
			#the second player gets the opposite color
			else:
				selected_color = not selected_color

			#instantiate a player for each channel
			player = HumanPlayer(channel, self.game)
			self.players.append(player)
			self.player_colors[channel] = selected_color

		#if the second player is black reverse the players and player_names lists to match the colors' values (False, True)
		if selected_color == chess.BLACK:
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
			move_actions = self.game.move_actions()

			#get the result of the opponent's move, only returns a square if a piece was captured
			capture_square = self.game.opponent_move_results() if not first_ply else None
	
			try:
				await self.play_human_turn(self.players[self.game.turn], capture_square=capture_square, move_actions=move_actions, first_ply=first_ply)
				first_ply = False
			except TimeoutError:
				break

		await self.end_game()
				
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