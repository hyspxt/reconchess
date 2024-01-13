from django.test import TestCase
from channels.testing import WebsocketCommunicator
from api.consumers import GameConsumer
from server.asgi import application
import chess

game_over = 'game over'

class TestSingleplayer(TestCase):
	async def connect(self):
		communicator = WebsocketCommunicator(GameConsumer.as_asgi(), "/ws/game")
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		return communicator
	
	async def test_start(self):
		communicator = await self.connect()
		await communicator.send_json_to({
			'action': 'start_game',
			'color': 'white',
			'bot': 'random'
		})

		self.assertEqual(await communicator.receive_json_from(), {
			'message': 'game started',
			'board': chess.STARTING_FEN,
			'color': 'w',
			'opponent_name': 'RandomBot',
			'time': 900

		})
		await communicator.disconnect()

	async def test_turn(self):
		communicator = await self.connect()
		await communicator.send_json_to({
			'action': 'start_game',
			'color': 'white',
			'bot': 'random'
		})
		
		# await the game started message, it's not necessary to test it as it is tested in test_start
		await communicator.receive_json_from()
		
		self.assertDictContainsSubset({'message': 'your turn to sense'}, await communicator.receive_json_from())
		await communicator.send_json_to({
			'action': 'sense',
			'sense': 'a1'
		})
		response = await communicator.receive_json_from()
		self.assertEqual(response['message'], 'your turn to move')
		await communicator.send_json_to({
			'action': 'move',
			'move': 'a2a3'
		})
		#make the selected move on a new board to compare it with the received board
		board = chess.Board()
		board.push(chess.Move.from_uci('a2a3'))

		response = await communicator.receive_json_from()
		self.assertEqual(response['message'], 'turn ended')

		self.assertEqual(await communicator.receive_json_from(), {
			'message': 'move result',
			'requested_move': 'a2a3',
			'taken_move': 'a2a3',
			'captured_opponent_piece': False,
			'capture_square': 'None',
			'board': board.fen()
		})

		response = await communicator.receive_json_from()
		self.assertEqual(response['message'], 'opponent move')

		await communicator.disconnect()

	async def test_pass(self):
		communicator = await self.connect()
		await communicator.send_json_to({
			'action': 'start_game'
		})
		# await the game started message, it's not necessary to test it as it is tested in test_start
		await communicator.receive_json_from()
		# await the sense message and send a pass action
		await communicator.receive_json_from()
		await communicator.send_json_to(({'action': 'pass'}))

		response = await communicator.receive_json_from()
		self.assertEqual(response['message'], 'turn ended')
		
		board = chess.Board()
		board.push(chess.Move.null())

		self.assertEqual(await communicator.receive_json_from(), {
			'message': 'move result',
			'requested_move': 'None',
			'taken_move': 'None',
			'captured_opponent_piece': False,
			'capture_square': 'None',
			'board': board.fen()
		})

		await communicator.disconnect()

	async def test_resign(self):
		communicator = await self.connect()
		await communicator.send_json_to({
			'action': 'start_game'
		})
		# receive the game started message and sense messages
		await communicator.receive_json_from()
		await communicator.receive_json_from()

		await communicator.send_json_to(({'action': 'resign'}))
		self.assertDictContainsSubset({
			'message': game_over,
			'winner': False,
			'reason': 'white resigned'
		}, await communicator.receive_json_from(), )

		await communicator.disconnect()

	async def test_rematch(self):
		communicator = await self.connect()
		await communicator.send_json_to({
			'action': 'start_game'
		})
		# receive the game started message and sense messages
		await communicator.receive_json_from()
		await communicator.receive_json_from()

		await communicator.send_json_to(({'action': 'resign', 'rematch': True}))
		self.assertDictContainsSubset({
			'message': game_over,
			'winner': False,
			'reason': 'white resigned'
		}, await communicator.receive_json_from(), )

		response = await communicator.receive_json_from()
		self.assertEqual(response['message'], 'game started')

		await communicator.disconnect()

	async def test_timeout(self):
		communicator = await self.connect()
		await communicator.send_json_to({
			'action': 'start_game',
			'seconds': 1
		})

		# receive the game started message and sense messages
		await communicator.receive_json_from()
		await communicator.receive_json_from()
	
		self.assertDictContainsSubset({
			'message': game_over,
			'winner': False,
			'reason': 'timeout'
		}, await communicator.receive_json_from(timeout=1.5))

		await communicator.disconnect()
