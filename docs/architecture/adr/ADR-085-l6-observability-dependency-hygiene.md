# ADR-085: L6 Observability / System Learning Dependency Hygiene

**Status:** Accepted  
**Date:** 2026-05-25  
**Plan:** [l6-repo-reorganization-mental-model-c4e8f2](../../.claude/plans/l6-repo-reorganization-mental-model-c4e8f2.md) W6  
**Child plan:** [l6-gravity-hybrid-7c4e2a](../../.claude/plans/_archive/2026-05/l6-gravity-hybrid-7c4e2a.md) (Option 1 hybrid — partial execution)

## Context

Static ADG (`artifacts/adg/adg_indexed_05252026_0751.sqlite`) records **86** distinct `imports` edges from L6 surfaces (`agentic_core/L6_observability/`, `agentic_core/L6_system_learning/`) into L0..L5 modules across **37** source files. The orchestration plan W6 success criterion allows either burndown to **≤24** edges or **full documentation** of residuals.

Prior work (2026-05-01) moved `integrity_report_generator_util.py` to `ops_scripts/reports/` (W2.P2), eliminating the single largest offender. Category A type extraction to `agentic_core/_shared/` remains **blocked** — candidate modules are instrumented envelopes with lifecycle trace side effects, not pure types.

Post-W5, the canonical active root is `agentic_core/L6_system_learning/`; L6-OBS and L6-TAG gates are fail-closed green (300/300 L6 tags, 0 observer-law findings).

## Decision

1. **Document** all residual L6→L0..L5 import edges in [`config/architectural_exceptions.yaml`](../../../config/architectural_exceptions.yaml) under `l6_downstream_exceptions`, grouped by category.
2. **Do not** introduce new compatibility shims or re-export trees in this wave.
3. **Defer** additional physical moves (`async_eval_packet.py`, `governed_handoff.py`, `desk_d_governed_board.py`) to a follow-on burndown — fan-in and eval-pipeline coupling require dedicated Author-Gate per file.
4. **Retain** `agentic_core/_shared/` as the only approved neutral layer for future Category A extraction; inclusion criteria: types/constants only, no I/O, no lifecycle instrumentation.

## Categories

| Category | Rationale |
|----------|-----------|
| `types_and_path_constants` | Shared determinism/path contracts; extraction blocked on instrumentation |
| `l5_safety_enforcement_readers` | Read-only registry/SSOT/compliance verification used by integrity reporters |
| `l2_execution_infrastructure` | Clock/provider/telemetry bus — passive observability subscribers |
| `l2_write_and_proof_infrastructure` | UWG write gateway + proof emitter — documented chokepoints; L6 must not bypass UWG |
| `l6_eval_orchestration_utilities` | Eval/promotion orchestration at L6 boundary; move to L_OPS deferred |
| `residual_documented` | Low-count edges with explicit per-edge listing in YAML |

## Consequences

- W6 closes via **documented_over_threshold** path (`86 > 24`).
- CI gates L6-OBS / L6-TAG remain authoritative for observer law and layer tags; this ADR does **not** weaken those gates.
- Future ADG burndown waves must update both the inventory JSON and `architectural_exceptions.yaml` in the same PR.

## Verification

- Inventory: [`l6_w6_gravity_edge_inventory_20260525.json`](../../reports/cursor/l6_w6_gravity_edge_inventory_20260525.json)
- Receipt: [`l6_w6_gravity_receipt_20260525.json`](../../reports/cursor/l6_w6_gravity_receipt_20260525.json)
