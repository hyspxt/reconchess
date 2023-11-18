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

function createWebSocket() {
    const socket = new WebSocket('silverbullets.rocks/ws/game');
    socket.addEventListener("open",(event) => {
        socket.send(JSON.stringify({action:'start_game'}));
    } )
    socket.addEventListener("message", (event) => {
        switch(event.data.message){
            case 'opponent_capture','capture_square':
                //handleOpponentCapture();    
                break;
            case 'your turn to sense': // prendi da lib front chess.js e forse chessboard.js
                //handleYourTurnToSense();
                break;
            case 'your turn to move':
                makeMove(game,config);
                break;
            case 'invalid move':
                undoMove();
                break;
            case 'game over','game over: the king was captured','game over: timeout','game over: resign','game over: full turn limit exceeded','game over: full move limit exceeded':
                game.game_over();
                break;
            case 'time left':
                //handleTimeLeft(event.data.time);
                break;
            default:
            break;
        }
    })
}
