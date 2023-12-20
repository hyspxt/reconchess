import random
import chess
from django.test import TestCase
from channels.testing import WebsocketCommunicator
from api.consumers import GameConsumer
from reconchess import chess

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
		response = await communicator.receive_json_from()
		self.assertEqual(response, {
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
			'seconds': 3,
			'bot': 'random'
		})

		response = await communicator.receive_json_from()
		response = await communicator.receive_json_from()
		self.assertTrue(response['message'] == 'your turn to sense')
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

		response = await communicator.receive_json_from()
		self.assertEqual(response['message'], 'turn ended')

		response = await communicator.receive_json_from()
		board = chess.Board()
		board.push(chess.Move.from_uci('a2a3'))
		self.assertEqual(response, {
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

		response = await communicator.receive_json_from()
		self.assertEqual(response['color'], 'w')
		self.assertEqual(response['board'], chess.STARTING_FEN)

		response = await communicator.receive_json_from()
		self.assertTrue(response['message'] == 'your turn to sense')

		await communicator.send_json_to(({'action': 'pass'}))
		response = await communicator.receive_json_from()

		self.assertEqual(response['message'], 'turn ended')

		response = await communicator.receive_json_from()
		self.assertEqual(response['message'], 'move result')
		self.assertEqual(response['requested_move'], 'None')

		await communicator.disconnect()

	async def test_resign(self):
		communicator = await self.connect()
		await communicator.send_json_to({
			'action': 'start_game'
		})

		response = await communicator.receive_json_from()
		self.assertEqual(response['color'], 'w')
		self.assertEqual(response['board'], chess.STARTING_FEN)

		response = await communicator.receive_json_from()
		self.assertTrue(response['message'] == 'your turn to sense')

		await communicator.send_json_to(({'action': 'resign'}))
		response = await communicator.receive_json_from()

		self.assertEqual(response['message'], 'game over')

		await communicator.disconnect()

	async def test_rematch(self):
		communicator = await self.connect()
		await communicator.send_json_to({
			'action': 'start_game'
		})

		response = await communicator.receive_json_from()
		self.assertEqual(response['color'], 'w')
		self.assertEqual(response['board'], chess.STARTING_FEN)

		response = await communicator.receive_json_from()
		self.assertTrue(response['message'] == 'your turn to sense')

		await communicator.send_json_to(({'action': 'resign', 'rematch': True}))
		response = await communicator.receive_json_from()

		self.assertEqual(response['message'], 'game over')

		response = await communicator.receive_json_from()
		self.assertEqual(response['message'], 'game started')

		await communicator.disconnect()

	async def test_timeout(self):
		communicator = await self.connect()
		await communicator.send_json_to({
			'action': 'start_game',
			'seconds': 3
		})

		response = await communicator.receive_json_from()
		self.assertEqual(response['color'], 'w')
		self.assertEqual(response['board'], chess.STARTING_FEN)

		response = await communicator.receive_json_from()
		self.assertTrue(response['message'] == 'your turn to sense')
	

		response = await communicator.receive_json_from(timeout=5)
		self.assertEqual(response['message'], 'game over')

		await communicator.disconnect()
