from django.test import TransactionTestCase
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from api.routing import websocket_urlpatterns
import chess

# create a new application for testing
test_application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

turn_ended = 'turn ended'
game_started = 'game started'
game_over = 'game over'

class TestMultiplayer(TransactionTestCase):
	async def connect(self, room_name):
		communicator = WebsocketCommunicator(test_application, f"/ws/multiplayer/{room_name}")

		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		return communicator
	
	async def start_game(self, communicator):
		await communicator.send_json_to({
			'action': 'start_game'
		})

		response = await communicator.receive_json_from()

		return response
	
	async def get_colors(self, communicator1, communicator2):
		
		response = await communicator1.receive_json_from()
		white_player = communicator1 if response['color'] == 'w' else communicator2
		black_player = communicator2 if response['color'] == 'w' else communicator1

		return white_player, black_player
	
	async def begin_black_turn(self, black_player, board):
		response = await black_player.receive_json_from()
		self.assertEqual(response['message'], turn_ended)

		self.assertDictContainsSubset({
			'message': 'opponent move',
			'board': board.fen()
		}, await black_player.receive_json_from())
			
	async def test_start(self):
		communicator1 = await self.connect('start')
		self.assertEqual(await self.start_game(communicator1), {
			'message': 'waiting for opponent'
		})

		communicator2 = await self.connect('start')
		response = await self.start_game(communicator2)
		# check the start message of both players
		self.assertDictContainsSubset({
			'message': game_started,
			'board': chess.STARTING_FEN,
			'time': 900
		}, response)

		#set the expected color communicator1 depending on the color of communicator2
		color1 = 'w' if response['color'] == 'b' else 'b'
		
		self.assertDictContainsSubset({
			'message': game_started,
			'board': chess.STARTING_FEN,
			'color': color1, 
			'time': 900
		}, await communicator1.receive_json_from())

		await communicator1.disconnect()
		# let the second communicator receive the sense message if it's his turn
		if(color1 == 'b'):
			await communicator2.receive_json_from()

		#check if disconnection is treated correctly
		self.assertDictContainsSubset({
			'message': game_over,
			'reason': ('white ' if color1 == 'w' else 'black ') + 'resigned'
		}, await communicator2.receive_json_from())
		await communicator2.disconnect() 
		

	async def test_turn(self):
		communicator1 = await self.connect('turn')
		await self.start_game(communicator1)
		communicator2 = await self.connect('turn')
		await self.start_game(communicator2)

		white_player, black_player = await self.get_colors(communicator1, communicator2)

		board = chess.Board()
		for player in [white_player, black_player]:
			if player == black_player: await self.begin_black_turn(black_player, board)
	
			self.assertDictContainsSubset({
				'message': 'your turn to sense',
				'color': 'w' if player == white_player else 'b'
			}, await player.receive_json_from())

			await white_player.send_json_to({
				'action': 'sense',
				'sense': 'a1'
			})

			response = await player.receive_json_from()
			self.assertDictContainsSubset({
				'message': 'your turn to move',
				'color': 'w' if player == white_player else 'b',
			}, response)

			move = response['move_actions'][0]
			await white_player.send_json_to({
				'action': 'move',
				'move': move
			})
			
			board.push(chess.Move.from_uci(move))
			self.assertDictContainsSubset({
				'message': 'move result',
				'requested_move': move,
				'taken_move': move,
				'board': board.fen()
				}, await player.receive_json_from())

			response = await player.receive_json_from()
			self.assertEqual(response['message'], turn_ended)
		
		response = await white_player.receive_json_from()
		self.assertEqual(response['message'], turn_ended)
		
		self.assertDictContainsSubset({
			'message': 'opponent move',
			'board': board.fen()
		}, await white_player.receive_json_from())

		await communicator1.disconnect()
		await communicator2.disconnect()

	async def test_pass(self):
		communicator1 = await self.connect('pass')
		await self.start_game(communicator1)

		communicator2 = await self.connect('pass')
		await self.start_game(communicator2)

		white_player, black_player = await self.get_colors(communicator1, communicator2)
		board = chess.Board()
		for player in [white_player, black_player]:
			if player == black_player: await self.begin_black_turn(black_player, board)

			#wait for the sense message
			await player.receive_json_from()
			await player.send_json_to({
				'action': 'pass'
			})

			board.push(chess.Move.null())
			self.assertDictContainsSubset({
				'message': 'move result',
				'requested_move': 'None',
				'taken_move': 'None',
				'board': board.fen()
				}, await player.receive_json_from())
			
			response = await player.receive_json_from()
			self.assertEqual(response['message'], turn_ended)

		await communicator1.disconnect()
		await communicator2.disconnect()
		
	async def test_resign(self):
		communicator1 = await self.connect('resign')
		await self.start_game(communicator1)

		communicator2 = await self.connect('resign')
		await self.start_game(communicator2)

		white_player, _ = await self.get_colors(communicator1, communicator2)
		await white_player.receive_json_from()
		await white_player.send_json_to({
			'action': 'resign'
		})

		self.assertDictContainsSubset({
			'message': game_over,
			'reason': 'white resigned'
		}, await communicator1.receive_json_from())

		self.assertDictContainsSubset({
			'message': game_over,
			'reason': 'white resigned'
		}, await communicator2.receive_json_from())

		await communicator1.disconnect()
		await communicator2.disconnect()

	async def test_rematch(self):
		communicator1 = await self.connect('rematch')
		await self.start_game(communicator1)

		communicator2 = await self.connect('rematch')
		await self.start_game(communicator2)
		white, _ = await self.get_colors(communicator1, communicator2)
		#receive the sense message for white
		await white.receive_json_from()

		for resignee in [communicator1, communicator2]:
			opponent = communicator2 if resignee == communicator1 else communicator1
			await resignee.send_json_to({
				'action': 'resign',
				'rematch': True
			})

			self.assertDictContainsSubset({
				'message': game_over,
			}, await resignee.receive_json_from())

			# get the game over and rematch messages, they may come in any order
			response = await opponent.receive_json_from()
			self.assertTrue(response['message'] == game_over or response['message'] == 'rematch')
			response = await opponent.receive_json_from()
			self.assertTrue(response['message'] == game_over or response['message'] == 'rematch')

			await opponent.send_json_to({
				'action': 'rematch',
				'accept': True
			})

			self.assertDictContainsSubset({
				'message': game_started
			}, await communicator2.receive_json_from())
			white, _ = await self.get_colors(communicator1, communicator2)
			#receive the sense message for white
			await white.receive_json_from()

		await communicator1.disconnect()
		await communicator2.disconnect()

	async def test_timeout(self):
		communicator1 = await self.connect('timeout')
		await communicator1.send_json_to({
			'action': 'start_game',
			'seconds': 1
		})
		await communicator1.receive_json_from()

		communicator2 = await self.connect('timeout')
		await communicator2.send_json_to({'action': 'start_game'})
		await communicator2.receive_json_from()

		white, _ = await self.get_colors(communicator1, communicator2)
		#receive the sense message for white
		await white.receive_json_from()
		self.assertDictContainsSubset({
			'message': game_over,
			'reason': 'timeout'
		}, await communicator2.receive_json_from(timeout=1.5))
		self.assertDictContainsSubset({
			'message': game_over,
			'winner': False,
			'reason': 'timeout'
		}, await communicator1.receive_json_from(timeout=1.5))

		await communicator1.disconnect()
		await communicator2.disconnect()