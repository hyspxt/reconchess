exports.updateTimer = updateTimer
exports.start_timer = start_timer
exports.stop_timer = stop_timer
exports.set_timer = set_timer

function set_timer(time_seconds, element) {
	minutes = Math.floor(time_seconds / 60);
	seconds = time_seconds % 60;

	formattedMinutes = addZero(minutes);
	formattedSeconds = addZero(seconds);

	document.getElementById('timer').innerText = `${formattedMinutes}:${formattedSeconds}`;
}

function start_timer(time, element) {
	updateTimer(time, element);
	timer = setInterval(updateTimer, 1000);
}

function stop_timer(element) {

	clearInterval(element);
}

function updateTimer(time, element) {
	
	if (time.minutes === 0 && time.seconds === 0) {
		element.innerText = `00:00`;
		stop_timer(element);
		return;
	}
	else if (time.seconds === 0 && time.minutes > 0) {
		time.minutes--;
		time.seconds = 59;
	} 
	else {
		time.seconds--;
	}
	
	const formattedMinutes = addZero(time.minutes);
	const formattedSeconds = addZero(time.seconds);
	
	element.innerText = `${formattedMinutes}:${formattedSeconds}`;

	
}

//adds a zero if the value is less than 10
function addZero(value) {
	return value < 10 ? `0${value}` : value;
}