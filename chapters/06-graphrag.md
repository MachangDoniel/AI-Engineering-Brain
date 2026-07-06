> [◀ Chapter 5](05-knowledge-graphs.md) · [🏠 Home](../README.md) · [Chapter 7 ▶](07-graphify.md)

---

# Chapter 6 — GraphRAG: Building a Production Graph Retrieval System for Software Engineering

> *"Vector search finds information. Graph search finds relationships. GraphRAG combines both to answer engineering questions that neither approach can solve alone."*

---

# 6.1 Introduction

Retrieval-Augmented Generation (RAG) transformed AI systems by enabling language models to access external knowledge at inference time. For many applications, retrieving semantically similar documents is sufficient.

Software engineering presents a different challenge.

Developers rarely ask questions about isolated documents. They ask questions about systems:

* What depends on this service?
* Which APIs ultimately modify this database table?
* What will break if I rename this interface?
* Which Flutter screens are affected by this backend change?
* Which infrastructure resources support this feature?

These questions require traversing relationships before retrieving documentation.

GraphRAG addresses this need by combining **graph traversal**, **semantic retrieval**, and **LLM reasoning** into a unified architecture.

---

# 6.2 What Is GraphRAG?

GraphRAG extends traditional Retrieval-Augmented Generation by introducing a structured knowledge graph into the retrieval process.

Instead of asking:

> "Which documents are most similar to this question?"

GraphRAG asks:

> "Which entities are relevant, what is their architectural neighborhood, and which supporting documents explain them?"

The graph becomes the primary navigation mechanism, while vector search enriches the retrieved context with semantic information.

---

# 6.3 High-Level Architecture

A production GraphRAG system typically consists of several coordinated components.

```text
                        User Question
                              │
                              ▼
                     Query Understanding
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        Graph Traversal Engine     Vector Retrieval
                 ▼                         ▼
         Related Entities        Supporting Documents
                 └────────────┬────────────┘
                              ▼
                     Context Composer
                              ▼
                      Large Language Model
                              ▼
                          Final Answer
```

Each component has a distinct responsibility:

* The graph identifies the relevant architectural neighborhood.
* The vector database provides detailed implementation context.
* The context composer assembles a coherent prompt for the language model.

---

# 6.4 Why Graph Traversal Comes First

Many GraphRAG implementations retrieve vectors first and attempt graph traversal afterward.

For software engineering, the opposite order is often more effective.

Consider the question:

> Which Flutter screens are affected by changes to the `users` table?

The graph already contains explicit relationships:

```text
users Table
     ▲
 WRITES
     ▲
UserRepository
     ▲
CALLS
     ▲
UserService
     ▲
CALLS
     ▲
UserController
     ▲
EXPOSES
     ▲
REST Endpoint
     ▲
CALLS
     ▲
Flutter Repository
     ▲
USED_BY
     ▲
Flutter Screen
```

Once this architectural path is identified, semantic retrieval can gather implementation details such as documentation, comments, and design decisions.

This ordering reduces irrelevant retrieval and improves answer quality.

---

# 6.5 GraphRAG Pipeline

A production pipeline consists of six stages.

```text
Repositories
      │
      ▼
Tree-sitter Parsing
      │
      ▼
Entity Extraction
      │
      ▼
Knowledge Graph Construction
      │
      ▼
Embedding Generation
      │
      ▼
Vector Database
      │
      ▼
AI Agent
```

At query time:

```text
Question
↓
Graph Traversal
↓
Neighborhood Expansion
↓
Vector Search
↓
Context Assembly
↓
LLM
```

This separation between **offline indexing** and **online retrieval** is essential for scalability.

---

# 6.6 Entity-Centric Retrieval

Traditional RAG retrieves document chunks.

GraphRAG retrieves entities.

Example entities:

* Repository
* Module
* File
* Class
* Function
* Endpoint
* Database Table
* Kafka Topic
* Kubernetes Deployment

Each entity serves as an anchor for additional retrieval.

Instead of returning arbitrary text, the system returns structured engineering concepts.

---

# 6.7 Neighborhood Expansion

A key strength of GraphRAG is the ability to expand the search beyond the initial entity.

Suppose the starting node is:

```text
UserService
```

The traversal engine may expand to:

```text
UserController
↓
UserService
↓
UserRepository
↓
users Table
↓
UserIntegrationTests
↓
Authentication ADR
```

The expansion depth depends on the question.

Shallow traversals are suitable for localized changes.

Deeper traversals support impact analysis.

---

# 6.8 Choosing Traversal Depth

Traversal depth is a trade-off.

| Depth    | Typical Use Case           | Advantages       | Risks                 |
| -------- | -------------------------- | ---------------- | --------------------- |
| 1 hop    | Local navigation           | Fast, precise    | Limited context       |
| 2–3 hops | Service-level reasoning    | Good balance     | Moderate graph size   |
| 4–6 hops | Architecture analysis      | Rich context     | More irrelevant nodes |
| 7+ hops  | Organization-wide analysis | Broad visibility | Context explosion     |

