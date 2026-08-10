document.addEventListener("DOMContentLoaded", () => {

    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");

    const showRegister = document.getElementById("showRegister");
    const showLogin = document.getElementById("showLogin");

    showRegister.addEventListener("click", (e) => {
        e.preventDefault();

        loginForm.classList.remove("show");
        loginForm.classList.add("hide");

        registerForm.classList.remove("hide");
        registerForm.classList.add("show");
    });

    showLogin.addEventListener("click", (e) => {
        e.preventDefault();

        registerForm.classList.remove("show");
        registerForm.classList.add("hide");

        loginForm.classList.remove("hide");
        loginForm.classList.add("show");
    });

});