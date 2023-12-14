import { updateTimer, stop_timer, start_timer, set_timer } from '../js/timer.js';
import { showSense, showSideToMove, showGameOver, illegalMove, haveEaten, lightsOn, lightsOff, makeOpponentMove, flipSide} from '../js/board.js';

var light = false
export let valid_moves = []
export let player_color = null
let currentTime;

export function createWebsocket(game, player_timer, opponent_timer) {
	const WEBSOCKET_URL = window.location.hostname === "localhost" ? 'ws://localhost:8000/ws/game' : 'wss://silverbullets.rocks/ws/game'
	const socket = new WebSocket(WEBSOCKET_URL);
	socket.onopen = function () {
		console.log('websocket is connected ...')
	}
	
	socket.onmessage = function (event) {
		var data = JSON.parse(event.data)

		console.log(data)
		switch (data.message) { //metodi da lib front chess.js e chessboard.js
			case 'game started':
				console.log('start game')
				game.is_over = false;
				console.log(player_timer)

				set_timer(data.time, player_timer);
				set_timer(data.time, opponent_timer);

				player_color = data.color;

				console.log(player_color)
				flipSide(player_color);
				if (player_color === 'b') {
					showSideToMove('w');
					start_timer(data.time, opponent_timer)
				}
				break;
			case 'opponent move':
				// It is better to check if the turn is w/b alonside fen, but it should go for now.
				// The problem is basically that given the fact that game.move() is not used anymore, 
				// the turn (from game.turn()) is not automatically updated, we should do it manually.
				stop_timer();
				//use the information from the backend to update the board in the frontend
				let board = data.board
				makeOpponentMove(board)
				if (data.capture_square != null) {
					haveEaten('w')
					lightsOff();
				}
				break;

			case 'your turn to sense':
				console.log('your turn to sense')
				// data.time qui non é definito
				console.log('this is current time: ' + currentTime)
				start_timer(data.time, player_timer);
				showSense()
				console.log(data.color);
				lightsOn(data.color);
				break;
			case 'your turn to move':
				showSideToMove(data.color);

				valid_moves = data.move_actions;
				console.log('your valid moves' + valid_moves)
				console.log('your turn to move')
				light = true;
				break;
			case 'invalid move':

				console.log('invalid move')
				// So, this is a bit tricky. Basically, when the pawn moves diagonally (cause it is possible by its property) 
				// but if there is no piece the move is and should be illegal. Unfortunately, the move is still valid in 
				// valid_moves array so the message "Illegal move" is not shown.

				illegalMove()
				// undoMove();
				break;
			case 'move result':
				console.log('move result');
				game.load(data.board);
				if (data.captured_opponent_piece) haveEaten('b')
				break;
			case 'time left':
				console.log('time left')
				let timer =  data.color === player_color ? player_timer : opponent_timer
				//update the active timer with the time left sent from the backend
				if (!game.is_over) {
					start_timer(Math.floor(data.time), timer);
				}
				else
					set_timer(Math.floor(data.time), timer);
				break
			case 'turn ended':
				console.log('turn started')
				console.log("COLOR:", data.color)
				showSideToMove(data.color);
				//the turn is over, get the time left and stop the timer
				stop_timer();
				//round the remaining time down to the nearest integer

				set_timer(Math.floor(data.my_time), player_timer);
				set_timer(Math.floor(data.opponent_time), opponent_timer);

				start_timer(data.opponent_time, opponent_timer)

				break;
			case 'game over':
				showGameOver(data.reason, data.winner)
				stop_timer();
				game.load(data.board);
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