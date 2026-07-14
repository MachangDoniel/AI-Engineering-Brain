#!/usr/bin/env python3
"""Generate the project knowledge graph artifacts.

The graph models this library itself: chapters, tools, and concepts as
nodes; COVERS / USES / STORES_IN / SUPPORTS / ... as relationships.

Outputs (all in this directory unless noted):
  graph.json   - nodes + edges data
  graph.cypher - Neo4j import script (works on AuraDB Free / Community)
  index.html   - self-contained interactive force-directed viewer
  ../assets/knowledge-graph.svg - static overview for the README
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

CH = "chapter"
TOOL = "tool"
CONCEPT = "concept"

NODES = [
    # Chapters (url = repo-relative path)
    {"id": "c1",  "label": "Ch 1 — Executive Summary",        "type": CH, "url": "../chapters/01-executive-summary.md"},
    {"id": "c2",  "label": "Ch 2 — Evolution",                "type": CH, "url": "../chapters/02-evolution-of-ai-software-engineering.md"},
    {"id": "c3",  "label": "Ch 3 — Prompt → Knowledge",       "type": CH, "url": "../chapters/03-prompt-to-knowledge-engineering.md"},
    {"id": "c4",  "label": "Ch 4 — Why RAG Isn't Enough",     "type": CH, "url": "../chapters/04-why-rag-isnt-enough.md"},
    {"id": "c5",  "label": "Ch 5 — Knowledge Graphs",         "type": CH, "url": "../chapters/05-knowledge-graphs.md"},
    {"id": "c6",  "label": "Ch 6 — GraphRAG",                 "type": CH, "url": "../chapters/06-graphrag.md"},
    {"id": "c7",  "label": "Ch 7 — Graphify",                 "type": CH, "url": "../chapters/07-graphify.md"},
    {"id": "c8",  "label": "Ch 8 — Graphiti",                 "type": CH, "url": "../chapters/08-graphiti.md"},
    {"id": "c9",  "label": "Ch 9 — Tree-sitter",              "type": CH, "url": "../chapters/09-tree-sitter.md"},
    {"id": "c10", "label": "Ch 10 — Neo4j & Qdrant",          "type": CH, "url": "../chapters/10-neo4j-and-qdrant.md"},
    {"id": "c11", "label": "Ch 11 — MCP & Agents",            "type": CH, "url": "../chapters/11-mcp-and-ai-agents.md"},
    {"id": "c12", "label": "Ch 12 — Production",              "type": CH, "url": "../chapters/12-costs-deployment-future.md"},
    {"id": "c13", "label": "Ch 13 — Compound Engineering",    "type": CH, "url": "../chapters/13-compound-engineering.md"},
    {"id": "c14", "label": "Ch 14 — Multi-Agent Systems",     "type": CH, "url": "../chapters/14-multi-agent-systems.md"},
    {"id": "c15", "label": "Ch 15 — Virtual Organizations",   "type": CH, "url": "../chapters/15-virtual-organizations.md"},
    {"id": "cA",  "label": "Appendix — Tool Directory",       "type": CH, "url": "../appendix/tool-directory.md"},
    # Tools
    {"id": "graphify",   "label": "Graphify",    "type": TOOL, "url": "https://github.com/safishamsi/graphify"},
    {"id": "graphiti",   "label": "Graphiti",    "type": TOOL, "url": "https://github.com/getzep/graphiti"},
    {"id": "neo4j",      "label": "Neo4j",       "type": TOOL, "url": "https://neo4j.com"},
    {"id": "qdrant",     "label": "Qdrant",      "type": TOOL, "url": "https://qdrant.tech"},
    {"id": "treesitter", "label": "Tree-sitter", "type": TOOL, "url": "https://github.com/tree-sitter/tree-sitter"},
    {"id": "mcp",        "label": "MCP",         "type": TOOL, "url": "https://modelcontextprotocol.io"},
    {"id": "claudecode", "label": "Claude Code", "type": TOOL, "url": "https://claude.com/claude-code"},
    {"id": "codex",      "label": "Codex",       "type": TOOL, "url": "https://openai.com/codex/"},
    {"id": "cursor",     "label": "Cursor",      "type": TOOL, "url": "https://cursor.com"},
    {"id": "geminicli",  "label": "Gemini CLI",  "type": TOOL, "url": "https://github.com/google-gemini/gemini-cli"},
    {"id": "continue",   "label": "Continue",    "type": TOOL, "url": "https://continue.dev"},
    {"id": "opencode",   "label": "OpenCode",    "type": TOOL, "url": "https://github.com/sst/opencode"},
    {"id": "sourcegraph","label": "Sourcegraph", "type": TOOL, "url": "https://sourcegraph.com"},
    {"id": "llamaindex", "label": "LlamaIndex",  "type": TOOL, "url": "https://www.llamaindex.ai"},
    {"id": "deepwiki",   "label": "DeepWiki",    "type": TOOL, "url": "https://deepwiki.com"},
    {"id": "gitingest",  "label": "Gitingest",   "type": TOOL, "url": "https://gitingest.com"},
    {"id": "langgraph",  "label": "LangGraph",   "type": TOOL, "url": "https://github.com/langchain-ai/langgraph"},
    # Concepts
    {"id": "prompteng",  "label": "Prompt Engineering",  "type": CONCEPT},
    {"id": "contexteng", "label": "Context Engineering", "type": CONCEPT},
    {"id": "rag",        "label": "RAG",                 "type": CONCEPT},
    {"id": "kg",         "label": "Knowledge Graph",     "type": CONCEPT},
    {"id": "graphrag",   "label": "GraphRAG",            "type": CONCEPT},
    {"id": "specdriven", "label": "Spec-Driven Dev",     "type": CONCEPT},
    {"id": "memory",     "label": "Agent Memory",        "type": CONCEPT},
    {"id": "ast",        "label": "AST",                 "type": CONCEPT},
    {"id": "embeddings", "label": "Embeddings",          "type": CONCEPT},
    {"id": "propgraph",  "label": "Property Graph",      "type": CONCEPT},
    {"id": "compound",   "label": "Compound Engineering","type": CONCEPT},
    {"id": "orchestration", "label": "Agent Orchestration", "type": CONCEPT},
    {"id": "mas",        "label": "Multi-Agent System",  "type": CONCEPT},
    {"id": "vo",         "label": "Virtual Organization","type": CONCEPT},
]

E = lambda s, r, t: {"source": s, "rel": r, "target": t}
EDGES = [
    # Reading order
    *[E(f"c{i}", "FOLLOWED_BY", f"c{i+1}") for i in range(1, 15)],
    E("c15", "FOLLOWED_BY", "cA"),
    # Chapter -> topic coverage
    E("c1", "COVERS", "kg"),
    E("c2", "COVERS", "rag"), E("c2", "COVERS", "graphrag"),
    E("c3", "COVERS", "prompteng"), E("c3", "COVERS", "contexteng"), E("c3", "COVERS", "specdriven"),
    E("c4", "COVERS", "rag"), E("c4", "COVERS", "embeddings"),
    E("c5", "COVERS", "kg"), E("c5", "COVERS", "propgraph"),
    E("c6", "COVERS", "graphrag"),
    E("c7", "COVERS", "graphify"),
    E("c8", "COVERS", "graphiti"), E("c8", "COVERS", "memory"),
    E("c9", "COVERS", "treesitter"), E("c9", "COVERS", "ast"),
    E("c10", "COVERS", "neo4j"), E("c10", "COVERS", "qdrant"),
    E("c11", "COVERS", "mcp"), E("c11", "COVERS", "claudecode"),
    E("c12", "RECOMMENDS", "graphify"), E("c12", "RECOMMENDS", "claudecode"),
    E("c13", "COVERS", "compound"),
    E("c14", "COVERS", "mas"), E("c14", "COVERS", "orchestration"),
    E("c15", "COVERS", "vo"),
    E("cA", "CATALOGS", "sourcegraph"), E("cA", "CATALOGS", "llamaindex"),
    E("cA", "CATALOGS", "deepwiki"), E("cA", "CATALOGS", "gitingest"),
    E("cA", "CATALOGS", "langgraph"), E("cA", "CATALOGS", "continue"),
    # Tool / concept topology (the stack itself)
    E("graphify", "USES", "treesitter"),
    E("graphify", "BUILDS", "kg"),
    E("graphify", "STORES_IN", "neo4j"),
    E("graphiti", "STORES_IN", "neo4j"),
    E("graphiti", "ENABLES", "memory"),
    E("treesitter", "PRODUCES", "ast"),
    E("neo4j", "IMPLEMENTS", "propgraph"),
    E("qdrant", "STORES", "embeddings"),
    E("rag", "USES", "embeddings"),
    E("contexteng", "EVOLVES_FROM", "prompteng"),
    E("rag", "IMPLEMENTS", "contexteng"),
    E("specdriven", "COMPLEMENTS", "contexteng"),
    E("graphrag", "COMBINES", "rag"),
    E("graphrag", "COMBINES", "kg"),
    E("mcp", "CONNECTS", "neo4j"),
    E("mcp", "CONNECTS", "qdrant"),
    E("claudecode", "SUPPORTS", "mcp"),
    E("codex", "SUPPORTS", "mcp"),
    E("cursor", "SUPPORTS", "mcp"),
    E("geminicli", "SUPPORTS", "mcp"),
    E("continue", "SUPPORTS", "mcp"),
    E("opencode", "SUPPORTS", "mcp"),
    E("graphify", "INTEGRATES_WITH", "claudecode"),
    E("graphify", "INTEGRATES_WITH", "cursor"),
    E("graphify", "INTEGRATES_WITH", "codex"),
    E("llamaindex", "IMPLEMENTS", "rag"),
    E("sourcegraph", "RELATED_TO", "kg"),
    # Agents → organizations (Ch 13–15)
    E("compound", "FEEDS", "kg"),
    E("compound", "BUILDS_ON", "specdriven"),
    E("mas", "USES", "orchestration"),
    E("mas", "REQUIRES", "memory"),
    E("mas", "USES", "mcp"),
    E("claudecode", "IMPLEMENTS", "mas"),
    E("vo", "CONTAINS", "mas"),
    E("vo", "REQUIRES", "memory"),
    E("vo", "USES", "kg"),
    E("vo", "REQUIRES", "compound"),
]


def write_json():
    with open(os.path.join(HERE, "graph.json"), "w") as f:
        json.dump({"nodes": NODES, "edges": EDGES}, f, indent=2)


def write_cypher():
    label_for = {CH: "Chapter", TOOL: "Tool", CONCEPT: "Concept"}
    lines = [
        "// The AI Engineering Brain — project knowledge graph",
        "// Import into Neo4j (AuraDB Free or Community):  cat graph.cypher | cypher-shell",
        "MATCH (n:Chapter|Tool|Concept) DETACH DELETE n;",
        "",
    ]
    for n in NODES:
        props = f"id: '{n['id']}', name: \"{n['label']}\""
        if n.get("url"):
            props += f", url: \"{n['url']}\""
        lines.append(f"CREATE (:{label_for[n['type']]} {{{props}}});")
    lines.append("")
    for e in EDGES:
        lines.append(
            "MATCH (a {id: '%s'}), (b {id: '%s'}) CREATE (a)-[:%s]->(b);"
            % (e["source"], e["target"], e["rel"])
        )
    lines += [
        "",
        "// Example queries",
        "// Which chapters cover the recommended stack?",
        "// MATCH (c:Chapter)-[:COVERS]->(t:Tool) RETURN c.name, t.name;",
        "// What does Graphify connect to?",
        "// MATCH (g:Tool {name:'Graphify'})-[r]-(x) RETURN g.name, type(r), x.name;",
    ]
    with open(os.path.join(HERE, "graph.cypher"), "w") as f:
        f.write("\n".join(lines) + "\n")


def write_html():
    data = json.dumps({"nodes": NODES, "edges": EDGES})
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The AI Engineering Brain — Knowledge Graph</title>
<style>
  html, body { margin: 0; height: 100%; background: #0f172a; color: #e2e8f0;
               font-family: "Segoe UI", Helvetica, Arial, sans-serif; }
  #hud { position: fixed; top: 12px; left: 16px; z-index: 2; }
  #hud h1 { font-size: 18px; margin: 0 0 4px; }
  #hud p { font-size: 12px; color: #94a3b8; margin: 0; }
  #legend { position: fixed; bottom: 12px; left: 16px; z-index: 2; font-size: 12px; }
  .chip { display: inline-block; margin-right: 12px; }
  .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%;
         margin-right: 4px; vertical-align: -1px; }
  #info { position: fixed; top: 12px; right: 16px; z-index: 2; background: #1e293bcc;
          border: 1px solid #334155; border-radius: 8px; padding: 10px 14px;
          font-size: 13px; max-width: 260px; display: none; }
  #info a { color: #7dd3fc; }
  canvas { display: block; }
</style>
</head>
<body>
<div id="hud">
  <h1>🧠 The AI Engineering Brain — Knowledge Graph</h1>
  <p>Drag nodes · hover for relationships · click a node to open it</p>
</div>
<div id="legend">
  <span class="chip"><span class="dot" style="background:#60a5fa"></span>Chapter</span>
  <span class="chip"><span class="dot" style="background:#4ade80"></span>Tool</span>
  <span class="chip"><span class="dot" style="background:#c084fc"></span>Concept</span>
</div>
<div id="info"></div>
<canvas id="c"></canvas>
<script>
const DATA = __DATA__;
const COLORS = { chapter: "#60a5fa", tool: "#4ade80", concept: "#c084fc" };
const canvas = document.getElementById("c"), ctx = canvas.getContext("2d");
const info = document.getElementById("info");
let W, H;
function resize() { W = canvas.width = innerWidth; H = canvas.height = innerHeight; }
addEventListener("resize", resize); resize();

const nodes = DATA.nodes.map((n, i) => ({ ...n,
  x: W/2 + Math.cos(i * 2.399) * (120 + 9*i),
  y: H/2 + Math.sin(i * 2.399) * (90 + 6*i),
  vx: 0, vy: 0 }));
const byId = Object.fromEntries(nodes.map(n => [n.id, n]));
const edges = DATA.edges.map(e => ({ ...e, a: byId[e.source], b: byId[e.target] }));
const degree = {}; edges.forEach(e => { degree[e.source]=(degree[e.source]||0)+1;
                                        degree[e.target]=(degree[e.target]||0)+1; });
const R = n => 7 + Math.min(11, (degree[n.id]||1) * 1.3);

let dragging = null, hovered = null;
function tick() {
  for (const e of edges) {                        // springs
    const dx = e.b.x - e.a.x, dy = e.b.y - e.a.y;
    const d = Math.hypot(dx, dy) || 1, f = (d - 130) * 0.004;
    e.a.vx += f*dx/d; e.a.vy += f*dy/d; e.b.vx -= f*dx/d; e.b.vy -= f*dy/d;
  }
  for (let i = 0; i < nodes.length; i++)          // repulsion
    for (let j = i+1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      let dx = b.x-a.x, dy = b.y-a.y, d2 = dx*dx+dy*dy || 1;
      if (d2 < 90000) { const f = 1400 / d2, d = Math.sqrt(d2);
        a.vx -= f*dx/d; a.vy -= f*dy/d; b.vx += f*dx/d; b.vy += f*dy/d; }
    }
  for (const n of nodes) {                        // centering + integrate
    n.vx += (W/2 - n.x) * 0.0008; n.vy += (H/2 - n.y) * 0.0008;
    if (n !== dragging) { n.x += n.vx *= 0.85; n.y += n.vy *= 0.85; }
  }
}
function draw() {
  ctx.clearRect(0, 0, W, H);
  for (const e of edges) {
    const hot = hovered && (e.a === hovered || e.b === hovered);
    ctx.strokeStyle = hot ? "#e2e8f0" : "#33415577";
    ctx.lineWidth = hot ? 1.6 : 1;
    ctx.beginPath(); ctx.moveTo(e.a.x, e.a.y); ctx.lineTo(e.b.x, e.b.y); ctx.stroke();
    if (hot) {
      ctx.fillStyle = "#fbbf24"; ctx.font = "10px sans-serif"; ctx.textAlign = "center";
      ctx.fillText(e.rel, (e.a.x+e.b.x)/2, (e.a.y+e.b.y)/2 - 4);
    }
  }
  for (const n of nodes) {
    ctx.beginPath(); ctx.arc(n.x, n.y, R(n), 0, 7);
    ctx.fillStyle = COLORS[n.type]; ctx.globalAlpha = hovered && n !== hovered &&
      !edges.some(e => (e.a===hovered&&e.b===n)||(e.b===hovered&&e.a===n)) ? 0.25 : 1;
    ctx.fill(); ctx.globalAlpha = 1;
    ctx.fillStyle = "#e2e8f0"; ctx.font = (n===hovered?"bold ":"") + "11px sans-serif";
    ctx.textAlign = "center"; ctx.fillText(n.label, n.x, n.y - R(n) - 5);
  }
}
(function loop() { tick(); draw(); requestAnimationFrame(loop); })();

function pick(x, y) { return nodes.find(n => Math.hypot(n.x-x, n.y-y) < R(n)+4); }
canvas.onmousedown = e => { dragging = pick(e.clientX, e.clientY); };
canvas.onmouseup = () => { dragging = null; };
canvas.onmousemove = e => {
  if (dragging) { dragging.x = e.clientX; dragging.y = e.clientY; return; }
  hovered = pick(e.clientX, e.clientY);
  canvas.style.cursor = hovered ? "pointer" : "default";
  if (hovered) {
    const rels = edges.filter(x => x.a===hovered || x.b===hovered)
      .map(x => x.a===hovered ? `→ ${x.rel} → ${x.b.label}` : `← ${x.rel} ← ${x.a.label}`);
    info.style.display = "block";
    info.innerHTML = `<b>${hovered.label}</b><br>` +
      (hovered.url ? `<a href="${hovered.url}">open</a><br>` : "") +
      `<span style="color:#94a3b8">${rels.slice(0, 8).join("<br>")}` +
      (rels.length > 8 ? `<br>… ${rels.length-8} more` : "") + `</span>`;
  } else info.style.display = "none";
};
canvas.onclick = e => { const n = pick(e.clientX, e.clientY);
  if (n && n.url) open(n.url, "_blank"); };
</script>
</body>
</html>
"""
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(html.replace("__DATA__", data))


