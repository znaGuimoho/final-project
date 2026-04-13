// admins.js

// ── Live search filter ────────────────────────────────
function filterAdmins(query) {
  const q = query.toLowerCase().trim();
  const rows = document.querySelectorAll(".adm-row");
  let visible = 0;

  rows.forEach(row => {
    const name  = row.dataset.name  || "";
    const email = row.dataset.email || "";
    const match = name.includes(q) || email.includes(q);
    row.style.display = match ? "" : "none";
    if (match) visible++;
  });

  document.getElementById("adm-no-results").style.display = visible === 0 ? "block" : "none";
}

// ── Confirm modal ─────────────────────────────────────
let _pendingAction = null;

function openModal(title, body, onConfirm) {
  document.getElementById("adm-modal-title").textContent   = title;
  document.getElementById("adm-modal-body").textContent    = body;
  document.getElementById("adm-modal-confirm").onclick     = onConfirm;
  document.getElementById("adm-modal").style.display       = "flex";
}

function closeModal() {
  document.getElementById("adm-modal").style.display = "none";
  _pendingAction = null;
}

// close on backdrop click
document.getElementById("adm-modal").addEventListener("click", function(e) {
  if (e.target === this) closeModal();
});

// ── Actions ───────────────────────────────────────────
function confirmDemote(userId, userName) {
  openModal(
    "Demote Admin",
    `Remove admin privileges from ${userName}? They will become a regular user.`,
    () => demoteAdmin(userId)
  );
}

function confirmBan(userId, userName) {
  openModal(
    "Ban User",
    `Ban ${userName}? They will lose access to the platform immediately.`,
    () => banUser(userId)
  );
}

async function demoteAdmin(userId) {
  const res = await fetch(`/super_admin/admins/demote/${userId}`, { method: "POST" });
  closeModal();
  if (res.ok) location.reload();
  else        alert("Failed to demote. Check your permissions.");
}

async function banUser(userId) {
  const res = await fetch(`/super_admin/users/ban/${userId}`, { method: "POST" });
  closeModal();
  if (res.ok) location.reload();
  else        alert("Failed to ban user. Check your permissions.");
}
