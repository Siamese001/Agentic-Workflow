---
slug: plan-ssot-hook-path-recognition-a4f2c1
status: Not Started
plan_type: governance_hook_fix
dod_exempt: false
supersedes: []
owner: Amit Ayer
created: 2026-06-08
---

# Plan SSOT hook path recognition (Option B — repo-root `plans/`)

## Decision summary

RCA (2026-06-08) found the plan-governance hooks keyed on the legacy `.claude/plans/` path, so the
disk→Notion plan reconcile/registration did **not** fire for plans at the relocated canonical
repo-root `plans/`. **Option B** = make the three hooks recognize repo-root `plans/` (parent-dir ==
`plans`), matching `pre_notion_plan_write_gate.py`.

**Key finding on execution:** on this branch (`apps_rg_e2e`, from the `aig-e2e-waves` lineage) the
fix is **already implemented** (forward-only relocation, commit ref `c1a17d`) and **verified working**:

- `after_file_edit.py` → `_is_active_plan_file()` = `rel.endswith(".md") and not _archive and (rel.startswith("plans/") or rel.startswith(".claude/plans/"))` ✓ (plus the file-driven §36 registration enqueue).
- `post_write_plan_reconcile.py` → `_pp.parent.name == "plans" and "reports" not in _pp.parts` ✓.
- `post_agent_plan_registration_capture.py` → path defaults to `plans/<slug>.md` ✓.
- Shared helper `_plan_registration.py` → "canonical NEW plans live in repo-root `plans/`"; `plan_file_path()` returns `plans/<slug>.md`; `PLAN_FILE_RE` is location-agnostic ✓.

So the bug the RCA described is **only on `main`** (`git show main:.claude/hooks/after_file_edit.py`
still has `startswith(".claude/plans/")`). The residual work on `apps_rg_e2e` is a **regression test**
(none currently asserts repo-root recognition) + flag the `main` forward-port.

### Wave summary

| Wave | Focus | Status | Success criteria |
|---|---|---|---|
| W1 | Confirm the 3 hooks + helper recognize repo-root `plans/` | Done | Verified: `_is_active_plan_file`/reconcile predicate/`plan_file_path` accept `plans/`, reject `docs/reports/plans/` + `_archive` |
| W2 | Add regression test locking in repo-root `plans/` recognition | Done | `tests/unit/windsurf_scripts/test_plan_ssot_path_recognition.py` — 6 tests green |
| W3 | Forward-port the fix to `main` | Not Started (flagged) | `main`'s `after_file_edit.py` uses `_is_active_plan_file`; W2 test green on `main` |

## Gap register

| ID | Sev | Wave | Gap | Acceptance |
|---|---|---|---|---|
| H1 | HIGH | W1 | Plan hooks keyed on `.claude/plans/`, missing relocated repo-root `plans/` | Already fixed on `apps_rg_e2e` (c1a17d) — verified W1 |
| H2 | MEDIUM | W2 | No regression test asserts repo-root `plans/` recognition (could silently revert) | Add `test_plan_ssot_path_recognition.py`; assert `plans/` recognized, `reports/`+`_archive` excluded |
| H3 | HIGH | W3 | `main` still has the `.claude/plans/`-only bug | Forward-port `_is_active_plan_file` + helper to `main`; W2 test green there |

## Verification (W1, done)

`python artifacts/apps_rg/e2e_hardening/_verify_plan_path.py`:
- `_is_active_plan_file`: `plans/foo-abc123.md`→True, `.claude/plans/foo-abc123.md`→True,
  `docs/reports/plans/x.md`→False, `plans/_archive/old.md`→False, `apps_rg/foo.py`→False.
- reconcile predicate: `plans/…`→True, `.claude/plans/…`→True, `docs/reports/plans/…`→False.

## Definition of Done

| # | Criterion | Verify |
|---|---|---|
| 1 | All 3 hooks + helper recognize repo-root `plans/` | W1 verify script (done) |
| 2 | Regression test asserts `plans/` recognized + `reports/`/`_archive` excluded across the helper + `post_write_plan_reconcile` | `python -m pytest <new test> -q` green |
| 3 | Test fails if a hook reverts to `.claude/plans/`-only (guard) | mutate-then-run check |
| 4 | `main` forward-port tracked (H3) | this plan + spawn_task |
| 5 | No behavior change for non-plan / report / archive paths | test asserts exclusions |

## Non-goals

- The reverse direction (Notion→disk SSOT writer) — that is RCA Option C, not chosen here.
- Editing `main` from this worktree (W3 is flagged for a `main`-rooted change).

## Evidence
- RCA: this session (hooks key on `.claude/plans/` vs relocated `plans/`).
- Verify: `artifacts/apps_rg/e2e_hardening/_verify_plan_path.py`.
- Helper: `.claude/governance/scripts/_plan_registration.py` (`plan_file_path`, `PLAN_FILE_RE`).
