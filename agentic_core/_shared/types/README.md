# `_shared/types/` — Future Pure-Type Home (ADR-088)

**Layer:** `L_SHARED` (ADG generator)  
**Status:** Scaffold only — Category A modules remain in L0/L3 until lifecycle split.

## Target split pattern (future plan)

| Today | Future pure module | Stays in layer |
|-------|------------------|----------------|
| `L0_routing/types/determinism_types.py` | `_shared/types/determinism_pure.py` (enums, frozen dataclasses) | `determinism_bootstrap.py` with `record_execution_trace` |
| `L0_routing/config/path_constants.py` | `_shared/types/path_constants_pure.py` | `path_constants_bootstrap.py` |
| `L3_orchestration/types/human_decision_artifact_types.py` | `_shared/types/human_decision_pure.py` | L3 bootstrap |
| `L0_routing/enforcement/mutation_prohibition.py` | `_shared/types/mutation_prohibition_pure.py` | L0 bootstrap |

## Rules

1. **No** `lifecycle_trace_contract` imports in `_shared/types/*`.
2. Layer modules import pure types first, then call bootstrap at app entry.
3. L6 gravity exceptions for Category A remain until importers switch to `_shared` paths.

See [ADR-088](../../../docs/architecture/adr/ADR-088-l6-category-a-shared-permanent-exception.md).