A production system should adjust traversal depth dynamically based on the query intent.

---

# 6.9 Semantic Enrichment

After graph traversal, the system retrieves supporting artifacts from the vector database.

Examples include:

* Source code
* README files
* ADRs
* API specifications
* Database migration scripts
* Unit tests
* Integration tests
* Design documents

Each retrieved document is associated with one or more graph entities, creating a richer and more explainable context.

---

# 6.10 Context Composition

One of the most overlooked aspects of GraphRAG is how retrieved information is assembled before being sent to the language model.

A typical context might contain:

1. Question
2. Relevant entities
3. Relationship paths
4. Supporting documentation
5. Source code excerpts
6. Repository metadata
7. Architectural summary

Instead of presenting unrelated chunks, the system organizes information into a coherent narrative.

For example:

```text
Question:
Which Flutter screens depend on Redis?

Relevant Path:
FlutterScreen → Repository → REST Endpoint →
UserController → UserService →
CacheService → Redis

Supporting Documentation:
Caching Strategy ADR
Redis Deployment Guide

Relevant Source Files:
CacheService.java
UserRepository.dart
```

This structured context significantly improves reasoning.

---

# 6.11 Query Classification

Not every question requires graph traversal.

A production system should classify incoming queries.

| Query Type              | Preferred Retrieval       |
| ----------------------- | ------------------------- |
| Explain a class         | Vector search             |
| Summarize documentation | Vector search             |
| Find similar code       | Vector search             |
| Impact analysis         | Graph traversal + vectors |
| Dependency analysis     | Graph traversal           |
| Architecture questions  | Graph traversal + vectors |
| Security analysis       | Graph traversal + vectors |
| Refactoring support     | Hybrid                    |

This avoids unnecessary graph operations.

---

# 6.12 Ranking Retrieved Context

GraphRAG systems often retrieve more information than can fit into the model's context window.

Ranking therefore becomes essential.

Signals may include:

* Graph distance
* Semantic similarity
* File importance
* Recent modification time
* Repository priority
* Test coverage
* Ownership
* User interaction history

A weighted scoring function helps determine which entities and documents are included.

---

# 6.13 Explainability

One advantage of graph-based retrieval is transparency.

Instead of returning an answer without justification, the system can expose the reasoning path.

Example:

```text
FlutterScreen
↓
UserRepository
↓
REST Endpoint
↓
UserController
↓
UserService
↓
users Table
```

This makes answers easier to validate and debug.

Explainability is particularly important for production AI systems.

---

# 6.14 Caching Strategies

Graph traversal and vector retrieval can both be cached.

Common cache layers include:

* Frequently traversed subgraphs
* Entity metadata
* Embeddings
* Relationship paths
* Final prompts
* LLM responses

Caching reduces latency and operational cost.

---

# 6.15 Common Failure Modes

GraphRAG systems introduce new challenges.

### Incomplete Graphs

Missing relationships lead to incomplete reasoning.

### Stale Embeddings

Recently modified code may not yet be indexed.

### Over-Traversal

Large traversals can overwhelm the language model with irrelevant information.

### Poor Entity Extraction

Incorrect parsing propagates errors throughout the graph.

Monitoring these failure modes is critical for production deployments.

---

# 6.16 Metrics

GraphRAG systems should be evaluated using engineering-specific metrics.

Examples include:

* Dependency path accuracy
* Entity extraction precision
* Relationship extraction recall
* Retrieval latency
* Graph traversal latency
* Answer correctness
* Hallucination rate
* Context utilization
* Token efficiency

Traditional LLM benchmarks are insufficient for evaluating engineering knowledge systems.

---

# 6.17 Putting It All Together

A production GraphRAG system for software engineering combines multiple specialized components:

* Tree-sitter for language-aware parsing.
* Entity and relationship extraction.
* Neo4j for storing the engineering graph.
* Qdrant for semantic retrieval.
* A query planner that selects graph, vector, or hybrid retrieval.
* A context composer that assembles structured prompts.
* An LLM that performs reasoning over the retrieved context.

No single component is sufficient on its own. The effectiveness of the system emerges from the coordination of these layers.

---

# 6.18 Key Takeaways

GraphRAG is not merely "RAG with a graph database." It is an architectural pattern that integrates structural reasoning and semantic retrieval.

For software engineering, this distinction is crucial because the most valuable questions concern dependencies, execution paths, ownership, and architecture—concepts that are inherently relational.

A well-designed GraphRAG system enables AI coding assistants to move beyond document search toward genuine engineering reasoning.

The remaining chapters will build on this foundation by examining the technologies that implement these ideas in practice, beginning with Graphify.

---

## References

* Microsoft Research, *GraphRAG* (2024)
* Neo4j Developer Guides
* Qdrant Documentation: Hybrid Search
* Tree-sitter Documentation
* Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (2020)

---

**End of Chapter 6**

---

> [◀ Chapter 5: Knowledge Graphs](05-knowledge-graphs.md) · [🏠 Home](../README.md) · [Chapter 7: Graphify ▶](07-graphify.md)
