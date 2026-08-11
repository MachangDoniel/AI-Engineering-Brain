> [◀ Chapter 17](17-git-worktrees.md) · [🏠 Home](../README.md) · [Appendix: Tool Directory ▶](../appendix/tool-directory.md)

---

# Chapter 18 — Sprint Tracking: The Engineering Record That Writes Itself

> *"Your repository records what the code is. Git records what changed. Neither records what you were trying to do, what you considered, and why you chose this way — and that is the only part you cannot reconstruct."*

---

# 18.1 Introduction

Six weeks after a sprint closes, the questions are always the same shape:

* *Why is the idempotency key generated on the client and not the server?*
* *What actually shipped in Sprint 12 — and what quietly slipped?*
* *We tried Redis for this once. What happened?*
* *How much of last month was new capability, and how much was paying down the refactor?*

Every one of those has an answer. None of them is in the repository.

The code says *what is*. `git log` says *what changed*. The pull request says *what was reviewed*. The reasoning — the constraint that forced the choice, the two alternatives that were weighed and rejected, the measurement that made it necessary — lived in a person's head, a chat thread, and an agent's context window. All three expire. The context window expires fastest of all.

This chapter is about closing that gap with a small, deliberately boring artifact: **a tracker file, declared once in `AGENTS.md`, that the agent updates as a normal part of doing the work, and that renders as a dashboard you open in a browser.** Not a project management tool — those plan the future. This records engineering history, including the reasoning that ticket systems structurally throw away.

The reference implementation lives in [`sprint-tracker/`](../sprint-tracker/) — one self-contained HTML file, its schema, and the `AGENTS.md` block that makes it automatic.

---

# 18.2 The Amnesia Problem

[Chapter 13](13-compound-engineering.md) framed the compound-engineering loop: Plan → Work → Review → Compound. The fourth step is the one everybody skips, and skipping it is why AI-assisted teams so often feel fast and end up lost.

The mechanism is specific. During a sprint, an agent holds an enormous amount of live reasoning: which approach it tried first, why it abandoned it, which constraint made the second approach necessary, what it deliberately left out of scope. Then the session ends. The next session — same repository, same agent, same person — starts from zero and rediscovers the same walls.

```text
Session 1:  full reasoning, live constraints, rejected paths ████████████████
Session end                                                  ────────────────
Session 2:  code + git log only                              ███
                                                              ▲
                                          everything above this line is gone
```

Three things are lost, and they are not equally recoverable:

| Lost | Recoverable from git? | Cost of losing it |
|---|---|---|
| What was built | **Yes** — it's the diff | Low |
| When and by whom | **Yes** — it's the log | Low |
| **Why it was built that way** | **No** | **The whole thing** |

The first two are the ones every tool already captures. The third is the only one worth building a system for — and it is the one nothing captures by default, because at the moment it exists it feels too obvious to write down.

**The asymmetry of the decision log.** A feature list can be rebuilt from `git log` in ten minutes. A *rejected alternative* cannot be rebuilt at any price. "We considered Redis and rejected it because it adds a network hop we don't need at this instance count" is available for roughly one hour after the decision, and then it is gone forever — leaving behind only a cache implementation that looks arbitrary and that someone will "improve" into the thing you already rejected.

---

# 18.3 The Loop

The tracker's whole design follows from one constraint: **it must be written at the moment of the decision, by whoever is already in that context.** That is not a human at sprint retro. It is the agent, mid-task.

```text
  You develop a feature or run a sprint
              │
              ▼
  Agent reads AGENTS.md → finds the declared tracker path
              │
              ▼
  Agent appends to the JSON data block inside tracker/index.html
    · features & work items       · decisions taken (and rejected)
    · commit / PR / test metrics  · blockers, risks, timeline
              │
              ▼
  You open tracker/index.html → the whole sprint, rendered
              │
              ▼
  The record feeds the next sprint's plan ──▶ compounds
```

Three properties make this work where "remember to write an ADR" does not:

