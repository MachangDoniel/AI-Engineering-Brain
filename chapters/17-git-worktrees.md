> [◀ Chapter 16](16-spec-driven-development.md) · [🏠 Home](../README.md) · [Chapter 18: Sprint Tracking ▶](18-sprint-tracking.md)

---

# Chapter 17 — Git Worktrees: Parallel Filesystems for Parallel Agents

> *"Version control was designed for one human switching between branches. Agents don't switch — they run at the same time. The working directory, not the model, becomes the bottleneck."*

---

# 17.1 Introduction

[Chapter 14](14-multi-agent-systems.md) argued that a single agent breaks down and that the answer is many agents working in parallel. [Chapter 15](15-virtual-organizations.md) scaled that into departments. Both chapters were about *coordination* — who does what, who reviews whom, how work is routed.

Neither answered a physical question: **where do those agents put their files?**

Three agents refactoring three modules of the same repository, in the same folder, is not a multi-agent system. It is a race condition with a git history attached. Agent A writes `auth.service.ts`, agent B reads it mid-write, agent C runs `git checkout` and pulls the floor out from under both. There is one index, one `HEAD`, and one set of files on disk — and none of them can represent three simultaneous truths.

The fix is not a better prompt or a smarter orchestrator. It is a git feature that has existed since 2015 and that almost nobody used, because until recently nobody needed it: **`git worktree`**, which gives one repository many working directories, each on its own branch, all sharing one history.

```text
Single working directory              Worktrees
─────────────────────────             ─────────────────────────
  repo/  ← agent A ⚡                   repo/main/       ← human, always clean
         ← agent B ⚡  collision        repo/agent-a/    ← agent A, branch a
         ← agent C ⚡                   repo/agent-b/    ← agent B, branch b
                                       repo/agent-c/    ← agent C, branch c
  one HEAD, one index                          ↑
  serialized or corrupted              one object DB, shared instantly
```

This chapter is the physical layer under Chapters 14 and 15. It is short on theory and long on mechanics, because the failure mode it prevents is mundane, expensive, and entirely avoidable.

---

# 17.2 Why One Working Directory Became the Bottleneck

Git's default workflow assumes a specific shape of work: one person, one task, one branch at a time. Switching tasks means `git stash`, `git checkout`, wait for the IDE to re-index, wait for the dev server to restart, wait for the build cache to warm up again. That cost was tolerable when a task took a day, because you paid it once a day.

Three things about AI-driven development make it intolerable.

* **Task starts became cheap; task slots did not.** You can plausibly begin four features in a morning, because an agent does the typing. But four features need four branches to exist *on disk at the same time*, and `git checkout` gives you one.
* **Review requires a reference.** Agent-written code has to be compared against something known-good — not just as text, but as *behavior*. That means the baseline must stay checked out and running while the candidate also runs. One directory cannot do this.
* **Disposal became routine.** When an agent takes a wrong turn, the correct response is to throw the work away and re-run it. In a single tree, "throw it away" means untangling a stash, resetting a dirty index, and hoping nothing untracked survived. It should be one command.

`git stash` is the tool people reach for, and it is the wrong one. Stash serializes work that is not serial. Worse, as §17.3 shows, the stash is *shared across worktrees* — it is repository state, not directory state — which makes it actively hazardous once parallel work begins.

The deeper point connects back to [Chapter 13](13-compound-engineering.md): compound engineering assumes each loop's output is preserved and built on. A workflow whose default move is "stash the previous attempt" leaks exactly the artifacts compounding depends on.

---

# 17.3 What a Worktree Actually Is

A worktree is a **checkout, not a copy**. The repository — objects, refs, config, remotes — exists once. Only the working files are duplicated.

```text
myrepo/                           ← "main worktree"
├── .git/
│   ├── objects/                  ← SHARED across all worktrees
│   ├── refs/                     ← SHARED
│   ├── config                    ← SHARED
│   └── worktrees/
│       └── feat-x/               ← per-worktree metadata
│           ├── HEAD              (which branch this tree is on)
│           ├── index             (this tree's staging area)
│           └── gitdir
└── src/

myrepo-feat-x/                    ← "linked worktree"
├── .git                          ← a FILE, not a directory:
│                                   "gitdir: /…/myrepo/.git/worktrees/feat-x"
└── src/
```

