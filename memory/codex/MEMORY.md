# Task Group: Agentic-Workflow-FRESH git worktree merge and publish workflows

scope: Safe branch-to-main publication, local branch/worktree audit, and archival-branch containment in `C:\Git\Agentic-Workflow-FRESH`; use for merge/push requests, not for feature implementation details.
applies_to: cwd=C:\Git\Agentic-Workflow-FRESH; reuse_rule=reuse for this repo's git publication workflows, especially when `main` may be dirty, worktrees exist, or local preservation branches need containment

## Task 1: merge `codex/apps-rg-wave2-tests` into `main` and push `origin/main`, success

### rollout_summary_files

- rollout_summaries/2026-06-15T15-13-24-iqbJ-apps_rg_hotspot_analysis_worktree_merge_push.md (cwd=\\?\C:\Git\Agentic-Workflow-FRESH, rollout_path=C:\Users\amita\.codex\sessions\2026\06\15\rollout-2026-06-15T11-13-29-019ecbd8-34c7-7480-9feb-7a3f9ecb69ef.jsonl, updated_at=2026-06-15T23:04:53+00:00, thread_id=019ecbd8-34c7-7480-9feb-7a3f9ecb69ef, detached merge worktree + archive shim unblocked final push)

### keywords

- codex/apps-rg-wave2-tests, detached merge worktree, tools.archive, archive_old_adg, git add -f, tests -k apps_rg --collect-only, Guardian Shield PASS, origin/main

- Related skill: skills/repo-main-merge-publish/SKILL.md

## Task 2: ensure all local worktree branches merged to `main` and pushed, success

### rollout_summary_files

- rollout_summaries/2026-06-15T23-07-10-8HXC-merge_all_local_branches_into_main_and_push_origin.md (cwd=\\?\C:\Git\Agentic-Workflow-FRESH, rollout_path=C:\Users\amita\.codex\sessions\2026\06\15\rollout-2026-06-15T19-07-15-019ecd89-f3e4-7f20-9827-5f6394f7ee6c.jsonl, updated_at=2026-06-16T00:04:58+00:00, thread_id=019ecd89-f3e4-7f20-9827-5f6394f7ee6c, worktree-branch audit + clean merge path)

### keywords

- git worktree list --porcelain, git branch --merged, git branch --no-merged, work/apps-lic-w1-model-ssot, merge-tree, origin/main, bypassed rule violations

- Related skill: skills/repo-main-merge-publish/SKILL.md

## Task 3: merge archival preservation branch with `ours` and push, success

### rollout_summary_files

- rollout_summaries/2026-06-15T23-07-10-8HXC-merge_all_local_branches_into_main_and_push_origin.md (cwd=\\?\C:\Git\Agentic-Workflow-FRESH, rollout_path=C:\Users\amita\.codex\sessions\2026\06\15\rollout-2026-06-15T19-07-15-019ecd89-f3e4-7f20-9827-5f6394f7ee6c.jsonl, updated_at=2026-06-16T00:04:58+00:00, thread_id=019ecd89-f3e4-7f20-9827-5f6394f7ee6c, stale preservation branch recorded as merged without replaying tree content)

### keywords

- codex/preserve-local-main-20260614, git merge -s ours --no-ff, branch containment, generated ADG reports, ops_scripts/ci/baselines, tools/git, Automatic merge failed

- Related skill: skills/repo-main-merge-publish/SKILL.md

## User preferences

- when the user asks to "Merge to Main push origin main" after analysis, treat that as approval to publish the branch work instead of stopping at design discussion [Task 1]
- when the user asks to "Ensure all local worktree branches merged to main and pushed origin main", audit the full local branch/worktree topology before changing refs [Task 2]
- when the git task is multi-step or cross-branch, keep it plan-first and wait for explicit approval before merges/pushes [Task 2]
- when the user follows with "Merge all to main push origin", treat "all" literally and include archival/local preservation branches unless they are provably unsafe to record as merged [Task 3]
- when the task is actionable and approved, the user wants the actual merge/push outcome, not only a recommendation [Task 2][Task 3]

## Reusable knowledge

- `git worktree list --porcelain` plus `git branch --merged/--no-merged` is the fastest reliable way in this repo to separate active worktree branches from already-contained or archival local branches [Task 2]
- if the main checkout is dirty, a detached merge worktree such as `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-main-merge-push` is the safe place to merge and push without disturbing local changes [Task 1]
- `origin/main` can advance during a merge workflow; the safe publish path is fetch remote main, ensure it is an ancestor of `HEAD`, rerun the focused regression / collection gate, then push `HEAD:main` [Task 1]
- `tools/archive/` is ignored by `.gitignore`, so restoring compatibility code there requires `git add -f`; the stale regression here expected `tools.archive.archive_old_adg` with `_has_sqlite` and `identify_runs_to_archive` [Task 1]
- `work/apps-lic-w1-model-ssot` merged cleanly and the targeted verification selector was `python -m pytest tests/apps_lic/test_w4_eval_lane_matrix.py tests/apps_lic/test_w5_c0_readiness_and_jd_gate.py tests/apps_lic/test_w6_shared_ssot_briefing_ops.py -q` -> `11 passed, 4 warnings` [Task 2]
- a direct push to `origin/main` can succeed while GitHub reports "Bypassed rule violations for refs/heads/main" and "3 of 3 required status checks are expected"; preserve that signal in rollout reporting instead of assuming branch protections enforced the push [Task 2]
- when an archival/preservation branch conflicts broadly in generated/governance-owned surfaces such as `.codex/hooks/*`, `docs/reports/adg/*`, `ops_scripts/ci/baselines/*`, and `tools/git/*`, treat it as branch-containment work rather than content replay [Task 3]
- `git merge -s ours --no-ff --no-edit <branch>` is the current pattern when the goal is to mark stale preservation content as merged while preserving current `main`; the older `codex/preserve-local-main-20260614` run created merge commit `4ca3997164` with no tree changes [Task 3]

