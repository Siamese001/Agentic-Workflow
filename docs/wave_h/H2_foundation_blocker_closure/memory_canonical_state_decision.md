# H2 — Memory Canonical State Decision

wave: H2
adg_snapshot: artifacts/adg/adg_indexed_04182026_0858.sqlite
adg_snapshot_timestamp: "04182026_0858"

## Scope

- `B7-G4-03`
- `B7-G6-03`

## H1 closure tests applied

Required tests from H1:

1. canonical memory store decision ratified
2. non-canonical stores dispositioned
3. runtime config binding points prove canonical-state enforcement

## Direct evidence observed

From `docs/wave_g/G4_storage_infra/storage_catalogue.yaml`:

- `STORE-MEMORY-SQLITE-CANONICAL` at `artifacts/memory/knowledge_graph.sqlite`
  - owner modules explicitly listed (`tools/memory/sqlite_memory_store.py`, `tools/memory/adg_memory_server.py`)
  - active reader/writer paths listed
- `STORE-MEMORY-SQLITE-DUPLICATE` at `data/memory/knowledge_graph.sqlite`
  - owner list empty
  - marked ambiguous and env-driven fallback in notes
- `STORE-MEMORY-UNIFIED-DB` at `data/memory/unified_memory.db`
  - owner/writer/reader not enumerated
  - explicitly flagged as ambiguous in notes

From G4/G4b/G7/H1 documentation:

- `MEMORY_DB` may redirect effective store path (control-plane dependency)
- ambiguity is explicitly carried as blocker in G7 and H1

## H2 decision

### Canonical decision (narrowed)

For H production-scope truth packaging, treat:

- `artifacts/memory/knowledge_graph.sqlite` as **provisional canonical** store candidate.

Rationale:

- only candidate with explicit owner and active read/write surfaces in storage catalogue.

### Non-canonical disposition (provisional)

- `data/memory/knowledge_graph.sqlite`: duplicate_noncanonical (pending enforcement proof)
- `data/memory/unified_memory.db`: unresolved (insufficient direct ownership/runtime binding evidence)

## Why not full closure yet

Closure test #3 is not fully met from repo-doc evidence alone:

- config binding points indicate `MEMORY_DB` can redirect runtime to non-canonical store,
- no definitive production-scope enforcement evidence in this wave proving canonical path cannot be overridden in H production scope.

## Net result

- Blockers `B7-G4-03` and `B7-G6-03` are **narrowed** to a smaller residual:
  - unresolved enforcement proof of canonical-state in production scope.
