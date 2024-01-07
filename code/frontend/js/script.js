//change eye icon when clicked
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

document.addEventListener("DOMContentLoaded", function() {
    var element = document.getElementById("not_signed_ini6gdrs9oeic0");
    if(element) {
        element.innerHTML = "Sign in with Google";
    }
});

window.handleGoogleLogin = function(response) {
    console.log('Google login response', response);
    var id_token = response.credential;

    // Send the id_token to Django server
    fetch('/api/googleID/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id_token: id_token
        })
    })
    .then(response => response.json())
    .then(data => {
        const alert = document.createElement("div");
        alert.classList.add("alert", "mt-3", "text-center");

        if (data.success) {
            alert.classList.add("alert-success");
            alert.innerHTML = `Logged in successfully as ${data.user_name}`;
        } else {
            alert.classList.add("alert-danger");
            alert.innerHTML = `Error: ${data.error}`;
        }

        // Append the alert to the form
        const form = document.getElementById('log');
        const nextElement = form.nextElementSibling;

        if (nextElement && nextElement.classList.contains("alert")) {
            nextElement.remove();
        }

        form.after(alert);
    })
    .catch(error => {
        console.log('There was a problem with the AJAX request.', error);
    });
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
function fetchPlayerUsername(playerMail){
    if (!playerMail) {
        console.error('Indirizzo email del giocatore non valido');
        return;
    }
    const apiUrl = `/api/player_username/${encodeURIComponent(playerMail)}/`;

    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Errore durante la richiesta API ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`Username per ${playerMail}:`, data);
            username=data
            console.log('username:', username)
        })
        .catch(error => {
            console.error(`Errore durante la richiesta API: ${error.message}`);
        });
}

//check if there is a user logged in and change the navbar accordingly
window.onload = checkLogin;
function checkLogin() {
    fetch('/api/check_login/')
        .then(response => response.json())
        .then(data => {
            const loginDiv = document.querySelector('.user');
            const boardUserDiv = document.querySelector('.white_id');
            const aHuman = document.querySelector('.a_human');
            const aLeaderboard = document.querySelector('#a-leaderboard');
            if (data.loggedIn) {
                loginDiv.innerHTML = `
                    <div><p>You're logged in as <span style="color: #FFF;">${data.username}</span></p></div>
                    <div>
                        <form class="form-inline mt-auto" id="btn_signOut" method="post">
                            <button type="submit" class="btn btn-outline-danger">Sign out</button>
                        </form>
                    </div>
                `;
                document.getElementById('btn_signOut').addEventListener('submit', handleLogout);
                boardUserDiv.innerHTML = `${data.username}`;
                aHuman.classList.remove('disabled');
                aLeaderboard.classList.remove('disabled');
            } else {
                loginDiv.innerHTML = `
                    <form class="form-inline mt-auto" id="btn_signIn">
                        <button type="submit" formaction="loginForm.html" class="btn btn-outline-success">Sign in</button>
                    </form>
                `;
                boardUserDiv.innerHTML = `Player 1`;
                aHuman.classList.add('disabled');
                aLeaderboard.classList.add('disabled');
            }
        })
        .catch(error => console.error('Error:', error));
}

function handleLogout(event){
    event.preventDefault();
    fetch('/api/logout/')
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                console.error('Logout failed');
            }
        })
        .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', (event) => {
    const aLeaderboard = document.querySelector('#a-leaderboard');
    aLeaderboard.addEventListener('click', (event) => {
        event.preventDefault();
        if (aLeaderboard.classList.contains('disabled')) {
            Swal.fire({
                title: 'Oops...',
                text: 'This option is not available yet, please log in to unlock this feature.',
                icon: 'warning',
                confirmButtonText: 'OK'
            });
        }
        else {
            window.location.href = aLeaderboard.href;
        }
    });
});