1. **The trigger is the work, not a calendar.** The record is written when an item ships or a decision is taken — not batched at sprint close, when the reasoning has already evaporated and you produce a changelog wearing a decision log's costume.
2. **The writer is already in context.** The agent that just weighed three caching strategies can name the two it rejected. Nobody else can, an hour later.
3. **The instruction is standing, not repeated.** Declared once in `AGENTS.md`, it applies to every session forever — the same mechanism [Chapter 13](13-compound-engineering.md) uses for `CLAUDE.md` conventions.

---

# 18.4 Why One HTML File

The reference implementation is a single self-contained HTML file: markup, styles, renderer, and the data, all in one document with no dependency, no build step, and no server.

This looks primitive. It is deliberate, and every alternative was worse:

| Alternative | Why not |
|---|---|
| A web app with a database | The tracker has to survive being ignored for six months. Anything with a runtime rots — dependencies break, the service moves, the API key expires |
| Markdown files per sprint | Fine to write, bad to read. You cannot see rhythm, distribution, or trend in twelve markdown files |
| A separate `data.json` + HTML | `file://` fetch is blocked by CORS in every modern browser. A separate data file forces you to run a local server just to read your own notes |
| A hosted dashboard (Notion, Confluence) | It leaves the repository. History that doesn't survive `git clone` isn't history |
| Jira / Linear | They coordinate people and plan future work — and they discard the rejected alternative by design. Different job |

The embedded-JSON design is the specific trade that keeps the double-click promise:

```html
<script type="application/json" id="tracker-data">
{ "project": { … }, "sprints": [ … ] }
</script>
```

The agent edits **only** that block. Markup, CSS and renderer above it are frozen — which means the template stays a template, and a project never forks it. The cost is one file to diff; the benefit is that the diff is *all data*, so a sprint's changes are readable in a pull request.

**The file will still open in 2030.** That is the actual requirement, and it rules out almost everything else.

---

# 18.5 What Gets Recorded

The schema ([`SCHEMA.md`](../sprint-tracker/SCHEMA.md)) is small on purpose. Six objects:

| Object | Records | Notes |
|---|---|---|
| `project` | Name, repo, stack, last updated | Header identity |
| `sprint` | Id, name, **goal**, dates, status | The goal is one sentence with a target, not a theme |
| `feature` | Id, title, type, status, owner, points, commits, files | Any work item — `feature` · `fix` · `refactor` · `chore` |
| `decision` | Context, decision, **alternatives**, consequences | The ADR. The reason the system exists |
| `blocker` | Severity, owner, what it stalls | Rolls into an all-time KPI so it can't be forgotten |
| `event` | Dated, typed, one sentence | The sprint as a narrative |

Two fields carry disproportionate weight.

**`type`** — the `feature`/`fix`/`refactor`/`chore` split is what tells you, three sprints later, that 60% of what felt like velocity was interest payments on a design decision made in Sprint 9. Without the split, every sprint looks equally productive.

**`alternatives`** — the rejected options and why. An ADR without them isn't a decision record; it's a changelog entry. In review, treat an empty `alternatives` array as a finding: it usually means the decision wasn't examined, only made.

## Metrics come from the repository

Commits, files changed, lines added and removed are **derived, never estimated**:

```bash
git log --since=2026-08-03 --until=2026-08-16 --oneline | wc -l
```

```bash
git diff --shortstat $(git rev-list -1 --before=2026-08-03 main) HEAD
```

If a number can't be derived, it is omitted — every metric field is optional and the dashboard renders a dash. A fabricated metric is strictly worse than a missing one, because it survives review and gets quoted.

---

# 18.6 Wiring It Into `AGENTS.md`

The tracker is inert until the agent knows about it. That is one block in `AGENTS.md` (or `CLAUDE.md`) — reproduced in full in [`AGENTS-snippet.md`](../sprint-tracker/AGENTS-snippet.md), abbreviated here:

```markdown
## Sprint tracker — maintain this

**Tracker file:** `docs/tracker/index.html`
**Data contract:** the script element with id=tracker-data at the bottom of that
file. Edit only that block — never the markup, CSS, or renderer above it.

Write to the tracker when:
  · a sprint begins ............ new entry at the front of sprints[]
  · an item starts / ships ..... status + dates + commit count + files
  · a non-obvious decision ..... a full ADR, including rejected alternatives
  · something is blocked ....... severity, owner, and the item it stalls
  · a sprint closes ............ reconcile metrics from git, mark complete

Derive metrics from git — never estimate. Omit what you cannot derive.
Never retro-edit a past sprint to look complete.
```

