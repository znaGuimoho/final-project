// super_admin.js — per-page script, matches project's script/ convention

// ── Sidebar active state on scroll ───────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const navLinks = document.querySelectorAll(".sa-nav-item[href^='#']");
  const sections = [...navLinks].map(a => document.querySelector(a.getAttribute("href"))).filter(Boolean);

  window.addEventListener("scroll", () => {
    let current = "";
    sections.forEach(s => {
      if (window.scrollY >= s.offsetTop - 90) current = "#" + s.id;
    });
    navLinks.forEach(a => a.classList.toggle("active", a.getAttribute("href") === current));
  }, { passive: true });
});

// ── Save platform settings ────────────────────────────────
async function saveSettings() {
  const body = {
    platform_fee_percent:    parseFloat(document.getElementById("sa-fee").value),
    max_listings_per_user:   parseInt(document.getElementById("sa-max-listings").value),
    allow_new_registrations: document.getElementById("sa-allow-reg").checked,
  };

  try {
    const res = await fetch("/super_admin/settings", {
      method:  "PATCH",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(body),
    });
    if (res.ok) {
      showFlash("Settings saved successfully.", "success");
    } else {
      showFlash("Failed to save — check permissions.", "error");
    }
  } catch {
    showFlash("Network error. Try again.", "error");
  }
}

// ── Reuse project's flash message pattern (if you have one) ──
function showFlash(message, type) {
  // If your base.html already has a flash container, use it:
  const existing = document.querySelector(".flash-message");
  if (existing) {
    existing.textContent = message;
    existing.className = `flash-message flash-${type}`;
    return;
  }
  // Fallback
  alert(message);
}

// ── Promote / demote / ban helpers (called from user/admin tables) ──
async function promoteUser(userId) {
  const res = await fetch(`/super_admin/admins/promote/${userId}`, { method: "POST" });
  if (res.ok) location.reload();
}
async function demoteAdmin(userId) {
  const res = await fetch(`/super_admin/admins/demote/${userId}`, { method: "POST" });
  if (res.ok) location.reload();
}
async function banUser(userId) {
  if (!confirm("Ban this user?")) return;
  const res = await fetch(`/super_admin/users/ban/${userId}`, { method: "POST" });
  if (res.ok) location.reload();
}
async function unbanUser(userId) {
  const res = await fetch(`/super_admin/users/unban/${userId}`, { method: "POST" });
  if (res.ok) location.reload();
}
async function deleteListing(houseId) {
  if (!confirm("Permanently delete this listing?")) return;
  const res = await fetch(`/super_admin/listings/${houseId}`, { method: "DELETE" });
  if (res.ok) location.reload();
}
