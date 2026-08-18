> [◀ Chapter 19](19-loop-engineering.md) · [🏠 Home](../README.md) · [Appendix: Tool Directory ▶](../appendix/tool-directory.md)

---

# Chapter 20 — Graph Engineering in the Long-Context Era

> *"The graph beats the model size. Consistently."*
> — the claim this chapter takes seriously enough to check

---

# 20.1 Introduction

Every chapter in Part II of this book rests on an assumption that gets challenged roughly once per model release:

> *Why build a knowledge graph at all? Just put everything in the context window.*

In July 2026 that objection acquired its strongest form yet. Moonshot AI released **Kimi K3** — a 2.8-trillion-parameter open mixture-of-experts model with a **1-million-token context window** and an attention architecture specifically designed to make long sequences cheap rather than merely possible. For the first time the naive answer is not obviously wrong: a million tokens is a mid-sized repository, or a few hundred documents, or an entire quarter's worth of engineering discussion.

This chapter argues three things:

1. Long context **is** a genuine change, and it changes the graph's job — the graph stops being a workaround for a small window.
2. It does **not** remove the need for one, because context length and memory are different problems and always were.
3. The pairing of the two — a long-context model reasoning over a structured graph, an approach now being marketed as **graph engineering** — is the strongest configuration available in 2026, but the numbers attached to it in circulation are borrowed from elsewhere and deserve to be labelled honestly.

That third point is why this chapter exists at the end of the book rather than in Part II. It is a chapter about reading a claim carefully.

---

# 20.2 What Kimi K3 Actually Is

| Property | Value |
|---|---|
| Parameters | 2.8T total, sparse MoE — **16 of 896 experts** active per token |
| Attention | **Kimi Delta Attention (KDA)** — linear attention with a delta-rule state update — hybridised with full attention (MLA) |
| Depth mechanism | **Attention Residuals (AttnRes)** — selective retrieval of earlier-depth representations |
| Context | **1,000,000 tokens**, native multimodal (vision) |
| Training | Quantization-aware: MXFP4 weights, MXFP8 activations; fully balanced expert-parallel |
| Pricing (API) | $0.30/MTok cache-hit input · $3.00/MTok cache-miss input · $15.00/MTok output |
| Reported cache hit rate | >90% in coding workflows |
| Weights | Open release, 27 July 2026 |
| Honest benchmark position | Competitive on coding (DeepSWE, SWE Marathon, FrontierSWE) and productivity (OfficeQA Pro, SpreadsheetBench), **trailing Claude Fable 5 and GPT 5.6 Sol** |

Two of these rows matter for this book, and it is not the parameter count.

**KDA + MLA hybrid.** The published configuration mixes linear KDA layers with full-attention MLA layers at roughly 3:1, cutting KV-cache usage by about 75% versus full attention while outperforming MLA alone. Practically: the cost curve for long inputs flattens. Feeding a model 200,000 tokens of retrieved subgraph stops being a decision you agonise over and becomes a line item.

**The cache-hit price.** A 10× gap between cache-hit and cache-miss input, with a >90% hit rate in coding workflows, tells you something about how these systems are meant to be used: **stable prefix, variable suffix.** That is an architectural instruction disguised as a price list, and §20.7 takes it seriously.

---

# 20.3 What Long Context Actually Fixed

[Chapter 4](04-why-rag-isnt-enough.md) catalogued the failures of naive RAG: chunking destroys structure, similarity search misses causal chains, multi-hop questions require traversal that embeddings cannot perform. It is worth being precise about which of those a million-token window repairs.

| Ch. 4 failure | Fixed by long context? | Why |
|---|---|---|
| **Chunking destroys structure** | **Largely yes** | If the whole file — or the whole module — fits, you never had to cut it |
| **Top-k truncation loses evidence** | **Largely yes** | You can afford to pass the top 200 instead of the top 5 |
| **Reasoning across many documents** | **Partly** | The evidence is present; whether the model *finds* it is a different question |
| **Similarity ≠ relevance** | **No** | You still have to decide what to put in the window. Retrieval did not disappear; it moved |
| **Multi-hop causal chains** | **No** | Requires traversal over relationships that were never written down anywhere |
| **Knowing what changed and when** | **No** | A context window has no history. It is a scratchpad, not a record |

