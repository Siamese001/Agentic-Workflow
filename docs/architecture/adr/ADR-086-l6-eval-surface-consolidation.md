# ADR-086: L6 Eval Surface Consolidation (Deferred Implementation)

**Status:** Accepted (M1 executed 2026-05-25)
**Date:** 2026-05-25
**Plan:** [l6-reorg-deferred-followup-f3a9c2](../../.codex/plans/l6-reorg-deferred-followup-f3a9c2.md) W1.3 / W4
**Parent:** [l6_w4_passive_drift_20260525.md](../../reports/cursor/l6_w4_passive_drift_20260525.md) GAP-6

## Context

Three parallel eval surfaces exist on L6:

| Surface | Path | Modules | Role |
|---------|------|---------|------|
| A | `shadow_eval/` | 12 | Canonical passive shadow pipeline |
| B | `utils/evaluation/` | 24 | Legacy/broad eval toolkit |
| C | `L6_system_learning/validators/` | 7 | Active 06.2 structural validators |

Reporter-class modules (`async_eval_packet`, `governed_handoff`, `desk_d_governed_board`) canonical home is **`ops_scripts/reports/`** (L_OPS, ADR-095). L6 retains thin compat shims only.

## Decision

1. **Owner surface:** `shadow_eval/` (A) is canonical passive pipeline.
2. **`utils/evaluation/` (B)** is `legacy_parallel`; M1 dead modules removed.
3. **Validators (C)** stay on active root — no merge with passive trees.
4. **M2:** Canonical 06.7 gauntlet is `shadow_eval/gauntlet.py`; B `promotion_gauntlet.py` is compat-only (docstring + retained API).
5. **M3:** B implementations live under `shadow_eval/legacy_parallel/`; `utils/evaluation/` holds 90-day re-export shims.

## Implementation status

| Wave | Status | Evidence |
|------|--------|----------|
| M1 | **Done** | 12 zero-importer modules deleted; paired unit tests removed |
| M2 | **Done (compat)** | `promotion_gauntlet.py` tagged legacy; owner = `shadow_eval/gauntlet.py` |
| M3 | **Done** | 9 modules → `shadow_eval/legacy_parallel/`; shims at `utils/evaluation/` |

## Consequences

- B surface: 11 shim files under `utils/evaluation/` (2 → `ops_scripts.reports`, 9 → `legacy_parallel`).
- Future work: migrate callers off shims; merge `legacy_parallel` APIs into native `shadow_eval` 06.x modules where types align.
