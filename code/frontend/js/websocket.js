function createWebsocket() {
	const socket = new WebSocket('ws://silverbullets.rocks/ws/gamegit ') //'silverbullets.rocks/ws/game'
	socket.onopen = function () {
		console.log('websocket is connected ...')
		socket.send(JSON.stringify({ action: 'start_game' }))
	}

	socket.onmessage = function (event) {
		data = JSON.parse(event.data)
		switch (data.message) { //metodi da lib front chess.js e chessboard.js
			case 'game started':
				console.log('start game')
				set_timer(data.time)
				break;
			case 'your turn to sense':
				console.log('your turn to sense')
				//TODO: this is a test, remove it when it's possible to sense from frontend
				socket.send(JSON.stringify({ action: 'sense', sense: 'a1' }))
				start_timer()
				break;
			case 'your turn to move':
				console.log('your turn to move')
				break;
			case 'invalid move':
				console.log('invalid move')
				undoMove();
				break;
			case 'opponent move':
				//use the information from the backend to update the board in the frontend
				let board = data.board
				makeOpponentMove(board)
				break;
			case 'move result':
				console.log('move result')
				//TODO: the information that comes from is possibly useless since the board updates itself
				//it could still be used to show captures in the frontend though
				break;
			case 'time left':
				console.log('time left')
				set_timer(data.game.get_seconds_left())
				start_timer()
			case 'turn ended':
				console.log('turn ended')
				//the turn is over, get the time left and stop the timer
				stop_timer();
				//round the remaining time down to the nearest integer
				set_timer(Math.floor(data.time));
				break;
			case 'game over':
				stop_timer();
				//tell the frontend library to stop the game
				game.is_over = true;
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