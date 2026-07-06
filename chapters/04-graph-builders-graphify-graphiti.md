# Chapter 4 — Graph Builders: Graphify & Graphiti

> [◀ Chapter 3](03-system-architecture.md) · [🏠 Home](../README.md) · [Chapter 5 ▶](05-storage-neo4j-qdrant.md)

---

Two open-source projects with confusingly similar names do very different jobs: **Graphify** turns *repositories* into graphs; **Graphiti** turns *time* into graphs.

## 4.1 Graphify — From Repository to Knowledge Graph

- **Repository:** [github.com/safishamsi/graphify](https://github.com/safishamsi/graphify)
- **Website:** [graphify.net](https://graphify.net)
- **License:** MIT · Built on [Tree-sitter](https://github.com/tree-sitter/tree-sitter), [NetworkX](https://networkx.org), and Leiden community clustering

Graphify is a knowledge-graph *skill* for AI coding assistants (Claude Code, Codex, OpenCode, Cursor, Gemini CLI, and more). It reads every file in a folder — code, SQL schemas, shell scripts, Markdown docs, PDFs, even diagrams and screenshots — and builds a queryable graph of the structure, relationships, and the *why* behind them.

### Pipeline

```
Repository → Parsing → Entity Extraction → Relationship Extraction → Graph Storage
```

1. **Repo ingestion** — the whole folder, not just source files
2. **Language parsing** — local Tree-sitter AST extraction, zero API calls for code
3. **Entity detection** — classes, functions, APIs, services, tables, dependencies
4. **Relationship extraction** — `CALLS`, `IMPORTS`, database usage
5. **Output** — graph-ready data the agent (or Neo4j) can query

### Why It Matters

Traditional RAG treats code as text:

```
Code → Chunks → Embeddings → Search
```

Graphify treats code as a system:

```
Code → Relationships → Knowledge Graph
```

Example — Graphify stores this chain explicitly:

```
UserController → UserService → UserRepository → users table
```

The practical payoff is context efficiency: roughly **~1.7k tokens per query vs ~123k** with a naive read-everything approach (about a 71× reduction).

### Strengths & Trade-offs

| Strengths | Trade-offs |
|-----------|------------|
| Code- and architecture-aware | Younger ecosystem than enterprise platforms |
| Multi-artifact ingestion (code + schema + docs + images) | Rapidly evolving platform |
| Local parsing, engineering-focused, open source | |

**Best use cases:** architecture exploration, impact analysis, dependency discovery, powering AI engineering assistants.

## 4.2 Graphiti — Temporal Knowledge Graphs

- **Repository:** [github.com/getzep/graphiti](https://github.com/getzep/graphiti)
- **Maintainer:** [Zep](https://www.getzep.com)

Graphiti is a temporal knowledge graph framework, created primarily for **AI agent memory**. Where most RAG systems store documents, Graphiti stores *facts and relationships* — and, crucially, tracks how they change over time.

### Temporal Memory in Action

```
2024:  AuthService → MySQL
2026:  AuthService → PostgreSQL
```

Graphiti keeps *both* states with validity intervals. An agent can answer "what does AuthService use now?" and "what did it use before the migration?" — something a static graph or a vector store cannot do.

### Why It Matters

Long-running agents need:

- **Memory** that survives across sessions
- **Historical context** — why decisions were made and when they changed
- **Evolution tracking** for systems that never stop changing

**Best use cases:** AI agent memory, organizational knowledge, engineering memory systems, project history tracking.

## 4.3 Using Them Together

In the [reference architecture](03-system-architecture.md), Graphify builds the *structural* graph from your repositories, while Graphiti layers *temporal* facts on top — design decisions, migrations, ownership changes. Both can persist into the same [Neo4j](https://neo4j.com) instance, which is where the next chapter picks up.

---

> [◀ Chapter 3: The Reference Architecture](03-system-architecture.md) · [🏠 Home](../README.md) · [Chapter 5: The Storage Layer ▶](05-storage-neo4j-qdrant.md)
