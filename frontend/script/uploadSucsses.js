// Create floating particles
function createParticle() {
  const particle = document.createElement("div");
  particle.classList.add("particle");
  const size = Math.random() * 5 + 3;
  particle.style.width = `${size}px`;
  particle.style.height = `${size}px`;
  particle.style.left = `${Math.random() * 100}vw`;
  particle.style.top = `${Math.random() * 100}vh`;
  particle.style.animationDelay = `${Math.random() * 5}s`;
  document.body.appendChild(particle);

  setTimeout(() => {
    particle.remove();
  }, 6000);
}

// Generate particles periodically
setInterval(createParticle, 300);

// Create confetti on load
window.onload = () => {
  for (let i = 0; i < 80; i++) {
    setTimeout(() => {
      const confetti = document.createElement("div");
      confetti.classList.add("confetti");
      confetti.style.left = `${Math.random() * 100}vw`;
      confetti.style.background = [
        "#f8d04a",
        "#f43f5e",
        "#3b82f6",
        "#10b981",
        "#a78bfa",
      ][Math.floor(Math.random() * 5)];
      confetti.style.animationDelay = `${Math.random() * 2}s`;
      confetti.style.animationDuration = `${Math.random() * 2 + 2}s`;
      document.body.appendChild(confetti);

      setTimeout(() => confetti.remove(), 4000);
    }, i * 50);
  }
};
