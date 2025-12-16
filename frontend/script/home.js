document.addEventListener("DOMContentLoaded", function () {
  const filterButtons = document.querySelectorAll(".categorys a");
  const houseCards = document.querySelectorAll(".house-card");

  const updateNoResultsMessage = () => {
    let visibleCount = 0;
    houseCards.forEach((card) => {
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

  filterButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();

      // Update active state on buttons
      filterButtons.forEach((btn) => btn.classList.remove("active"));
      this.classList.add("active");

      const filterValue = this.getAttribute("data-filter");

      houseCards.forEach((card) => {
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

document.addEventListener("DOMContentLoaded", () => {
  const stars = document.querySelectorAll(".favorite-star");

  stars.forEach((star) => {
    star.addEventListener("click", async () => {

      user_id = await checkLogin();

      if (!user_id){
        alert("plz log in first")
        return
      }

      const houseId = star.dataset.houseId;
      const isSelected = star.classList.contains("selected");

      if (isSelected) {
        star.classList.remove("selected");
        star.classList.add("not-selected");
        star.src = "/frontend/imgs/star.png";
      } else {
        star.classList.remove("not-selected");
        star.classList.add("selected");
        star.src = "/frontend/imgs/selectedStar.png";
      }

      const newState = star.classList.contains("selected");

      try {
        const response = await fetch("/favorite", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            house_id: houseId,
            favorite: newState,
          }),
        });

        const result = await response.json();
        console.log("Server replied:", result);
      } catch (err) {
        console.error("Error updating favorite:", err);
      }
    });
  });
});
