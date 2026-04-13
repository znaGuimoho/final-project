// listings.js

console.log("listings is called");
let _activeFilter = "all";

// ── Filter logic ──────────────────────────────────────
function filterListings(query) {
  _applyFilters(query.toLowerCase().trim(), _activeFilter);
}

function setFilter(filter, btn) {
  _activeFilter = filter;
  document.querySelectorAll(".usr-filter-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  const query = document.getElementById("lst-search").value.toLowerCase().trim();
  _applyFilters(query, filter);
}

function _applyFilters(query, filter) {
  const cards = document.querySelectorAll(".lst-card");
  let visible = 0;

  cards.forEach(card => {
    const matchesSearch =
      !query ||
      (card.dataset.host     || "").includes(query) ||
      (card.dataset.location || "").includes(query);   // ← was .city, now .location

    const matchesFilter =
      filter === "all" || card.dataset.category === filter;

    const show = matchesSearch && matchesFilter;
    card.style.display = show ? "" : "none";
    if (show) visible++;
  });

  document.getElementById("lst-no-results").style.display = visible === 0 ? "block" : "none";
}

// ── Modal ─────────────────────────────────────────────
function confirmDelete(houseId, label) {
  document.getElementById("lst-modal-body").textContent =
    `Permanently delete "${label}"? This cannot be undone.`;
  document.getElementById("lst-modal-confirm").onclick = () => deleteListing(houseId);
  document.getElementById("lst-modal").style.display   = "flex";
}

function closeModal() {
  document.getElementById("lst-modal").style.display = "none";
}

document.getElementById("lst-modal").addEventListener("click", function (e) {
  if (e.target === this) closeModal();
});

// ── Delete ────────────────────────────────────────────
async function deleteListing(houseId) {
  const res = await fetch(`/super_admin/listings/${houseId}`, { method: "DELETE" });
  closeModal();
  if (res.ok) {
    const card = document.querySelector(`.lst-card[data-id="${houseId}"]`);
    if (card) card.remove();
    else location.reload();
  } else {
    alert("Failed to delete listing.");
  }
}
