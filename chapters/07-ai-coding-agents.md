# Chapter 7 — AI Coding Agents on a Graph Brain

> [◀ Chapter 6](06-parsing-and-mcp.md) · [🏠 Home](../README.md) · [Chapter 8 ▶](08-costs-deployment-future.md)

---

The brain is only as useful as the agent sitting on top of it. This chapter surveys the major coding agents and what graph-backed retrieval adds to each.

## 7.1 Claude Code

- **Website:** [claude.com/claude-code](https://claude.com/claude-code)
- **Docs:** [docs.claude.com/en/docs/claude-code](https://docs.claude.com/en/docs/claude-code/overview)

A terminal-first agent from Anthropic with strong architecture reasoning and large context. It supports MCP servers and *skills* natively, which makes it a natural fit for graph-backed retrieval — [Graphify](https://github.com/safishamsi/graphify) ships as a Claude Code skill.

**With a graph brain:** a question like *"Which Flutter screens call this API?"* becomes a single graph traversal instead of a multi-file exploration.

## 7.2 Codex

- **Website:** [openai.com/codex](https://openai.com/codex/)

OpenAI's coding agent (CLI and cloud). Strong at code generation and refactoring; benefits significantly from graph-provided dependency context, since generated changes can be checked against what actually depends on the modified code.

## 7.3 Cursor

- **Website:** [cursor.com](https://cursor.com)

An AI-native IDE with excellent built-in semantic indexing and code navigation. Its weak spot is *cross-repository* awareness — exactly what a shared knowledge graph adds. Cursor supports MCP, so it can query the same Neo4j/Qdrant brain as your terminal agents.

## 7.4 Gemini CLI

- **Repository:** [github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli)

Google's open-source terminal agent. Its very large context window suits large-codebase exploration; MCP support lets it participate in the same graph workflows.

## 7.5 Continue

- **Website:** [continue.dev](https://continue.dev)

An open-source assistant platform (IDE extensions + CLI) that works with Claude, GPT, Gemini, and local models. Notable for codebase indexing, custom prompts, and internal-documentation retrieval — a good choice if you want full control over models and retrieval sources.

## 7.6 OpenCode

- **Repository:** [github.com/sst/opencode](https://github.com/sst/opencode)

An open-source terminal coding agent, model-agnostic like Continue. Also among the assistants Graphify supports out of the box.

## 7.7 Choosing an Agent

| Agent | Form factor | Standout strength | Graph payoff |
|-------|-------------|-------------------|--------------|
| [Claude Code](https://claude.com/claude-code) | Terminal / IDE | Architecture reasoning, skills, MCP | Highest — designed for tool-driven retrieval |
| [Codex](https://openai.com/codex/) | Terminal / cloud | Generation & refactoring | Dependency-aware changes |
| [Cursor](https://cursor.com) | IDE | Semantic navigation | Cross-repo awareness |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | Terminal | Huge context | Large-codebase exploration |
| [Continue](https://continue.dev) | IDE ext / CLI | Open source, any model | Custom retrieval pipelines |
| [OpenCode](https://github.com/sst/opencode) | Terminal | Open source, any model | Same MCP/graph access |

The good news: because the brain speaks **MCP**, you don't have to choose forever. The same graph serves every agent — switch agents freely, keep the knowledge.

---

> [◀ Chapter 6: Parsing & Integration](06-parsing-and-mcp.md) · [🏠 Home](../README.md) · [Chapter 8: Costs, Deployment & the Road Ahead ▶](08-costs-deployment-future.md)
