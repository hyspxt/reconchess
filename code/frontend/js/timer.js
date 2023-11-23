let minutes;
let seconds
let activeTimer

//expects to receive the initial time in seconds
function set_timer(time_seconds, id) {
	minutes = Math.floor(time_seconds / 60);
	seconds = time_seconds % 60;

	formattedMinutes = addZero(minutes);
	formattedSeconds = addZero(seconds);

	document.getElementById(id).innerText = `${formattedMinutes}:${formattedSeconds}`;
}

function start_timer(id) {
	updateTimer(id);
	//stop timer if it is already running
	if (activeTimer) clearInterval(activeTimer);
	//start the timer
	activeTimer = setInterval(() => updateTimer(id), 1000);
}

function stop_timer() {
	clearInterval(activeTimer);
}

function updateTimer(id) {
	
	if (seconds === 0) {
		minutes--;
		seconds = 59;
	} else {
		seconds--;
	}
	
	const formattedMinutes = addZero(minutes);
	const formattedSeconds = addZero(seconds);
	
	document.getElementById(id).innerText = `${formattedMinutes}:${formattedSeconds}`;

	if (minutes === 0 && seconds === 0) {
		stop_timer();
		return;
	}
}

//adds a zero if the value is less than 10
function addZero(value) {
	return value < 10 ? `0${value}` : value;
}