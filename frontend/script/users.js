// users.js

let _activeFilter = "all";

// ── Filter logic ──────────────────────────────────────
function filterUsers(query) {
  _applyFilters(query.toLowerCase().trim(), _activeFilter);
}

function setFilter(filter, btn) {
  _activeFilter = filter;
  document.querySelectorAll(".usr-filter-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  const query = document.getElementById("usr-search").value.toLowerCase().trim();
  _applyFilters(query, filter);
}

function _applyFilters(query, filter) {
  const rows = document.querySelectorAll(".adm-row");
  let visible = 0;

  rows.forEach(row => {
    const matchesSearch =
      !query ||
      row.dataset.name.includes(query)  ||
      row.dataset.email.includes(query) ||
      row.dataset.city.includes(query);

    const matchesFilter =
      filter === "all"        ||
      (filter === "host"       && row.dataset.host       === "host")    ||
      (filter === "banned"     && row.dataset.banned     === "banned")  ||
      (filter === "unverified" && row.dataset.verified   === "unverified");

    const show = matchesSearch && matchesFilter;
    row.style.display = show ? "" : "none";
    if (show) visible++;
  });

  document.getElementById("usr-no-results").style.display = visible === 0 ? "block" : "none";
}

// ── Modal ─────────────────────────────────────────────
function openModal(title, body, onConfirm) {
  document.getElementById("usr-modal-title").textContent = title;
  document.getElementById("usr-modal-body").textContent  = body;
  document.getElementById("usr-modal-confirm").onclick   = onConfirm;
  document.getElementById("usr-modal").style.display     = "flex";
}

function closeModal() {
  document.getElementById("usr-modal").style.display = "none";
}

document.getElementById("usr-modal").addEventListener("click", function (e) {
  if (e.target === this) closeModal();
});

// ── Confirm helpers ───────────────────────────────────
function confirmPromote(userId, userName) {
  openModal(
    "Make Admin",
    `Grant admin privileges to ${userName}? They will be able to review host applications.`,
    () => promoteUser(userId)
  );
}

function confirmBan(userId, userName) {
  openModal(
    "Ban User",
    `Ban ${userName}? They will lose access to the platform immediately.`,
    () => banUser(userId)
  );
}

function confirmUnban(userId, userName) {
  openModal(
    "Unban User",
    `Restore access for ${userName}?`,
    () => unbanUser(userId)
  );
}

// ── API calls ─────────────────────────────────────────
async function promoteUser(userId) {
  const res = await fetch(`/super_admin/admins/promote/${userId}`, { method: "POST" });
  closeModal();
  if (res.ok) location.reload();
  else        alert("Failed to promote user.");
}

async function banUser(userId) {
  const res = await fetch(`/super_admin/users/ban/${userId}`, { method: "POST" });
  closeModal();
  if (res.ok) location.reload();
  else        alert("Failed to ban user.");
}

async function unbanUser(userId) {
  const res = await fetch(`/super_admin/users/unban/${userId}`, { method: "POST" });
  closeModal();
  if (res.ok) location.reload();
  else        alert("Failed to unban user.");
}
