# Chapter 3 — The Reference Architecture

> [◀ Chapter 2](02-rag-knowledge-graphs-graphrag.md) · [🏠 Home](../README.md) · [Chapter 4 ▶](04-graph-builders-graphify-graphiti.md)

---

This chapter assembles the full pipeline of an AI engineering brain — the architecture the rest of the library dissects component by component.

## 3.1 The Pipeline

<p align="center">
  <img src="../assets/architecture.svg" alt="Reference architecture: repositories through Tree-sitter, Graphify, Neo4j, Qdrant, and MCP to AI coding agents" width="720">
</p>

```
Repositories (code, SQL, docs, infra)
   ↓
Tree-sitter          — parse code into ASTs
   ↓
Graphify             — extract entities & relationships
   ↓
Neo4j                — store the knowledge graph
   ↓
Qdrant               — store embeddings for semantic search
   ↓
MCP Server           — expose graph + vectors as agent tools
   ↓
Claude Code / Codex / Cursor / Gemini CLI
```

## 3.2 What Each Layer Contributes

| Layer | Tool | Role | Covered in |
|-------|------|------|-----------|
| Parsing | [Tree-sitter](https://github.com/tree-sitter/tree-sitter) | Code → AST → entities | [Chapter 6](06-parsing-and-mcp.md) |
| Extraction | [Graphify](https://github.com/safishamsi/graphify) | Repos, schemas, docs → graph-ready entities & edges | [Chapter 4](04-graph-builders-graphify-graphiti.md) |
| Memory | [Graphiti](https://github.com/getzep/graphiti) | Temporal facts — how knowledge changes over time | [Chapter 4](04-graph-builders-graphify-graphiti.md) |
| Graph store | [Neo4j](https://neo4j.com) | Relationships as first-class, queryable data | [Chapter 5](05-storage-neo4j-qdrant.md) |
| Vector store | [Qdrant](https://qdrant.tech) | Semantic similarity over code & docs | [Chapter 5](05-storage-neo4j-qdrant.md) |
| Integration | [MCP](https://modelcontextprotocol.io) | Standard protocol connecting agents to all of the above | [Chapter 6](06-parsing-and-mcp.md) |
| Agents | [Claude Code](https://claude.com/claude-code) et al. | Reasoning and code generation on top of the brain | [Chapter 7](07-ai-coding-agents.md) |

## 3.3 Three Sizes of the Same Idea

You don't need the whole stack on day one.

### Option A — Simple Setup

```
Coding agent + Graphify
```

Graphify builds a local knowledge graph the agent queries directly. Good for individual developers; a code-only corpus needs no external services at all.

### Option B — Advanced Engineering Assistant

```
Coding agent → Graphify → Neo4j → Qdrant
```

Adds a persistent graph database and semantic search: architecture awareness plus "find similar" retrieval.

### Option C — Full Engineering Brain

```
Coding agent(s) → Graphify + Graphiti → Neo4j + Qdrant → (optionally LlamaIndex for extra data sources)
```

Adds temporal memory (Graphiti) and broader ingestion ([LlamaIndex](https://www.llamaindex.ai) connects PDFs, databases, APIs). Capabilities:

- Repository understanding & architectural reasoning
- Long-term memory across sessions
- Cross-project relationships
- Semantic search + knowledge graph traversal

## 3.4 A Query, End to End

*"Which Flutter screens call this API?"*

1. The agent sends the question through **MCP** to the graph tool.
2. **Neo4j** traverses `(:Screen)-[:CALLS]->(:Endpoint)` edges — built earlier by Tree-sitter + Graphify.
3. **Qdrant** supplements with semantically related docs (API specs, ADRs).
4. The agent answers with exact file paths — no guessing, no grepping.

The next three chapters open up each box in this diagram.

---

> [◀ Chapter 2: RAG vs Knowledge Graphs vs GraphRAG](02-rag-knowledge-graphs-graphrag.md) · [🏠 Home](../README.md) · [Chapter 4: Graph Builders ▶](04-graph-builders-graphify-graphiti.md)