The specificity is load-bearing. "Keep the tracker updated" is an instruction agents drift away from within a session or two. **A named path, named triggers, and a named forbidden region are ones they follow** — the same lesson [Chapter 16](16-spec-driven-development.md) draws about specs: precision is what makes an instruction executable rather than aspirational.

If you want it enforced mechanically rather than by instruction, a `PostToolUse` hook can validate the JSON on every write:

```bash
python3 -c "import json;h=open('docs/tracker/index.html').read();json.loads(h.split('id=\"tracker-data\">')[-1].split('</script>')[0]);print('tracker JSON valid')"
```

---

# 18.7 Reading the Dashboard

Opening the file gives you, in one screen: all-time KPI tiles (sprints, features, commits, decisions, net lines, open blockers), then per sprint — the goal, a status rail with counts, derived metrics, a commits-per-day chart, the full item table, the decision log, blockers, and the timeline.

What you are actually looking for is rarely a single number. It's the shapes:

| Shape on the dashboard | What it usually means |
|---|---|
| Commit chart with a flat middle and a spike at the end | Work was blocked, then rushed. Look at the blockers |
| High commit count, low `shipped` count | Scope was wrong, or items are too large to finish |
| `refactor` and `fix` dominating three sprints running | You are servicing debt, not building. Find the ADR that caused it |
| A sprint with zero decisions | Either genuinely routine, or the log is being skipped |
| Blockers with an external `owner` recurring | The bottleneck isn't engineering |

The dashboard follows light and dark mode, carries a manual toggle, and states status as **colour plus a written label** — never colour alone — with a table view behind the commit chart, so it stays readable for colour-blind readers and in print.

---

# 18.8 Conventions and Honesty Rules

The tracker's only asset is that it is true. Every convention below exists to protect that.

**Identifiers.** Sprints `S-14`. Features `F-141` (leading digits echo the sprint). Decisions `ADR-021`, numbered globally and **never reused**. Blockers `B-07`.

**A reversal is a new ADR.** You never delete or rewrite a decision. The old one keeps its number, takes `"status": "superseded"`, and names its replacement in `consequences`. The history of a decision that was wrong is more instructive than the decision that replaced it.

**Unfinished work stays unfinished.** Anything not done at sprint close is carried into the next sprint as a **new** entry. The old entry stays exactly as it was. Tidying a past sprint to look complete is the one edit that destroys the entire point of keeping the file.

**Dates are ISO.** `2026-08-12`. Never "last Tuesday".

**Commit it.** The tracker lives in the repository and is versioned with the code. A gitignored tracker is a tracker that vanishes on the next `git clone`.

**Review the tracker diff.** Because the data is JSON, a sprint shows up as a readable diff next to the code diff. Reading it is the cheapest quality gate available here — an empty `alternatives` field is visible in review in a way that a shallow decision never is in the code.

---

# 18.9 Scaling It

**Long-running projects.** Past roughly a dozen sprints the file gets heavy to diff. Archive: move closed sprints into `tracker/archive/2026-H1.html` — a copy of the same template carrying only those sprints — and keep the live file to the recent few. Because the template is self-contained, an archive is just another file you can open.

**Multiple repositories.** One tracker per repository, each declared in its own `AGENTS.md`. A cross-repo roll-up is a separate file whose data block concatenates their `sprints` arrays; the schema is flat specifically so this is a copy-paste rather than a merge.

**Parallel agents.** [Chapter 17](17-git-worktrees.md) runs several agents at once in separate worktrees. Each worktree has its own copy of the tracker file, and concurrent writes to the same JSON block will conflict. Two workable patterns: let only the integrating agent write the tracker after merge, or have each worktree agent write its sprint entry and reconcile at merge time — the entries are append-only and keyed by id, so reconciliation is mechanical.

