import json
import asyncio
import chess
from reconchess import Player, Color, WinReason, GameHistory
from reconchess.types import *
from channels.layers import get_channel_layer

class HumanPlayer(Player):
	def __init__(self, channel_name, game):
		self.channel_layer = get_channel_layer()
		self.channel_name = channel_name
		self.game = game 
		self.color = None
		self.move = None
		self.sense = None
		self.finished = True

	async def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
		self.color = color
		self.color_name = 'w' if color == chess.WHITE else 'b'
		await self.channel_layer.send(
			self.channel_name,
			{
				'type': 'game.message',
				'message': 'game started',
				'board': board.fen(),
				'color': self.color_name,
				'opponent_name': opponent_name,
				'time': self.game.get_seconds_left()
			})
	
	async def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[chess.Square]):
		await self.channel_layer.send(
			self.channel_name,
			{
				'type': 'game.message',
				'message': 'opponent move',
				'capture_square': capture_square,
				'board': self.game.board.fen()
			})
	
	async def choose_sense(self) -> chess.Square | None:
		await self.channel_layer.send(
			self.channel_name,
			{
				"type": "game.message",
				'message': 'your turn to sense',
				'color': self.color_name,
				'time': self.game.get_seconds_left()
			})

		#waits for the client to send a sense action
		while self.sense is None:
			if(self.game.get_seconds_left() <= 0):
				raise TimeoutError('player ran out of time')
			await asyncio.sleep(0.1)

		if self.sense != 'pass': 
			#convert the received move to a chess.Move object
			sense = chess.parse_square(self.sense)
		else:
			sense = None
		
		self.sense = None
		return sense

	async def choose_move(self, move_actions: List[chess.Move]) -> chess.Move | None:
		if self.move != 'pass':
			await self.channel_layer.send(
				self.channel_name,
				{
					'type': 'game.message',
					'message': 'your turn to move',
					'color': self.color_name,
					'move_actions': [str(move) for move in move_actions]
				})

		#waits for the client to send a valid move
		while self.move is None or (self.move != 'pass' and chess.Move.from_uci(self.move) not in move_actions):
			if self.move is not None:
				await self.channel_layer.send(
					self.channel_name,
					{
						'type': 'game.message',
						'message': 'invalid move',
						'board': self.game.board.fen()
					})
				self.move = None
				
			if(self.game.get_seconds_left() <= 0):
				raise TimeoutError('player ran out of time')
			
			#wait for the client to send a move
			await asyncio.sleep(0.1)
		
	
		if self.move != 'pass': 
			#convert the received move to a chess.Move object
			move = chess.Move.from_uci(self.move)
			#make sure that pass doesn't remain as the sense action if the player passed after sensing
			self.sense = None
		else:
			move = None
		
		self.move = None

		return move
	
	async def handle_move_result(self, requested_move: chess.Move | None, taken_move: chess.Move | None, captured_opponent_piece: bool, capture_square: Square | None):
		#finish the turn
		self.finished = True
		#send the move results to the client
		await self.channel_layer.send(
			self.channel_name,
			{
				'type': 'game.message',
				'message': 'move result',
				'requested_move': str(requested_move),
				'taken_move': str(taken_move),
				'captured_opponent_piece': captured_opponent_piece,
				'capture_square': str(capture_square),
				'board': self.game.board.fen()
			})

	
	async def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason], game_history: GameHistory):
		self.finished = True
		win_reason_messages = {
        	WinReason.KING_CAPTURE: 'the king was captured',
        	WinReason.TIMEOUT: 'timeout',
        	WinReason.RESIGN: ('white ' if self.game._resignee else 'black ') + 'resigned',
        	WinReason.TURN_LIMIT: 'full turn limit exceeded',
        	WinReason.MOVE_LIMIT: 'full move limit exceeded',
        	None: 'game over'
    	}

		await self.channel_layer.send(
			self.channel_name,
			{
				'type': 'game.message',
				'message': 'game over',
				'winner': winner_color,
				'reason': win_reason_messages.get(win_reason),
                'board': self.game.board.fen()
			})