The pattern is clear. Long context solves **capacity** problems. It does not solve **structure** or **persistence** problems, because those are not about how much fits — they are about whether the relationship was ever recorded at all.

The most common question this book opened with — *what breaks if this service is removed?* — is unanswerable by a model reading a million tokens of source, not because the tokens do not fit, but because the answer is a transitive closure over a dependency edge set that exists nowhere in the text.

---

# 20.4 Working Memory vs Persistent Memory

The cleanest framing of the pairing:

```text
  1M-token context window          Knowledge graph
  ───────────────────────          ───────────────
  Working memory                   Persistent memory
  Per-session                      Cross-session
  Large but temporary              Small but permanent
  Cost scales with every call      Cost paid once at write time
  Unstructured, positional         Structured, addressable
  Forgets at the turn boundary     Accumulates, and is diffable
```

They are complements, not competitors — and the confusion between them is the same category error [Chapter 8](08-graphiti.md) named when distinguishing *knowledge* from *memory*.

A useful test: **if the session ended right now, what would you want to still be true tomorrow?** Everything in that answer belongs in the graph. Everything else can live in the window, and long context means "everything else" is now a very generous allowance.

There is a second, less obvious benefit. Once the window is large, the graph is free to stop optimising for compression. Earlier GraphRAG designs spent significant effort on community summaries and hierarchical rollups largely because the retrieved context had to fit in 128k. With a million tokens available, you can retrieve **raw subgraphs plus their supporting evidence** and let the model do the summarising at read time. The graph gets simpler and more faithful; the model absorbs the work that used to require a preprocessing stage.

**Long context does not retire the graph. It lets the graph be less clever.**

---

# 20.5 The Eight-Layer Pipeline

The graph-engineering stack circulating with Kimi K3 is an eight-layer system. Every layer already has a chapter in this book, which is worth showing explicitly — it is a repackaging of Part II with a bigger model at the reasoning step.

