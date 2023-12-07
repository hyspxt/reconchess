import { updateTimer, stop_timer, start_timer, set_timer } from '/js/timer.js';
import { showSense, showSideToMove, showGameOver, illegalMove, haveEaten, lightsOn, lightsOff, makeOpponentMove } from '/js/board.js';

var light = false
export let valid_moves = []

export function createWebsocket(game, element) {
	const socket = new WebSocket('wss://silverbullets.rocks/ws/game') //'silverbullets.rocks/ws/game'
	socket.onopen = function () {
		console.log('websocket is connected ...')
		socket.send(JSON.stringify({ action: 'start_game' }))
	}

	socket.onmessage = function (event) {
		var data = JSON.parse(event.data)
		console.log(data)
		const time = { minutes: 0, seconds: data.time };
		switch (data.message) { //metodi da lib front chess.js e chessboard.js
			case 'game started':
				console.log('start game')
				game.is_over = false;

				
				set_timer(data.time, 'my_timer');
				set_timer(data.time, 'opponent_timer');

				set_timer(time, element);
				break;
			case 'opponent move':
				stop_timer(element);
				showSideToMove()
				//use the information from the backend to update the board in the frontend
				let board = data.board
				makeOpponentMove(board)
				if (data.capture_square != null) {
					haveEaten('w')
					lightsOff()
				}
				break;
			case 'your turn to sense':
				console.log('your turn to sense')
				start_timer(time, element)
				showSense()
				lightsOn();
				break;
			case 'your turn to move':
				showSideToMove();

				valid_moves = data.move_actions;
				console.log('your valide moves' + valid_moves)
				console.log('your turn to move')
				break;
			case 'invalid move':
				console.log('invalid move')
				illegalMove()
				undoMove();
				break;

			case 'move result':
				console.log('move result');
				if (data.captured_opponent_piece) haveEaten('b')
				break;
			//case 'time left':
			//	console.log('time left')
			//	set_timer(data.game.get_seconds_left())
			//	start_timer(time, end)
			case 'turn ended':
				console.log('turn ended')
				//the turn is over, get the time left and stop the timer
				stop_timer(Element);
				//round the remaining time down to the nearest integer
				set_timer(Math.floor(data.my_time), 'my_timer');
				set_timer(Math.floor(data.opponent_time), 'opponent_timer',);

				start_timer('opponent_timer')

				break;
			case 'game over':
				console.log(data)
				showGameOver(data.reason, data.winner)
				stop_timer(element);
				//tell the frontend library to stop the game
				game.is_over = true;
				light = true;
				break;
			default:
				break;
		}


	}
	socket.onclose = function (event) {
		console.log('websocket is disconnected ...')
	}
	return socket
}