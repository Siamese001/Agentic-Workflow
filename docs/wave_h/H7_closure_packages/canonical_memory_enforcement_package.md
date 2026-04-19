# H7 — Canonical Memory Enforcement Package

wave: H7
adg_snapshot: artifacts/adg/adg_indexed_04182026_1947.sqlite
adg_snapshot_timestamp: "04182026_1947"

## Scope

- `B7-G4-03`
- `B7-G6-03`

## H1 closure tests targeted

1. canonical memory store decision ratified
2. non-canonical stores dispositioned
3. runtime config binding points prove canonical-state enforcement

## Buildable package components from direct repo evidence

### A) Canonical decision and store disposition (buildable)

- Canonical candidate remains explicit:
  - `STORE-MEMORY-SQLITE-CANONICAL` -> `artifacts/memory/knowledge_graph.sqlite`
  - evidence: `docs/wave_g/G4_storage_infra/storage_catalogue.yaml`
- Non-canonical/ambiguous candidates remain explicitly dispositioned:
  - `STORE-MEMORY-SQLITE-DUPLICATE` -> `data/memory/knowledge_graph.sqlite`
  - `STORE-MEMORY-UNIFIED-DB` -> `data/memory/unified_memory.db`
  - evidence: `docs/wave_h/H2_foundation_blocker_closure/store_disposition_table.md`

### B) Runtime binding evidence (buildable)

- `MEMORY_DB` remains process-start binding key in control-plane docs:
  - `docs/wave_g/G4b_control_plane/defaults_and_reload_policy.md`
- Code-level env binding points exist in multiple runtime surfaces:
  - `tools/memory/adg_memory_server.py`
  - `tools/memory/sqlite_memory_store.py`
  - `tools/memory/purge_sync.py`
  - `agentic_core/L4_state/enforcement/graph_memory_bridge.py`

## Still-missing components (preventing score 3)

### Production-scope canonical-memory enforcement proof (missing)

Missing evidence that production runtime cannot be redirected away from canonical store by `MEMORY_DB`.

### MEMORY_DB redirect control proof (missing)

No in-repo evidence of a production policy gate that rejects non-canonical `MEMORY_DB` values.

## Score impact

| blocker_id | H6 | H7 | reason |
|---|---:|---:|---|
| B7-G4-03 | 2 | 2 | decision/disposition are strong, but enforcement proof against runtime redirection remains missing |
| B7-G6-03 | 2 | 2 | same unresolved enforcement proof gap as B7-G4-03 |

## Explicit answer to required H7 question

Can `B7-G4-03` and `B7-G6-03` both reach score 3 in H7 from repo evidence alone?

No. Both remain below 3 because enforcement-grade proof for non-redirectable canonical state is not present in the current repo evidence.
