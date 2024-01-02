export function generaStringaCasuale(length) {
	const permittedChar = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
	let string = '';

	for (let i = 0; i < length; i++) {
		const casualIndex = Math.floor(Math.random() * permittedChar.length);
		string += permittedChar.charAt(casualIndex);
	}
	return string;
}

export function handleRegistration(event) {
	event.preventDefault();
	//get form data
	const formData = new FormData(event.target);
	//get csfttoken value from cookie

	fetch("/api/register/", {
		method: "POST",
		body: formData,
	}).then(response => {
		const alert = document.createElement("div");
		alert.classList.add("alert", "mt-3", "text-center");

		if (response.ok) {
			alert.classList.add("alert-success");
		} else {
			alert.classList.add("alert-danger");
		}

		response.text().then(data => {
			alert.innerHTML = data;
		});

		const nextElement = event.target.nextElementSibling;
		if (nextElement.classList.contains("alert")) {
			nextElement.remove();
		}
		event.target.after(alert);
	})
		.catch(error => {
			console.error(error);
		});
}

export function handleLogin(event) {
	event.preventDefault();

	//get form data
	const formData = new FormData(event.target);
	//get csfttoken value from cookie

	fetch("/api/login/", {
		method: "POST",
		body: formData,
	}).then(response => {
		const alert = document.createElement("div");
		alert.classList.add("alert", "mt-3", "text-center");

		if (response.ok) {
			alert.classList.add("alert-success");
			//window.location.href = "../board.html";
		} else {
			alert.classList.add("alert-danger");
		}

		response.text().then(data => {
			alert.innerHTML = data;
		});

		const nextElement = event.target.nextElementSibling;
		if (nextElement.classList.contains("alert")) {
			nextElement.remove();
		}
		event.target.after(alert);
	})
}