**Feeding the graph.** The tracker is already structured data with stable identifiers, which makes it a natural ingest source for the knowledge graph of [Chapters 5](05-knowledge-graphs.md)–[6](06-graphrag.md). `ADR-022` *decided* `F-145`, which *touched* `api/payment/IdempotencyFilter.java`, which *belongs to* the payment service — that is the multi-hop path that answers *"which architectural decision introduced this dependency?"*, the question this book opened with. The tracker is where the `DECIDED` edge comes from; nothing else in the repository has it.

---

# 18.10 When *Not* to Track

The tracker earns its keep on work with a future. It is overhead everywhere else.

* **Throwaway or exploratory work.** A spike you will delete on Friday has no history worth keeping.
* **Solo scripts and one-file utilities.** If the whole project is 200 lines, the code *is* the documentation.
* **Teams with a genuinely working ADR practice.** If decisions are already captured with rejected alternatives, you have the valuable half. Add the dashboard only if you want the metrics view too.
* **When it would become fiction.** A tracker filled in retroactively to look organized is worse than no tracker: it carries the authority of a record with the accuracy of a memory. If you won't keep it honest, don't keep it.
* **As a substitute for planning tools.** It records history. It does not assign work, plan capacity, or coordinate people, and bending it toward that will break the honesty rules first.

The test is simple: *will someone — including future you, or a future agent — need to know why this was built this way?* If no, skip it.

---

# 18.11 Summary

| | |
|---|---|
| The gap | Code records *what is*, git records *what changed*; nothing records *why it was chosen* |
| The asymmetry | Features are recoverable from git; **rejected alternatives are recoverable from nothing** |
| The mechanism | One tracker path declared in `AGENTS.md`; the agent writes as a side effect of the work |
| The trigger | The work itself — item ships, decision taken, blocker raised — never a calendar or a retro |
| The artifact | A single self-contained HTML file; agent edits only the embedded JSON block |
| Why one file | No dependency, no build, no server — it still opens in 2030, and its diff is readable in review |
| The rule that matters | Every ADR names what was **rejected** and why |
| Honesty | Metrics derived from git, unfinished work stays unfinished, reversals are new ADRs |
| The connection | It is the *Compound* step of [Ch. 13](13-compound-engineering.md) made concrete — and the source of the `DECIDED` edge in the graph of [Ch. 5](05-knowledge-graphs.md) |

---

# 18.12 References

* Nygard, *[Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)* (2011) — the original ADR pattern this chapter's decision log follows
* [`sprint-tracker/`](../sprint-tracker/) — the reference implementation in this repository: dashboard, [schema](../sprint-tracker/SCHEMA.md), and [`AGENTS.md` block](../sprint-tracker/AGENTS-snippet.md)
* [Chapter 13 — Compound Engineering](13-compound-engineering.md) — the loop this chapter operationalizes
* [Chapter 16 — Spec-Driven Development](16-spec-driven-development.md) — intent recorded *before* the work; this chapter is intent recorded *during* it
* [Chapter 17 — Git Worktrees](17-git-worktrees.md) — parallel agents, and the tracker-reconciliation problem they create
* Fowler, *[Architectural Decision Records](https://martinfowler.com/bliki/)* — on decisions as the durable unit of architecture

---

### Author's Note

The first version of this was a markdown file per sprint, and it was abandoned after four sprints — not because writing it was hard, but because reading it was useless. Twelve markdown files don't show you that two-thirds of a quarter went to refactoring, or that the same blocker owner appears in five sprints running. The dashboard changed nothing about what was recorded and everything about whether anybody looked.

The second thing worth saying: the temptation, always, is to make the record flattering. Every honesty rule in §18.8 exists because I broke it first — quietly moving an unfinished item's status, rounding a metric I hadn't actually measured. A tracker that has been tidied is not a weaker record than an untidied one; it is a *worse* artifact than no record at all, because it still reads like evidence. Keep it true or don't keep it.

---

**End of Chapter 18**

---

> [◀ Chapter 17: Git Worktrees](17-git-worktrees.md) · [🏠 Home](../README.md) · [Appendix: Tool Directory ▶](../appendix/tool-directory.md)