| Shared by every worktree | Private to each worktree |
|---|---|
| Objects — commits, trees, blobs | `HEAD` — the branch you're on |
| Branches and tags (`refs/heads`, `refs/tags`) | The index / staging area |
| Remotes and remote-tracking refs | The working files themselves |
| `.git/config` | `MERGE_HEAD`, `ORIG_HEAD`, rebase state |
| Hooks (`.git/hooks`) | Untracked and ignored files (`node_modules/`, `.env`, `build/`) |
| **The stash** (`refs/stash`) | `refs/bisect`, the `HEAD` reflog |

Two consequences deserve to be memorized, because both surprise people:

1. **Hooks are shared.** Install a pre-commit lint gate once and every agent's worktree inherits it. This is the cheapest governance mechanism in the whole multi-agent stack — see §17.11.
2. **Refs are shared.** Isolation is at the *working-file* level, not the ref level. `git reset --hard` or `git branch -D` executed in agent C's worktree can destroy agent A's branch. Filesystem isolation is not permission isolation.

### The safety rail

Git refuses to check out one branch in two worktrees:

```text
fatal: 'main' is already used by worktree at '/Users/you/code/nexuspay/main'
```

This is a feature. "Which directory owns this branch" stops being a convention you have to remember and becomes a fact git enforces. For a read-only second view of the same commit, `--detach` sidesteps it deliberately.

### The command surface

```bash
# The 90% case: new branch, based explicitly on origin/main
git worktree add ../feat-x -b feat/x origin/main

git worktree add ../hotfix hotfix/1234       # existing branch
git worktree add --detach ../peek v2.1.0     # read-only, at a tag
git worktree add --orphan ../docs gh-pages   # fresh orphan branch (git 2.42+)

git worktree list [--porcelain]              # --porcelain for scripts
git worktree remove ../feat-x                # refuses if dirty; --force overrides
git worktree move ../old ../new              # relocate, updating metadata
git worktree prune                           # forget trees you rm -rf'd
git worktree repair                          # fix pointers after moving folders
git worktree lock ../on-ssd --reason "external drive"
```

Base branches on `origin/main` **explicitly**, not on whatever `HEAD` happens to be. Independent bases produce independent diffs, which is what makes agent branches mergeable in any order (§17.9).

---

# 17.4 Layouts That Scale

### Sibling folders — start here

```text
~/code/
├── nexuspay/                 ← the clone; stays on main
├── nexuspay-qr-scanner/
└── nexuspay-payment-fix/
```

Zero setup. One rule: **never nest a worktree inside another worktree's working directory** — git will see it as untracked content of the parent branch.

### Bare-repo hub — for sustained parallel work

Here no directory is privileged; every worktree is a peer and all of them are disposable.

```text
~/code/nexuspay/
├── .bare/          ← the repository itself (bare)
├── .git            ← file: "gitdir: ./.bare"
├── main/           ← worktree on main
├── agent-01/
└── agent-02/
```

```bash
mkdir -p ~/code/nexuspay && cd ~/code/nexuspay
git clone --bare git@github.com:org/nexuspay.git .bare
echo "gitdir: ./.bare" > .git

# A bare clone sets no tracking refspec — without this, origin/main won't exist
git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
git fetch origin

git worktree add main main
```

The payoff is that `git worktree list` becomes the complete inventory of active work. In the sibling layout, one folder is structurally special — it can't be deleted, and it's stuck holding whatever branch it's on.

### Naming

Make the folder derivable from the branch, mechanically:

```text
feat/qr-scanner      →  feat-qr-scanner
agent/refactor-auth  →  agent-refactor-auth
```

This is not cosmetic. Port assignment (§17.7), cleanup scripts (§17.9), and agent reports ("I finished in `agent-refactor-auth`") all key off the mapping. An arbitrary naming scheme forces a lookup every time.

---

# 17.5 The Agent-per-Worktree Pattern

> **The discipline, in one line: one agent → one worktree → one branch → one pull request.**

```text
~/code/nexuspay/
├── main/                  ← human. Always clean. Always running. The reference.
├── agent-qr-scanner/      ← agent 1 → agent/qr-scanner
├── agent-payment-fix/     ← agent 2 → agent/payment-race
├── agent-api-migration/   ← agent 3 → agent/api-v2
└── integration/           ← where the combined result is tested (§17.9)
```

