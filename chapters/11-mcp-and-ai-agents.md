> [◀ Chapter 10](10-neo4j-and-qdrant.md) · [🏠 Home](../README.md) · [Chapter 12 ▶](12-costs-deployment-future.md)

---

# Chapter 11 — MCP & AI Coding Agents

> *"The brain is only as useful as the agent sitting on top of it — and the protocol connecting them."*

---

# 11.1 The Model Context Protocol

* **Website:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
* **Spec & SDKs:** [github.com/modelcontextprotocol](https://github.com/modelcontextprotocol)

MCP is an open standard (introduced by [Anthropic](https://www.anthropic.com), now broadly adopted) that lets AI agents call external tools through a uniform protocol — "USB-C for AI tools."

## What MCP Connects

An MCP server can expose:

* **[Neo4j](https://neo4j.com)** — graph queries ([official MCP server](https://github.com/neo4j-contrib/mcp-neo4j))
* **[Qdrant](https://qdrant.tech)** — vector search ([official MCP server](https://github.com/qdrant/mcp-server-qdrant))
* **Filesystem & Git** — repository access
* **GitHub, Jira, databases** — organizational context

## The Flow

```text
LLM → MCP client → MCP server → Tool (Neo4j / Qdrant / Git) → Response → LLM
```

The agent needs no bespoke integration code per tool. Any MCP-capable agent can query the knowledge graph the moment it is pointed at the server.

<p align="center">
  <img src="../assets/graphrag-flow.svg" alt="GraphRAG query flow through MCP" width="720">
</p>

---

# 11.2 The Agents

## Claude Code

* **Website:** [claude.com/claude-code](https://claude.com/claude-code)
* **Docs:** [docs.claude.com](https://docs.claude.com/en/docs/claude-code/overview)

A terminal-first agent from Anthropic with strong architecture reasoning and large context. It supports MCP servers and *skills* natively, which makes it a natural fit for graph-backed retrieval — [Graphify](https://github.com/safishamsi/graphify) ships as a Claude Code skill.

**With a graph brain:** a question like *"Which Flutter screens call this API?"* becomes a single graph traversal instead of a multi-file exploration.

## Codex

* **Website:** [openai.com/codex](https://openai.com/codex/)

OpenAI's coding agent (CLI and cloud). Strong at code generation and refactoring; benefits significantly from graph-provided dependency context, since generated changes can be checked against what actually depends on the modified code.

## Cursor

* **Website:** [cursor.com](https://cursor.com)

An AI-native IDE with excellent built-in semantic indexing and code navigation. Its weak spot is *cross-repository* awareness — exactly what a shared knowledge graph adds. Cursor supports MCP, so it can query the same Neo4j/Qdrant brain as terminal agents.

## Gemini CLI

* **Repository:** [github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli)

Google's open-source terminal agent. Its very large context window suits large-codebase exploration; MCP support lets it participate in the same graph workflows.

## Continue

* **Website:** [continue.dev](https://continue.dev)

An open-source assistant platform (IDE extensions + CLI) that works with Claude, GPT, Gemini, and local models. Notable for codebase indexing, custom prompts, and internal-documentation retrieval — a good choice for full control over models and retrieval sources.

## OpenCode

* **Repository:** [github.com/sst/opencode](https://github.com/sst/opencode)

An open-source terminal coding agent, model-agnostic like Continue. Also among the assistants Graphify supports out of the box.

---

# 11.3 Choosing an Agent

| Agent                                                        | Form factor    | Standout strength                | Graph payoff                             |
| ------------------------------------------------------------ | -------------- | -------------------------------- | ---------------------------------------- |
| [Claude Code](https://claude.com/claude-code)                | Terminal / IDE | Architecture reasoning, skills   | Highest — designed for tool-driven retrieval |
| [Codex](https://openai.com/codex/)                           | Terminal / cloud | Generation & refactoring       | Dependency-aware changes                 |
| [Cursor](https://cursor.com)                                 | IDE            | Semantic navigation              | Cross-repo awareness                     |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli)    | Terminal       | Huge context                     | Large-codebase exploration               |
| [Continue](https://continue.dev)                             | IDE ext / CLI  | Open source, any model           | Custom retrieval pipelines               |
| [OpenCode](https://github.com/sst/opencode)                  | Terminal       | Open source, any model           | Same MCP/graph access                    |

---

# 11.4 Key Takeaways

Because the brain speaks **MCP**, the choice of agent is not permanent. The same graph serves every agent — switch agents freely, keep the knowledge.

This completes the technical architecture. The final chapter addresses the practical questions: what it costs, how to deploy it, and where the field is heading.

---

## References

* [Model Context Protocol](https://modelcontextprotocol.io)
* [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code/overview)
* [Neo4j MCP Server](https://github.com/neo4j-contrib/mcp-neo4j)
* [Qdrant MCP Server](https://github.com/qdrant/mcp-server-qdrant)

---

**End of Chapter 11**

---

> [◀ Chapter 10: Neo4j & Qdrant](10-neo4j-and-qdrant.md) · [🏠 Home](../README.md) · [Chapter 12: Costs, Deployment & the Road Ahead ▶](12-costs-deployment-future.md)
