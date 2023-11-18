document.addEventListener("DOMContentLoaded", createWebsocket);

function createWebsocket() {
	const socket = new WebSocket('ws://localhost:8000/ws/game')
	socket.onopen = function () {
		console.log('websocket is connected ...')
		socket.send(JSON.stringify({ action: 'start_game' }))
	}
	socket.onmessage = function (event) {
		console.log(event.data)

		data = JSON.parse(event.data)
		console.log(data.me)

		switch (data.message) {
			case 'game started':
				console.log('start game')
				set_timer(data.time)
				start_timer()
				break;
			case 'your turn to sense':
				console.log('your turn to sense')
				setTimeout(socket.send(JSON.stringify({ action: 'sense', sense: 'a1' })), 10000)
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