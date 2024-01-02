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

 // Funzione per effettuare una richiesta HTTP e gestire la risposta JSON per leaderboard
 document.addEventListener("DOMContentLoaded", function fetchLeaderboard () {

    fetch('leaderboard/')
      .then(response => response.json())
      .then(data => {
        console.log('Classifica dei giocatori:', data);
      })
      .catch(error => console.error('Errore durante la richiesta API:', error));
  })

 // Funzione per effettuare una richiesta HTTP e gestire la risposta JSON per statistiche giocatore
  document.addEventListener("DOMContentLoaded", function fetchPlayerLocStats(playerMail){
    
    fetch(`player_loc_stats/${playerMail}/`)
      .then(response => response.json())
      .then(data => {
        console.log(`Statistiche per ${playerMail}:`, data);
      })
      .catch(error => console.error('Errore durante la richiesta API:', error));
  })

  // Funzione per effettuare una richiesta HTTP e gestire la risposta JSON per username giocatore
  document.addEventListener("DOMContentLoaded", function fetchPlayerLocStats(playerMail){
    
    fetch(`player_username/${playerMail}/`)
      .then(response => response.json())
      .then(data => {
        console.log(`Username per ${playerMail}:`, data);
      })
      .catch(error => console.error('Errore durante la richiesta API:', error));
  })

