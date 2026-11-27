// Dashboard de solo lectura: carga /api/results y dibuja la tabla con filtros.
(function () {
  const rowsEl = document.getElementById("rows");
  const statusEl = document.getElementById("status");
  const fStrategy = document.getElementById("f-strategy");
  const fSymbol = document.getElementById("f-symbol");
  const fAnos = document.getElementById("f-anos");
  const fContracts = document.getElementById("f-contracts");
  const fTp = document.getElementById("f-tp");
  const fVerdict = document.getElementById("f-verdict");
  let allRows = [];
  let sortKey = null;
  let sortDir = "asc";

  const fmt = (v, digits = 2) => (v === null || v === undefined ? "—" : Number(v).toFixed(digits));

  function cell(text, cls) {
    const td = document.createElement("td");
    if (cls) td.className = cls;
    td.textContent = text;
    return td;
  }

  function checkCell(value, text) {
    const cls = value === true ? "chk-ok" : value === false ? "chk-no" : "chk-na";
    return cell(text, cls);
  }

  function render() {
    const s = fStrategy.value;
    const sym = fSymbol.value;
    const a = fAnos.value;
    const c = fContracts.value;
    const tp = fTp.value;
    const v = fVerdict.value;
    const rows = allRows.filter((r) => (!s || r.estrategia === s) && (!sym || r.simbolo === sym) &&
      (!a || r.anos === Number(a)) && (!c || r.contratos === Number(c)) && (!tp || r.tp_usd === Number(tp)) && (!v || r.veredicto === v));
    if (sortKey) rows.sort((a, b) => compareRows(a, b, sortKey, sortDir));
    updateArrows();
    rowsEl.innerHTML = "";
    for (const r of rows) {
      const tr = document.createElement("tr");
      tr.appendChild(cell(r.estrategia, "l"));
      tr.appendChild(cell(r.simbolo || "—", "l"));
      tr.appendChild(cell(fmt(r.anos, 0)));
      tr.appendChild(cell(fmt(r.contratos, 0)));
      tr.appendChild(cell(fmt(r.tp_usd, 0)));
      tr.appendChild(cell(fmt(r.sl_usd, 0)));
      tr.appendChild(checkCell(r.checks.trades, fmt(r.trades, 0)));
      tr.appendChild(cell(fmt(r.win_rate_pct, 1)));
      tr.appendChild(cell(fmt(r.payoff)));
      tr.appendChild(checkCell(r.checks.profit_factor, fmt(r.profit_factor)));
      tr.appendChild(checkCell(r.checks.expectancy_usd, fmt(r.expectancy_usd)));
      tr.appendChild(checkCell(r.checks.net_profit_usd, fmt(r.net_profit_usd)));
      tr.appendChild(cell(fmt(r.max_dd_usd)));
      tr.appendChild(cell(fmt(r.max_consec_losses, 0)));
      tr.appendChild(checkCell(r.checks.sharpe, fmt(r.sharpe)));
      tr.appendChild(cell(fmt(r.sortino)));
      tr.appendChild(checkCell(r.checks.top3_pct, fmt(r.top3_pct, 1)));
      tr.appendChild(cell(r.veredicto, "l v-" + r.veredicto));
      tr.appendChild(cell(r.notas || "", "l"));
      rowsEl.appendChild(tr);
    }
    statusEl.textContent = rows.length + " de " + allRows.length + " corridas";
  }

  // Ordena por una columna; los valores vacíos (null) van siempre al final.
  function compareRows(a, b, key, dir) {
    const x = a[key];
    const y = b[key];
    if (x === null || x === undefined) return (y === null || y === undefined) ? 0 : 1;
    if (y === null || y === undefined) return -1;
    let cmp;
    if (typeof x === "number" && typeof y === "number") cmp = x - y;
    else cmp = String(x).localeCompare(String(y), "es");
    return dir === "asc" ? cmp : -cmp;
  }

  function updateArrows() {
    document.querySelectorAll("th.sortable").forEach((th) => {
      const old = th.querySelector(".arrow");
      if (old) old.remove();
      if (th.dataset.key === sortKey) {
        const span = document.createElement("span");
        span.className = "arrow";
        span.textContent = sortDir === "asc" ? "▲" : "▼";
        th.appendChild(span);
      }
    });
  }

  document.querySelectorAll("th.sortable").forEach((th) => {
    th.addEventListener("click", () => {
      const key = th.dataset.key;
      if (sortKey === key) {
        sortDir = sortDir === "asc" ? "desc" : "asc";
      } else {
        sortKey = key;
        sortDir = "asc";
      }
      render();
    });
  });

  function fillStrategies() {
    const names = [...new Set(allRows.map((r) => r.estrategia))].sort();
    fStrategy.innerHTML = '<option value="">todas</option>' +
      names.map((n) => '<option value="' + n + '">' + n + "</option>").join("");
  }

  async function load() {
    statusEl.textContent = "Cargando…";
    try {
      const res = await fetch("/api/results");
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      allRows = data.rows;
      fillStrategies();
      render();
    } catch (err) {
      statusEl.textContent = "Error al cargar: " + err.message;
    }
  }

  // --- Estrategias recomendadas: acordeón cerrado por defecto, carga /api/recommended al abrirlo. ---
  const recEl = document.getElementById("recomendadas");
  const recAnos = document.getElementById("rec-anos");
  const recGroups = document.getElementById("rec-groups");
  const recStatus = document.getElementById("rec-status");
  const recTpl = document.getElementById("rec-table");
  let recData = null;
  let recLoaded = false;

  function renderRecommended() {
    if (!recData) return;
    const a = recAnos.value;
    recGroups.innerHTML = "";
    const tps = Object.keys(recData).sort((x, y) => Number(x) - Number(y));
    for (const tp of tps) {
      const group = document.createElement("div");
      group.className = "rec-group";
      const h = document.createElement("h3");
      h.textContent = "TP $" + tp;
      group.appendChild(h);
      const cands = recData[tp] || [];
      if (!cands.length) {
        const p = document.createElement("p");
        p.className = "rec-empty";
        p.textContent = "sin datos";
        group.appendChild(p);
        recGroups.appendChild(group);
        continue;
      }
      const table = recTpl.content.firstElementChild.cloneNode(true);
      const body = table.querySelector("tbody");
      for (const c of cands) {
        const d = (c.detalle && c.detalle[a]) || {};
        const n = c.neto_by_anos || {};
        const tr = document.createElement("tr");
        tr.appendChild(cell(c.estrategia, "l"));
        tr.appendChild(cell(fmt(c.sl_usd, 0)));
        tr.appendChild(cell(fmt(c.contratos, 0)));
        tr.appendChild(cell(c.aprueba + " / 3"));
        tr.appendChild(cell(fmt(n["6"])));
        tr.appendChild(cell(fmt(n["3"])));
        tr.appendChild(cell(fmt(n["1"])));
        tr.appendChild(cell(fmt(d.profit_factor)));
        tr.appendChild(cell(fmt(d.expectancy_usd)));
        tr.appendChild(cell(fmt(d.net_profit_usd)));
        tr.appendChild(cell(fmt(d.max_consec_losses, 0)));
        tr.appendChild(cell(fmt(d.sharpe)));
        tr.appendChild(cell(fmt(d.top3_pct, 1)));
        tr.appendChild(cell(d.veredicto || "—", "l v-" + (d.veredicto || "pendiente")));
        tr.appendChild(cell(fmt(d.win_rate_pct, 1)));
        body.appendChild(tr);
      }
      group.appendChild(table);
      recGroups.appendChild(group);
    }
    if (!tps.length) recGroups.innerHTML = '<p class="rec-empty">sin datos</p>';
  }

  async function loadRecommended() {
    recStatus.textContent = "Cargando…";
    try {
      const res = await fetch("/api/recommended");
      if (!res.ok) throw new Error("HTTP " + res.status);
      recData = (await res.json()).por_tp || {};
      recLoaded = true;
      recStatus.textContent = "";
      renderRecommended();
    } catch (err) {
      recStatus.textContent = "Error al cargar: " + err.message;
    }
  }

  recEl.addEventListener("toggle", () => {
    if (recEl.open && !recLoaded) loadRecommended();
  });
  recAnos.addEventListener("change", renderRecommended);

  fStrategy.addEventListener("change", render);
  fSymbol.addEventListener("change", render);
  fAnos.addEventListener("change", render);
  fContracts.addEventListener("change", render);
  fTp.addEventListener("change", render);
  fVerdict.addEventListener("change", render);
  document.getElementById("reload").addEventListener("click", () => {
    load();
    // Recarga las recomendadas si ya se abrieron alguna vez.
    if (recLoaded || recEl.open) loadRecommended();
  });
  load();
})();
