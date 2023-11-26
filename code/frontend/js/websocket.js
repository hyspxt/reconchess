//define constant to allow local testing
const WEBSOCKET_URL = window.location.hostname === "localhost" ? 'ws://localhost:8000/ws/game' : 'wss://silverbullets.rocks/ws/game'

function createWebsocket() {
	const socket = new WebSocket(WEBSOCKET_URL)
	socket.onopen = function () {
		console.log('websocket is connected ...')
		socket.send(JSON.stringify({ action: 'start_game' }))
	}

	socket.onmessage = function (event) {
		data = JSON.parse(event.data)
		console.log(data)
		switch (data.message) { //metodi da lib front chess.js e chessboard.js
			case 'game started':
				console.log('start game')
				game.is_over = false;
				set_timer(data.time, 'my_timer');
				set_timer(data.time, 'opponent_timer');
				break;
			case 'opponent move':
				stop_timer();
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
				start_timer('my_timer')
				showSense()
				lightsOn();
				light = false;
				break;
			case 'your turn to move':
				showSideToMove();
				valid_moves = data.move_actions;
				console.log('your turn to move')
				break;
			case 'invalid move':
				console.log('invalid move')
				illegalMove()
				break;
			case 'move result':
				console.log('move result')
				game.load(data.board)
				if(data.captured_opponent_piece) haveEaten('b')
				break;
			case 'turn ended':
				console.log('turn ended')
				//the turn is over, get the time left and stop the timer
				stop_timer();
				//round the remaining time down to the nearest integer
				set_timer(Math.floor(data.my_time), 'my_timer');
				set_timer(Math.floor(data.opponent_time), 'opponent_timer',);

				start_timer('opponent_timer')

				break;
			case 'game over':
				console.log(data)
				showGameOver(data.reason, data.winner)
				stop_timer();
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