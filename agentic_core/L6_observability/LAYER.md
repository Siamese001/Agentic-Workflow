# LAYER: L6 (passive surface)

This directory is the **passive half of L6** in the agentic spine.

| Field | Value |
|---|---|
| Layer | L6 |
| Surface | passive (capture exhaust) |
| Sibling surface | active — `agentic_core/L6_system_learning/` |
| Doctrinal docs | `@docs/reference/06_L6_Observability_and_System_Learning/` (chapters 06.1–06.9) |
| Mental model | `@docs/reference/_notes/L6_mental_model.md` |

## Subdirectory map

| Subdir | Role |
|---|---|
| `runtime_trace/` | OTEL spans, trace correlation, runtime ADG hand-off |
| `semconv/` | Semantic-convention vocabulary for span attributes |
| `execution/` | Exec-side tracing (tool calls, agent dispatch) |
| `reasoning/` | Reasoning-side tracing (planner / cognition spans) |
| `shadow_eval/` | Observe-only eval hooks (no policy effect) |
| `enforcement/` | Anti-bypass monitors, `agent_monitor.py` |
| `types/` | Span / event / decision-event schemas |
| `utils/` | Shared helpers |

## Documented layout drift (W4 — map only, no moves)

Items below are **on disk** but omitted from the mental-model tree in [L6_mental_model.md](../../docs/reference/_notes/L6_mental_model.md). Relocations require a separate Author-Gate; see [l6_w4_passive_drift_20260525.md](../../docs/reports/cursor/l6_w4_passive_drift_20260525.md).

| Path / module | Drift type | W4 classification | Deferred action |
|---------------|------------|-------------------|-----------------|
| ~~`promotion/`~~ | **Resolved W1.1** — moved to `L6_system_learning/promotion/` | Active-adjacent 06.7 | [ADR-087](../../docs/architecture/adr/ADR-087-l6-passive-layout-followup.md) |
| `promotion_gates.py`, `flywheel_promoter.py` | Root promotion helpers | Passive stats / triage | Document; no move |
| `otel_runtime_ingest.py`, `*_otel.py` (root shims) | **Resolved W1.2** — implementations under `runtime_trace/` | Compat re-exports at root | [ADR-087](../../docs/architecture/adr/ADR-087-l6-passive-layout-followup.md) |
| `decision_*`, `routing_*` schemas | Root schema modules | Belongs under `types/` | Document only |
| `utils/evaluation/` (11 shims) | **Resolved M3** — impl in `shadow_eval/legacy_parallel/` | 90-day compat re-exports | [ADR-086](../../docs/architecture/adr/ADR-086-l6-eval-surface-consolidation.md) |

**Eval surfaces (GAP-6):** `shadow_eval/` (12 modules, canonical passive pipeline) · `utils/evaluation/` (24 modules, legacy parallel) · active validators live under `system_learning/validators/` (not passive).

## L6 invariants

1. **Synchronous emission, fail-soft.** Tracing MUST NOT block runtime. Drop spans before blocking.
2. **No promotion path.** This surface is a terminal sink for runtime exhaust. Active learning happens in `agentic_core/L6_system_learning/`.
3. **ADG layer tag.** Every module here resolves to `layer=L6` in the static ADG snapshot.

## Sibling reference

The active surface (`agentic_core/L6_system_learning/`) consumes exhaust emitted by this package and feeds the gauntlet → UWG promotion loop. See chapter `06.1_L6_Runtime_Exhaust_Ingest_and_Normalization.md` for the exhaust contract.
