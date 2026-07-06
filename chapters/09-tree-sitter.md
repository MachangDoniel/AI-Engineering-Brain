> [◀ Chapter 8](08-graphiti.md) · [🏠 Home](../README.md) · [Chapter 10 ▶](10-neo4j-and-qdrant.md)

---

# Chapter 9 — Tree-sitter: Parsing Code into Structure

> *"Before a system can reason about code, something has to turn text into structure. That something is a parser."*

---

# 9.1 Introduction

Both Graphify and most custom knowledge-graph pipelines depend on one foundational technology: **Tree-sitter**.

* **Repository:** [github.com/tree-sitter/tree-sitter](https://github.com/tree-sitter/tree-sitter)
* **Documentation:** [tree-sitter.github.io](https://tree-sitter.github.io/tree-sitter/)

Tree-sitter is an incremental parser generator. It turns source code into a concrete syntax tree (AST) fast enough to run on every keystroke — which is why editors such as Neovim and Zed, and GitHub's own code navigation, rely on it.

For an AI Engineering Brain, Tree-sitter is the first stage of the pipeline: everything downstream — entities, relationships, the graph itself — derives from the trees it produces.

---

# 9.2 The Parsing Pipeline

```text
Code
↓
AST
↓
Entities (classes, functions)
↓
Relationships (calls, imports)
↓
Knowledge Graph
```

Instead of splitting code into text chunks, the parser exposes the actual structure of the program: declarations, references, types, and scopes.

---

# 9.3 Language Coverage for a Cross-Stack Brain

Tree-sitter has grammars for essentially every mainstream language. For the stacks referenced throughout this whitepaper:

| Language                | Stack                  |
| ----------------------- | ---------------------- |
| Dart                    | Flutter                |
| Java / Kotlin           | Spring Boot, Android   |
| Swift                   | iOS                    |
| PHP                     | Laravel                |
| TypeScript / JavaScript | Web frontends, Node    |
| SQL                     | Schemas and migrations |

A single ingestion pipeline can therefore span a heterogeneous system — mobile, backend, and database — with one parsing technology.

---

# 9.4 Why Local Parsing Matters

Because Tree-sitter parsing is **local and deterministic**:

* No tokens are spent — code entity extraction requires zero LLM calls.
* No code leaves the machine — important for private repositories.
* Parsing is fast enough to re-run on every commit, keeping the graph current.

This is why tools like [Graphify](https://github.com/safishamsi/graphify) can index a code-only corpus without any API key at all.

---

# 9.5 From AST to Graph

A concrete example. This Dart snippet:

```dart
class UserRepository {
  Future<User> getUser() {}
}
```

parses into a tree of typed nodes:

```text
class_definition
↓
method_signature
↓
return_type
↓
parameters
```

An extractor walks this tree and emits graph elements:

* `(:Class {name: "UserRepository"})`
* `(:Function {name: "getUser"})`
* `(:Class)-[:DEFINES]->(:Function)`

Multiply this by every file in every repository, and the engineering topology described in [Chapter 5](05-knowledge-graphs.md) emerges.

---

# 9.6 Key Takeaways

Tree-sitter supplies the structural raw material for the entire AI Engineering Brain. It is fast, local, language-agnostic, and battle-tested by the largest code platforms in the world.

With parsing in place, the next question is where the extracted structure lives — the storage layer of Neo4j and Qdrant.

---

## References

* [Tree-sitter Repository](https://github.com/tree-sitter/tree-sitter)
* [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
* [Graphify](https://github.com/safishamsi/graphify) — Tree-sitter-based extraction in practice

---

**End of Chapter 9**

---

> [◀ Chapter 8: Graphiti](08-graphiti.md) · [🏠 Home](../README.md) · [Chapter 10: Neo4j & Qdrant ▶](10-neo4j-and-qdrant.md)
