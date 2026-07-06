> [◀ Chapter 3](03-prompt-to-knowledge-engineering.md) · [🏠 Home](../README.md) · [Chapter 5 ▶](05-knowledge-graphs.md)

---

# Chapter 4 — Why RAG Isn't Enough: Understanding the Limits of Retrieval-Augmented Generation

> *"RAG made large language models useful for enterprise knowledge. GraphRAG makes them useful for engineering knowledge."*

---

# 4.1 Introduction

Retrieval-Augmented Generation (RAG) has become the de facto architecture for AI systems that operate over private knowledge.

Instead of relying solely on information learned during model training, a RAG system retrieves relevant documents at query time and injects them into the model's context.

For documentation-heavy domains, this works remarkably well.

Software engineering, however, presents a fundamentally different challenge.

Unlike legal documents or knowledge bases, software is **not just information**. It is an interconnected system of entities and relationships. Understanding a codebase requires more than reading files—it requires reasoning about structure, dependencies, execution flow, ownership, and evolution over time.

This chapter explains why traditional RAG is often insufficient for engineering tasks and why graph-based approaches have become increasingly important.

---

# 4.2 What Is Retrieval-Augmented Generation?

A standard RAG pipeline consists of four stages:

```text
                User Question
                       │
                       ▼
              Embedding Model
                       │
                       ▼
               Vector Database
                       │
                       ▼
          Top-K Relevant Documents
                       │
                       ▼
                  Large Language Model
                       │
                       ▼
                    Final Answer
```

The core idea is straightforward:

1. Convert documents into embeddings.
2. Store embeddings in a vector database.
3. Convert the user's question into an embedding.
4. Retrieve the most similar documents.
5. Ask the language model to reason over those documents.

This architecture dramatically reduces hallucinations because the model reasons over current, domain-specific information.

---

# 4.3 Why RAG Works So Well

Consider a documentation question:

> "How do I configure JWT authentication?"

The retriever may return:

```
Security.md
Authentication Guide
README.md
SecurityConfig.java
```

All of these documents are semantically related to JWT authentication.

The language model synthesizes them into a coherent explanation.

This works because the answer exists *within the retrieved documents*.

Many enterprise use cases fit this pattern:

* Internal documentation
* API references
* HR policies
* Product manuals
* Technical guides

Semantic similarity is sufficient.

---

# 4.4 Why Software Is Different

Software systems contain explicit relationships.

Consider a seemingly simple question:

> **Which Flutter screens are affected if the `users` table changes?**

The answer requires traversing multiple abstraction layers.

```
users table
↓
UserRepository
↓
UserService
↓
UserController
↓
REST Endpoint
↓
Flutter Repository
↓
Flutter ViewModel
↓
Flutter Screen
```

No single file contains this answer.

No documentation page describes this path.

The information exists only in the relationships among entities.

This is where RAG begins to struggle.

---

# 4.5 Documents vs. Relationships

Traditional RAG treats engineering artifacts as independent documents.

```
File A
File B
File C
File D
```

Relationships are implicit.

Graph-based systems treat them as connected entities.

```
File A
↓
imports
↓
File B
↓
calls
↓
Service C
↓
writes
↓
Table D
```

The graph stores the architecture itself rather than expecting the language model to infer it repeatedly.

---

# 4.6 The Chunking Problem

Every RAG system must divide large documents into smaller chunks.

Example:

```
UserService.java
↓
Chunk 1
Chunk 2
Chunk 3
Chunk 4
```

Chunking is necessary because:

* Embedding models have token limits.
* Smaller chunks improve retrieval precision.
* Large repositories contain millions of tokens.

However, chunking introduces new problems.

---

## Example

Imagine the following execution path:

```
Flutter Screen
↓
Repository
↓
API Client
↓
Spring Controller
↓
Service
↓
Database
```

Each component may reside in a different file.

Each file may be divided into multiple chunks.

The retrieval system must independently retrieve every relevant chunk.

If even one important chunk is missed, the reasoning chain becomes incomplete.

---

# 4.7 The Similarity Trap

Vector databases retrieve information based on semantic similarity.

This is ideal for natural language.

Software often depends on exact structural relationships.

Consider:

```
CustomerService
OrderService
NotificationService
```

The names are semantically similar.

However:

```
CustomerService
↓
calls
↓
PaymentGateway
```

may have nothing to do with:

```
NotificationService
```

Semantic similarity does not imply architectural relevance.

Conversely, two components with little lexical similarity may be tightly coupled.

---

# 4.8 Multi-Hop Reasoning

Many engineering questions require traversing several relationships.

Example:

> "Which APIs eventually write to the orders table?"

The reasoning path may span:

```
API
↓
Controller
↓
Service
↓
Repository
↓
Database
```

Each hop depends on the previous one.

Traditional RAG retrieves documents independently.

It does not naturally perform multi-hop traversal.

Knowledge graphs, by contrast, are designed precisely for this purpose.

