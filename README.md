# 🧠 The AI Engineering Brain

**An open study library on Knowledge Graphs, GraphRAG, and AI Coding Assistants**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-contributing)
[![Made for Developers](https://img.shields.io/badge/Made_for-Developers-blue.svg)](#)

Modern AI coding assistants are powerful, but they mostly see your code as *text*. This library explains how to give them **architecture awareness, dependency awareness, and long-term memory** by combining knowledge graphs, vector search, and the Model Context Protocol (MCP) — so tools like [Claude Code](https://claude.com/claude-code), [Codex](https://openai.com/codex/), and [Cursor](https://cursor.com) can answer questions like:

- *Which Flutter screens call this API?*
- *Which service writes to the `users` table?*
- *What breaks if this service is removed?*

<p align="center">
  <img src="assets/architecture.svg" alt="The AI Engineering Brain reference architecture" width="720">
</p>

---

## 📚 Table of Contents

| # | Chapter | What you'll learn |
|---|---------|-------------------|
| 1 | [Why AI Assistants Need More Than a Context Window](chapters/01-why-ai-assistants-need-more.md) | The limits of today's tools and the problem this library solves |
| 2 | [RAG vs Knowledge Graphs vs GraphRAG](chapters/02-rag-knowledge-graphs-graphrag.md) | The three retrieval paradigms and when to use each |
| 3 | [The Reference Architecture](chapters/03-system-architecture.md) | The full pipeline: parsing → graph → vectors → MCP → agent |
| 4 | [Graph Builders: Graphify & Graphiti](chapters/04-graph-builders-graphify-graphiti.md) | How repositories become graphs, and how graphs remember time |
| 5 | [The Storage Layer: Neo4j & Qdrant](chapters/05-storage-neo4j-qdrant.md) | Graph schema design and vector indexing strategy |
| 6 | [Parsing & Integration: Tree-sitter & MCP](chapters/06-parsing-and-mcp.md) | Turning code into ASTs, and connecting agents to tools |
| 7 | [AI Coding Agents](chapters/07-ai-coding-agents.md) | Claude Code, Codex, Cursor, Gemini CLI, Continue — with graph superpowers |
| 8 | [Costs, Deployment & the Road Ahead](chapters/08-costs-deployment-future.md) | Self-hosted vs SaaS, budgets, startup ideas, 2027–2030 outlook |
| A | [Appendix: Tool Directory](appendix/tool-directory.md) | Reference catalog of 10+ tools with links and use cases |

> **New here?** Start with [Chapter 1](chapters/01-why-ai-assistants-need-more.md) and follow the *Next* links at the bottom of each chapter.

---

## 🚀 TL;DR — The Recommended 2026 Stack

| Layer | Tool | Link |
|-------|------|------|
| Code parsing | Tree-sitter | [github.com/tree-sitter/tree-sitter](https://github.com/tree-sitter/tree-sitter) |
| Graph building | Graphify | [github.com/safishamsi/graphify](https://github.com/safishamsi/graphify) |
| Temporal memory | Graphiti | [github.com/getzep/graphiti](https://github.com/getzep/graphiti) |
| Knowledge graph | Neo4j | [neo4j.com](https://neo4j.com) |
| Vector search | Qdrant | [qdrant.tech](https://qdrant.tech) |
| Agent ↔ tool bridge | Model Context Protocol | [modelcontextprotocol.io](https://modelcontextprotocol.io) |
| Coding agent | Claude Code | [claude.com/claude-code](https://claude.com/claude-code) |

**Minimum setup:** Graphify + a coding agent. **Advanced:** add Neo4j, Qdrant, Graphiti, and MCP. Details in [Chapter 8](chapters/08-costs-deployment-future.md).

---

## 🎯 Who Is This For?

- **Individual developers** building a personal "engineering brain" across Flutter, Spring Boot, Laravel, Android, and iOS projects
- **Teams** who want their AI assistants to understand architecture, not just retrieve snippets
- **Builders** exploring GraphRAG, agent memory, or code-intelligence products

## 🤝 Contributing

This is a living library. Found an error, a broken link, or a new tool worth covering? Open an issue or a pull request.

## 📄 License

Content is licensed under [CC BY 4.0](LICENSE) — share and adapt freely with attribution.
