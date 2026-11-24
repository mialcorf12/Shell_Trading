// Mindmap + folder panels. Relations are by strategy name (S3).
const $ = (id) => document.getElementById(id);

function status(msg, ok = true) {
  const el = $("status");
  el.textContent = msg;
  el.style.color = ok ? "#3fb950" : "#f85149";
}

function fill(ul, names) {
  ul.innerHTML = "";
  names.forEach((n) => {
    const li = document.createElement("li");
    li.textContent = n;
    ul.appendChild(li);
  });
}

function strategyOf(idea) {
  const m = idea.match(/^(.+)_\d+\.md$/);
  return m ? m[1] : idea.replace(/\.md$/, "");
}

function buildGraph(tree) {
  const elements = [];
  const strategyNames = new Set(tree.strategies.map((s) => s.replace(/\.md$/, "")));
  const contextNames = new Set((tree.context || []).map((s) => s.replace(/\.md$/, "")));
  tree.strategies.forEach((s) => {
    const name = s.replace(/\.md$/, "");
    elements.push({ data: { id: "S:" + name, label: name, kind: "strategy" } });
  });
  (tree.context || []).forEach((c) => {
    const name = c.replace(/\.md$/, "");
    elements.push({ data: { id: "C:" + name, label: name, kind: "context" } });
  });
  tree.ideas.forEach((i) => {
    const id = "I:" + i.replace(/\.md$/, "");
    const strat = strategyOf(i);
    elements.push({ data: { id, label: i.replace(/\.md$/, ""), kind: "idea" } });
    // An idea links to its strategy, or to its contexto note when it moved there.
    // An idea with no parent node stays unlinked: an edge to a missing node aborts cy.add().
    if (strategyNames.has(strat)) {
      elements.push({ data: { id: "e:" + id, source: "S:" + strat, target: id } });
    } else if (contextNames.has(strat)) {
      elements.push({ data: { id: "e:" + id, source: "C:" + strat, target: id } });
    }
  });
  tree.draft.forEach((d) => {
    elements.push({ data: { id: "D:" + d, label: d.replace(/\.md$/, ""), kind: "draft" } });
  });
  return elements;
}

// Icons: lightbulbs are SVG data URIs (Cytoscape has no bulb shape).
const bulb = (fill) => "data:image/svg+xml;utf8," + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">' +
  `<path fill="${fill}" stroke="#333" stroke-width="0.9" d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/>` +
  '<rect fill="#555" x="9" y="18" width="6" height="2" rx="1"/>' +
  '<rect fill="#555" x="9.5" y="20.5" width="5" height="1.5" rx="0.7"/></svg>');

const cy = cytoscape({
  container: $("graph"),
  style: [
    // Labels stay hidden until the pointer is over the node (class "hover").
    { selector: "node", style: { label: "", color: "#c9d1d9", "font-size": 11, "text-valign": "bottom", "text-margin-y": 4, "border-width": 0 } },
    { selector: "node.hover", style: { label: "data(label)", color: "#e6edf3", "text-background-color": "#161b22", "text-background-opacity": 0.92, "text-background-padding": 3 } },
    // Strategy: blue star.
    { selector: 'node[kind = "strategy"]', style: { shape: "star", "background-color": "#58a6ff", width: 42, height: 42 } },
    // Ideas depuradas: yellow lightbulb.
    { selector: 'node[kind = "idea"]', style: { shape: "ellipse", "background-opacity": 0, "background-image": bulb("#ffd33d"), "background-fit": "contain", width: 30, height: 30 } },
    // Contexto no operable: fuchsia diamond.
    { selector: 'node[kind = "context"]', style: { shape: "diamond", "background-color": "#ff00ff", width: 38, height: 38 } },
    // ideas/draft: gray lightbulb.
    { selector: 'node[kind = "draft"]', style: { shape: "ellipse", "background-opacity": 0, "background-image": bulb("#9aa0a6"), "background-fit": "contain", width: 26, height: 26 } },
    { selector: "edge", style: { width: 2, "line-color": "#484f58", "target-arrow-shape": "triangle", "target-arrow-color": "#484f58", "curve-style": "bezier" } },
  ],
  layout: { name: "breadthfirst", directed: true, spacingFactor: 1.3 },
});

// Preload the bulb icons and redraw once they are ready; otherwise they stay blank until a zoom.
[bulb("#ffd33d"), bulb("#9aa0a6")].forEach((src) => {
  const img = new Image();
  img.onload = () => cy.forceRender();
  img.src = src;
});

// Show a node's name only while the pointer is over it.
cy.on("mouseover", "node", (e) => e.target.addClass("hover"));
cy.on("mouseout", "node", (e) => e.target.removeClass("hover"));

async function refresh() {
  const tree = await (await fetch("/api/tree")).json();
  fill($("draft"), tree.draft);
  fill($("ideas"), tree.ideas);
  fill($("strategies"), tree.strategies.map((s) => s.replace(/\.md$/, "")));
  fill($("context"), tree.context.map((s) => s.replace(/\.md$/, "")));

  $("promote-draft").innerHTML = tree.draft.map((d) => `<option>${d}</option>`).join("");
  $("promote-strategy").innerHTML = tree.strategies.map((s) => `<option>${s.replace(/\.md$/, "")}</option>`).join("");

  cy.elements().remove();
  cy.add(buildGraph(tree));
  cy.layout({ name: "breadthfirst", directed: true, spacingFactor: 1.3 }).run();
  cy.forceRender();
}

async function post(url, body) {
  const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

$("promote").onclick = async () => {
  try {
    const r = await post("/api/promote", { draft: $("promote-draft").value, strategy: $("promote-strategy").value });
    status("Creada " + r.idea);
    refresh();
  } catch (e) { status(e.message, false); }
};

$("clean").onclick = async () => {
  status("Limpiando con Claude...");
  try {
    const r = await post("/api/clean", { draft: $("promote-draft").value, strategy: $("promote-strategy").value });
    status("Idea creada: " + r.idea);
    refresh();
  } catch (e) { status(e.message, false); }
};

refresh();
