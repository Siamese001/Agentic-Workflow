---
name: repo-main-merge-publish
description: Audit local branches/worktrees, merge approved work into main safely, and choose detached-worktree or ours-merge paths when C:\Git\Agentic-Workflow-FRESH has a dirty main checkout or stale preservation branches.
argument-hint: "[branch-or-mode]"
disable-model-invocation: true
user-invocable: false
allowed-tools:
  - Read
  - Grep
  - Bash
---

# Repo Main Merge Publish

Use this when:
- The task is to merge a branch into `main` and push `origin/main` in `C:\Git\Agentic-Workflow-FRESH`.
- The user asks to ensure local worktree branches are merged or to merge "all" local branches.
- You need a proven path for dirty-checkout-safe publish or archival branch containment.

Do not use this when:
- The task is feature implementation without a publication request.
- The repo is not `C:\Git\Agentic-Workflow-FRESH`.
- The branch state is ambiguous and the user has not approved a multi-step merge/push plan.

Inputs / context to gather first:
1. Confirm repo scope is `C:\Git\Agentic-Workflow-FRESH`.
2. Read the current git state:
   - `git status --short --branch`
   - `git worktree list --porcelain`
   - `git fetch origin`
   - `git rev-parse --short origin/main`
   - `git branch --merged origin/main`
   - `git branch --no-merged origin/main`
3. Identify whether `main` is dirty, whether the target branch is already checked out in another worktree, and whether the request covers one branch or all local branches.
4. For branch-containment requests, inspect conflict shape before choosing merge strategy.

Procedure:
1. If the request is multi-step or cross-branch, present a short plan first and wait for explicit approval before merging or pushing.
2. Audit topology before touching refs:
   - Use `git worktree list --porcelain` to enumerate checked-out worktrees.
   - Use `git branch --merged/--no-merged origin/main` to split already-contained branches from active ones after fetching.
   - Use `git cherry -v origin/main <branch>` only as diagnostic evidence; `-` rows do not satisfy closeout.
   - Treat "Merge all" literally; include preservation branches unless they are provably unsafe to replay.
3. Choose the execution surface:
   - If `main` is dirty, create or use a detached merge worktree rooted from current `origin/main`.
   - If `main` is clean and the merge target is not checked out elsewhere, merging in the main checkout is acceptable.
4. For active feature/worktree branches:
   - Validate merge shape with a quick diff or merge-tree check when useful.
   - Merge into `main`.
   - Run the smallest targeted regression that covers the changed surface.
5. For preservation or archival branches:
   - Attempt a normal merge only long enough to validate conflict shape.
   - If conflicts are broad and center on generated or governance-owned files, abort and switch to `git merge -s ours --no-ff --no-edit <branch>`.
   - Use an `ours` merge to record ancestry only after confirming the branch content is already represented or intentionally superseded.
6. Before push:
   - Fetch `origin` again if the workflow took time or if any earlier remote SHA is stale.
   - Ensure `origin/main` is an ancestor of `HEAD` or merge the new remote tip first.
   - Rerun the targeted verification gate; for broad repo publication, add a collection or smoke gate when available.
7. Push `HEAD:main`, then verify remote state with `git ls-remote origin refs/heads/main`.
8. Verify branch closeout by ancestry, not patch equivalence:
   - `git branch --no-merged origin/main` is empty or contains only explicitly retained branches.
   - For every branch being cleaned up: `git merge-base --is-ancestor <branch> origin/main` succeeds.
9. Report the merge commit(s), verification commands/results, and any bypassed-rule output from the remote push.

Efficiency plan:
1. Start with topology commands, not file-by-file branch exploration.
2. Reuse one detached merge worktree for the full publish path when the primary checkout is dirty.
3. Prefer the smallest verification selector that still covers the merged surface.
4. Stop normal merge investigation early when conflict files cluster in `.claude/hooks/*`, `docs/reports/adg/*`, `ops_scripts/ci/baselines/*`, or `tools/git/*`; that pattern already justifies an `ours` merge for archival containment.

Pitfalls and fixes:
- Symptom: edits land in the wrong checkout or worktree.
  Likely cause: tool path inheritance did not follow the intended worktree.
  Fix: patch by absolute path and re-check `git status --short --branch` in the target worktree before continuing.
- Symptom: `ModuleNotFoundError: No module named 'tools.archive'` appears during a merge verification gate.
  Likely cause: stale compatibility import in `tests/unit/tools/archive/test_archive_old_adg_sqlite_guard.py`.
  Fix: restore only the tiny compatibility surface the test imports, then `git add -f` because `tools/archive/` is ignored.
- Symptom: push would overwrite newer remote work.
  Likely cause: `origin/main` advanced during the local merge workflow.
  Fix: fetch again and merge the newer remote tip before pushing; do not force-push.
- Symptom: normal merge produces many conflicts across generated/governance files.
  Likely cause: stale preservation branch.
  Fix: abort the content merge and use `git merge -s ours --no-ff --no-edit <branch>` if the goal is branch containment.

Verification checklist:
- `git worktree list --porcelain` and `git branch --no-merged origin/main` match the intended post-merge state.
- Every branch deleted or declared done is exact-tip ancestor-contained in `origin/main`; patch-equivalence alone is not enough.
- Required targeted tests or collection gates passed.
- If `tools/archive/` was touched, the archive regression passed and the ignored path was force-added intentionally.
- `git ls-remote origin refs/heads/main` matches the local pushed `HEAD`.
- Report includes final commit SHA(s), verification command(s), and whether the remote reported bypassed required checks.

Minimal usage example:
- Merge one approved branch with dirty local `main`: audit topology, create detached merge worktree from `origin/main`, merge branch, run focused regression, refetch, push `HEAD:main`, confirm remote SHA.
- Merge "all" local branches: audit worktrees + merged state, merge active worktree branches normally, switch preservation branches with broad generated/governance conflicts to `-s ours --no-ff`, verify `git branch --no-merged origin/main` is empty after push, then clean up.
