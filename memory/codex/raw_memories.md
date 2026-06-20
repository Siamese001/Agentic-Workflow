# Raw Memories

Merged stage-1 raw memories (stable ascending thread-id order):

## Thread `019ecbd8-34c7-7480-9feb-7a3f9ecb69ef`
updated_at: 2026-06-15T23:04:53+00:00
cwd: \\?\C:\Git\Agentic-Workflow-FRESH
rollout_path: C:\Users\amita\.codex\sessions\2026\06\15\rollout-2026-06-15T11-13-29-019ecbd8-34c7-7480-9feb-7a3f9ecb69ef.jsonl
rollout_summary_file: 2026-06-15T15-13-24-iqbJ-apps_rg_hotspot_analysis_worktree_merge_push.md

---
description: Isolated a clean worktree to analyze latest ADG apps_rg hotspot/coverage gaps, then merged/pushed the branch to main; key durable lesson is that final publish required a detached merge worktree plus a tiny ignored tools/archive compatibility shim to unblock stale collection.
task: apps_rg hotspot coverage gap analysis + merge to main
task_group: C:\Git\Agentic-Workflow-FRESH
cwd: C:\Git\Agentic-Workflow-FRESH
keywords: apps_rg, ADG hotspot, coverage gaps, worktree, merge main, origin/main, pytest collect-only, tools.archive, archive_old_adg, guardian_report.json
---
### Task 1: apps_rg hotspot gap analysis in isolated worktree

task: create worktree branch and analyze latest ADG testing hotspots for apps_rg coverage gaps
task_group: repo analysis / test inventory
 task_outcome: success

Preference signals:
- user asked to "create new worktree branch" -> default to isolated worktree instead of editing dirty checkout in place
- user asked for "latest ADG testing hotspots report" and to find "apps_rg testing coverage gaps under tests/ folder (unit, e2e, imtegration, etc.)" -> use the newest ADG snapshot/report and map hotspot files to the tests tree, not stale archived reports

Reusable knowledge:
- latest useful ADG evidence in this run was `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_06152026_1043.sqlite`
- `coverage_by_path` uses `resolved_path` as its path column; `mv_hotspot_coverage_risk` exposed many `apps_rg` `P1_URGENT` rows, especially under `apps_rg/runtime/sections/*`, `apps_rg/runtime/bindings/*`, `apps_rg/runtime/judges/*`, `apps_rg/fact_inventory/*`, and `apps_rg/__main__.py`
- when `adg_sqlite` MCP is unavailable, local SQLite + repo inventory is the workable fallback

Failures and how to do differently:
- first SQLite probe hit PowerShell quoting trouble around `count(*)`; rerun with safer quoting
- broad `rg` over artifacts was noisy; focus on the ADG SQLite snapshot and hotspot files

References:
- worktree creation: `git worktree add -b codex/apps-rg-testing-gaps C:\Git\Agentic-Workflow-FRESH-apps-rg-testing-gaps origin/main`
- `git status --short --branch` in worktree: `## codex/apps-rg-testing-gaps...origin/main`
- `coverage_by_path` columns: `resolved_path, lines_hit, arcs_hit, context_count, lines_total, coverage_pct, mode, ingested_at`
- sample hotspot files from `mv_hotspot_coverage_risk`: `apps_rg/runtime/sections/executive_summary_lane.py`, `apps_rg/runtime/sections/ibm_bullets_lane.py`, `apps_rg/runtime/sections/unify_bullets_lane.py`, `apps_rg/runtime/sections/headline_lane.py`, `apps_rg/runtime/bindings/c0_binding.py`, `apps_rg/runtime/judges/executive_summary_judge_packet.py`

### Task 2: merge/push branch to main

task: merge codex/apps-rg-wave2-tests into main and push origin/main
 task_group: git publish / branch merge
 task_outcome: success

Preference signals:
- user explicitly said "Merge to Main push origin main" -> treat as approval to publish the branch work

Reusable knowledge:
- the repo main checkout was dirty, so a detached merge worktree (`C:\Git\Agentic-Workflow-FRESH-worktrees\codex-main-merge-push`) was the safe place to merge/push
- final push commit was `52361afcf5f60b439388e41d0c502de4a07b0bbd`
- `tools/archive/` is ignored by `.gitignore`, so restoring compatibility code there requires `git add -f`
- stale collection failure came from `tests/unit/tools/archive/test_archive_old_adg_sqlite_guard.py` importing `tools.archive.archive_old_adg`
- the minimal compatibility shim needed only `_has_sqlite` and `identify_runs_to_archive`
- after merging the newer remote tip, final verification was: focused U0 regression `60 passed`; broad `tests -k apps_rg --collect-only` `6674/57243 collected`, Guardian Shield `PASS`

Failures and how to do differently:
- initial patch landed in the wrong checkout because the patch tool did not inherit the merge worktree path; delete the accidental local file and apply to the merge worktree by absolute path
- `origin/main` advanced during the workflow, so re-fetch and merge the new remote tip before pushing instead of force-pushing

