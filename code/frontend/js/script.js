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

document.addEventListener("DOMContentLoaded", function fetchLeaderboard () {

    fetch('/api/leaderboard/')
      .then(response => response.json())
      .then(data => {
        console.log('Classifica dei giocatori:', data);
        // Manipola i dati della classifica
      })
      .catch(error => console.error('Errore durante la richiesta API:', error));
  })
  
  document.addEventListener("DOMContentLoaded", function fetchPlayerStats(playerName){
    
    fetch(`/api/player-stats/${playerName}/`)
      .then(response => response.json())
      .then(data => {
        console.log(`Statistiche per ${playerName}:`, data);
        // Manipola i dati delle statistiche del giocatore
      })
      .catch(error => console.error('Errore durante la richiesta API:', error));
  })

  document.addEventListener("DOMContentLoaded", function fetchPlayerLocStats(playerName){
    
    fetch(`/api/player_loc_stats/${playerName}/`)
      .then(response => response.json())
      .then(data => {
        console.log(`Statistiche per ${playerName}:`, data);
        // Manipola i dati delle statistiche del giocatore
      })
      .catch(error => console.error('Errore durante la richiesta API:', error));
  })


