# H2 — Store Disposition Table (Memory Store Candidates)

wave: H2
adg_snapshot: artifacts/adg/adg_indexed_04182026_0858.sqlite
adg_snapshot_timestamp: "04182026_0858"

Required classification enum:

- canonical
- duplicate_noncanonical
- archival_only
- compatibility_only
- test_only
- unresolved

## Memory store candidates

| store_id | path | evidence_basis | disposition | rationale |
|---|---|---|---|---|
| STORE-MEMORY-SQLITE-CANONICAL | artifacts/memory/knowledge_graph.sqlite | G4 storage catalogue lists explicit owner/writer/reader modules | canonical | strongest direct ownership and active usage evidence |
| STORE-MEMORY-SQLITE-DUPLICATE | data/memory/knowledge_graph.sqlite | G4 storage catalogue lists no owner/writer; env-driven fallback mention | duplicate_noncanonical | duplicate location with ambiguous activation via config |
| STORE-MEMORY-UNIFIED-DB | data/memory/unified_memory.db | G4 storage catalogue lists no owner/writer/reader; explicit ambiguity note | unresolved | insufficient direct evidence to classify as archival/compat/test-only |

## Notes

- This table is evidence-bound and does not mutate runtime behavior.
- Final production closure still requires proof that config binding cannot silently re-promote non-canonical stores in production scope.
