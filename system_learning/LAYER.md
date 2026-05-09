# LAYER: L6 (active surface)

This directory is the **active half of L6** in the agentic spine.

| Field | Value |
|---|---|
| Layer | L6 |
| Surface | active (learn from exhaust) |
| Sibling surface | passive — `agentic_core/L6_observability/` |
| Doctrinal docs | `@docs/reference/06_L6_Shadow_Evaluation_System_Learning/` (chapters 06.1–06.9) |
| Mental model | `@docs/reference/_notes/L6_mental_model.md` |
| Doctrinal alias | `agentic_core.L6_system_learning` (forward import — both paths first-class) |

## Why this directory is at repo root, not under `agentic_core/L6_*/`

For historical reasons. The `L6_` prefix was applied to `agentic_core/L6_observability/` first; `system_learning/` predates the convention. A non-invasive alignment plan (`.windsurf/plans/l6-doctrinal-alignment-noninvasive-b9d3f5.md`) declares L6 membership via in-tree markers (`__layer__ = "L6"`), a forward-import alias, and CI gates rather than forcing a 205-import-site rename. The invasive sibling plan (`l6-folder-rename-doctrinal-alignment-a8c4e2`) is Deprioritized.

## L6 invariants

1. **Observer law.** This package MUST NOT write back to L0..L5 runtime layers. Read-only access to types/contracts is permitted; writers, emitters, dispatchers, routers, executors are forbidden. Enforced by `ops_scripts/ci/check_l6_observer_law.py`.
2. **Async posture.** System-learning code MUST NOT block runtime. All ingestion is async/batch.
3. **Promotion gate.** The only path back to runtime is the UWG promotion gate (chapter 06.7), itself HITL-gated.
4. **ADG layer tag.** Every module here resolves to `layer=L6` in the static ADG snapshot. Verified by `ops_scripts/ci/check_l6_layer_tag_consistency.py`.

## Subpackage chapter map

See `@docs/reference/_notes/L6_mental_model.md` for the canonical 27-subpackage → chapter mapping. Each subpackage `__init__.py` declares its primary chapter via `__l6_chapter__ = "06.X"` (or `""` for cross-cutting modules like `logs/`, `types/`).
