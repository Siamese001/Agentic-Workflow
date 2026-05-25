# L6 Category A `_shared` Extraction Spike (W3.1)

**Date:** 2026-05-25  
**Plan:** [l6-reorg-deferred-followup-f3a9c2](../../.cursor/plans/l6-reorg-deferred-followup-f3a9c2.md)  
**Verdict:** `permanent_exception_documented` — closed by [ADR-088](../../architecture/adr/ADR-088-l6-category-a-shared-permanent-exception.md)

---

## Candidates (7c4e2a W1.P2)

| Module | Path | Blocker |
|--------|------|---------|
| determinism_types | `L0_routing/types/determinism_types.py` | `record_execution_trace` at import; 30+ lifecycle imports |
| path_constants | `L0_routing/config/path_constants.py` | Same pattern |
| human_decision_artifact_types | `L3_orchestration/types/...` | Instrumented envelope |
| mutation_prohibition | `L0_routing/enforcement/mutation_prohibition.py` | Instrumented envelope |

## Spike finding

Extracting to `agentic_core/_shared/types/` without dragging `lifecycle_trace_contract` would require:

1. Split **pure types** into `_shared/types/` (no side effects).
2. Leave **instrumentation bootstrap** in layer-specific `*_bootstrap.py` modules imported explicitly at app startup.
3. Update ADG layer tags for `_shared` (already `L_SHARED` in generator).

Estimated effort: **2–3 days** — exceeds follow-up W3 scope.

## Recommendation

- **Do not extract** in follow-up plan.
- Keep Category A edges in [architectural_exceptions.yaml](../../../config/architectural_exceptions.yaml) under `types_and_path_constants`.
- Open **new plan** `l6-shared-types-split-*` if instrumentation split is prioritized.

## DS-5 status

`blocked_instrumentation` → **`permanent_exception_documented`**