def write_svg():
    # Curated static overview: the stack topology (chapters omitted for clarity).
    pos = {
        "prompteng": (100, 80), "contexteng": (255, 80), "rag": (400, 80),
        "graphrag": (545, 80), "kg": (700, 80), "memory": (845, 80),
        "treesitter": (140, 215), "ast": (60, 300), "graphify": (330, 215),
        "graphiti": (520, 215), "neo4j": (680, 215), "qdrant": (830, 215),
        "embeddings": (830, 305), "propgraph": (610, 305),
        "mcp": (470, 330),
        "claudecode": (150, 430), "codex": (310, 430), "cursor": (470, 430),
        "geminicli": (630, 430), "continue": (790, 430),
    }
    color = {CH: ("#1e3a5f", "#60a5fa", "#bfdbfe"), TOOL: ("#14532d", "#22c55e", "#bbf7d0"),
             CONCEPT: ("#4a1d6e", "#a855f7", "#e9d5ff")}
    show_edges = [(e["source"], e["target"]) for e in EDGES
                  if e["source"] in pos and e["target"] in pos]
    node_by_id = {n["id"]: n for n in NODES}
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 500" '
           'font-family="Segoe UI, Helvetica, Arial, sans-serif">',
           '<rect x="0" y="0" width="940" height="500" rx="12" fill="#0f172a"/>',
           '<text x="470" y="34" text-anchor="middle" fill="#e2e8f0" font-size="18" '
           'font-weight="700">Project Knowledge Graph — Concepts, Stack &amp; Agents</text>']
    for s, t in show_edges:
        (x1, y1), (x2, y2) = pos[s], pos[t]
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                   'stroke="#334155" stroke-width="1.4"/>')
    for nid, (x, y) in pos.items():
        n = node_by_id[nid]
        fill, stroke, text = color[n["type"]]
        out.append(f'<circle cx="{x}" cy="{y}" r="30" fill="{fill}" stroke="{stroke}" '
                   'stroke-width="1.5"/>')
        words = n["label"].split(" ")
        if len(words) > 1 and len(n["label"]) > 11:
            out.append(f'<text x="{x}" y="{y-1}" text-anchor="middle" fill="{text}" '
                       f'font-size="9.5" font-weight="600">{words[0]}</text>')
            out.append(f'<text x="{x}" y="{y+10}" text-anchor="middle" fill="{text}" '
                       f'font-size="9.5" font-weight="600">{" ".join(words[1:])}</text>')
        else:
            out.append(f'<text x="{x}" y="{y+4}" text-anchor="middle" fill="{text}" '
                       f'font-size="10" font-weight="600">{n["label"]}</text>')
    out.append(f'<text x="470" y="486" text-anchor="middle" fill="#94a3b8" font-size="11">'
               f'Interactive version with all {len(NODES)} nodes: knowledge-graph/index.html · '
               'Neo4j import: knowledge-graph/graph.cypher</text>')
    out.append('</svg>')
    with open(os.path.join(HERE, "..", "assets", "knowledge-graph.svg"), "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    write_json()
    write_cypher()
    write_html()
    write_svg()
    print(f"nodes={len(NODES)} edges={len(EDGES)} -> graph.json, graph.cypher, index.html, ../assets/knowledge-graph.svg")
