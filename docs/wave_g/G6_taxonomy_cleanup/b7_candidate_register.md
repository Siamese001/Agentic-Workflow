# G6 — B7 Candidate Register

wave: G6
produced_at: 2026-04-18
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
adg_snapshot_timestamp: "04182026_0814"

## Purpose

Track normalization findings that may require formal B7 interaction/completeness treatment in G7+.

## Entries

| b7_id | derived_from_surface | summary | owner | g7_blocker |
|---|---|---|---|---|
| B7-G6-01 | G6-S001 (`agentic_core/L_CONTRACTS/`) | Declared layer-contract surface is effectively runtime-dead; requires explicit keep/archive/wire decision | G7 traceability + architecture owner | yes |
| B7-G6-02 | G6-S006 (execution trace duplicate surfaces) | Duplicate execution-trace contract surfaces across L2/L3 need canonical contract ownership decision | L2/L3 owners + G7 traceability | yes |
| B7-G6-03 | G6-S009 (memory SQLite triplet) | Multiple candidate persistent memory sqlite stores create unresolved canonical-state ambiguity | memory owner + G4b config owner | yes |
| B7-G6-04 | G6-S013 (`role=other` cluster set) | 337 unresolved cross-cutting modules prevent fully crisp taxonomy closure without further decomposition | G6/G7 taxonomy owner | yes |
| B7-G6-05 | G6-S014 (ownership boundary ambiguity) | Operator-managed vs repo-managed boundary requires explicit per-surface ownership tagging in integrated map | G7 runtime map owner | yes |

## Non-blocking but tracked

| reference_surface | note |
|---|---|
| G6-S010 (`STORE-CHROMA-ARTEFACT`) | Vestigial vector registry; cleanup can occur post-G7 |
| G6-S011 (`bench:*`) | Orphan Redis namespace; operational cleanup item |
| G6-S012 (`_legacy_adg_archives`) | Legacy archive pruning item |
