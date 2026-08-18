# Appendix A — Tool Directory

> [◀ Chapter 20](../chapters/20-graph-engineering-long-context.md) · [🏠 Home](../README.md)

A reference catalog of the tools that make up the engineering-intelligence ecosystem. Each entry links to the official project.

---

## 1. Graphify

**Repo:** [github.com/safishamsi/graphify](https://github.com/safishamsi/graphify) · **Site:** [graphify.net](https://graphify.net) · **License:** MIT

Converts any folder — code, SQL schemas, shell scripts, docs, papers, images, videos — into a queryable knowledge graph for AI coding assistants (Claude Code, Codex, OpenCode, Cursor, Gemini CLI). Built on Tree-sitter, NetworkX, and Leiden clustering; code parsing is fully local.

**Best for:** architecture exploration, impact analysis, dependency discovery, AI engineering assistants.
**Deep dive:** [Chapter 7](../chapters/07-graphify.md)

## 2. Graphiti

**Repo:** [github.com/getzep/graphiti](https://github.com/getzep/graphiti) · **Maintainer:** [Zep](https://www.getzep.com)

Temporal knowledge graph framework built for AI memory. Stores facts and relationships with validity over time — *Service A used PostgreSQL in January, MongoDB in June* — so agents can reason about history, not just current state.

**Best for:** agent memory, organizational knowledge, project history tracking.
**Deep dive:** [Chapter 8](../chapters/08-graphiti.md)

## 3. Sourcegraph

**Site:** [sourcegraph.com](https://sourcegraph.com)

The most mature code-intelligence platform: repository indexing, cross-repo search, symbol navigation, dependency analysis, plus the [Cody](https://sourcegraph.com/cody) AI assistant. Production-ready with wide enterprise adoption.

**Best for:** large engineering teams, multi-repository environments, enterprise development.

## 4. Neo4j

**Site:** [neo4j.com](https://neo4j.com) · **GenAI ecosystem:** [neo4j.com/labs/genai-ecosystem](https://neo4j.com/labs/genai-ecosystem/)

The leading graph database — relationships are first-class, queryable citizens via the Cypher language. Provides GenAI tooling for knowledge graphs, RAG, and agent memory.

**Best for:** dependency analysis, architecture visualization, impact analysis.
**Deep dive:** [Chapter 10](../chapters/10-neo4j-and-qdrant.md)

## 5. LlamaIndex

**Site:** [llamaindex.ai](https://www.llamaindex.ai) · **Repo:** [github.com/run-llama/llama_index](https://github.com/run-llama/llama_index)

Framework for building AI knowledge systems over many data sources: Git repos, PDFs, Word docs, Markdown, databases, APIs. Supports RAG, knowledge graphs, and agent workflows through a large connector ecosystem.

**Best for:** custom AI assistants, enterprise search, knowledge management.

## 6. Qdrant

**Site:** [qdrant.tech](https://qdrant.tech) · **Repo:** [github.com/qdrant/qdrant](https://github.com/qdrant/qdrant)

High-performance open-source vector database. Stores embeddings for semantic search — the "what is similar to this?" half of GraphRAG, complementing the graph's "what depends on this?"

**Best for:** semantic code/doc search, the vector half of GraphRAG.
**Deep dive:** [Chapter 10](../chapters/10-neo4j-and-qdrant.md)

## 7. DeepWiki

**Site:** [deepwiki.com](https://deepwiki.com)

Automatically generates AI-readable wikis from repositories: architecture summaries, documentation, and Q&A over any public GitHub repo.

**Best for:** repository onboarding, documentation generation.

## 8. Gitingest

**Site:** [gitingest.com](https://gitingest.com) · **Repo:** [github.com/coderamp-labs/gitingest](https://github.com/coderamp-labs/gitingest)

Transforms repositories into LLM-friendly text digests — the quickest way to feed a whole repo into a model's context.

**Best for:** one-shot repository ingestion and summarization.

## 9. Continue

**Site:** [continue.dev](https://continue.dev) · **Repo:** [github.com/continuedev/continue](https://github.com/continuedev/continue)

Open-source AI coding assistant platform (IDE extensions + CLI) supporting Claude, GPT, Gemini, and local models, with codebase indexing, custom prompts, and internal-doc retrieval.

**Best for:** teams wanting full control over models and retrieval.
**Deep dive:** [Chapter 11](../chapters/11-mcp-and-ai-agents.md)

## 10. LangGraph

**Docs:** [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/) · **Repo:** [github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)

Agent orchestration framework from the LangChain team. Coordinates tools, memory, retrieval, and multi-step workflows:

```
User question → Graph search → Vector search → Repository analysis → Final answer
```

**Best for:** building multi-step agent pipelines on top of the brain.

---

## Ranking at a Glance

For AI-powered software engineering specifically (rankings shift depending on whether your goal is coding assistance, enterprise search, or agent memory):

1. [Graphify](https://github.com/safishamsi/graphify) — purpose-built for coding-agent knowledge graphs
2. [Graphiti](https://github.com/getzep/graphiti) — temporal memory
3. [Sourcegraph](https://sourcegraph.com) — enterprise code intelligence
4. [Neo4j](https://neo4j.com) — the graph store
5. [LlamaIndex](https://www.llamaindex.ai) — broad ingestion
6. [DeepWiki](https://deepwiki.com) — instant repo docs
7. [Qdrant](https://qdrant.tech) — vector search
8. [Gitingest](https://gitingest.com) — quick ingestion
9. [Continue](https://continue.dev) — open assistant platform
10. [LangGraph](https://github.com/langchain-ai/langgraph) — orchestration

---

> [◀ Chapter 20: Graph Engineering in the Long-Context Era](../chapters/20-graph-engineering-long-context.md) · [🏠 Home](../README.md)
