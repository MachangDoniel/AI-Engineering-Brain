# 📊 Sprint Tracker

**A single HTML file that remembers what you built, what you decided, and why.**

*A convention for AI coding agents — declare a tracker path in `AGENTS.md`, and every sprint documents itself.*

---

## The problem

Your repository records **what the code is**. Git records **what changed**. Neither records **what you were trying to do, what you considered, and why you chose this way** — that lives in your head, in a Slack thread, or in the agent's context window, and all three expire.

Six weeks later the questions are always the same:

- *Why is the idempotency key generated on the client?*
- *What actually shipped in Sprint 12 — and what silently slipped?*
- *We tried Redis for this once. What happened?*
- *How much of last sprint was new features versus paying down the refactor?*

Reconstructing that from `git log` is archaeology. The Sprint Tracker captures it **at the moment the decision is made**, by the agent already sitting in that context, and renders it as one self-contained dashboard you can open in a browser.

## The idea in one loop

```
  You develop a feature or run a sprint
              │
              ▼
  Agent reads AGENTS.md → finds the tracker path
              │
              ▼
  Agent appends to the JSON data block inside tracker/index.html
    · features & work items      · decisions taken (and rejected)
    · commit / PR / test metrics · blockers, risks, timeline
              │
              ▼
  You open tracker/index.html → the whole sprint, rendered
```

No database, no build step, no server, no dependency. **One file. Open it in any browser.**

---

## 📁 What's in this package

| Path | Purpose |
|------|---------|
| [`template/tracker/index.html`](template/tracker/index.html) | **The dashboard.** Self-contained: markup, styles, renderer, and a `<script type="application/json">` data block. Ships populated with a realistic two-sprint sample so you can see it working before you write a line. |
| [`SCHEMA.md`](SCHEMA.md) | The data contract — every object, every field, every allowed value. This is what the agent writes against. |
| [`AGENTS-snippet.md`](AGENTS-snippet.md) | The copy-paste block for your project's `AGENTS.md`. This is the piece that makes it automatic. |

---

## 🚀 Setup (three steps, about two minutes)

### 1. Copy the tracker into your project

```bash
cp -R "template/tracker" /path/to/your-project/docs/tracker
```

Recommended locations, in order of preference:

| Location | When |
|----------|------|
| `docs/tracker/index.html` | Default. Versioned with the code, reviewable in PRs. |
| `.tracker/index.html` | You want it out of the way but still committed. |
| `tracker/index.html` | Repo root — fine for small projects. |

Keep it **inside the repository and committed**. The tracker's value compounds with history; a gitignored tracker is a tracker that disappears on the next machine.

### 2. Clear the sample data

Open the copied file, scroll to the `<script type="application/json" id="tracker-data">` block at the bottom, and replace it with your project's stub:

```json
{
  "project": {
    "name": "Your Project",
    "repo": "github.com/you/your-project",
    "owner": "Your Name",
    "stack": ["Flutter", "Spring Boot", "PostgreSQL"],
    "updated": "2026-08-12"
  },
  "sprints": []
}
```

Everything above that block — the markup, the CSS, the renderer — is frozen. You never touch it.

### 3. Point `AGENTS.md` at it

Paste the block from [`AGENTS-snippet.md`](AGENTS-snippet.md) into your project's `AGENTS.md` (or `CLAUDE.md`), with the path adjusted. That file is the agent's standing instruction set — once the tracker is named there, the agent maintains it without being asked each time.

Then verify:

```bash
open docs/tracker/index.html
```

---

## 🔁 How the tracking actually happens

The tracker is **agent-maintained, human-reviewed**. You don't fill in forms; you work normally, and the agent writes the record as a side effect of doing the work.

### Update triggers

The `AGENTS.md` contract tells the agent to write to the tracker at these moments — not on a timer, and not in a batch at the end when the reasoning has already evaporated:

| Trigger | What gets written |
|---------|-------------------|
| A sprint starts | New `sprints[]` entry: id, name, goal, dates, committed items |
| Work on an item starts | Feature moves to `in-progress`, `started` date set |
| An item ships | Status `shipped`, `completed` date, final commit count, files touched |
| **A non-obvious technical decision is taken** | A full ADR entry — context, decision, **rejected alternatives**, consequences |
| Something gets blocked | Blocker entry with severity, owner, and the item it stalls |
| A sprint closes | Final metrics reconciled; status `complete`; closing timeline event |

### The one rule that matters

> **Record the decision when you take it, including what you rejected.**

A feature list you can rebuild from `git log`. A rejected alternative you cannot — that reasoning exists for about an hour and then is gone forever. The `alternatives` and `consequences` fields are the highest-value data in the whole file; an ADR without them is a changelog entry wearing a costume.

### Where the numbers come from

Metrics are derived from the repository, not estimated. The agent runs the equivalent of:

```bash
git log --since=2026-08-03 --until=2026-08-16 --oneline | wc -l
```

```bash
git diff --shortstat $(git rev-list -1 --before=2026-08-03 main) HEAD
```

If a number can't be derived, it's omitted rather than guessed — the schema treats every metric as optional, and the dashboard renders a dash.

---

## 📈 What the dashboard shows

| Section | Answers |
|---------|---------|
| **KPI tiles** | All-time totals — sprints, features, commits, decisions, net lines, open blockers |
| **Sprint tabs** | Every sprint, newest first, with a live/complete/planned indicator |
| **Goal + status rail** | The sprint's one-sentence objective, and a stacked bar of item status with counts and percentages |
| **Sprint metrics** | Commits, PRs merged, files changed, lines ±, tests added, coverage, points |
| **Commits per day** | Daily commit bars with hover detail — and a "view as table" fallback |
| **Features & work items** | Every item: id, title, type, status, owner, points, commits, files touched |
| **Decision log** | ADR cards — context, decision, rejected alternatives, consequences |
| **Blockers & risks** | Severity, who owns it, what it stalls |
| **Timeline** | The sprint as a dated narrative |

Design notes: the page follows light and dark mode automatically and carries a manual toggle. Status is always **colour *plus* a written label** — never colour alone — and the commit chart ships a table view, so the dashboard stays readable for colour-blind readers and in print.

---

## 📐 Conventions

**Identifiers.** Sprints `S-14`. Features `F-141` (first digits echo the sprint). Decisions `ADR-021`, numbered globally and never reused — a superseded ADR keeps its number and gets `"status": "superseded"` with a pointer in `consequences`. Blockers `B-07`.

**Item statuses.** `planned` → `in-progress` → `review` → `shipped`, with `blocked` as an orthogonal state. Anything not finished when a sprint closes moves to the next sprint **as a new entry** — the old one stays where it was, marked honestly. Retroactively tidying a sprint to look complete destroys the only thing the tracker is for.

**Types.** `feature` · `fix` · `refactor` · `chore`. The split is what tells you, three sprints later, that 60% of "velocity" was interest payments.

**Dates.** ISO `YYYY-MM-DD`, always. Never "last Tuesday".

**Sprint order.** Newest first in the `sprints` array — `sprints[0]` is what the dashboard opens on.

---

## 🧩 Scaling it

**Long-running projects.** Past ~12 sprints the file gets heavy to diff. Archive: move closed sprints into `tracker/archive/2026-H1.html` (a copy of the same template with only those sprints in its data block) and keep the live file to the last few. The template is self-contained, so an archive is just another openable file.

**Multiple repositories.** One tracker per repository, each pointed at from its own `AGENTS.md`. A cross-repo roll-up is a separate file that concatenates their `sprints` arrays — the schema is designed so this is a copy-paste, not a merge.

**Review it in PRs.** Because the data is JSON inside the file, a sprint's changes show up as a readable diff. Reviewing the tracker diff alongside the code diff is the cheapest quality gate here: if an ADR's `alternatives` field is empty, the decision wasn't examined.

**Publishing.** The file is standalone HTML, so GitHub Pages, an S3 bucket, or an email attachment all work with zero adaptation.

---

## ⚠️ Failure modes to avoid

| Anti-pattern | Why it kills the tracker |
|---|---|
| Writing the sprint record at the end, from memory | The reasoning is already gone; you get a changelog, not a decision log |
| ADRs with no rejected alternatives | The most valuable field is the one you left blank |
| Editing the renderer or CSS per project | The template stops being a template; upgrades become merges |
| Quietly rewriting a past sprint to look better | The tracker's only asset is that it's true |
| Gitignoring the tracker | History that doesn't survive `git clone` isn't history |
| Tracking every commit as a "feature" | Signal drowns; use `type` honestly |

---

## FAQ

**Why one HTML file instead of a real app?**
Because the tracker has to survive being ignored for six months. No dependency, no build, no runtime means nothing to break, nothing to update, and nothing to install before you can read it. Double-click and it works — in 2030 too.

**Why JSON embedded in the HTML rather than a separate `data.json`?**
`file://` fetch is blocked by CORS in every modern browser, so a separate data file would force you to run a local server just to look at your own notes. Embedding keeps the double-click promise. The trade — one file to diff — is acceptable, since the renderer never changes and every diff line is data.

**Can I edit it by hand?**
Yes. It's JSON in a text file; edit the data block freely. Just leave everything above it alone.

**Does this replace Jira / Linear / a project tracker?**
No. Those coordinate people and plan future work. This records engineering history — including the reasoning that ticket systems structurally throw away. They answer *what's next*; this answers *why is it like this*.

---

*The reference implementation for [Chapter 18 — Sprint Tracking](../chapters/18-sprint-tracking.md) of [The AI Engineering Brain](../README.md).*
