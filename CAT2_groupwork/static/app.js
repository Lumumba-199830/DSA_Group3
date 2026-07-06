/* =====================================================================
   Flock Ledger — front-end controller
   Talks to the Flask API defined in server.py (new file). Does not
   touch or duplicate the project's existing app.js demo script.
   ===================================================================== */

const API = "/api";

// ---------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------

function $(sel, root = document) { return root.querySelector(sel); }
function $all(sel, root = document) { return [...root.querySelectorAll(sel)]; }

function badgeFor(status) {
  const cls = status === "Critical" ? "badge--critical"
            : status === "Sick" ? "badge--sick"
            : "badge--healthy";
  return `<span class="badge ${cls}">${status}</span>`;
}

let toastTimer = null;
function showToast(message, kind = "default") {
  const el = $("#toast");
  el.textContent = message;
  el.className = "toast" + (kind === "error" ? " is-error" : kind === "success" ? " is-success" : "");
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, 3200);
}

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  let data = null;
  try { data = await res.json(); } catch (e) { /* no body */ }
  if (!res.ok) {
    const message = (data && data.error) || `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data;
}

// ---------------------------------------------------------------------
// Tabs
// ---------------------------------------------------------------------

function initTabs() {
  $all(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
      $all(".tab").forEach(t => { t.classList.remove("is-active"); t.setAttribute("aria-selected", "false"); });
      $all(".panel").forEach(p => p.classList.remove("is-active"));
      tab.classList.add("is-active");
      tab.setAttribute("aria-selected", "true");
      $(`.panel[data-panel="${tab.dataset.tab}"]`).classList.add("is-active");
    });
  });
}

// ---------------------------------------------------------------------
// Stats
// ---------------------------------------------------------------------

async function loadStats() {
  try {
    const s = await api("/stats");
    $("#stat-total").textContent = s.total_birds;
    $("#stat-healthy").textContent = s.healthy;
    $("#stat-sick").textContent = s.sick;
    $("#stat-critical").textContent = s.critical;
    $("#stat-eggs").textContent = s.total_eggs;
  } catch (e) {
    // stats are non-critical; fail silently in the header
  }
}

// ---------------------------------------------------------------------
// Registry table
// ---------------------------------------------------------------------

function renderRegistryRows(birds) {
  const tbody = $("#registry-tbody");
  const empty = $("#registry-empty");
  tbody.innerHTML = "";

  if (!birds.length) {
    empty.hidden = false;
    return;
  }
  empty.hidden = true;

  birds.forEach(b => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="col-tag">${b.tag_id}</td>
      <td>${b.breed}</td>
      <td>${b.age_weeks}</td>
      <td>${Number(b.weight_kg).toFixed(2)}</td>
      <td>${b.egg_count}</td>
      <td>${badgeFor(b.health_status)}</td>
      <td class="col-actions">
        <button class="btn btn--text" data-action="edit" data-tag="${b.tag_id}">Edit</button>
        <button class="btn btn--text btn--danger" data-action="delete" data-tag="${b.tag_id}">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

async function loadRegistry() {
  const birds = await api("/birds");
  renderRegistryRows(birds);
}

async function refreshAll() {
  await Promise.all([loadRegistry(), loadStats(), loadAlerts()]);
}

// Row actions (event delegation)
$("#registry-tbody")?.addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;
  const tag = btn.dataset.tag;

  if (btn.dataset.action === "delete") {
    if (!confirm(`Remove bird ${tag} from the registry?`)) return;
    try {
      await api(`/birds/${encodeURIComponent(tag)}`, { method: "DELETE" });
      showToast(`Removed ${tag}`, "success");
      refreshAll();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  if (btn.dataset.action === "edit") {
    try {
      const result = await api(`/birds/${encodeURIComponent(tag)}`);
      openEditModal(result.bird);
    } catch (err) {
      showToast(err.message, "error");
    }
  }
});

// ---------------------------------------------------------------------
// Search
// ---------------------------------------------------------------------

$("#search-btn")?.addEventListener("click", runSearch);
$("#search-input")?.addEventListener("keydown", (e) => { if (e.key === "Enter") runSearch(); });
$("#search-clear")?.addEventListener("click", () => {
  $("#search-input").value = "";
  $("#search-clear").hidden = true;
  loadRegistry();
});

async function runSearch() {
  const tag = $("#search-input").value.trim();
  if (!tag) { loadRegistry(); return; }
  try {
    const result = await api(`/birds/${encodeURIComponent(tag)}`);
    renderRegistryRows([result.bird]);
    $("#search-clear").hidden = false;
  } catch (err) {
    renderRegistryRows([]);
    showToast(err.message, "error");
  }
}

$("#refresh-btn")?.addEventListener("click", () => {
  $("#search-input").value = "";
  $("#search-clear").hidden = true;
  refreshAll();
  showToast("Registry refreshed");
});

// ---------------------------------------------------------------------
// Add bird
// ---------------------------------------------------------------------

$("#add-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const msg = $("#add-msg");
  msg.textContent = "";
  msg.className = "form-msg";

  const payload = {
    tag_id: form.tag_id.value.trim(),
    breed: form.breed.value.trim(),
    age_weeks: form.age_weeks.value,
    weight_kg: form.weight_kg.value,
    egg_count: form.egg_count.value,
    health_status: form.health_status.value,
  };

  try {
    await api("/birds", { method: "POST", body: JSON.stringify(payload) });
    msg.textContent = `✔ ${payload.tag_id} added to the registry.`;
    msg.classList.add("is-success");
    form.reset();
    refreshAll();
  } catch (err) {
    msg.textContent = `⚠ ${err.message}`;
    msg.classList.add("is-error");
  }
});

// ---------------------------------------------------------------------
// Edit modal
// ---------------------------------------------------------------------

function openEditModal(bird) {
  const backdrop = $("#edit-backdrop");
  const form = $("#edit-form");
  form.tag_id.value = bird.tag_id;
  form.breed.value = bird.breed;
  form.age_weeks.value = bird.age_weeks;
  form.weight_kg.value = bird.weight_kg;
  form.egg_count.value = bird.egg_count;
  form.health_status.value = bird.health_status;
  $("#edit-title").textContent = `Edit bird — ${bird.tag_id}`;
  $("#edit-msg").textContent = "";
  backdrop.hidden = false;
}

$("#edit-cancel")?.addEventListener("click", () => { $("#edit-backdrop").hidden = true; });
$("#edit-backdrop")?.addEventListener("click", (e) => {
  if (e.target === e.currentTarget) e.currentTarget.hidden = true;
});

$("#edit-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const msg = $("#edit-msg");
  const tag = form.tag_id.value;

  const payload = {
    breed: form.breed.value.trim(),
    age_weeks: form.age_weeks.value,
    weight_kg: form.weight_kg.value,
    egg_count: form.egg_count.value,
    health_status: form.health_status.value,
  };

  try {
    await api(`/birds/${encodeURIComponent(tag)}`, { method: "PUT", body: JSON.stringify(payload) });
    $("#edit-backdrop").hidden = true;
    showToast(`Updated ${tag}`, "success");
    refreshAll();
  } catch (err) {
    msg.textContent = `⚠ ${err.message}`;
    msg.className = "form-msg is-error";
  }
});

// ---------------------------------------------------------------------
// Search panel (hash table lookup — SystemSearch.py)
// ---------------------------------------------------------------------

$("#search2-btn")?.addEventListener("click", runSearch2);
$("#search2-input")?.addEventListener("keydown", (e) => { if (e.key === "Enter") runSearch2(); });

async function runSearch2() {
  const tag = $("#search2-input").value.trim();
  const msg = $("#search2-msg");
  const tbody = $("#search2-tbody");
  const empty = $("#search2-empty");
  msg.textContent = "";
  msg.className = "form-msg";

  if (!tag) {
    msg.textContent = "⚠ Enter a Tag ID first.";
    msg.classList.add("is-error");
    return;
  }

  try {
    const result = await api(`/birds/${encodeURIComponent(tag)}`);
    const b = result.bird;

    tbody.innerHTML = `
      <tr>
        <td class="col-tag">${b.tag_id}</td>
        <td>${b.breed}</td>
        <td>${b.age_weeks}</td>
        <td>${Number(b.weight_kg).toFixed(2)}</td>
        <td>${b.egg_count}</td>
        <td>${badgeFor(b.health_status)}</td>
      </tr>
    `;
    empty.hidden = true;
    msg.innerHTML = `<span class="algo-badge">Found via Hash Table</span>`;
    msg.className = "form-msg is-success";
  } catch (err) {
    tbody.innerHTML = "";
    empty.hidden = false;
    empty.textContent = `No bird found with Tag ID "${tag}".`;
    msg.textContent = `⚠ ${err.message}`;
    msg.classList.add("is-error");
  }
}

// ---------------------------------------------------------------------
// Sort panel
// ---------------------------------------------------------------------

$("#sort-btn")?.addEventListener("click", async () => {
  const criteria = $("#sort-select").value;
  try {
    const sorted = await api(`/sort?criteria=${encodeURIComponent(criteria)}`);
    const tbody = $("#sort-tbody");
    const empty = $("#sort-empty");
    tbody.innerHTML = "";

    if (!sorted.length) {
      empty.hidden = false;
      empty.textContent = "No birds to sort yet.";
      return;
    }
    empty.hidden = true;

    sorted.forEach(b => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="col-tag">${b.tag_id}</td>
        <td>${b.breed}</td>
        <td>${b.age_weeks}</td>
        <td>${Number(b.weight_kg).toFixed(2)}</td>
        <td>${b.egg_count}</td>
        <td>${badgeFor(b.health_status)}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    showToast(err.message, "error");
  }
});

// ---------------------------------------------------------------------
// Alert rail
// ---------------------------------------------------------------------

async function loadAlerts() {
  try {
    const [urgent, alerts] = await Promise.all([
      api("/alerts/most-urgent"),
      api("/alerts"),
    ]);
    renderUrgentSlot(urgent);
    renderAlertList(alerts, urgent);
  } catch (e) {
    // non-fatal
  }
}

function renderUrgentSlot(bird) {
  const slot = $("#urgent-slot");
  if (!bird) {
    slot.innerHTML = `<div class="urgent-slot__empty" id="urgent-empty">No active alerts. Flock is clear.</div>`;
    return;
  }
  slot.innerHTML = `
    <div class="urgent-card">
      <span class="urgent-card__stamp">${bird.health_status.toUpperCase()}</span>
      <div class="urgent-card__tag">${bird.tag_id}</div>
      <div class="urgent-card__meta">${bird.breed} · ${bird.age_weeks}w · ${bird.weight_kg}kg</div>
    </div>
  `;
}

function renderAlertList(alerts, urgent) {
  const list = $("#alert-list");
  list.innerHTML = "";

  const rest = alerts.filter(b => !urgent || b.tag_id !== urgent.tag_id);

  if (!rest.length) {
    if (!alerts.length) {
      list.innerHTML = `<div class="alert-empty">Nothing else in the queue.</div>`;
    }
    return;
  }

  rest.forEach(b => {
    const row = document.createElement("div");
    row.className = "alert-row" + (b.health_status === "Critical" ? " is-critical" : "");
    row.innerHTML = `
      <span class="alert-row__tag">${b.tag_id}</span>
      <span class="alert-row__status">${b.health_status}</span>
    `;
    list.appendChild(row);
  });
}

// ---------------------------------------------------------------------
// Header ledger stamp (date/time)
// ---------------------------------------------------------------------

function updateStamp() {
  const now = new Date();
  const opts = { weekday: "short", year: "numeric", month: "short", day: "numeric" };
  $("#clock-stamp").textContent = now.toLocaleDateString(undefined, opts);
}

// ---------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  updateStamp();
  refreshAll();
});