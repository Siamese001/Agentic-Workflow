# LAYER: L6 (passive surface)

This directory is the **passive half of L6** in the agentic spine.

| Field | Value |
|---|---|
| Layer | L6 |
| Surface | passive (capture exhaust) |
| Sibling surface | active — `system_learning/` |
| Doctrinal docs | `@docs/reference/06_L6_Shadow_Evaluation_System_Learning/` (chapters 06.1–06.9) |
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

## L6 invariants

1. **Synchronous emission, fail-soft.** Tracing MUST NOT block runtime. Drop spans before blocking.
2. **No promotion path.** This surface is a terminal sink for runtime exhaust. Active learning happens in `system_learning/`.
3. **ADG layer tag.** Every module here resolves to `layer=L6` in the static ADG snapshot.

## Sibling reference

The active surface (`system_learning/`) consumes exhaust emitted by this package and feeds the gauntlet → UWG promotion loop. See chapter `06.1_L6_Runtime_Exhaust_Ingest_and_Normalization.md` for the exhaust contract.
