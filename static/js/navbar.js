const menuToggle = document.getElementById("menuToggle");
const mobileMenu = document.getElementById("mobileMenu");

menuToggle.addEventListener("click", () => {

    mobileMenu.classList.toggle("active");

    if (mobileMenu.classList.contains("active")) {
        menuToggle.innerHTML = '<i class="fas fa-times"></i>';
    } else {
        menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
    }

});

window.addEventListener("resize", () => {

    if (window.innerWidth > 1100) {

        mobileMenu.classList.remove("active");
        menuToggle.innerHTML = '<i class="fas fa-bars"></i>';

    }

});