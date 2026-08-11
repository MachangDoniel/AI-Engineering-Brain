# The `AGENTS.md` block

Paste this into your project's `AGENTS.md` (or `CLAUDE.md`), adjusting the path on the
first line. This block is what turns the tracker from a file you'd have to remember into
something the agent maintains on its own.

Keep it verbatim otherwise — the specificity is the point. "Keep the tracker updated" is
an instruction agents drift away from; a named path, named triggers, and a named
forbidden region are ones they follow.

---

```markdown
## Sprint tracker — maintain this

**Tracker file:** `docs/tracker/index.html`
**Data contract:** the `<script type="application/json" id="tracker-data">` block at the
bottom of that file. Edit **only** that block — never the markup, CSS, or renderer above it.

Keep this file current as a normal part of doing the work. Do not wait to be asked, and do
not batch it up at the end of a sprint: the reasoning behind a decision is available for
about an hour, and reconstructing it later produces a changelog, not a decision log.

### Write to the tracker when

| Trigger | Action |
|---|---|
| A sprint or work cycle begins | Append a new entry to the **front** of `sprints[]` — id, name, goal, dates, `status: "active"`, and the committed items as `planned` features |
| Work on an item starts | Set that feature to `in-progress` and fill `started` |
| An item ships | Set `shipped`, fill `completed`, its commit count, and the directories touched |
| **A non-obvious technical decision is taken** | Append a Decision (ADR) — see the rule below |
| Something becomes blocked | Append a Blocker with severity, owner, and the item it stalls; set that feature to `blocked` |
| A notable event occurs | Append a timeline entry — release, incident, coverage move, scope change |
| A sprint closes | Reconcile metrics from git, set `status: "complete"`, add a closing timeline entry |

Set `project.updated` to today's date on **every** write.

### The decision rule

A decision goes in the log when a reasonable engineer could have chosen otherwise —
a library choice, a data-model shape, a caching strategy, a fix that treats a cause
rather than a symptom, anything traded off against performance, cost, or complexity.

Every ADR records **`alternatives`: what was rejected and why.** That field is the reason
this system exists; everything else can be reconstructed from git, and that cannot. An ADR
without rejected alternatives is incomplete — go back and fill it in.

Never delete or rewrite a past decision. A reversal is a **new** ADR, and the old one is
marked `"status": "superseded"` with a pointer to its replacement in `consequences`.

### Metrics come from the repository

Derive `commits`, `filesChanged`, `linesAdded`, `linesRemoved` and `prsMerged` from git for
the sprint window — do not estimate them. If a number can't be derived, omit the field;
the dashboard renders a dash. Never invent a metric to fill a gap.

### Honesty rules

- Work that didn't finish stays recorded as unfinished. Carry it into the next sprint as a
  **new** entry; never retro-edit a past sprint to look complete.
- Use `type` truthfully (`feature` · `fix` · `refactor` · `chore`). The split is what later
  reveals how much of a sprint was interest payments.
- Dates are ISO `YYYY-MM-DD`, always.

### After editing

Confirm the JSON still parses before considering the change done:

    python3 -c "import json;h=open('docs/tracker/index.html').read();json.loads(h.split('id=\"tracker-data\">')[-1].split('</script>')[0]);print('tracker JSON valid')"
```

---

## Optional: enforce it with a hook

The `AGENTS.md` block is an instruction — followed reliably, but still an instruction. If
you want the JSON validated mechanically on every write, add a `PostToolUse` hook in
`.claude/settings.json` that runs the parse check above and fails loudly on invalid JSON.
Ask your agent to "add a PostToolUse hook validating the tracker JSON" — it will wire the
matcher and command for you.
