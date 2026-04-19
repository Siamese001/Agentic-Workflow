# H13 — Canonical Memory Enforcement Validation

wave: H13
adg_snapshot: artifacts/adg/adg_indexed_04182026_2044.sqlite
adg_snapshot_timestamp: "04182026_2044"

## Scope

- `B7-G4-03`
- `B7-G6-03`

## Enforced production-scope behavior

Implemented behavior (`resolve_canonical_memory_db_path`):

- If running production-scope closure path (no test override):
  - reject non-canonical `MEMORY_DB` with `RuntimeError`.
- Canonical accepted path:
  - `artifacts/memory/knowledge_graph.sqlite`
- Explicit test-mode override path:
  - `ALLOW_NONCANONICAL_MEMORY_DB_FOR_TESTS=1`

Graph-memory runtime fallback now uses this resolver in:
- `agentic_core/L4_state/enforcement/graph_memory_bridge.py`

## Reproducible validation steps

1. Run: `pytest -v tests/unit/agentic_core/L4_state/enforcement/test_memory_db_canonical_policy.py`
2. Verify outcomes:
   - non-canonical path rejected in production scope,
   - canonical path accepted,
   - test override permits non-canonical path.

## Validation outcome

- Executed result: `3 passed`
- Closure-grade technical proof now present for:
  - production-scope non-canonical `MEMORY_DB` rejection,
  - canonical-path acceptance behavior,
  - reproducible enforcement verification.

## Blocker result

- `B7-G4-03`: eligible for score `3` in H13.
- `B7-G6-03`: eligible for score `3` in H13.
