document.addEventListener("DOMContentLoaded", function () {
  const filterButtons = document.querySelectorAll(".categorys a");
  const houseCards = document.querySelectorAll(".house-card");

  const updateNoResultsMessage = () => {
    let visibleCount = 0;
    houseCards.forEach(card => {
      if (!card.classList.contains("hidden")) visibleCount++;
    });

    let message = document.getElementById("no-results");
    if (visibleCount === 0) {
      if (!message) {
        message = document.createElement("p");
        message.id = "no-results";
        message.textContent = "No rentals found in this category.";
        message.style.textAlign = "center";
        message.style.padding = "40px";
        message.style.fontSize = "18px";
        message.style.color = "#666";
        document.querySelector(".houses").appendChild(message);
      }
    } else {
      if (message) message.remove();
    }
  };

  filterButtons.forEach(button => {
    button.addEventListener("click", function (e) {
      e.preventDefault();

      // Update active state on buttons
      filterButtons.forEach(btn => btn.classList.remove("active"));
      this.classList.add("active");

      const filterValue = this.getAttribute("data-filter");

      houseCards.forEach(card => {
        const cardCategory = card.getAttribute("data-category")?.toLowerCase();

        if (filterValue === "all" || cardCategory === filterValue) {
          card.classList.remove("hidden");
        } else {
          card.classList.add("hidden");
        }
      });

      updateNoResultsMessage();
    });
  });
  updateNoResultsMessage();
});