```bash
cd ~/code/nexuspay
git fetch origin

for task in qr-scanner payment-fix api-migration; do
  git worktree add "agent-$task" -b "agent/$task" origin/main
  (cd "agent-$task" && ../scripts/seed-worktree.sh)   # §17.6
done
```

Every agent starts from the *same* `origin/main` commit. That is what makes their diffs comparable and their conflicts meaningful: a conflict then represents a genuine semantic disagreement, not an artifact of mismatched bases.

### The contract each agent gets

This is [Chapter 16](16-spec-driven-development.md)'s idea applied to the environment rather than the feature — the boundary is specified before the work starts, not discovered afterward:

```text
You are working in ~/code/nexuspay/agent-qr-scanner on branch agent/qr-scanner.
- Commit your own work in this directory.
- Do NOT modify files outside this directory.
- Do NOT merge, rebase onto main, force-push, or delete branches.
- When done, report the branch name and stop.
```

Agents commit; **humans merge**. Merge is the review gate, and it is the last decision that should stay manual — it is where a mistake is both expensive and easy.

### Tooling support

Coding agents have started to build this in. Claude Code, for instance, can spawn a subagent with worktree isolation, which creates a throwaway worktree for the agent and discards it automatically if nothing changed. Use that for exploratory work; use explicit, named worktrees for work you intend to review and merge — the difference is whether you need the result to *survive*.

### Review, with both versions alive

```bash
git -C agent-qr-scanner log --oneline origin/main..HEAD   # what did it do?
git -C agent-qr-scanner diff origin/main --stat           # how much?

cd agent-qr-scanner && PORT=3001 pnpm dev                 # run it...
# ...while main/ is still serving :3000
```

That last line is the capability branch-switching cannot provide at any price: **the baseline and the candidate running simultaneously**, so review compares behavior rather than text. For agent-written code — which is fluent, plausible, and wrong in ways that read fine — that distinction is the whole game.

---

# 17.6 Bootstrapping: The Gitignored Gap

This is where most first attempts fail. A new worktree contains **tracked files only**. Everything gitignored is missing: `node_modules/`, `.env`, `vendor/`, `Pods/`, `.dart_tool/`, `build/`, `venv/`.

