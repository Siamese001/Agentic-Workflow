# ADG Decision Synthesis

- Status: Approved
- Created: 2026-06-14
- Scope: `tools/reports/adg_review_template.py`, `tools/reports/adg_burndown_report.py`, `tests/unit/tools/reports/test_adg_review_template.py`, `tests/unit/tools/reports/test_adg_burndown_report_mandatory.py`, and new shared synthesis module. Verification also fixed two gate regressions in `tools/generate/materialized_views/phase_c_trace_drift_debt.py`.

## Goal

Create a generic ADG decision-synthesis layer for future ADG runs so report surfaces consistently separate FIX, ratchet TRACK floors, open non-ratchet TRACK work, CLEAR gates, GraphDB/MV reasoning, testing placement, and artifact health.

## Approved Implementation Steps

1. Add `tools/reports/adg_decision_synthesis.py` for gate normalization, FIX/TRACK/CLEAR splits, MV reasoning, canonical action plan, testing placement, after-green plan, audit notes, and artifact consistency.
2. Refactor `tools/reports/adg_review_template.py` to use shared synthesis output for JSON/YAML fields and render only the required inline decision sections.
3. Fix `tools/reports/adg_burndown_report.py` so band counts distinguish fix records, ratchet floor records, open non-ratchet records, clear records, and totals.
4. Update unit tests for burndown semantics, six-section inline output, driver MV reasoning, MV categorization, testing-hotspot reasoning, and artifact consistency behavior.
5. Verify targeted report tests and the full ADG generator.

## Notion Registration

Registered in Notion Plans via the direct Notion API fallback after the Codex Notion connector did not expose the required query/create tool.

- Page: https://app.notion.com/p/adg-decision-synthesis-9f3a2c-37f27693f55c81f4a636e5af28c013ae
- Page ID: `37f27693-f55c-81f4-a636-e5af28c013ae`
- Status: `In Progress`
- Exists On Disk: `true`
- Plan File Path: `.claude/plans/adg-decision-synthesis-9f3a2c.md`

## Verification Notes

- `pytest-timeout` is available in the current environment, so pytest no longer fails collection on `--timeout=180`.
- P0 `infra_wiring` blockers found during generator verification were fixed by removing direct provider/storage imports from runtime/app files.
- `.claude` hook scripts are now excluded from Phase C runtime trace/replay/eval and replay-surface gap views; those scripts are non-runtime governance hooks.
- Full generator verification reached the gate dispatcher, with block failures clear. Latest remaining failures are five ratchet regressions requiring separate per-gate remediation or an explicit baseline decision: `G_REACH_l0_reachability` +2, `C3_silent_writes_ratchet` +4, `M1_module_loc_ratchet` +1, `S4_unused_imports_ratchet` +4, and `Q2_cyclomatic_complexity_ratchet` +1.
