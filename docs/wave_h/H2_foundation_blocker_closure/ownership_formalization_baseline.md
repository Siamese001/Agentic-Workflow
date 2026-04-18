# H2 — Ownership Formalization Baseline

wave: H2
adg_snapshot: artifacts/adg/adg_indexed_04182026_0858.sqlite
adg_snapshot_timestamp: "04182026_0858"

## Scope

- `B7-G6-05`

## H1 closure tests applied

Required tests from H1:

1. per-surface ownership tags finalized for production scope
2. mixed-control ambiguities reduced below agreed threshold
3. owner matrix and runtime map are consistent

## Direct evidence observed

From `docs/wave_g/G7_integrated_runtime_map/ownership_matrix.md` and `whole_system_runtime_map.md`:

- ownership classes explicitly present:
  - `repo-managed`
  - `operator-managed`
  - `external-tool-owned`
  - `mixed-control`
- major runtime clusters are tagged with ownership class
- mixed-control surfaces explicitly listed (memory, vector, redis client usage, observability, governance exit/write-gate posture)
- `B7-G6-05` explicitly carried as unresolved formalization residual

## H2 baseline formalization outcome

### Production-scope surface tags (baseline)

- repo-managed:
  - app runtimes
  - core runtime libraries
  - ADG generation and python MCP server logic
- operator-managed:
  - Redis daemon lifecycle
  - external provider account/endpoints
- external-tool-owned:
  - DeepWiki endpoint
  - GitKraken bridge behavior and comparable external MCP tool contracts
- mixed-control:
  - memory lifecycle plane
  - vector retrieval/embedding plane
  - redis client/cache semantics
  - observability ingestion path
  - governance override control surfaces

## Consistency check result

- owner classes are internally consistent across G7 ownership matrix and runtime map.
- ambiguity remains in mixed-control production-safe thresholding:
  - no explicit numeric/operational threshold definition found in current evidence corpus,
  - no closure evidence proving mixed-control ambiguity reduced below that threshold.

## Net result

`B7-G6-05` is **narrowed but not closed**:

- ownership taxonomy exists and is consistently applied at baseline,
- production-safe closure threshold evidence is still missing.
