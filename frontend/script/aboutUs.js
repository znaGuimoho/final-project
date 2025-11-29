AOS.init({
  duration: 1000,
  once: true,
});

// Navbar shrink on scroll
window.addEventListener("scroll", () => {
  document.querySelector("nav").style.padding =
    window.scrollY > 50 ? "1rem 5%" : "1.5rem 5%";
});
