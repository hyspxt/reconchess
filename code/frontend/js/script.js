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