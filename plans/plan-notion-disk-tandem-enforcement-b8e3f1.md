---
slug: plan-notion-disk-tandem-enforcement-b8e3f1
status: Not Started
plan_type: governance_hook_fix
dod_exempt: false
supersedes: []
owner: Amit Ayer
created: 2026-06-08
---

# Plan ↔ Notion disk tandem enforcement (always fail-closed)

## Decision summary

A plan must exist on **disk (SSOT)** AND in the **Notion Plans DB**, in tandem. Today the gates
exist but are **advisory by default**, and the Notion-create gate trusts a self-reported
`Exists On Disk` checkbox instead of the filesystem. Per Author-Gate sign-off (2026-06-08,
governance/policy config change, "full fail-closed both directions"), make enforcement always-on.

Builds on `apps_rg_e2e` (relocation-aware plan governance + `_plan_registration`). Scoped to the
plan-governance files only so it cherry-picks to `main` via the forward-port task.

### Wave summary

| Wave | Focus | Status | Success criteria |
|---|---|---|---|
| W1 | Notion→disk: creation gate verifies the REAL `plans/<slug>.md` file | Done | Block `API-post-page` to Plans DB when the disk file is absent |
| W2 | Disk→Notion: T7u commit gate fail-closed by default | Done | `_fail_closed()` defaults True; opt-out `PLAN_REGISTRATION_FAIL_CLOSED=0`; still SKIPs w/o token |
| W3 | Identity: write gate fail-closed by default | Done | `run_gate` mismatch → exit 2 without env; opt-out `=0` |
| W4 | Tests | Done | `test_plan_notion_disk_tandem.py` — 7 green; existing write-gate test unchanged (3 pre-existing legacy failures, not caused here) |

## Gap register

| ID | Sev | Wave | Gap | Acceptance |
|---|---|---|---|---|
| T1 | HIGH | W1 | Creation gate checks the `Exists On Disk` checkbox (a claim), not the file | `_validate_disk_file` blocks when `plans/<slug>.md` and `.codex/plans/<slug>.md` both absent |
| T2 | HIGH | W2 | `check_plan_registration_freshness` advisory by default → disk plan can commit with no Notion row | `_fail_closed()` defaults True; bypass `=0`; no-token still SKIP exit 0 |
| T3 | MEDIUM | W3 | `pre_notion_plan_write_gate.run_gate` advisory by default → identity mismatch allowed | mismatch → exit 2 by default; bypass `=0` or `NOTION_PLAN_IDENTITY_BYPASS=1` |

## Changes (files)

- `.codex/governance/scripts/pre_notion_plan_creation_gate.py` — add `REPO_ROOT`, `_extract_slug`,
  `_validate_disk_file`; call it in `_check_payload`.
- `ops_scripts/ci/check_plan_registration_freshness.py` — `_fail_closed()` defaults True.
- `.codex/governance/scripts/pre_notion_plan_write_gate.py` — `run_gate` fail-closed default.
- `tests/unit/windsurf_scripts/test_plan_notion_disk_tandem.py` — new.

## Definition of Done

| # | Criterion | Verify |
|---|---|---|
| 1 | Notion-create blocked when the real disk file is absent | unit test |
| 2 | Notion-create allowed when `plans/<slug>.md` exists | unit test (tmp file) |
| 3 | Freshness gate fail-closed by default; `=0` → advisory; no-token → SKIP | unit test of `_fail_closed` + main skip path |
| 4 | Identity gate fail-closed by default on mismatch | unit test of `run_gate` |
| 5 | Existing `test_pre_notion_plan_write_gate.py` still green | pytest |
| 6 | All bypass env kill-switches retained + documented | source review |

## Non-goals
- Reverse Notion→disk file *writer* (RCA Option C) — not chosen; enforcement requires the agent to write disk first.
- Editing `main` from this worktree (carried by the forward-port task).
