# H13 — Remediation Plan and Changes

wave: H13
adg_snapshot: artifacts/adg/adg_indexed_04182026_2044.sqlite
adg_snapshot_timestamp: "04182026_2044"

## Scope-bound remediation plan

Target blockers only:
- `B7-G4-03`
- `B7-G6-03`
- `B7-G6-05`
- `B7-G6-02`

Plan:
1. enforce canonical `MEMORY_DB` behavior in production scope,
2. produce executable proof via focused tests,
3. converge execution-trace contract authority to selected owner module,
4. produce mixed-control threshold measurement evidence post-remediation.

## Implemented technical changes

### 1) Canonical memory enforcement (`B7-G4-03`, `B7-G6-03`)

- Added `agentic_core/L4_state/enforcement/memory_db_canonical_policy.py`.
- Added `resolve_canonical_memory_db_path()` behavior:
  - in production-scope closure terms (no test override), non-canonical `MEMORY_DB` is rejected with `RuntimeError`,
  - canonical path accepted: `artifacts/memory/knowledge_graph.sqlite`,
  - explicit test-mode override supported via `ALLOW_NONCANONICAL_MEMORY_DB_FOR_TESTS=1`.
- Updated `agentic_core/L4_state/enforcement/graph_memory_bridge.py` SQLite fallback initialization to use canonical policy resolver.

### 2) Execution-trace authority convergence (`B7-G6-02`)

- Converted `agentic_core/L_CONTRACTS/execution_trace.py` into an explicit compatibility shim.
- Selected authority module for runtime execution-trace contract: `agentic_core/runtime/types/execution_trace.py`.
- Shim now re-exports authority APIs from selected authority module.

### 3) Mixed-control measurement evidence (`B7-G6-05`)

- Added reproducible measurement test over G7 ownership matrix:
  - `tests/unit/docs/wave_h/test_h13_mixed_control_threshold.py`
- Measured unresolved mixed-control surfaces from matrix: `5`.
- Accepted threshold for closure remains: `0`.

## Validation runs executed

1. `pytest -v tests/unit/agentic_core/L4_state/enforcement/test_memory_db_canonical_policy.py`
   - result: `3 passed`
2. `pytest -v tests/unit/agentic_core/runtime/test_execution_trace_authority_alignment.py`
   - result: `2 passed`
3. `pytest -v tests/unit/docs/wave_h/test_h13_mixed_control_threshold.py`
   - result: `1 passed`
