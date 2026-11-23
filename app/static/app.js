// Mindmap + folder panels. Relations are by strategy name (S3).
const $ = (id) => document.getElementById(id);

function status(msg) { $("status").textContent = msg; }

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
  tree.strategies.forEach((s) => {
    const name = s.replace(/\.md$/, "");
    elements.push({ data: { id: "S:" + name, label: name, kind: "strategy" } });
  });
  tree.ideas.forEach((i) => {
    const id = "I:" + i.replace(/\.md$/, "");
    const strat = strategyOf(i);
    elements.push({ data: { id, label: i.replace(/\.md$/, ""), kind: "idea" } });
    elements.push({ data: { id: "e:" + id, source: "S:" + strat, target: id } });
  });
  tree.draft.forEach((d) => {
    elements.push({ data: { id: "D:" + d, label: d.replace(/\.md$/, ""), kind: "draft" } });
  });
  return elements;
}

const cy = cytoscape({
  container: $("graph"),
  style: [
    { selector: "node", style: { label: "data(label)", "font-size": 11, "text-valign": "bottom", "text-margin-y": 4 } },
    { selector: 'node[kind = "strategy"]', style: { shape: "round-rectangle", "background-color": "#1f6feb", color: "#fff", width: 60, height: 36, "text-valign": "center", "font-weight": "bold" } },
    { selector: 'node[kind = "idea"]', style: { shape: "ellipse", "background-color": "#2da44e", width: 28, height: 28 } },
    { selector: 'node[kind = "draft"]', style: { shape: "ellipse", "background-color": "#bf8700", "border-style": "dashed", width: 24, height: 24 } },
    { selector: "edge", style: { width: 2, "line-color": "#999", "target-arrow-shape": "triangle", "target-arrow-color": "#999", "curve-style": "bezier" } },
  ],
  layout: { name: "breadthfirst", directed: true, spacingFactor: 1.3 },
});

async function refresh() {
  const tree = await (await fetch("/api/tree")).json();
  fill($("draft"), tree.draft);
  fill($("ideas"), tree.ideas);
  fill($("strategies"), tree.strategies.map((s) => s.replace(/\.md$/, "")));

  $("promote-draft").innerHTML = tree.draft.map((d) => `<option>${d}</option>`).join("");
  $("promote-strategy").innerHTML = tree.strategies.map((s) => `<option>${s.replace(/\.md$/, "")}</option>`).join("");

  cy.elements().remove();
  cy.add(buildGraph(tree));
  cy.layout({ name: "breadthfirst", directed: true, spacingFactor: 1.3 }).run();
}

async function post(url, body) {
  const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

$("add-strategy").onclick = async () => {
  try { await post("/api/strategy", { name: $("new-strategy").value.trim() }); status("Estrategia creada"); refresh(); }
  catch (e) { status(e.message); }
};

$("promote").onclick = async () => {
  try {
    const r = await post("/api/promote", { draft: $("promote-draft").value, strategy: $("promote-strategy").value });
    status("Creada " + r.idea); $("clean").onclick = async () => {
  status("Limpiando con Claude...");
  try {
    const r = await post("/api/clean", { draft: $("promote-draft").value, strategy: $("promote-strategy").value });
    status("Idea creada: " + r.idea); refresh();
  } catch (e) { status(e.message); }
};

refresh();
  } catch (e) { status(e.message); }
};

$("clean").onclick = async () => {
  status("Limpiando con Claude...");
  try {
    const r = await post("/api/clean", { draft: $("promote-draft").value, strategy: $("promote-strategy").value });
    status("Idea creada: " + r.idea); refresh();
  } catch (e) { status(e.message); }
};

refresh();
