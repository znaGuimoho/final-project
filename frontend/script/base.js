document.addEventListener("DOMContentLoaded", () => {
  const navbar = document.querySelector(".navbar");
  if (navbar) navbar.classList.add("navbar-loaded");

  // ---- SCROLL HANDLER ----
  if (navbar) {
    const scrollHandler = () => {
      navbar.classList.toggle("scrolled", window.scrollY > 10);
    };

    let ticking = false;
    const throttledScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          scrollHandler();
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener("scroll", throttledScroll, { passive: true });
  }

  // ---- MORE MENU ----
  const moreBtn = document.querySelector(".more");
  const closeBtn = document.querySelector(".close-more");
  const drawer = document.querySelector(".more-things");

  if (moreBtn && closeBtn && drawer) {
    const open = () => drawer.classList.add("open");
    const close = () => drawer.classList.remove("open");

    moreBtn.addEventListener("click", open);
    closeBtn.addEventListener("click", close);

    document.addEventListener("click", (e) => {
      if (!drawer.contains(e.target) && !moreBtn.contains(e.target)) close();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") close();
    });
  }
});
const searchBar = document.getElementById("searchBar");
const searchIcon = document.getElementById("searchIcon");
const input = searchBar.querySelector("input");
const results = document.querySelector(".results");

// Toggle search bar
searchIcon.addEventListener("click", () => {
  const isActive = searchBar.classList.toggle("active");

  if (isActive) {
    input.focus();
    results.classList.add("show");
  } else {
    results.classList.remove("show");
    input.value = "";
  }
});

// Clicking outside closes everything
document.addEventListener("click", (e) => {
  if (!searchBar.contains(e.target)) {
    searchBar.classList.remove("active");
    results.classList.remove("show");
    input.value = "";
  }
});

// Prevent closing when clicking inside search bar
searchBar.addEventListener("click", (e) => {
  e.stopPropagation();
});

// Instead of just toggling display, use the .show class
function showResults() {
  resultsElement.classList.add("show");
}

function hideResults() {
  resultsElement.classList.remove("show");
  // Optional: remove after animation ends for performance
  resultsElement.addEventListener("transitionend", function handler() {
    if (!resultsElement.classList.contains("show")) {
      resultsElement.style.display = "none";
    }
    resultsElement.removeEventListener("transitionend", handler);
  });
}

const searchInput = document.getElementById("searchInput");
const resultsList = document.getElementById("resultsList");

searchInput.addEventListener("input", function () {
  const hasValue = this.value.trim().length > 0;
  const hasResults = resultsList.querySelector("li:not(.no-results)") !== null;

  if (hasValue && hasResults) {
    resultsList.classList.add("show");
  } else {
    resultsList.classList.remove("show");
  }
});

// Optional: hide when clicking outside
const searchWrapper = document.querySelector(".search-wrapper");
document.addEventListener("click", function (e) {
  if (!searchWrapper.contains(e.target)) {
    resultsList.classList.remove("show");
  }
});

let searchTimeout;

searchInput.addEventListener("input", () => {
  const query = searchInput.value.trim();

  clearTimeout(searchTimeout);

  // Debounce: wait 300ms after user stops typing
  searchTimeout = setTimeout(() => {
    if (query.length > 0) {
      fetch(`/api/search?query=${encodeURIComponent(query)}`)
        .then((response) => response.json())
        .then((data) => {
          updateResultsList(data.results);
        })
        .catch((err) => console.error("Search error:", err));
    } else {
      updateResultsList([]);
    }
  }, 300);
});

function updateResultsList(results) {
  resultsList.innerHTML = "";

  if (results.length === 0) {
    resultsList.innerHTML = `<li class="no-results">No results found</li>`;
    return;
  }

  results.forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <a href="/house/${encodeURIComponent(item.id)}">
        ${item.details}
      </a>
    `;
    resultsList.appendChild(li);
  });

  resultsList.classList.add("show");
}