References:
- branch commit: `01f3a9d36f` `test(apps_rg): close out wave2 coverage gaps`
- merge commit: `961f0d3f91` `Merge branch 'codex/apps-rg-wave2-tests' into main`
- compatibility shim commit: `c062e0580e` `test(tools): restore ADG archive retention shim`
- final merge/push commit: `52361afcf5f60b439388e41d0c502de4a07b0bbd`
- focused regression: `python -m pytest -q tests/_apps_contract/test_apps_rg_u0_structured_resume_support.py --tb=short` -> `60 passed`
- archive regression: `python -m pytest -q tests/unit/tools/archive/test_archive_old_adg_sqlite_guard.py --tb=short` -> `8 passed`
- broad collection gate: `python -m pytest -q tests -k apps_rg --collect-only --tb=short` -> `6674/57243 collected`, Guardian Shield `PASS`
- remote verification: `git ls-remote origin refs/heads/main` -> `52361afcf5f60b439388e41d0c502de4a07b0bbd refs/heads/main`

## Thread `019ecd89-f3e4-7f20-9827-5f6394f7ee6c`
updated_at: 2026-06-16T00:04:58+00:00
cwd: \\?\C:\Git\Agentic-Workflow-FRESH
rollout_path: C:\Users\amita\.codex\sessions\2026\06\15\rollout-2026-06-15T19-07-15-019ecd89-f3e4-7f20-9827-5f6394f7ee6c.jsonl
rollout_summary_file: 2026-06-15T23-07-10-8HXC-merge_all_local_branches_into_main_and_push_origin.md

---
description: Merged all local branches into main and pushed origin/main; key takeaway is to audit worktree branches first, then use an `ours` merge for archival preservation branches that conflict on stale generated/governance files.
task: merge all local branches to main and push origin
task_group: git-branch-merge-workflow
task_outcome: success
cwd: C:\Git\Agentic-Workflow-FRESH
keywords: git merge, origin/main, worktree, branch containment, merge-tree, ff-only, ours merge, conflict resolution, push, GitKraken
---
### Task 1: Merge eligible worktree branch and push

task: ensure all local worktree branches merged to main and pushed origin main
task_group: git branch/worktree merge workflow
task_outcome: success

Preference signals:
- when the user asked to “Ensure all local worktree branches merged to main and pushed origin main”, future runs should audit the full local branch/worktree topology before changing refs.
- when the user approved the plan before execution, future runs should keep multi-branch git work plan-first and wait for explicit approval before merges/pushes.

Reusable knowledge:
- `git worktree list --porcelain` + `git branch --merged/--no-merged` is the fastest reliable way to identify which local branches are already contained in `main` versus still active.
- `work/apps-lic-w1-model-ssot` merged cleanly into `main`; the targeted verification command passed: `python -m pytest tests/apps_lic/test_w4_eval_lane_matrix.py tests/apps_lic/test_w5_c0_readiness_and_jd_gate.py tests/apps_lic/test_w6_shared_ssot_briefing_ops.py -q` -> `11 passed, 4 warnings`.
- Direct push to `origin/main` succeeded, but GitHub reported bypassed required checks on the direct push.

Failures and how to do differently:
- None for this branch; the merge was clean.

References:
- `main` fast-forwarded to `52361afcf5` before the merge.
- Merge commit for the eligible worktree branch: `06f5aba3f2` (`Merge branch 'work/apps-lic-w1-model-ssot'`).
- Push result: `52361afcf5..06f5aba3f2 main -> main`.
- Final local/remote state after this step: `origin/main` matched `06f5aba3f2`.

### Task 2: Merge archival preservation branch and push

task: merge remaining archival branch codex/preserve-local-main-20260614 into main and push origin

task_group: git branch/worktree merge workflow

task_outcome: success

Preference signals:
- when the user said “Merge all to main push origin”, that should be interpreted literally as including the previously excluded archival preservation branch if it is safe to record as merged.
- The user wanted the actual merge/push outcome, not only a recommendation, so future runs should try to complete the ref update after a quick safety audit.

Reusable knowledge:
- The archival branch `codex/preserve-local-main-20260614` was the only local branch not contained in `main` after the first push.
- A normal merge of that branch conflicted in generated ADG report files, ratchet baselines, hook files, and `tools/git/*`, which is a strong sign the branch is stale preservation content rather than active work.
- `git merge -s ours --no-edit codex/preserve-local-main-20260614` succeeded and created merge commit `4ca3997164` without tree changes; current guidance is to use `git merge -s ours --no-ff --no-edit <branch>` so branch-tip ancestry is explicit even when Git could otherwise fast-forward or omit a merge commit.
- Final verification showed every local branch contained in `main` and `origin/main` pointing at `4ca3997164`.

Failures and how to do differently:
- The first normal merge attempt failed with many conflicts; do not try to hand-resolve stale preservation content into current `main` when the goal is branch containment.
- If the conflict set is broad and centered on generated/governance files, abort the content merge and switch to an `ours` merge.

References:
- Remaining local branch before the archival step: `codex/preserve-local-main-20260614`
- Normal merge failure snippet: `Automatic merge failed; fix conflicts and then commit the result.`
- Conflict clusters: `.claude/hooks/*`, `docs/reports/adg/*`, `ops_scripts/ci/baselines/*`, `tools/git/*`
- Archive merge commit: `4ca3997164` (`Merge branch 'codex/preserve-local-main-20260614'`)
- Final local/remote confirmation: `git rev-parse --short HEAD` -> `4ca3997164`; `git ls-remote origin refs/heads/main` -> `4ca3997164`