The instinct is to symlink a shared `node_modules`. Resist it — it holds until two branches disagree on a dependency version, or a native module is rebuilt for the wrong tree. Use a content-addressed package manager instead (pnpm's global store hard-links, giving the disk savings with correct per-tree resolution), and script the rest:

```bash
#!/usr/bin/env bash
# scripts/seed-worktree.sh — run once inside a fresh worktree
set -euo pipefail
MAIN="$(git worktree list --porcelain | awk '/^worktree /{print $2; exit}')"

for f in .env .env.local local.properties; do
  [ -f "$MAIN/$f" ] && [ ! -f "./$f" ] && cp "$MAIN/$f" "./$f"
done

[ -f package.json ]  && (command -v pnpm >/dev/null && pnpm install || npm ci)
[ -f pubspec.yaml ]  && flutter pub get
[ -f composer.json ] && composer install --no-interaction
[ -f Podfile ]       && pod install
```

| Stack | Missing after `worktree add` | Notes |
|---|---|---|
| Node / Next.js | `node_modules`, `.env.local` | pnpm makes this near-instant |
| Flutter | `.dart_tool`, `.packages` | pub cache is global — fast |
| Laravel / PHP | `vendor/`, `.env` | composer cache is global |
| Spring / Gradle / Maven | build dirs only | `~/.gradle`, `~/.m2` already shared |
| iOS | `Pods/`, DerivedData | SPM resolves from a shared cache; CocoaPods must reinstall per tree |
| Submodules | everything | `git submodule update --init --recursive` per worktree |

Seeding is a one-time script per repository. Skipping it is the single most common reason people conclude "worktrees don't work for our project."

---

# 17.7 Running Them All at Once

Isolating source code is half the job. Two instances of the same application will fight over port 3000, one database, one Docker network, and one build cache — producing failures that look like code bugs and are not.

| Contended resource | Isolation |
|---|---|
| HTTP port | `PORT=` derived per worktree (below) |
| Database | one per tree: `createdb nexuspay_$(basename $PWD)` |
| Docker Compose | `export COMPOSE_PROJECT_NAME="$(basename "$PWD")"` |
| Xcode | per-tree DerivedData path; separate simulator devices |
| Android | separate AVDs; `build/` is already per-tree |

`COMPOSE_PROJECT_NAME` deserves emphasis: without it, `docker compose up` in one worktree will stop and replace another worktree's containers, and the hour that follows will be spent blaming the agent.

Deterministic, collision-free ports from the folder name:

```bash
name="$(basename "$PWD")"
offset=$(( 0x$(printf '%s' "$name" | shasum | cut -c1-4) % 50 ))
echo $(( 3000 + offset ))
```

Or store it in git's per-worktree config, which exists precisely for this:

```bash
git config extensions.worktreeConfig true
git config --worktree app.port 3001
```

A practical limit: running four full stacks concurrently is real memory. Keep `main/` live permanently as the reference, run one candidate under a live server at a time, and review the rest by diff. Test suites are the exception — short-lived and, once ports and databases are isolated, genuinely parallel.

---

# 17.8 Fan-Out / Fan-In: Comparing Implementations

Worktrees enable a pattern that is impractical otherwise: give the same specification to several agents and compare the *implementations* rather than reasoning about which prompt might have been better.

```bash
for n in 1 2 3; do
  git worktree add "try-$n" -b "try/approach-$n" origin/main
done
# ...a different agent, model, or prompt in each...

git diff try/approach-1 try/approach-2 -- src/payments/
diff -ru try-1/src/payments try-2/src/payments
```

Keep the winner; `git worktree remove` the other two. The cost of two discarded attempts is one command each — which changes how willing you are to attempt something aggressive.

This is the [Chapter 16](16-spec-driven-development.md) loop with the verification step made concrete: one spec, three candidate implementations, one shared set of acceptance criteria, and a decision made by running all three against it. Without worktrees the comparison is sequential and lossy; with them it is simultaneous and direct.

---

# 17.9 Merging Back: The Integration Worktree

### The default path — pull request

```bash
cd ~/code/nexuspay/agent-qr-scanner
git fetch origin
git rebase origin/main          # conflicts resolved HERE, in isolation
pnpm test && pnpm build         # prove it before pushing
git push -u origin agent/qr-scanner
gh pr create --fill --base main
```

The rebase line carries more weight than it appears to. Conflict resolution happens inside the feature's own worktree while `main/` keeps running and every other agent keeps working. In the single-tree model, a difficult rebase blocks everything.

### Local fast-forward — solo, small, trusted

```bash
git -C agent-qr-scanner rebase origin/main
cd main
git pull --ff-only origin main
git merge --ff-only agent/qr-scanner
```

`--ff-only` is deliberate: if it fails, `main` moved and you should rebase again rather than manufacture a surprise merge commit.

### The integration worktree — several agents at once

Three independently correct branches can still combine into something broken. Both agents renamed the same helper. Both added a migration numbered `007`. Merging them into `main` one at a time discovers this *after* `main` is already broken.

```bash
git worktree add integration -b integration/2026-08-12 origin/main
cd integration && ../scripts/seed-worktree.sh

for b in agent/qr-scanner agent/payment-fix agent/api-migration; do
  git merge --no-ff "$b" || { echo "CONFLICT in $b — resolve here, not in main"; break; }
done

pnpm test && pnpm build && pnpm e2e     # do they work TOGETHER?

cd ../main && git merge --ff-only integration/2026-08-12 && git push origin main
cd .. && git worktree remove integration
```

This is the fan-in step [Chapter 14](14-multi-agent-systems.md) describes as the orchestrator's hardest job, given a physical location. The integration worktree is a disposable staging area whose only purpose is to answer *does the combination hold?* before the answer costs anything.

### Cleanup

```bash
git worktree remove agent-qr-scanner
git branch -d agent/qr-scanner            # -d refuses if unmerged — that's the net
git push origin --delete agent/qr-scanner
git worktree prune
```

Prefixing agent branches (`agent/…`) makes bulk cleanup mechanical and makes "which code has no human author yet" a `grep`.

---

# 17.10 Tooling: The GUI Gap

Most git GUIs were designed around the model worktrees replace — *one repository, one working copy, switch branches to move around*. The difference shows up sharply between two popular clients (versions checked on macOS, August 2026):

| Capability | **Fork 2.69** | **Sourcetree 4.2.14** |
|---|---|---|
| All worktrees of a repo in one view | ✅ dedicated sidebar section | ❌ not a concept in the UI |
| Create a worktree | ✅ menu + branch context menu | ❌ terminal only |
| Checkout a **remote** branch *as* a worktree | ✅ one action | ❌ |
| Remove worktree, with explicit "also delete folder" | ✅ | ❌ |
| Knows a linked worktree's `.git` is a *file* | ✅ | ⚠️ each worktree must be added as a separate, unrelated repository |

Sourcetree's binary references `core.worktree` only as a config key; there is no worktree UI in it. The workaround — bookmarking every worktree as its own repository — produces N disconnected entries with no indication they share a history, which discards the exact thing worktrees were adopted for: *the overview*.

Others, briefly: GitHub Desktop has no worktree support by design. VS Code has no worktree UI but works well anyway — open each worktree as a folder and you get an independent window, terminal, and language server per branch. Xcode is worktree-unaware but indifferent: a worktree is just another folder with a `.xcodeproj`. `lazygit` has a worktrees panel and makes a good terminal companion.

The division of labor that works in practice: **CLI for creating and destroying** (scriptable, agent-drivable, repeatable), **GUI for seeing and reviewing** (side-by-side diffs, line-level staging of an agent's partially-correct output). They operate on the same state, so mixing them is safe.

### And why not simply clone twice?

| | Second clone | Worktree |
|---|---|---|
| Disk | Full object database again | Working files only |
| `git fetch` | Once per clone | Once — every worktree sees it |
| Branch created in A | Invisible to B until push + fetch | Immediately visible |
| Same branch in both | Allowed → silent divergence | Blocked by git |
| Config, remotes, hooks | Duplicated; drift over time | Single source of truth |

For agent workflows the third row matters most: an agent commits in its worktree, and you can review or cherry-pick from yours with no synchronization step at all.

---

# 17.11 Git Governance for Agents

Because refs and hooks are shared (§17.3), the repository is a piece of **shared mutable state** in a multi-agent system — and [Chapter 14](14-multi-agent-systems.md)'s warnings about shared state apply directly.

Encode the boundary where agents will actually read it — `CLAUDE.md`, `AGENTS.md`, or the equivalent context file, which [Chapter 13](13-compound-engineering.md) already establishes as the durable home for this kind of rule:

```text
Forbidden without explicit human approval:
  git push --force        (any shared branch)
  git rebase / git merge  (onto main or develop)
  git reset --hard        (any branch but your own)
  git branch -D           (any branch you did not create)
  git worktree remove     (any worktree you did not create)
```

And enforce what can be enforced rather than asked. A `pre-commit` hook installed once in `.git/hooks` applies to every worktree automatically — lint gates, secret scanning, test runs, commit-message format. Shared hooks turn a policy document into a mechanism.

Then set the rhythm:

| Cadence | Action |
|---|---|
| Once per morning | `git fetch origin --prune` — one fetch serves every worktree |
| Per active branch, daily | `git rebase origin/main` in its own worktree |
| Before every PR | `git rebase -i origin/main` — squash 14 "wip" commits into a reviewable story |
| On merge | remove worktree, delete branch local and remote, `git worktree prune` |

That squash step is not fussiness. Agents produce many small commits — useful as rollback points during the work, actively harmful at review time, when forty commits titled "fix" defeat the human attention the merge gate exists to apply.

---

# 17.12 When NOT to Use Worktrees

* **Solo work on a single task.** One branch, one directory. Worktrees add folders and cognitive overhead you get nothing for.
* **Repositories with heavy, un-shareable setup.** If every tree needs a 20-minute `pod install` and 8 GB of Docker images, the bootstrap cost can exceed the switching cost you were avoiding. Fix the setup first (§17.6), then reconsider.
* **Teams that would treat them as long-lived.** A worktree that lives for three months is a second clone with extra steps — and it accumulates drift, stale dependencies, and disk. Worktrees are meant to be disposable.
* **Trivial or read-only inspection.** `git show`, `git diff`, or a `--detach` tree beat a full worktree for "what did this commit change?"
* **When the real problem is coordination, not filesystem contention.** Worktrees make parallel work *possible*; they do not decide what should run in parallel. If agents keep colliding semantically — same modules, same interfaces — the fix is task decomposition ([Chapter 14](14-multi-agent-systems.md)) and clearer specs ([Chapter 16](16-spec-driven-development.md)), not more directories.

---

# 17.13 How Worktrees Connect to the Rest of the Book

* **[Chapter 13 — Compound Engineering](13-compound-engineering.md):** the Plan/Work/Review/Compound loop needs each iteration's output preserved, not stashed. A worktree per attempt keeps every candidate inspectable until you decide what to keep.
* **[Chapter 14 — Multi-Agent Systems](14-multi-agent-systems.md):** worktrees are the physical substrate of parallel agents. Orchestration answers *who does what*; worktrees answer *where*. The integration worktree is fan-in with a filesystem address.
* **[Chapter 15 — Virtual Organizations](15-virtual-organizations.md):** departments running concurrently need branch and directory conventions the way a company needs an org chart. `git worktree list` becomes the roster of work in flight.
* **[Chapter 16 — Spec-Driven Development](16-spec-driven-development.md):** the fan-out pattern (§17.8) turns one spec into several implementations judged against shared acceptance criteria — verification made simultaneous rather than sequential.
* **[Chapter 11 — MCP & AI Coding Agents](11-mcp-and-ai-agents.md):** an agent's working directory is part of its context. Scoping an agent to a worktree scopes its file tools, its `git status`, and its test runs — isolation by construction rather than by instruction.
* **[Chapter 7 — Graphify](07-graphify.md):** each worktree is a distinct repository state, so a knowledge graph indexed per worktree can answer *what does this branch's architecture look like* — and diff it against `main`'s.

---

# 17.14 Key Takeaways

| Idea | Summary |
|------|---------|
| The bottleneck | Git assumes one human switching branches; agents run concurrently — the **working directory** becomes the constraint, not the model |
| What it is | A **checkout, not a copy** — many working directories, one object database, one set of refs |
| The rule | One agent → one worktree → one branch → one PR. Two agents in one folder is a race condition, not a MAS |
| Isolation is partial | Files are isolated; **refs, hooks, and the stash are shared** — `reset --hard` in one tree can destroy another's branch |
| `main/` is sacred | Always clean, always running — it is the reference the candidate is compared against, live and side by side |
| Bootstrap or fail | Gitignored deps are missing in a new tree; a seed script is what separates "works" from "worktrees don't work for us" |
| Isolate the runtime too | Ports, databases, and `COMPOSE_PROJECT_NAME` — or you will debug the collision as if it were a code bug |
| Merging | Rebase in the feature's own tree; combine agent branches in a disposable **integration worktree** before `main` ever sees them |
| Tooling | Fork treats worktrees as first-class; Sourcetree has no worktree UI at all — CLI to create and destroy, GUI to see and review |
| When not to | Solo single-task work, heavy per-tree setup, long-lived trees, or when the real problem is decomposition rather than disk |

---

# 17.15 References

* Git documentation, *[git-worktree](https://git-scm.com/docs/git-worktree)* — the authoritative reference; note `--orphan` (2.42+), `repair` (2.30+), `move`/`remove`/`lock` (2.17+)
* Git documentation, *[gitrepository-layout](https://git-scm.com/docs/gitrepository-layout)* — what lives in `.git/worktrees/`, and what is common vs. per-worktree
* Git documentation, *[git-config](https://git-scm.com/docs/git-config)* — `extensions.worktreeConfig` and `git config --worktree`
* *[Fork](https://git-fork.com)* — git client with first-class worktree support (sidebar, create, checkout-as, remove)
* *[pnpm](https://pnpm.io)* — content-addressed store; the practical answer to per-worktree `node_modules`
* Anthropic, *[Claude Code documentation](https://docs.claude.com/en/docs/claude-code)* — agent isolation, subagents, and `CLAUDE.md` conventions

---

### Author's Note

Worktrees are a ten-year-old feature that spent most of that decade as trivia. What changed is not git — it is that the assumption underneath the default workflow, *one person doing one thing at a time*, stopped being true. Almost everything in this chapter is unglamorous: copy the `.env` file, set `COMPOSE_PROJECT_NAME`, don't let the agent run `reset --hard`. But the unglamorous layer is where multi-agent development actually fails. Chapters 14 and 15 describe agents that collaborate; this chapter is about making sure they are not silently overwriting each other's files while they do it. Get the substrate right and the orchestration ideas become implementable. Get it wrong and no amount of orchestration will save you — you will simply have a very sophisticated way of producing merge conflicts.

---

**End of Chapter 17**

---

> [◀ Chapter 16: Spec-Driven Development](16-spec-driven-development.md) · [🏠 Home](../README.md) · [Chapter 18: Sprint Tracking ▶](18-sprint-tracking.md)
