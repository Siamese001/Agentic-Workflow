# LAYER: L6 (active surface)

This directory is the **canonical active half of L6** in the agentic spine (`PATH_RENAME_CANONICAL`, W5.3).

| Field | Value |
|---|---|
| Layer | L6 |
| Surface | active (learn from exhaust) |
| Canonical package path | `agentic_core/L6_system_learning/` |
| Sibling surface | passive — `agentic_core/L6_observability/` |
| Doctrinal docs | `@docs/reference/06_L6_Observability_and_System_Learning/` (chapters 06.1–06.9) |
| Mental model | `@docs/reference/_notes/L6_mental_model.md` |

## L6 invariants

1. **Observer law.** This package MUST NOT write back to L0..L5 runtime layers. Read-only access to types/contracts is permitted; writers, emitters, dispatchers, routers, executors are forbidden. Enforced by `ops_scripts/ci/check_l6_observer_law.py`.
2. **Async posture.** System-learning code MUST NOT block runtime. All ingestion is async/batch.
3. **Promotion gate.** The only path back to runtime is the UWG promotion gate (chapter 06.7), itself HITL-gated.
4. **ADG layer tag.** Every module here resolves to `layer=L6` in the static ADG snapshot. Verified by `ops_scripts/ci/check_l6_layer_tag_consistency.py`.

## Subpackage chapter map

See `@docs/reference/_notes/L6_mental_model.md` for the canonical subpackage → chapter mapping. Each subpackage `__init__.py` declares its primary chapter via `__l6_chapter__ = "06.X"` (or `""` for cross-cutting modules like `logs/`, `types/`).
