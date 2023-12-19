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
/*
document.addEventListener("DOMContentLoaded", function fetchLeaderboard () {

    fetch('leaderboard/')
      .then(response => response.json())
      .then(data => {
        console.log('Classifica dei giocatori:', data);
        // Manipola i dati della classifica
      })
      .catch(error => console.error('Errore durante la richiesta API:', error));
  })

  document.addEventListener("DOMContentLoaded", function fetchPlayerLocStats(playerName){
    
    fetch(`player_loc_stats/${playerName}/`)
      .then(response => response.json())
      .then(data => {
        console.log(`Statistiche per ${playerName}:`, data);
        // Manipola i dati delle statistiche del giocatore
      })
      .catch(error => console.error('Errore durante la richiesta API:', error));
  })
*/
  import React, { useState, useEffect } from 'react';

  const PlayerStatsTable = ({ stats }) => (
    <div>
      <h2>Statistiche del giocatore</h2>
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Vittorie</th>
            <th>Sconfitte</th>
            <th>Pareggi</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{stats.player_name}</td>
            <td>{stats.n_wins}</td>
            <td>{stats.n_lost}</td>
            <td>{stats.n_draws}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
  
  const LeaderboardTable = ({ leaderboard }) => (
    <div>
      <h2>Classifica</h2>
      <table>
        <thead>
          <tr>
            <th>Posizione</th>
            <th>Nome</th>
            <th>Vittorie</th>
            <th>Pareggi</th>
            <th>Sconfitte</th>
            <th>Elo</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((player, index) => (
            <tr key={index}>
              <td>{index + 1}</td>
              <td>{player.player_name}</td>
              <td>{player.wins}</td>
              <td>{player.draws}</td>
              <td>{player.losses}</td>
              <td>{player.elo}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
  

  const StatsComponent = () => {
    const [playerStats, setPlayerStats] = useState({});
    const [leaderboard, setLeaderboard] = useState([]);
  
    useEffect(() => {
      const fetchData = async () => {
        try {
          // Richiesta API per ottenere statistiche del giocatore
          const playerResponse = await fetch('player_loc_stats/${playerName}/');
          const playerData = await playerResponse.json();
          setPlayerStats(playerData);
  
          // Richiesta API per ottenere la classifica
          const leaderboardResponse = await fetch('leaderboard/');
          const leaderboardData = await leaderboardResponse.json();
          setLeaderboard(leaderboardData.leaderboard);
        } catch (error) {
          console.error('Errore durante la richiesta API:', error);
        }
      };
  
      fetchData();
    }, []); //passare un array vuoto come secondo argomento per eseguire l'effetto solo una volta
  
    return (
        <div>
        <PlayerStatsTable stats={playerStats} />
        <LeaderboardTable leaderboard={leaderboard} />
      </div>
    );
  };
  
  export default StatsComponent;