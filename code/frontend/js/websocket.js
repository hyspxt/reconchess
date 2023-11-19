document.addEventListener("DOMContentLoaded", createWebsocket);

function createWebsocket() {
	const socket = new WebSocket('ws://localhost:8000/ws/game') //'silverbullets.rocks/ws/game'
	socket.onopen = function () {
		console.log('websocket is connected ...')
		socket.send(JSON.stringify({ action: 'start_game' }))
	}
	socket.onmessage = function (event) {
		console.log(event.data)

		data = JSON.parse(event.data)
		console.log(data.me)

		switch (data.message) { //metodi da lib front chess.js e chessboard.js
			case 'game started':
				console.log('start game')
				set_timer(data.time)
				start_timer()
				break;
			case 'your turn to sense':
				console.log('your turn to sense')
				setTimeout(socket.send(JSON.stringify({ action: 'sense', sense: 'a1' })), 10000)
				break;
			case 'your turn to move':
				console.log('your turn to move')
				setTimeout(socket.send(JSON.stringify({ action: 'move', move: ''})))
				break;
			case 'invalid move':
				console.log('invalid move')
				data.game.undoMove();
				break;
			case 'opponent_capture':
				console.log('opponent_capture')
				break;
			case 'move result':
				console.log('move result')
				break;
			case 'time left':
				console.log('time left')
				set_timer(data.game.get_seconds_left())
				start_timer()
				break;
			case 'game over':
				console.log('game over'+ data.game.reason)
				data.game.game_over();
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