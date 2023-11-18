//expects to receive the initial time in seconds
function set_timer(time_seconds) {
	minutes = Math.floor(time_seconds / 60);
	seconds = time_seconds % 60;
	document.getElementById('timer').innerText = `${minutes}:${seconds}`;
}

function start_timer() {
	updateTimer();
	timer = setInterval(updateTimer, 1000);
}

function stop_timer() {
	clearInterval(timer);
}

function updateTimer() {
	
	if (seconds === 0) {
		minutes--;
		seconds = 59;
	} else {
		seconds--;
	}
	
	const formattedMinutes = addZero(minutes);
	const formattedSeconds = addZero(seconds);
	
	document.getElementById('timer').innerText = `${formattedMinutes}:${formattedSeconds}`;

	if (minutes === 0 && seconds === 0) {
		stop_timer();
		return;
	}
}

//adds a zero if the value is less than 10
function addZero(value) {
	return value < 10 ? `0${value}` : value;
}