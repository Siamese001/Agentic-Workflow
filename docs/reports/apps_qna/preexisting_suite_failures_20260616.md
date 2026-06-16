# apps_qna Pre-Existing Suite Failures - 2026-06-16

Status: OBSERVED AS PRE-EXISTING BLOCKERS, THEN RESOLVED IN THIS BRANCH.

Worktree: `C:\Git\Agentic-Workflow-FRESH-worktrees\claude-apps-qna-graph-experience`

Branch: `claude-apps-qna-graph-experience` (behind `origin/main` by 12 commits at observation time)

## Scope

This note records failures observed while auditing the in-progress apps_qna graph-source implementation. These failures were initially classified as pre-existing blockers for merge/readiness tracking, not as required fixes for the graph adapter patch. A later instruction expanded scope to make `tests/apps_qna` pass before merge, so the blockers below were resolved in this branch.

No clean-baseline rerun was performed before the Claude worktree changes were inspected, so this is an operator classification record rather than a historical proof that every failing test failed before the patch.

## Graph Adapter Slice

The graph-specific/touched test slice passed:

```powershell
python -m pytest tests/apps_qna/test_integrations.py tests/apps_qna/test_w3_star_synthesis.py -q
```

Observed result: `50 passed`.

Whitespace check passed:

```powershell
git diff --check
```

## Full apps_qna Suite Observation

Command:

```powershell
python -m pytest tests/apps_qna -q
```

Initial observed result: `392 collected`, `374 passed`, `18 failed`.

Resolved observed result after follow-up fixes:

```powershell
python -m pytest tests/apps_qna -q
```

Observed result: `392 passed`, `9 warnings`.

## Failure Buckets

1. Ledger/schema fixture failures.
   Multiple tests failed with missing ledger tables such as `events` and `schema_version`, or empty event ids after ledger append attempts. Representative failing modules:
   - `tests/apps_qna/test_deferred_scope_completion.py`
   - `tests/apps_qna/test_spine_handoff.py`
   - `tests/apps_qna/test_w1_4_pack_lifecycle_ledger.py`
   - `tests/apps_qna/test_w4_1_route_bandit.py`
   - `tests/apps_qna/test_w5_1_learning_adapter.py`

2. Missing spine/skill fixture artifacts.
   Failures referenced missing compatibility/test artifacts such as:
   - `tests/integrations/spine_handoff.py`
   - `tests/spine_manifest.yaml`
   - `.claude/skills/ledger-consulter-apps-qna-pack-lifecycle/SKILL.md`

3. Paste optimization route fixture mismatch.
   `tests/apps_qna/fixtures/synthetic_mini/interview.yaml` declares `route_id: apps_qna.live_interview_runtime_pack_v1`, while the builder route registry uses route ids such as `architecture`, `executive_fit`, `governance`, and related card-route ids. This produced paste counts of 8/9 where tests expected 21/22 in:
   - `tests/apps_qna/test_paste_optimization.py::test_single_interview_default_under_cap`
   - `tests/apps_qna/test_paste_optimization.py::test_panel_two_interviewers_under_cap`

## Merge Readiness Note

These failures are no longer open in this branch. Before publishing, rerun the focused graph slice and `tests/apps_qna` after rebasing/merging the newer `origin/main` commits.