| # | Layer | What it does | Where this book covers it |
|---|---|---|---|
| 1 | **Ingestion** | Pull from PDFs, APIs, databases, repositories | [Ch. 7 — Graphify](07-graphify.md) for code; source-specific otherwise |
| 2 | **Extraction** | Model identifies entities and relationships | [Ch. 5](05-knowledge-graphs.md); for code, [Ch. 9 — Tree-sitter](09-tree-sitter.md) does this **deterministically and for free** |
| 3 | **Resolution** | Deduplicate entity references — the same thing named three ways | [Ch. 5](05-knowledge-graphs.md); the layer everyone underestimates |
| 4 | **Storage** | Neo4j, Memgraph, or Postgres + a vector index | [Ch. 10 — Neo4j & Qdrant](10-neo4j-and-qdrant.md) |
| 5 | **Retrieval** | Vector search + entity lookup + path search, combined | [Ch. 6 — GraphRAG](06-graphrag.md), §6.6–6.8 |
| 6 | **Agent** | Model writes queries, reads results, reasons | [Ch. 11 — MCP](11-mcp-and-ai-agents.md) |
| 7 | **Verification** | Check evidence, surface contradictions | [Ch. 6 §6.13 explainability](06-graphrag.md); [Ch. 19 §19.4](19-loop-engineering.md#194-the-five-components) for the maker/checker rule |
| 8 | **Update** | Write new facts **with timestamps** | [Ch. 8 — Graphiti](08-graphiti.md) — temporal, bi-temporal memory |

Three notes on where this stack is weaker than it looks, and where this book's version is stronger.

**Layer 2 is where money leaks.** Using a frontier model to extract entities from source code is paying LLM prices for something [Tree-sitter](09-tree-sitter.md) does deterministically, locally, and in milliseconds. Reserve model-based extraction for the sources where structure genuinely is not recoverable by parsing — prose, tickets, incident write-ups, design discussions. For code, parse first and let the model annotate what parsing cannot see: intent, rationale, and the reason a boundary exists.

**Layer 3 is the layer projects skip and then rebuild.** `AuthService`, `auth_service`, and "the auth thing" are one node or they are three, and if they are three, every path query silently returns partial answers. Entity resolution failures do not throw errors; they quietly reduce recall, which is the hardest class of bug to notice.

**Layer 8 is what turns a snapshot into a brain.** A graph without timestamps answers *what is true*. A graph with them answers *what changed, when, and what we believed before* — which is the question [Chapter 18](18-sprint-tracking.md) argued is the only one you cannot reconstruct later.

---

# 20.6 Prompts as Pipeline Stages

The second idea worth taking from the graph-engineering framing is structural rather than technical: the system is described as **five distinct prompts**, each a stage in a program, rather than one conversation.

| Stage | Prompt's job | Failure if you merge it with another |
|---|---|---|
| **Extract** | Text → triples, strict schema, no prose | Extraction drifts toward summary; you get opinions instead of facts |
| **Normalize** | Canonicalise entity names and relation types | The vocabulary forks and paths break (see layer 3 above) |
| **Query** | Question → graph query, nothing else | The model starts answering from parametric memory instead of the graph |
| **Answer** | Query results → grounded answer with citations | Ungrounded claims mix with grounded ones and become indistinguishable |
| **Maintain** | Detect contradictions, stale facts, orphans | Nothing catches drift, and the graph decays into confidently wrong |

This is the same discipline [Chapter 14](14-multi-agent-systems.md) argued for at the agent level — **separation of responsibilities** — applied one level down, to prompts. And it composes directly with [Chapter 19](19-loop-engineering.md): each of these five stages has a machine-checkable output contract, which makes each of them loop-able. *Extract until every triple validates against the schema* is a goal loop. *Maintain until zero contradictions remain* is a ratchet loop.

The maintenance stage is the one nobody builds first and everybody needs by month three. A graph is not a build artifact; it is a living index, and an index nobody sweeps becomes a liability faster than no index at all — because people trust it.

---

# 20.7 The Numbers, Honestly

The headline attached to this pairing is **"85% lower token costs and 18% better accuracy."**

Both figures are real, and neither is a Kimi K3 result. They derive from **Microsoft Research's GraphRAG work** — already cited in [Chapters 4](04-why-rag-isnt-enough.md) and [6](06-graphrag.md) of this book — measuring graph-structured retrieval against a naive baseline on Microsoft's own evaluation. Attaching them to a specific 2026 model is marketing, not measurement.

That does not make the underlying claim wrong. It makes it **unbenchmarked for your case**, which is a different and more actionable statement. [Chapter 6 §6.16](06-graphrag.md) already specifies the metrics you would need to make the claim yourself; run those before quoting anyone's percentage, including this book's.

## Where the cost saving actually comes from

The honest version of the cost argument does not need borrowed numbers. It is arithmetic, using K3's published pricing:

| Approach | Input tokens/query | Cache-miss cost | Cache-hit cost |
|---|---|---|---|
| Stuff the full context window | 1,000,000 | **$3.00** | $0.30 |
| Graph-retrieved subgraph + evidence | ~20,000 | **$0.06** | $0.006 |
| Ratio | 50× | **50×** | 50× |

The saving is not a property of the graph being clever. It is that **you sent 50× fewer tokens**, and retrieval is what let you send fewer without losing the answer. Long context makes the expensive option *possible*; the graph makes it *unnecessary*. That is the entire economic argument, and it does not depend on anyone's benchmark.

Two corrections to the naive reading of that table:

* **Cache economics change the shape, not the conclusion.** A stable graph-schema prefix plus a variable query suffix is the pattern that earns the >90% hit rate. Design for it deliberately: schema and instructions first and unchanging, retrieved evidence last.
* **Accuracy gains are not free either.** Graph retrieval improves answers only when the relationships were extracted correctly. A wrong edge is worse than a missing one, because it retrieves confidently. Budget for layers 3 and 7, or the accuracy claim reverses on you.

---

# 20.8 A Seven-Day Build

The circulating implementation plan compresses to five working days; here is the version with the two days everyone omits added back.

| Day | Work | The thing that goes wrong |
|---|---|---|
| **1** | Neo4j up, schema drafted — nodes, relationships, properties ([Ch. 10](10-neo4j-and-qdrant.md)) | Schema designed for the data you have, not the questions you will ask. Write the queries first |
| **2** | Extraction: Tree-sitter for code, model prompts for prose ([Ch. 9](09-tree-sitter.md)) | Using the model for everything. Parse what can be parsed |
| **3** | **Entity resolution** — canonical names, alias table, merge rules | Skipped. This is the day that decides whether day 5 works |
| **4** | Retrieval: entity lookup + neighbourhood expansion + vector fallback ([Ch. 6](06-graphrag.md)) | Traversal depth set to 3 "to be safe"; context explodes and precision collapses ([§6.8](06-graphrag.md)) |
| **5** | Expose to the agent via MCP ([Ch. 11](11-mcp-and-ai-agents.md)) | Tool returns 40k tokens of raw nodes. Return answers with citations, not dumps |
| **6** | **Measure against a baseline** — the same 30 questions through plain RAG and through the graph ([§6.16](06-graphrag.md)) | Skipped, and then the 85% figure gets repeated internally as if it were yours |
| **7** | **Maintenance loop** — staleness detection, contradiction sweep, orphan cleanup ([Ch. 19](19-loop-engineering.md)) | Skipped, and the graph is quietly wrong by month three |

Days 6 and 7 are the ones that separate a demo from a system. Day 6 is how you learn whether it worked; day 7 is how it keeps working.

---

# 20.9 Failure Modes Specific to Long-Context Graph Systems

[Chapter 6 §6.15](06-graphrag.md) lists the general GraphRAG failure modes. Long context introduces four of its own.

**Lost in the middle.** Retrieval accuracy across a very long window is not uniform. Attention Residuals and KDA are designed to improve exactly this, and they do — but "improved" is not "flat." Placing critical evidence at the extremes of a 900k-token payload and assuming it will be weighted equally is an untested assumption, not a guarantee. If the answer depends on one fact, do not bury it at token 500,000.

**The capacity illusion.** Because everything fits, the temptation is to stop curating. Precision then falls even as recall rises: more irrelevant context is more opportunity for a plausible wrong connection. A million-token window makes bad retrieval *survivable*, which is precisely what stops teams from fixing it.

**Extraction drift.** Run the same extraction prompt across six months of model updates and the vocabulary shifts underneath you. Yesterday's `DEPENDS_ON` becomes today's `USES`. Pin the schema, validate every triple against it, and treat a schema violation as a build failure — not as a note.

**Cost that hides in the miss rate.** The $0.30 headline is the cache-*hit* price. A workload with a churning prefix pays $3.00 and wonders where the budget went. The 10× gap means prompt architecture is now a cost-control discipline, which is a genuinely new thing for engineers to own.

---

# 20.10 When NOT to Build This

* **When the corpus fits in the window and never changes.** If your entire domain is 300k tokens of stable documentation, put it in the prompt, cache the prefix, and go home. The graph is infrastructure you would be maintaining for nothing.
* **When nobody asks multi-hop questions.** Graphs earn their cost on traversal. If every real question is "find me the passage about X," vector search is the right tool and always was ([Ch. 4](04-why-rag-isnt-enough.md) cuts both ways).
* **When you cannot staff maintenance.** An unmaintained graph is worse than none, because it is trusted. If day 7 has no owner, do not start.
* **When entity resolution is genuinely intractable.** Some domains have no stable identifiers and no reliable way to invent them. A graph over ambiguous entities produces confident paths through coincidence.
* **When you are choosing a model to justify an architecture.** K3 is strong, open, and cheap on long inputs; it also trails the frontier on coding benchmarks by its own published results. Pick the model for the task, then design the retrieval around it — not the reverse.

---

# 20.11 How This Connects to the Rest of the Book

* **[Chapter 4 — Why RAG Isn't Enough](04-why-rag-isnt-enough.md):** long context fixes the capacity complaints and leaves the structural ones untouched. The chapter's argument narrows; it does not fall.
* **[Chapter 6 — GraphRAG](06-graphrag.md):** the retrieval pipeline survives intact, but the context-composition stage ([§6.10](06-graphrag.md)) gets dramatically easier — less summarisation, more raw evidence.
* **[Chapter 8 — Graphiti](08-graphiti.md):** the update layer with timestamps is what makes the graph a memory rather than a snapshot, and it is the layer a context window can never provide.
* **[Chapter 9 — Tree-sitter](09-tree-sitter.md):** the deterministic answer to layer 2. Parse what can be parsed; spend model tokens on what cannot.
* **[Chapter 11 — MCP](11-mcp-and-ai-agents.md):** the graph reaches the agent as a tool. With a 1M window the tool can afford to return evidence, not just answers — but it should still return *chosen* evidence.
* **[Chapter 12 — Costs](12-costs-deployment-future.md):** the 50× table in §20.7 belongs to that chapter's budget model; the cache-hit/miss split is a new line item worth adding.
* **[Chapter 19 — Loop Engineering](19-loop-engineering.md):** every one of the five prompt stages has a checkable output contract, which makes each one loop-able. Extraction and maintenance are the two that should never be run by hand twice.

---

# 20.12 Key Takeaways

| Idea | Summary |
|------|---------|
| What changed | Kimi K3: 2.8T MoE (16/896 active), KDA + MLA hybrid attention, **1M-token context**, open weights, cheap long inputs |
| What that fixes | **Capacity** problems — chunking damage, top-k truncation, evidence budget |
| What it does not fix | **Structure and persistence** — multi-hop traversal, relationships never written down, history |
| The right framing | Context = working memory (per-session). Graph = persistent memory (cross-session). Complements, not rivals |
| The unexpected benefit | With a big window the graph can be **simpler** — retrieve raw subgraphs, skip the summarisation scaffolding |
| The stack | Ingest → extract → **resolve** → store → retrieve → agent → verify → **update with timestamps** |
| The discipline | Five separate prompts with output contracts, not one conversation |
| The numbers | 85% / 18% come from **Microsoft's GraphRAG research**, not from K3. Cite them as such and measure your own |
| The real cost argument | 20k retrieved tokens vs 1M stuffed tokens = **50× fewer tokens**. No benchmark required |
| New failure modes | Lost-in-the-middle, the capacity illusion, extraction drift, and cache-miss cost |
| When not to | Small stable corpus, no multi-hop questions, no maintenance owner, or intractable entity resolution |

---

# 20.13 References

* Moonshot AI, *[Kimi K3: Open Frontier Intelligence](https://www.kimi.ai/blog/kimi-k3)* — architecture, benchmarks, pricing, and the 27 July 2026 weight release
* *[moonshotai/Kimi-K3](https://huggingface.co/moonshotai/Kimi-K3)* — model weights and card
* *[Kimi K3 quickstart](https://platform.kimi.ai/docs/guide/kimi-k3-quickstart)* — API pricing and cache behaviour
* MarkTechPost, *[Moonshot AI Releases Kimi K3](https://www.marktechpost.com/2026/07/16/moonshot-ai-releases-kimi-k3-a-2-8-trillion-parameter-open-moe-model-with-kimi-delta-attention-and-1m-context/)* (July 2026) — independent summary of KDA and the MoE configuration
* Acing AI, *[Linear Attention at Frontier Scale: Kimi K3's KDA Claim, Fact-Checked](https://acingai.com/articles/linear-attention-kimi-k3)* — the skeptical read of the attention claims
* Microsoft Research, *GraphRAG* (2024) — the actual source of the 85% / 18% figures
* Neo4j, *[Cypher documentation](https://neo4j.com/docs/cypher-manual/current/)* — the storage and traversal layer ([Ch. 10](10-neo4j-and-qdrant.md))

---

### Author's Note

This chapter began as a summary of a viral thread and turned into an exercise in separating three things that arrived bundled together: a genuinely interesting model, a sound architecture, and a pair of borrowed statistics.

The model is real and the architecture is the one this book has argued for since Chapter 5. The statistics belong to somebody else's evaluation, and the moment they are repeated without that attribution they become the kind of claim that gets a project funded and then quietly under-delivers.

There is a broader lesson in the sequencing. Each time context windows grow, the same prediction appears — that retrieval is obsolete now — and each time the prediction is half right in a way that is easy to mistake for entirely right. Capacity limits move. Structural ones do not. A model that can read a million tokens still cannot read a relationship nobody wrote down, and the discipline of writing them down is the entire subject of this book.

---

**End of Chapter 20**

---

> [◀ Chapter 19: Loop Engineering](19-loop-engineering.md) · [🏠 Home](../README.md) · [Appendix: Tool Directory ▶](../appendix/tool-directory.md)
