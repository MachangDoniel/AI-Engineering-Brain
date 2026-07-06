> [◀ Chapter 6](06-graphrag.md) · [🏠 Home](../README.md) · [Chapter 8 ▶](08-graphiti.md)

---

# Chapter 7 — Graphify: Converting Software Repositories into Knowledge Graphs

> *"Source code is only the beginning. The real challenge is extracting the architecture hidden inside it."*

---

# 7.1 Introduction

Every software repository contains a vast amount of implicit knowledge.

Consider a typical project:

```text
my-project/

├── backend/
├── mobile/
├── web/
├── database/
├── docs/
├── infra/
├── scripts/
└── README.md
```

To a human engineer, these folders describe an interconnected system.

To an AI assistant, they are simply files until relationships are extracted.

This is the problem Graphify addresses.

Rather than treating repositories as collections of documents, Graphify transforms them into structured engineering knowledge.

Instead of asking an LLM to repeatedly infer architecture, Graphify extracts that architecture once and stores it explicitly.

---

# 7.2 The Core Philosophy

Traditional indexing pipelines work like this:

```text
Repository

↓

Split Files

↓

Embeddings

↓

Vector Database
```

Everything becomes text.

Graphify takes a different approach.

```text
Repository

↓

Language Parsing

↓

Entity Extraction

↓

Relationship Extraction

↓

Knowledge Graph

↓

(Optional) Vector Index
```

The emphasis shifts from text to structure.

---

# 7.3 Why Parsing Matters

Programming languages are not natural language.

Consider this Java example.

```java
class UserService {

    UserRepository repository;

    NotificationService notification;

}
```

A text splitter sees words.

A parser sees:

```
Class

↓

Field

↓

Type

↓

Dependency
```

Graphify relies on language-aware parsing because syntax contains valuable structural information that embeddings alone cannot recover reliably.

---

# 7.4 The Ingestion Pipeline

A production Graphify deployment can be viewed as six stages.

```text
                Repository
                     │
                     ▼
              Repository Scanner
                     │
                     ▼
              Language Detection
                     │
                     ▼
              Source Parser
                     │
                     ▼
             Entity Extraction
                     │
                     ▼
          Relationship Extraction
                     │
                     ▼
             Knowledge Graph
```

Each stage performs a distinct transformation.

---

# 7.5 Repository Discovery

The first step is discovering project contents.

Typical inputs include:

```
Source Code

SQL

Markdown

Dockerfiles

Terraform

YAML

JSON

Images

Videos

PDFs
```

Graphify is not limited to source code.

Engineering knowledge exists across many artifact types.

One of its strengths is treating these artifacts as components of a unified graph.

---

# 7.6 Language Detection

Repositories often contain multiple languages.

Example:

```
Flutter

↓

Dart

Spring Boot

↓

Java

Laravel

↓

PHP

Android

↓

Kotlin

iOS

↓

Swift
```

Graphify identifies each language before selecting the appropriate parser.

This allows a single graph to span heterogeneous technology stacks.

---

# 7.7 Parsing

Graphify typically relies on language-aware parsers such as Tree-sitter (or equivalent parsing strategies depending on the language).

Instead of tokenizing text, parsing produces an Abstract Syntax Tree (AST).

Example:

```dart
class UserRepository {

 Future<User> getUser() {}

}
```

AST:

```
Class

↓

Method

↓

Return Type

↓

Parameters
```

The AST becomes the foundation for entity extraction.

---

# 7.8 Entity Extraction

Once the AST is available, Graphify identifies engineering entities.

Typical examples include:

**Code**

* Repository
* Package
* Module
* Namespace
* File
* Class
* Interface
* Enum
* Function
* Variable

**Database**

* Schema
* Table
* Column
* Foreign Key
* View
* Trigger

**API**

* REST Endpoint
* GraphQL Resolver
* gRPC Service
* WebSocket Channel

**Infrastructure**

* Kubernetes Deployment
* Docker Image
* Container
* Secret
* ConfigMap
* Load Balancer

**Documentation**

* README
* ADR
* RFC
* Design Document

Each entity becomes a node in the knowledge graph.

---

# 7.9 Relationship Extraction

This is where Graphify becomes significantly more valuable than traditional code indexing.

Example:

```java
UserController

↓

CALLS

↓

UserService

↓

CALLS

↓

UserRepository

↓

WRITES

↓

users Table
```

Relationships may include:

```
CALLS

IMPORTS

IMPLEMENTS

EXTENDS

READS

WRITES

DEPENDS_ON

DEPLOYS_TO

USES

DOCUMENTED_BY
```

