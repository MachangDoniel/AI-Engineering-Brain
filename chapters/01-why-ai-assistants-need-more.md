# Chapter 1 — Why AI Assistants Need More Than a Context Window

> [🏠 Home](../README.md) · **Chapter 1** · [Chapter 2 ▶](02-rag-knowledge-graphs-graphrag.md)

---

## 1.1 The State of AI Coding Assistants

Traditional AI coding assistants — [Claude Code](https://claude.com/claude-code), [Codex](https://openai.com/codex/), [Cursor](https://cursor.com), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [Continue](https://continue.dev) — mainly rely on three mechanisms:

1. **The current context window** — whatever fits in the prompt
2. **Repository indexing** — file trees, symbols, simple search
3. **Vector search (RAG)** — retrieving semantically similar chunks

These work well for local edits. They start to fail when a question spans *relationships*: services calling services, controllers writing to tables, features spanning repositories.

## 1.2 The Limits

| Limitation | What it looks like in practice |
|------------|-------------------------------|
| **Context window limits** | Large codebases simply don't fit; the agent sees fragments |
| **Poor cross-repo reasoning** | The Flutter app, Spring Boot backend, and Laravel admin panel are three separate blind spots |
| **No architectural memory** | Every session starts from zero; design decisions are forgotten |
| **Weak DB & infra awareness** | The agent doesn't know which endpoint writes to which table, or which Terraform resource backs which feature |

## 1.3 What We Actually Need

To move from "autocomplete with search" to an **engineering brain**, an assistant needs:

- **A dependency graph** — who calls whom, who imports what
- **Schema awareness** — how code touches tables, columns, and migrations
- **Cross-stack understanding** — mobile ↔ API ↔ database ↔ infrastructure as one connected system
- **Long-term memory** — facts and decisions that persist across sessions and evolve over time

## 1.4 The Questions a Brain Can Answer

With those capabilities in place, questions that stump a plain RAG setup become one-hop graph queries:

- *Which API updates the `users` table?*
- *Which Flutter screens call this endpoint?*
- *What breaks if this service is removed?*
- *Which infrastructure resources support this feature?*
- *Which research paper inspired this implementation?*

## 1.5 Where This Library Goes

The rest of this library builds the answer step by step:

- [Chapter 2](02-rag-knowledge-graphs-graphrag.md) compares the three retrieval paradigms — RAG, knowledge graphs, and GraphRAG.
- [Chapter 3](03-system-architecture.md) assembles them into a reference architecture.
- [Chapters 4–6](04-graph-builders-graphify-graphiti.md) go deep on each component.
- [Chapters 7–8](07-ai-coding-agents.md) connect the agents and cover costs, deployment, and the future.

---

> [🏠 Home](../README.md) · **Chapter 1** · [Chapter 2: RAG vs Knowledge Graphs vs GraphRAG ▶](02-rag-knowledge-graphs-graphrag.md)
