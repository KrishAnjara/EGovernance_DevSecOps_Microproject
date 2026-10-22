(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const el = (tag, text, cls) => { const e = document.createElement(tag); if (text !== undefined) e.textContent = text; if (cls) e.className = cls; return e; };
  const getJSON = (u) => fetch(u).then((r) => r.json());

  function renderCompare(rows) {
    const body = $("#cmp-table tbody");
    const q = $("#cmp-filter").value.trim().toLowerCase();
    body.replaceChildren();
    rows.filter((r) => !q || JSON.stringify(r).toLowerCase().includes(q)).forEach((r) => {
      const tr = el("tr");
      const th = el("th", r.dimension); th.scope = "row"; tr.append(th);
      tr.append(el("td", r.waterfall, "col-wf"), el("td", r.incremental, "col-inc"), el("td", r.agile, "col-ag"));
      body.append(tr);
    });
    if (!body.children.length) { const tr = el("tr"); const td = el("td", "No rows match your filter."); td.colSpan = 4; tr.append(td); body.append(tr); }
  }

  function initCompare() {
    getJSON("/api/models").then((d) => {
      renderCompare(d.comparison);
      $("#cmp-filter").addEventListener("input", () => renderCompare(d.comparison));
    }).catch(() => { $("#cmp-table tbody").textContent = "Could not load comparison data."; });
    document.querySelectorAll("[data-hl]").forEach((b) => b.addEventListener("click", () => {
      document.querySelectorAll("[data-hl]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      const t = $("#cmp-table"); t.className = "";
      const k = { waterfall: "dim-wf", incremental: "dim-inc", agile: "dim-ag" }[b.dataset.hl];
      if (k) t.classList.add(k);
    }));
  }

  function bars(id, obj) {
    const box = $(id); box.replaceChildren();
    const max = Math.max(...Object.values(obj), 1);
    Object.entries(obj).forEach(([k, v]) => {
      const row = el("div", undefined, "bar"), track = el("div", undefined, "track"), fill = el("span", undefined, "fill");
      fill.style.width = Math.round((v / max) * 100) + "%";
      track.append(fill); row.append(el("span", k), track, el("span", String(v)));
      box.append(row);
    });
  }

  function initAdmin() {
    getJSON("/api/admin/summary").then((s) => {
      const k = $("#admin-kpis"); k.replaceChildren();
      [["Synthetic applications", s.total], ["Avg. days to process", s.avg_days_to_process]].forEach(([l, v]) => {
        const d = el("div", undefined, "kpi"); d.append(el("b", String(v)), el("span", l)); k.append(d);
      });
      bars("#bar-service", s.by_service); bars("#bar-status", s.by_status); bars("#bar-month", s.by_month);
    }).catch(() => { $("#admin-kpis").textContent = "Could not load synthetic data."; });
  }

  function initPortal() {
    const sel = $("#svc");
    getJSON("/api/services").then((d) => d.services.forEach((s) => { const o = el("option", s.name); o.value = s.id; sel.append(o); }));
    $("#apply-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const msg = $("#apply-msg"); msg.className = ""; msg.textContent = "Submitting...";
      const res = await fetch("/api/applications", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ service: sel.value, alias: $("#alias").value, details: $("#details").value }) });
      const d = await res.json();
      if (res.ok) { msg.className = "ok"; msg.textContent = "Simulated application created. Reference: " + d.ref; $("#ref").value = d.ref; }
      else { msg.className = "err"; msg.textContent = Object.values(d.errors || { e: d.error || "Request failed." }).join(" "); }
    });
    $("#track-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const msg = $("#track-msg"), list = $("#track-steps");
      const res = await fetch("/api/applications/" + encodeURIComponent($("#ref").value.trim()));
      const d = await res.json();
      if (!res.ok) { msg.className = "err"; msg.textContent = d.error; list.hidden = true; return; }
      msg.className = "ok"; msg.textContent = d.service + ": " + d.status;
      list.replaceChildren(); list.hidden = false;
      d.steps.forEach((s, i) => list.append(el("li", s, i <= d.step ? "done" : "")));
    });
  }

  initCompare(); initAdmin(); initPortal();
})();