These relationships form the engineering topology.

---

# 7.10 Cross-Language Relationships

Modern applications rarely consist of a single language.

Example:

```
Flutter

↓

REST

↓

Spring Boot

↓

JPA

↓

PostgreSQL
```

A user interaction might traverse:

```
Flutter Screen

↓

Repository

↓

REST Client

↓

Controller

↓

Service

↓

Repository

↓

Database
```

One of Graphify's greatest strengths is representing this chain within a single graph, enabling cross-language impact analysis.

---

# 7.11 Beyond Source Code

Graphify is not limited to programming languages.

Additional artifacts can enrich the graph.

Examples:

**SQL**

```
Tables

Columns

Indexes

Foreign Keys
```

**Markdown**

```
README

Design Docs

Architecture Notes
```

**Terraform**

```
Resources

Networks

Security Groups
```

**Kubernetes**

```
Deployment

Pod

Service

Ingress
```

**OpenAPI**

```
Endpoint

Request

Response

Authentication
```

Each artifact contributes additional context.

---

# 7.12 Building the Graph

After extraction, Graphify creates a property graph.

Example:

```
(:Repository)

↓

CONTAINS

↓

(:Module)

↓

CONTAINS

↓

(:Class)

↓

CALLS

↓

(:Service)

↓

WRITES

↓

(:Table)
```

This graph can be stored in Neo4j or another compatible graph database.

---

# 7.13 Strengths

Graphify's approach offers several advantages.

### Structural Understanding

The system understands architecture rather than just text.

### Language Independence

The same graph can represent multiple programming languages.

### Extensibility

New parsers and entity extractors can be added incrementally.

### Explainability

Every relationship is explicit and queryable.

### AI Compatibility

The resulting graph integrates naturally with GraphRAG pipelines.

---

# 7.14 Current Limitations

As an evolving open-source project, Graphify also has limitations.

Examples include:

### Dynamic Languages

Relationships inferred at runtime (reflection, dynamic dispatch, metaprogramming) may be difficult to recover statically.

### Framework-Specific Semantics

Framework conventions (e.g., Spring annotations, Laravel service containers, Flutter widget trees) often require specialized extractors.

### Runtime Behavior

Static analysis alone cannot capture:

* Production traffic
* Runtime latency
* Feature flags
* User behavior

These require integration with observability systems.

---

# 7.15 Extending Graphify

For an AI Engineering Brain, Graphify should be viewed as the ingestion layer rather than the entire solution.

A typical architecture is:

```text
Repositories
      │
      ▼
   Graphify
      │
      ▼
    Neo4j
      │
      ├──────────────┐
      ▼              ▼
 Qdrant         Graphiti
      │              │
      └──────┬───────┘
             ▼
         MCP Server
             ▼
     Claude Code / Codex / Cursor
```

Graphify constructs the graph.

Other components provide retrieval, memory, and AI integration.

---

# 7.16 Example Workflow

Suppose you modify a Flutter screen.

Graphify updates the graph.

The AI can immediately answer:

* Which APIs are affected?
* Which backend services are involved?
* Which database tables are touched?
* Which integration tests should be rerun?
* Which documentation references this feature?

The graph becomes a continuously updated engineering map.

---

# 7.17 Opportunities for Improvement

Looking ahead, Graphify could evolve in several directions:

* Incremental indexing for very large repositories
* Live graph updates from Git events
* Framework-aware extractors (Flutter, Spring, Laravel, etc.)
* Runtime telemetry integration
* Git history integration
* Security relationship extraction
* AI-assisted entity validation

These are natural extensions of its current architecture.

---

# 7.18 Key Takeaways

Graphify's primary contribution is transforming repositories into structured engineering knowledge.

Rather than indexing text alone, it identifies entities, extracts relationships, and builds a graph that represents the architecture of a software system.

This graph is valuable on its own, but its full potential emerges when combined with vector search, persistent memory, and AI agents.

In the reference architecture presented throughout this whitepaper, Graphify serves as the ingestion engine—the component responsible for converting raw engineering artifacts into a form that AI systems can reason about efficiently.

---

## References

* [Graphify GitHub Repository](https://github.com/safishamsi/graphify) · [graphify.net](https://graphify.net)
* Neo4j Developer Documentation
* Tree-sitter Documentation
* Microsoft Research: GraphRAG

---

**End of Chapter 7**

---

> [◀ Chapter 6: GraphRAG](06-graphrag.md) · [🏠 Home](../README.md) · [Chapter 8: Graphiti ▶](08-graphiti.md)
