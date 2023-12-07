export function set_timer(time, element) {
	if (time.seconds >= 60) {
		time.minutes = Math.floor(time.seconds / 60);
		time.seconds = time.seconds % 60;
	}
	element.innerText = `${time.minutes}:${time.seconds}`;
}

export function start_timer(time, element) {
	updateTimer(time, element);
	// timer = setInterval(updateTimer, 1000);
}

export function stop_timer(element) {
	clearInterval(element);
}

export function updateTimer(time, element) {

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
export function addZero(value) {
	return value < 10 ? `0${value}` : value;
}