export function generaStringaCasuale(length) {
    const permittedChar = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let string = '';
  
    for (let i = 0; i < length; i++) {
      const casualIndex = Math.floor(Math.random() * permittedChar.length);
      string += permittedChar.charAt(casualIndex);
    }
    return string;
  }
  
  // Utilizzo della funzione per generare una stringa casuale di lunghezza 10
  const stringaCasuale = generaStringaCasuale(10);
  console.log(stringaCasuale);
  



document.addEventListener("DOMContentLoaded", function() {
    var element = document.getElementById("not_signed_ini6gdrs9oeic0");
    if(element) {
        element.innerHTML = "Sign in with Google";
    }
});

function handleCredentialResponse(response) {
    var id_token = response.credential;

    // Send the id_token to your Django server
    fetch('/api/social_log/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            //'X-CSRFToken': getCookie('csrftoken')  // Assuming you have a function to get the CSRF token
        },
        body: JSON.stringify({
            id_token: id_token
        })
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
    }).then(data => {
        // Handle the response from your Django server
    }).catch(error => {
        console.log('There was a problem with the AJAX request.', error);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const eyeIcons = document.querySelectorAll(".eye-icon");

    eyeIcons.forEach(eyeIcon => {
        eyeIcon.addEventListener("click", () => {
            const passwordFields = eyeIcon.parentElement.querySelectorAll(".password");

            passwordFields.forEach(password => {
                if (password.type === "password") {
                    password.type = "text";
                    eyeIcon.classList.replace("bx-hide", "bx-show");
                } else {
                    password.type = "password";
                    eyeIcon.classList.replace("bx-show", "bx-hide");
                }
            });
        });
    });
});

function handleRegistration(event) {
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


function handleLogin(event) {
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

  document.addEventListener("DOMContentLoaded", function checkUserPresenceByMail(mail){
    // Funzione per verificare la presenza di un utente con mail
      try {
        const response = fetch(`social_log/${mail}/`);
        const data = response.json();
  
        if (data.exists) {
          console.log(`L'utente con mail ${mail} esiste.`);
        } else {
          console.log(`L'utente con mail ${mail} non esiste.`);
        }
      } catch (error) {
        console.error('Errore durante la richiesta API:', error);
      }
    })