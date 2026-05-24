# W0.2 — Cross-plan sync: transport parity ↔ core panel harness

**Date:** 2026-05-24  
**Plans:** `exec-summary-x1d-transport-parity-d8f2a1` (apps_rg) · `core-judge-panel-harness-f3c8d1` (agentic_core)

## Sequencing (locked)

1. **apps_rg remediation first** — rubric/packet/reconcile/transport fixes in `executive_summary_*` (transport-parity plan W1–W2).
2. **Core harness W1** — generic `agentic_core/runtime/judges/panel/` + unit tests.
3. **apps_rg W2 migration** — `run_llm_judges` GRADE_ONLY path → `JudgePanelRunner` via `x1d_panel_bridge` + `x1d_panel_adapters`.
4. **W3 governance** — GOV-JPH boundary gate, core-backed transport preflight, docs.

## Division of SSOT

| Concern | Owner |
|---------|--------|
| Rubric text, X2 gates, packet builder | `apps_rg` |
| Panel fan-out, contract hash law, transport preflight API | `agentic_core` |
| Provider HTTP adapters | `apps_rg` (`_call_*` wrapped by adapters) |
| Gate-closure map data | `apps_rg` (`executive_summary_x1d_gate_closure_map.py`) |
| Gate-closure reconcile algorithm | `apps_rg` (rich fragment classifier); `core_gate_closure_map()` for core tests |

## Non-duplication

Transport-parity plan does **not** add core modules. Core harness plan does **not** change GRAPH rubric or X2 validators.
