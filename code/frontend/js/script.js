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
    let element = document.getElementById("not_signed_ini6gdrs9oeic0");
    if(element) {
        element.innerHTML = "Sign in with Google";
    }
});

window.handleGoogleLogin = function(response) {
    console.log('Google login response', response);
    let id_token = response.credential;

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
            alert.innerHTML = `Logged in successfully!`;
        } else {
            alert.classList.add("alert-danger");
            alert.innerHTML = `Error: ${data.error}`;
        }

        // Append the alert to the form
        const form = document.getElementById('log');
        const nextElement = form.nextElementSibling;

        if (nextElement?.classList.contains("alert")) {
            nextElement.remove();
        }

        form.after(alert);
        
        //reroute the user to the board page
        if (data.success) {
            window.location.href = "/board.html";
        }
    })
    .catch(error => {
        console.log('There was a problem with the AJAX request.', error);
    });
}

// Funzione per effettuare una richiesta HTTP e gestire la risposta JSON per leaderboard
export function fetchLeaderboard() {

    return fetch('/api/leaderboard/')
        .then(response => response.json())
        .then(data => {
            console.log('Classifica dei giocatori:', data);
            return data;
        })
        .catch(error => console.error('Errore durante la richiesta API:', error));
}

// Funzione per effettuare una richiesta HTTP e gestire la risposta JSON per statistiche giocatore
export function fetchPlayerLocStats(player){
    
    return fetch(`/api/player_loc_stats/${encodeURIComponent(player)}/`)
        .then(response => response.json())
        .then(data => {
            console.log(`Statistiche per ${player}:`, data);
            return data;
        })
        .catch(error => console.error('Errore durante la richiesta API:', error));
}

// Funzione per effettuare una richiesta HTTP e gestire la risposta JSON per username giocatore
export function fetchPlayerUsername(playerMail){
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
            let username=data
            console.log('username:', username)
        })
        .catch(error => {
            console.error(`Errore durante la richiesta API: ${error.message}`);
        });
}

//check if there is a user logged in and change things accordingly
window.onload = checkLogin;
export function checkLogin() {
    return fetch('/api/check_login/')
        .then(response => response.json())
        .then(data => {
            const loginDiv = document.querySelector('.user');
            const aLeaderboard = document.querySelector('#a-leaderboard');
            if (data.loggedIn) {
                loginDiv.innerHTML = `
                    <div id="name_user"><p>Welcome <span style="color: #FFF;">${data.username}</span> !</p></div>
                    <div>
                        <form class="form-inline mt-auto" id="btn_signOut" method="post">
                            <button type="submit" class="btn btn-outline-danger" style="padding-left: 8px; padding-right: 8px;">Sign out</button>
                        </form>
                    </div>
                `;
                document.getElementById('btn_signOut').addEventListener('submit', handleLogout);
                aLeaderboard.classList.remove('disabled');
            } else {
                loginDiv.innerHTML = `
                    <form class="form-inline mt-auto" id="btn_signIn">
                        <button type="submit" formaction="loginForm.html" class="btn btn-outline-success">Sign in</button>
                    </form>
                `;
                aLeaderboard.classList.add('disabled');
            }
            disableleaderboard();
            return data;
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

//disable leaderboard if noone is logged in
function disableleaderboard(){
    const aLeaderboard = document.querySelector('#a-leaderboard');
    console.log(aLeaderboard);
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
};