## Failures and how to do differently

- symptom: patch landed in the wrong checkout during merge-worktree work -> cause: the patch tool did not inherit the merge worktree path -> fix: delete the accidental file and apply the patch by absolute path to the intended worktree [Task 1]
- symptom: broad `apps_rg` collection failed with `ModuleNotFoundError: No module named 'tools.archive'` from `tests/unit/tools/archive/test_archive_old_adg_sqlite_guard.py` -> cause: stale compatibility import, not an apps_rg product regression -> fix: restore only the tiny compatibility surface the test imports, rerun the archive regression, then rerun the collection gate [Task 1]
- symptom: normal merge of a preservation branch explodes into many conflicts -> cause: stale archival content replaying old generated/governance files -> fix: abort the content merge and switch to `git merge -s ours --no-ff --no-edit` when the goal is branch containment [Task 3]
- symptom: remote main moved after the initial merge stack -> cause: `origin/main` advanced while the local merge workflow was in progress -> fix: fetch again and merge the new remote tip before pushing instead of force-pushing [Task 1]

# Task Group: Agentic-Workflow-FRESH apps_rg ADG hotspot coverage-gap analysis

scope: Finding the latest `apps_rg` hotspot evidence and mapping it to current repo test surface; use for repo analysis / test inventory questions, not for publishing workflow steps.
applies_to: cwd=C:\Git\Agentic-Workflow-FRESH; reuse_rule=reuse for `apps_rg` hotspot or test-gap analysis in this repo when ADG artifacts and `tests/` inventory are the evidence source

## Task 1: create isolated worktree and analyze latest `apps_rg` hotspot evidence, success

### rollout_summary_files

- rollout_summaries/2026-06-15T15-13-24-iqbJ-apps_rg_hotspot_analysis_worktree_merge_push.md (cwd=\\?\C:\Git\Agentic-Workflow-FRESH, rollout_path=C:\Users\amita\.codex\sessions\2026\06\15\rollout-2026-06-15T11-13-29-019ecbd8-34c7-7480-9feb-7a3f9ecb69ef.jsonl, updated_at=2026-06-15T23:04:53+00:00, thread_id=019ecbd8-34c7-7480-9feb-7a3f9ecb69ef, newest ADG SQLite snapshot was more useful than stale tracked hotspot markdown)

### keywords

- apps_rg, latest ADG testing hotspots report, adg_indexed_06152026_1043.sqlite, mv_hotspot_coverage_risk, coverage_by_path, resolved_path, tests/apps_rg, tests/_apps_contract, create new worktree branch

## User preferences

- when the user asks to "create new worktree branch" before analysis, default to an isolated worktree instead of editing the checked-out tree in place [Task 1]
- when the user asks for the "latest ADG testing hotspots report" and to find "`apps_rg` testing coverage gaps under `tests/` folder (unit, e2e, imtegration, etc.)", use the newest ADG snapshot/report and map hotspot files to the `tests/` tree rather than relying on stale archived reports [Task 1]

## Reusable knowledge

- the freshest useful ADG evidence in this run was `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_06152026_1043.sqlite`, not older tracked files like `docs/reports/adg/apps_*_hotspots_20260525*.md` [Task 1]
- `mv_hotspot_coverage_risk` exposed many `apps_rg` `P1_URGENT` rows concentrated in `apps_rg/runtime/sections/*`, `apps_rg/runtime/bindings/*`, `apps_rg/runtime/judges/*`, `apps_rg/fact_inventory/*`, and `apps_rg/__main__.py` [Task 1]
- `coverage_by_path` uses `resolved_path` as its path column; for this analysis it did not directly show coverage rows for the top hotspot files, so the useful answer came from comparing hotspot modules against the actual `tests/` inventory [Task 1]
- the repo already has substantial `tests/apps_rg`, `tests/unit/apps_rg`, `tests/_apps_contract`, and related `tests/e2e` surface; for hotspot-gap analysis, ask whether the right layer has test surface rather than only whether a filename string appears anywhere [Task 1]
- when `adg_sqlite` MCP is unavailable in this Codex surface, local SQLite reads plus repo inventory are the workable fallback [Task 1]

## Failures and how to do differently

- symptom: initial SQLite probe failed around `count(*)` -> cause: PowerShell quoting/parsing -> fix: rerun with safer Python or SQL quoting rather than retrying the same inline shell form [Task 1]
- symptom: broad `rg` over `artifacts/` is noisy and expensive -> cause: too much unrelated generated output -> fix: narrow immediately to the newest ADG SQLite snapshot and hotspot report files [Task 1]
