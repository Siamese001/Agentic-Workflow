v1

## User Profile

The user is operating a local Codex memory system on Windows + PowerShell and is actively using it around `C:\Git\Agentic-Workflow-FRESH`. Recent work centers on repo analysis, branch/worktree publication, and memory/governance-driven execution. They repeatedly want agents to carry tasks through to the real git outcome when approval is clear, while still staying plan-first for riskier multi-branch ref updates. In repo analysis tasks they care about freshest evidence, not stale tracked reports, and they explicitly steer toward isolated worktrees when the checkout should stay untouched.

## User preferences

- When they ask to "create new worktree branch", default to an isolated worktree instead of editing the checked-out tree in place.
- For "latest ADG testing hotspots report" work, use the newest artifact snapshot and map hotspot files to the current `tests/` tree instead of relying on stale archived reports.
- When a git task is multi-step or cross-branch, keep it plan-first and wait for explicit approval before merges/pushes.
- Once they say "Merge to Main push origin main", treat that as approval to complete the branch publication workflow rather than stopping at analysis.
- When they say "Ensure all local worktree branches merged to main and pushed origin main", audit the full branch/worktree topology before changing refs.
- When they say "Merge all to main push origin", treat "all" literally and include archival/local preservation branches unless they are provably unsafe to record as merged.
- For approved actionable git tasks, they want the actual merge/push outcome, not only advisory guidance.

## General Tips

- Environment baseline: Windows + PowerShell; Agentic Workflow project memory lives under `C:\Git\Agentic-Workflow-FRESH\memory\`; the global Codex memory path `C:\Users\amita\.codex\memories` is for cross-project/user-level state only.
- For repo-wide merge/publish work in `C:\Git\Agentic-Workflow-FRESH`, start with `git worktree list --porcelain` plus `git branch --merged/--no-merged main`; search `MEMORY.md` for `branch containment`, `detached merge worktree`, or `git merge -s ours --no-edit`.
- Use `skills/repo-main-merge-publish/SKILL.md` first for branch-to-main publication requests in this repo.
- If `main` is dirty, prefer a detached merge worktree for publish steps; if `origin/main` advances mid-workflow, fetch again and merge the new remote tip before pushing.
- In `apps_rg` hotspot analysis, the useful fallback when `adg_sqlite` MCP is unavailable is local SQLite plus repo test inventory; search `MEMORY.md` for `adg_indexed_06152026_1043.sqlite`, `mv_hotspot_coverage_risk`, and `resolved_path`.
- Watch for stale verification failures that are outside the target surface; the recorded example was `ModuleNotFoundError: No module named 'tools.archive'`, fixed by a minimal compatibility shim plus `git add -f` because `tools/archive/` is ignored.

## What's in Memory

### C:\Git\Agentic-Workflow-FRESH

#### 2026-06-16

- merge all local branches to main and push origin: git worktree list --porcelain, git branch --no-merged main, work/apps-lic-w1-model-ssot, codex/preserve-local-main-20260614, git merge -s ours --no-edit
  - desc: Search this first for repo-wide branch/worktree audit, approved multi-branch merge-to-main execution, and archival branch containment in `cwd=C:\Git\Agentic-Workflow-FRESH`.
  - learnings: Audit topology before touching refs; clean worktree branches can merge normally, but broad generated/governance conflicts on a preservation branch justify `ours` merge for branch containment.

#### 2026-06-15

- apps_rg hotspot coverage gap analysis + merge to main: apps_rg, adg_indexed_06152026_1043.sqlite, mv_hotspot_coverage_risk, detached merge worktree, tools.archive, tests -k apps_rg --collect-only
  - desc: Covers both the latest `apps_rg` ADG hotspot/test-surface analysis and the follow-on branch publication flow in `cwd=C:\Git\Agentic-Workflow-FRESH`; use it for freshest-evidence routing or dirty-checkout-safe publish steps.
  - learnings: The freshest hotspot signal was the ADG SQLite snapshot, not older tracked markdown; publishing from a dirty checkout required a detached merge worktree plus a minimal archive compatibility shim.

### Older Memory Topics

#### C:\Git\Agentic-Workflow-FRESH

- git worktree merge/publish workflow skill: skills/repo-main-merge-publish/SKILL.md, branch containment, origin/main, detached merge worktree
  - desc: Reusable step-by-step procedure for this repo's branch-to-main publication workflow, including approval gate, topology audit, detached-worktree execution, archival `ours` merge, and final remote verification; applicable at `cwd=C:\Git\Agentic-Workflow-FRESH`.
