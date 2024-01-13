let minutes;
let seconds
let activeTimer

export function set_timer(time, element) {
	minutes = Math.floor(time / 60);
	seconds = Math.ceil(time % 60);

	const formattedMinutes = addZero(minutes);
	const formattedSeconds = addZero(seconds);

	element.innerText = `${formattedMinutes}:${formattedSeconds}`;
}

export function start_timer(time, element) {
	time = updateTimer(time, element);
	// timer = setInterval(updateTimer, 1000);
	//stop timer if it is already running
	if (activeTimer) clearInterval(activeTimer);
	//start the timer

	activeTimer = setInterval(() => time = updateTimer(time, element), 1000);

}

export function stop_timer() {
	clearInterval(activeTimer);
}

export function updateTimer(time, element) {

	if (time >= 0) {
		minutes = Math.floor(time / 60);
		seconds = Math.ceil(time % 60);
		if (minutes === 0 && seconds === 0) {
			element.innerText = `00:00`;
			stop_timer();  // if something breaks, switch this with stop_timer(element);
			return;
		}
		else if (seconds === 0 && minutes > 0) {
			minutes--;
			seconds = 59;
		}
		else {
			seconds--;
		}
	}

	const formattedMinutes = addZero(minutes);
	const formattedSeconds = addZero(seconds);

	element.innerText = `${formattedMinutes}:${formattedSeconds}`;
	return (time - 1);
}

//adds a zero if the value is less than 10
export function addZero(value) {
	return value < 10 ? `0${value}` : value;
}