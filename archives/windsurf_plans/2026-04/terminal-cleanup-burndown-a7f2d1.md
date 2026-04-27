---
plan_type: tracker
---

# Terminal Cleanup Baseline Burndown

**Plan ID**: `terminal-cleanup-burndown-a7f2d1`
**Created**: 2026-04-22 (orphan-row recovery — Notion row existed since 10:44 UTC, plan file materialized 19:42 UTC)
**SSOT**: Notion Wave/Phase Convergence DB (1 phase row). This file is a disk anchor.
**Status**: Deferred — new gate wired; burndown not yet started.

## Parent Plan Summary

Standalone burndown for **30 legacy subprocess/Popen/os.system violations** left baselined when `check_terminal_cleanup.py` (T7h pre-commit hook) was introduced 2026-04-22. Gate prevents NEW violations from today forward; this plan clears the baseline.

Relates to constitutional §11 (terminal process lifecycle) + §14 (subprocess timeout required).

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|---|---|---|---:|---|
| **W1** | P1 | Burn 30 baselined violations across 25 files | 40k | Todo |

## Phase-Level Summary

| Phase ID | Title | Scope | Est. Tokens | Status |
|---|---|---|---:|---|
| P1 | Terminal Cleanup Baseline Burndown — 30 violations across 25 files | 27 `subprocess.run` add timeout=30; 3 Popen wrap in `with`; 1 `os.system` → subprocess.run | 40k | Todo |

## Baseline

- **File**: `artifacts/reports/terminal_cleanup_baseline_20260422.txt`
- **Gate**: `ops_scripts/ci/check_terminal_cleanup.py` (wired as pre-commit hook T7h, `--staged` mode)

## Violation Breakdown

- 27 × `subprocess.run` without `timeout=` — add `timeout=30`
- 3 × `Popen` leak — wrap in `with` block or explicit lifecycle
- 1 × `os.system` — replace with `subprocess.run(argv, shell=False, timeout=30)`

## Hotspots by File Count

- `agentic_core/L5_safety/enforcement/` (3)
- `agentic_core/` utils (6)
- `apps_shared/` orchestrators (4)
- +12 other files (full list in baseline txt)

## Success Criteria

- All 30 baselined violations resolved via the fix patterns above
- Baseline file `artifacts/reports/terminal_cleanup_baseline_20260422.txt` removed OR pinned at 0
- `check_terminal_cleanup.py` gate passes without baseline exemption
- P1 (constitutional §11/§14) ratchet ceiling restorable to 0

## Gap Register

None at creation. Surfacing burndown by file may expose layer-specific subprocess patterns that need their own ADR.

## Detail (cross-reference)

Full per-phase detail lives in Notion Wave/Phase Convergence DB row under `Plan File = terminal-cleanup-burndown-a7f2d1.md`.

Notion DB: https://www.notion.so/aa8d2507101e438481d960ea3fe33876

---

Generated 2026-04-22 as orphan-row recovery from the Notion audit report at `docs/reports/plans/notion_backlog_audit_20260422.md`. Original Notion row created 2026-04-22 10:44 UTC; enriched schema backfilled 19:35 UTC; plan file materialized 19:42 UTC.
