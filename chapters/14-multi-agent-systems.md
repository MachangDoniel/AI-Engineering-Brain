> [◀ Chapter 13](13-compound-engineering.md) · [🏠 Home](../README.md) · [Chapter 15: Virtual Organizations ▶](15-virtual-organizations.md)

---

# Chapter 14 — Stop Building AI Agents. Start Building Multi-Agent Systems.

> *"A single agent scales until it doesn't. The failure is never the model — it is asking one context window to hold every responsibility at once."*

---

# 14.1 Introduction

Most developers start with one agent.

One prompt. One model. One giant context window. It works — until the agent has to do too many unrelated things at once:

* search documentation
* write code
* review that code
* run tests
* debug the failures
* remember earlier decisions
* talk to the user

So the prompt grows. It reaches a thousand lines, then three thousand. The context window fills with tool output nobody needed. Instructions for reviewing code start bleeding into how the agent writes it. Performance drops. The agent forgets a decision it made twenty steps ago. The natural response is to add *more* prompt — more rules, more examples, more guardrails — and the cycle repeats.

The problem is not the model. The problem is the architecture.

This chapter argues that the same evolution software went through — from monoliths to services — is now happening to AI applications, and that the discipline for building agentic systems is not *better prompting* but *better separation of responsibilities*. It is the natural continuation of [Chapter 2's evolution](02-evolution-of-ai-software-engineering.md) and the [compound-engineering loop](13-compound-engineering.md): once generation is cheap, the scarce resource becomes *coordination*.

---

# 14.2 The Single-Agent Era

A single agent is the right default. It is simple, cheap, easy to debug, and for most tasks it is entirely sufficient. This chapter is not an argument against single agents — it is an argument about *when* one stops being enough.

The single-agent shape looks like this:

```text
User
 ↓
System Prompt  (role + rules + tools + examples)
 ↓
LLM  ──▶ tool call ──▶ result ──▶ LLM ──▶ …
 ↓
Answer
```

Everything the agent knows lives in one context window: its instructions, its conversation history, and every tool result it has ever seen this session. That single window is both the strength and the ceiling.

---

# 14.3 Why Single Agents Break Down

Single agents fail in predictable ways as scope grows. None of these are model-quality problems — a smarter model postpones them, it does not remove them.

**Context pollution.** Every tool call dumps its output into the same window. A file read, a failed test log, a stack trace — after a dozen steps the window is mostly noise, and the signal the agent needs is buried in the middle, where models attend to it least.

**Role blending.** The prompt that tells an agent *how to write code* is a poor prompt for *reviewing* it — the reviewer needs skepticism the author cannot supply for itself. Fuse both into one prompt and each dilutes the other. The agent that just wrote the code is the worst possible reviewer of it.

**Tool overload.** Give one agent forty tools and it spends reasoning budget deciding *which* tool to use rather than using it. Selection accuracy drops as the tool count rises.

**No parallelism.** A single agent is a single thread. Researching five libraries means researching them one after another, each result crowding the window for the next.

**One failure, whole restart.** When a monolithic agent goes wrong at step 30, there is no clean unit to retry. The bad state is entangled with everything else in the window.

```text
Single agent, growing scope:

  scope ↑
        │            ╭──── "just add more prompt"
        │          ╭─╯
quality │────╮   ╭─╯   ← quality falls as
        │    ╰─╮╭╯       responsibilities pile
        │      ╳         into one window
        └──────────────▶ time
```

---

# 14.4 The Monolith → Microservices Analogy

The framing that makes this click: **AI applications are repeating the monolith-to-microservices transition, one abstraction layer up.**

| Software architecture | Agent architecture |
|-----------------------|--------------------|
| One process, all responsibilities | One agent, all responsibilities |
| Shared mutable state everywhere | One context window holding everything |
| A change in billing breaks checkout | A rule for review corrupts generation |
| Scale the whole app to scale one part | Grow the whole prompt to fix one behavior |
| Split into services with clear contracts | Split into agents with clear responsibilities |
| Services talk over defined interfaces | Agents talk over defined handoffs |

The analogy is *load-bearing but not total* — and the honest version includes its limits, or it becomes the same hype it is trying to replace:

* Microservices communicate deterministically; agents communicate in natural language, which is lossy. A handoff can drop or distort information a function call never would.
* Every agent boundary you add is a new place for context to be lost in translation. Distributed *anything* trades local complexity for coordination complexity — and coordinating non-deterministic components is harder than coordinating deterministic ones.
* Premature decomposition is as real a mistake with agents as it is with services. Most teams reach for microservices too early; the same instinct will over-split agents.

Keep the analogy for its intuition — *separate responsibilities, define contracts, scale the part that needs scaling* — and drop it the moment it tempts you to add a boundary the task does not require.

---

# 14.5 What Counts as a Multi-Agent System

A multi-agent system (MAS) is **multiple LLM-driven components, each with a bounded responsibility and its own context, coordinated toward one goal.**

The load-bearing word is *bounded*. What you are really doing is giving each responsibility its own clean context window, its own focused instructions, and its own small set of tools — then wiring them together. The value comes less from having "many agents" and more from **context isolation**: the reviewer never sees the author's scratch work, the researcher's dead ends never reach the coder.

Common roles that emerge:

| Role | Responsibility | Reads | Writes |
|------|----------------|-------|--------|
| **Orchestrator** | Decompose the goal, route work, assemble results | The goal | Sub-tasks, final answer |
| **Planner** | Turn intent into an ordered, verifiable spec | The goal | A plan |
| **Researcher** | Gather external facts (docs, web, graph) | A question | Findings |
| **Coder** | Implement one well-scoped change | A spec | A diff |
| **Reviewer / Critic** | Find defects, challenge correctness | A diff + spec | Findings |
| **Tester / Executor** | Run code, tests, tools; report ground truth | A command | Results |
| **Memory** | Persist and recall decisions across time | Everything | Durable facts |

These are *roles*, not a required org chart. A small system might be two agents (a coder and a reviewer); a large one might spawn a fresh researcher per sub-question. Start with the fewest boundaries the task actually needs.

---

# 14.6 Orchestration Patterns

How agents are wired together matters more than how many there are. Five patterns cover most real systems.

### 1. Sequential Pipeline

Each agent's output is the next agent's input. Deterministic, easy to reason about, easy to debug.

```text
Planner → Coder → Reviewer → Tester
```

Best when the stages are genuinely ordered. Weak when work is exploratory or the path isn't known in advance.

### 2. Orchestrator–Worker

A lead agent decomposes the goal and dispatches sub-tasks to workers — often *identical* workers running in parallel on different slices. The lead synthesizes their results. This is the workhorse pattern for open-ended research and multi-file work.

```text
            ┌──────────────┐
            │ Orchestrator │
            └──────┬───────┘
        ┌──────────┼──────────┐
        ▼          ▼          ▼
    Worker A   Worker B   Worker C     (parallel, isolated contexts)
        └──────────┼──────────┘
                   ▼
              Orchestrator  → synthesized result
```

### 3. Hierarchical

Orchestrators of orchestrators. A top agent manages mid-level leads, each managing workers. This is the "AI software team" org-chart people find intuitive — CEO → PM → Architect → Engineers → QA. Powerful, but every layer adds latency and a place for intent to distort. Use the fewest layers that work.

### 4. Debate / Critic Loop

Two or more agents argue toward a better answer — a generator proposes, a critic attacks, they iterate. Improves quality on reasoning-heavy tasks at the cost of more turns. The [review step in Chapter 13](13-compound-engineering.md#133-the-four-step-loop) is this pattern with a human as one participant.

```text
Generator → draft → Critic → objections → Generator → revised → …
```

### 5. Blackboard / Shared Workspace

Agents don't call each other directly; they read from and write to a shared state (a scratchpad, a task board, a graph). Decouples agents and suits systems where the set of participants changes at runtime — but shared mutable state reintroduces exactly the coordination hazards microservices tried to escape, so the contract for who-writes-what has to be explicit.

---

# 14.7 Communication Between Agents

Agents coordinate in one of two ways, and most real systems mix them.

**Message passing (handoffs).** Agent A finishes and hands a structured payload to Agent B. Clean and traceable, but lossy — whatever A doesn't put in the message, B never learns. The discipline here is designing the *handoff contract*: the minimum an agent must emit for the next one to succeed.

**Shared memory.** Agents read and write a common store — a working document, a task list, or the knowledge graph and temporal memory from [Chapters 5–8](05-knowledge-graphs.md). Nothing is lost in translation, but the store becomes a synchronization problem and a new source of context pollution if every agent writes freely.

```text
Message passing:     A ──[payload]──▶ B        (lossy, traceable)

Shared memory:       A ──▶ ┌───────────┐ ◀── B
                           │  Blackboard │       (lossless, needs a
                     C ──▶ └───────────┘ ◀── D    write contract)
```

The single most common MAS failure is a **bad handoff**: the orchestrator's instruction to a worker was underspecified, so the worker confidently did the wrong thing. Natural language is a lossy protocol. Treat every handoff as an interface you would document — because it is one.

---

# 14.8 Parallel Execution and the Cost Multiplier

The headline benefit of MAS is parallelism: five researchers hit five sources at once; each has a clean window; the orchestrator merges the findings. Wall-clock time drops and quality on breadth-first tasks rises, because no single window has to hold everything.

The headline cost is **tokens**. Every agent carries its own instructions and context, and the orchestrator pays again to synthesize. As a rough order of magnitude, a chat turn spends some baseline of tokens; a single agent spends several times that; a multi-agent system can spend *an order of magnitude more* — Anthropic reported their multi-agent research system used roughly **15× the tokens** of a plain chat interaction.

```text
        tokens
          ▲
   ~15×   │                          ████  Multi-agent system
          │
    ~4×   │              ████              Single agent
          │
     1×   │   ████                         Chat turn
          └────────────────────────────▶
```

That multiplier is the central economic fact of this chapter. It means MAS only pays off when the **value of the task clears the token cost** — and it draws the boundary in [§14.11](#1411-when-not-to-use-a-multi-agent-system). Parallelism is not free; it is a purchase.

---

# 14.9 Failure Recovery

Isolation is what makes MAS *robust*, not just fast. Because each agent owns a bounded task with a bounded context, a failure is a bounded unit you can retry, replace, or escalate — unlike the monolithic agent where a bad step at turn 30 poisons everything after it.

Recovery strategies, cheapest first:

| Strategy | Mechanism |
|----------|-----------|
| **Retry** | Re-run the failed agent with the same input (handles flaky tools, transient errors) |
| **Reframe** | Re-run with a sharper handoff — most failures are underspecified inputs |
| **Reassign** | Give the sub-task to a different agent or a stronger model |
| **Escalate** | Return control to the orchestrator, or to a human ([§14.10](#1410-human-in-the-loop)) |
| **Checkpoint** | Persist state between stages so recovery resumes rather than restarts |

The design rule: **make failures cheap to contain.** Prefer many small agents with clear boundaries over a few large ones, precisely because the small ones fail in small, recoverable pieces. This is the same argument microservices make about blast radius.

---

# 14.10 Human-in-the-Loop

A MAS is not an argument for removing humans — it is an argument for placing them precisely. Because responsibilities are separated, the human can sit at exactly the boundary that matters and nowhere else:

* **Approve the plan** before any worker runs (cheap gate, high leverage)
* **Review at the handoff** between generation and merge, not on every token
* **Break ties** in a debate loop the agents can't resolve
* **Authorize side effects** — anything that spends money, sends a message, or ships

This maps directly onto [Chapter 13's Plan/Review allocation](13-compound-engineering.md#133-the-four-step-loop): the human's 40% planning and 40% review don't disappear in a MAS — they *concentrate* at the orchestrator's boundaries, where one decision steers many agents at once. That leverage is the point. A single well-placed human approval can gate a dozen parallel workers.

---

# 14.11 When NOT to Use a Multi-Agent System

This is the section most articles skip, and the one that separates architecture from hype. **Reach for a single agent first.** A MAS is the wrong choice when:

* **The task is simple or linear.** If one agent with a focused prompt does it reliably, decomposition only adds latency, cost, and failure modes. Most tasks are here.
* **The token budget doesn't justify 15×.** The economics only work when the task's value is high and its work is genuinely parallelizable ([§14.8](#148-parallel-execution-and-the-cost-multiplier)).
* **Sub-tasks are tightly coupled.** If agents constantly need each other's intermediate state, the handoff overhead exceeds the benefit of isolation. Coupled work wants one context, not many.
* **You need determinism.** More agents means more non-determinism and a larger surface where natural-language handoffs distort intent. High-stakes, reproducible pipelines may want fewer, more constrained components.
* **You can't yet observe a single agent.** If you can't trace and debug one agent, you have no hope of debugging five. Earn multi-agent complexity by first mastering the single-agent case.

> The right question is never "how many agents?" It is **"what is the smallest number of bounded responsibilities that makes this reliable?"** Sometimes the answer is one.

---

# 14.12 Real Systems

These systems are described from their public behavior and documentation; internal designs evolve, so treat the shapes as illustrative rather than exact.

* **Claude Code** — a terminal agent that can spawn **subagents** with their own context windows and tool sets for scoped work (search, review, planning), keeping the main conversation's window clean. A concrete instance of context isolation: the subagent does the noisy exploration and returns only the conclusion. Its `/code-review` and multi-agent review modes are the debate/critic pattern in production.
* **Devin** — an autonomous software-engineering agent built around planning, execution, and self-verification over long horizons, with a human reviewing at checkpoints — the plan-first, PR-level review of [Chapter 13's Stage 4–5](13-compound-engineering.md#134-five-maturity-stages).
* **Cursor** — an AI-native IDE whose strength is fast semantic indexing; its agent features increasingly coordinate scoped operations rather than running one monolithic loop.
* **Codex** — OpenAI's coding agent (CLI and cloud) that runs tasks in parallel, isolated environments — the orchestrator-worker shape applied to whole tasks.
* **GitHub Copilot** — began as single-agent completion ([Chapter 2, Era 4](02-evolution-of-ai-software-engineering.md#25-era-5-ai-code-completion)) and is layering in specialized, agentic workflows on top — a live example of the single→multi transition this chapter describes.

The through-line: none of these won by having a smarter single agent. They won by giving each responsibility a clean context and a clear contract.

---

# 14.13 From Teams to Organizations

A single MAS is one *team*. Follow the trend past a single team and the destination is an entire org chart made of agents — multiple specialized teams, each its own MAS, coordinated under shared policy, memory, and budgets, with humans supervising at the boundaries. That higher-level structure — the **Virtual Organization** — is where a MAS stops being the whole system and becomes one department inside it.

That is the subject of [Chapter 15](15-virtual-organizations.md). Two cautions carry forward into it. First, **every boundary is a liability, not a goal** — each agent, team, and layer is latency, cost, and a lossy handoff; the best system uses the fewest that work. Second, none of it functions without the infrastructure the rest of this book describes: shared **memory** so agents don't repeat each other ([Chapters 5–8](05-knowledge-graphs.md)), a protocol to reach tools and each other ([MCP, Chapter 11](11-mcp-and-ai-agents.md)), and the **compound-engineering discipline** ([Chapter 13](13-compound-engineering.md)) that gives every agent good context to begin with. A multi-agent system without a shared brain is just several confused agents talking past each other — and a Virtual Organization without one is that failure multiplied across departments.

---

# 14.14 Key Takeaways

| Idea | Summary |
|------|---------|
| The real problem | Single agents break on *architecture*, not model quality — one window can't hold every responsibility |
| The mental model | Monolith → microservices, one layer up: separate responsibilities, define contracts, scale the part that needs it |
| What a MAS really buys | **Context isolation** — each responsibility gets a clean window, focused tools, and a bounded failure |
| Patterns | Pipeline · orchestrator-worker · hierarchical · debate/critic · blackboard |
| The hard part | Handoffs — natural language is a lossy protocol; treat every handoff as a documented interface |
| The cost | Parallelism is a purchase — a MAS can cost ~15× the tokens of a chat turn |
| The discipline | Reach for one agent first; add a boundary only when the task demands it |
| The dependency | AI software teams only work atop shared memory (Ch. 5–8), a tool protocol (Ch. 11), and compound engineering (Ch. 13) |

---

## References

* Anthropic, *[How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)* (2025)
* Anthropic, *[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)* (2024)
* Anthropic, *[Model Context Protocol](https://modelcontextprotocol.io)* Specification
* Cognition, *[Introducing Devin](https://cognition.ai/blog/introducing-devin)* (2024)
* Cognition, *[Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)* (2025) — the counter-argument, worth reading against this chapter

---

### Author's Note

This chapter is deliberately two-sided. The strongest case *for* multi-agent systems and the strongest case *against* them agree on the same underlying fact: coordination is expensive and handoffs are lossy. The difference is only whether a given task's value clears that cost. Read alongside [Chapter 13](13-compound-engineering.md), the message is consistent — now that generation is cheap, engineering is the discipline of deciding *where the boundaries go*, whether those boundaries sit between steps in a loop or between agents in a system.

---

**End of Chapter 14**

---

> [◀ Chapter 13: Compound Engineering](13-compound-engineering.md) · [🏠 Home](../README.md) · [Chapter 15: Virtual Organizations ▶](15-virtual-organizations.md)
