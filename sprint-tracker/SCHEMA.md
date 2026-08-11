# Tracker data contract

Everything the dashboard renders lives in one JSON object, inside
`<script type="application/json" id="tracker-data">` at the bottom of
`tracker/index.html`. **This block is the only part of the file that is ever edited.**

Rules that hold everywhere:

- Dates are ISO `YYYY-MM-DD`. No relative dates, ever.
- Every field marked *optional* may be omitted; the dashboard renders `—` or hides the row. **Omit rather than guess** — a fabricated metric is worse than a missing one.
- `sprints` is ordered **newest first**. `sprints[0]` is what the dashboard opens on.
- The JSON must stay valid. After editing, verify:

```bash
python3 -c "import json;h=open('docs/tracker/index.html').read();json.loads(h.split('id=\"tracker-data\">')[-1].split('</script>')[0]);print('tracker JSON valid')"
```

---

## Root

```json
{ "project": { … }, "sprints": [ … ] }
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `project` | object | yes | Header identity — see below |
| `sprints` | array\<Sprint\> | yes | Newest first. `[]` is valid and renders an empty dashboard |

## `project`

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | Rendered as `<name> — Sprint Tracker` |
| `repo` | string | optional | Display only, e.g. `github.com/acme/nexuspay` |
| `owner` | string | optional | Person or team accountable |
| `stack` | array\<string\> | optional | Rendered as chips, e.g. `["Flutter", "Spring Boot"]` |
| `updated` | string (date) | optional | **Set this on every write.** Shown in the header and footer |

## `Sprint`

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | `S-14` |
| `name` | string | yes | Short theme, not a sentence — "Merchant Onboarding" |
| `goal` | string | yes | One or two sentences: the outcome, ideally with a target |
| `status` | enum | yes | `active` · `complete` · `planned` |
| `start` / `end` | string (date) | yes | Planned boundaries; leave `end` as planned even if work overruns |
| `metrics` | object | optional | See below |
| `commitActivity` | array\<{date, count}\> | optional | One entry per day worked; include zero-commit days for an honest rhythm |
| `features` | array\<Feature\> | optional | Work items — see below |
| `decisions` | array\<Decision\> | optional | ADRs — see below |
| `blockers` | array\<Blocker\> | optional | |
| `timeline` | array\<Event\> | optional | |

### `Sprint.metrics`

All optional, all integers except `coverage`. Derive them from the repository — never estimate.

| Field | Meaning | Typical source |
|---|---|---|
| `commits` | Commits in the sprint window | `git log --since=… --until=… --oneline \| wc -l` |
| `prsMerged` | PRs merged in the window | `gh pr list --state merged --search "merged:2026-08-03..2026-08-16" \| wc -l` |
| `filesChanged` | Distinct files touched | `git diff --shortstat <base> HEAD` |
| `linesAdded` / `linesRemoved` | Insertions / deletions | same `--shortstat` |
| `testsAdded` | Net new test cases | test-runner count delta |
| `coverage` | Percentage, `0`–`100` | coverage report at sprint close |

Points aren't a metric field — the dashboard sums `points` across `features`.

### `Feature` (any work item: feature, fix, refactor, chore)

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | `F-141` — first digits echo the sprint |
| `title` | string | yes | Imperative and concrete: "Merchant self-registration flow" |
| `type` | enum | yes | `feature` · `fix` · `refactor` · `chore` |
| `status` | enum | yes | `planned` · `in-progress` · `review` · `shipped` · `blocked` |
| `owner` | string | optional | |
| `points` | number | optional | Whatever scale you already use |
| `commits` | number | optional | Commits attributable to this item |
| `started` / `completed` | string (date) | optional | `completed` only when `status` is `shipped` |
| `notes` | string | optional | One line — the *how*, or why it's stuck |
| `files` | array\<string\> | optional | Directories are better than long file lists: `lib/features/kyc/` |

Unfinished at sprint close → create a **new** entry in the next sprint. Never retro-edit the old one.

### `Decision` (ADR)

The highest-value object in the file.

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | `ADR-021`. Globally numbered, never reused |
| `date` | string (date) | yes | When it was taken, not when it was written up |
| `status` | enum | yes | `proposed` · `accepted` · `superseded` |
| `title` | string | yes | State the decision, not the topic: "Persist onboarding drafts server-side" |
| `context` | string | yes | The forces — the measurement, constraint, or failure that made a choice necessary |
| `decision` | string | yes | What was chosen, in the active voice |
| `alternatives` | array\<string\> | **strongly expected** | **What was rejected and why.** This is the field that pays for the whole system |
| `consequences` | string | yes | What this costs, what it now constrains, what to watch. For `superseded`, name the ADR that replaced it |

An ADR with an empty `alternatives` array is a signal the decision wasn't examined — treat it as a review finding, not a formatting nit.

### `Blocker`

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | `B-07` |
| `title` | string | yes | |
| `severity` | enum | yes | `warning` · `serious` · `critical` |
| `raised` | string (date) | yes | |
| `owner` | string | optional | Who unblocks it — often outside the team |
| `status` | enum | yes | `open` · `resolved` |
| `note` | string | optional | Name the item it stalls: "F-144 stalled at 3 commits" |

Open blockers roll into the all-time KPI tile, so resolve them honestly.

### `Event` (timeline)

| Field | Type | Required | Notes |
|---|---|---|---|
| `date` | string (date) | yes | |
| `type` | string | yes | `sprint` · `feature` · `decision` · `release` · `blocker` · `note` |
| `text` | string | yes | One sentence, past tense, specific — include the number that moved |

---

## Minimal valid document

```json
{
  "project": { "name": "Your Project", "updated": "2026-08-12" },
  "sprints": []
}
```

## Minimal useful sprint

```json
{
  "id": "S-01",
  "name": "Foundations",
  "goal": "Stand up auth and the first end-to-end request path.",
  "status": "active",
  "start": "2026-08-12",
  "end": "2026-08-25",
  "features": [
    { "id": "F-011", "title": "Email + password auth", "type": "feature", "status": "in-progress" }
  ],
  "decisions": [],
  "blockers": [],
  "timeline": [
    { "date": "2026-08-12", "type": "sprint", "text": "Sprint 1 opened." }
  ]
}
```