---

# 4.9 Hidden Dependencies

Software contains numerous implicit relationships:

* Imports
* Inheritance
* Dependency Injection
* Reflection
* Event publishing
* Message queues
* Scheduled jobs
* Infrastructure bindings

Many of these relationships are difficult to recover from semantic similarity alone.

Example:

```
UserCreatedEvent
↓
Kafka Topic
↓
Notification Service
↓
Email Sender
```

The producer and consumer may never reference each other directly.

A graph can represent the event flow explicitly.

---

# 4.10 Engineering Questions RAG Finds Difficult

Consider the following questions:

* What breaks if this service is removed?
* Which mobile screens use this API?
* Which microservices depend on Redis?
* Which endpoints share this authentication middleware?
* Which infrastructure resources support Feature X?
* Which ADR introduced this dependency?
* Which tests validate this business rule?

These are not retrieval problems.

They are graph traversal problems.

---

# 4.11 Engineering Questions RAG Excels At

It is equally important to recognize where RAG performs exceptionally well.

Examples include:

* Explain this class.
* Summarize this document.
* Find examples of JWT usage.
* Show similar implementations.
* Explain this error message.
* Compare two approaches.

These tasks rely primarily on semantic similarity rather than structural reasoning.

---

# 4.12 Combining Graphs and Vectors

Rather than replacing RAG, modern engineering systems combine graph traversal with vector retrieval.

A simplified architecture is shown below.

```text
                 User Question
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
Knowledge Graph                 Vector Database
         ▼                             ▼
Related Entities             Supporting Documents
         └──────────────┬──────────────┘
                        ▼
                Large Language Model
                        ▼
                     Answer
```

The graph identifies the architectural neighborhood.

The vector database provides rich explanatory context.

The language model synthesizes both.

---

# 4.13 An Example Walkthrough

Suppose a developer asks:

> **"What happens when a user changes their password?"**

A GraphRAG system might proceed as follows:

### Step 1: Graph Traversal

Locate the `User` entity.

Traverse:

* Password Controller
* Authentication Service
* Password Repository
* Notification Service
* Audit Logger

### Step 2: Vector Retrieval

Retrieve:

* Password policy documentation
* Security ADR
* Relevant test cases
* API specification

### Step 3: LLM Reasoning

The language model now possesses:

* execution flow
* documentation
* architecture
* implementation details

It can generate a comprehensive answer that would be difficult to obtain from RAG alone.

---

# 4.14 Performance Considerations

Graph traversal and vector retrieval have different computational characteristics.

| Operation        | Strength               | Typical Complexity             |
| ---------------- | ---------------------- | ------------------------------ |
| Vector Search    | Semantic similarity    | Approximate nearest neighbor   |
| Graph Traversal  | Relationship reasoning | Traversal over connected nodes |
| Hybrid Retrieval | Best overall context   | Combined pipeline              |

In practice, hybrid retrieval introduces some additional latency but often yields significantly higher-quality answers for engineering tasks.

---

# 4.15 When Not to Use GraphRAG

GraphRAG is not universally necessary.

For small projects:

* A few thousand lines of code
* Single repository
* Limited documentation

Traditional RAG may be sufficient.

Graph construction introduces overhead in:

* parsing
* indexing
* storage
* maintenance

The benefits increase as systems become larger and more interconnected.

---

# 4.16 The Emerging Pattern

The industry is converging on a layered architecture:

```text
Source Code
      │
      ▼
Language Parser
      │
      ▼
Knowledge Graph
      │
      ├────────────┐
      ▼            ▼
Graph Query   Vector Search
      └──────┬─────┘
             ▼
        AI Coding Agent
```

Rather than choosing between graphs and vectors, modern systems increasingly leverage both.

---

# 4.17 Key Takeaways

Retrieval-Augmented Generation remains a foundational technology for AI-assisted software engineering. It excels at retrieving semantically relevant information and significantly improves the factual grounding of language models.

However, software engineering requires reasoning about **relationships**, **dependencies**, and **execution paths**—capabilities that are difficult to achieve through semantic similarity alone.

Knowledge graphs address this limitation by explicitly modeling the structure of software systems.

The combination of graph traversal and vector retrieval—commonly referred to as **GraphRAG**—represents a natural evolution rather than a replacement of traditional RAG.

As AI coding assistants mature, the most effective systems are likely to integrate both approaches, using each where it provides the greatest value.

---

## References

* Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (2020)
* Microsoft Research, *GraphRAG* (2024)
* Neo4j Documentation: Property Graph Model
* Qdrant Documentation: Hybrid Search
* Tree-sitter Documentation

---

**End of Chapter 4**

---

> [◀ Chapter 3: From Prompt Engineering to the AI Engineering Brain](03-prompt-to-knowledge-engineering.md) · [🏠 Home](../README.md) · [Chapter 5: Knowledge Graphs ▶](05-knowledge-graphs.md)
