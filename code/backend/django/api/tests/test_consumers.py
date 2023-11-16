import json
import chess
from django.test import TestCase
from channels.testing import WebsocketCommunicator
from api.consumers import GameConsumer, HumanPlayer
from reconchess import LocalGame, chess, WinReason
from reconchess.bots.random_bot import RandomBot

class TestGameConsumer(TestCase):
	async def connect(self):
		communicator = WebsocketCommunicator(GameConsumer.as_asgi(), "/ws/game")
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		return communicator

	async def test_receive_start_game(self):
		communicator = await self.connect()
		await communicator.send_json_to({
			'action': 'start_game'
		})
		response = await communicator.receive_json_from()
		self.assertEqual(response['color'], 'white')
		self.assertEqual(response['board'], chess.STARTING_FEN)

	
		response = await communicator.receive_json_from()
		self.assertEqual(response['message'], 'opponent_capture')
		response = await communicator.receive_json_from()
		self.assertEqual(response['message'], 'your turn to sense')
		await communicator.send_json_to({'action': 'sense', 'sense': 'd1'})

		response = await communicator.receive_json_from()
		self.assertEqual(response['message'], 'your turn to move')
		await communicator.send_json_to({'action': 'move', 'move': 'd2e2'})	
		self.assertEqual(await communicator.receive_json_from(), {'message': 'invalid move'})
		await communicator.send_json_to({'action': 'move', 'move': 'g1h3'})
		response = await communicator.receive_json_from()
		self.assertEqual(response, {'test': 'test'})

		await communicator.send_json_to({'action': 'resign'})
		response = await communicator.receive_json_from()
		self.assertEqual(response['message'], 'game over')

		await communicator.disconnect()

