# G6 — Dormant and Declared Surfaces

wave: G6
produced_at: 2026-04-18
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
adg_snapshot_timestamp: "04182026_0814"

## Scope

This file captures surfaces classified as:

- `dormant_but_intentional`
- `declared_not_wired`
- `orphan_vestigial`

## Records

### DORM-001 — `agentic_core/interfaces/` dormant subset

- surface_id: `G6-S002`
- path_or_surface: `agentic_core/interfaces/` (dormant subset, excluding live `gateway.py`, `mixins.py`, `spine.py`)
- current_role: boundary interface declarations
- observed_usage: concentrated app usage in only 3 files; remainder largely core-only or unused
- evidence: `docs/wave_g/G2_service_wiring/seam_usage_report.md`
- normalization_decision: `dormant_but_intentional`
- rationale: interface surface includes future/declarative contracts and live contracts; dormant subset retained intentionally
- downstream_owner: G6 taxonomy owner
- blocks_G7: no

### DECL-001 — Pinecone stub

- surface_id: `G6-S008`
- path_or_surface: `PINECONE_INDEX_NAME`, `EGRESS-PINECONE-STUB-01`
- current_role: provider config declaration without active wiring
- observed_usage: declared in maps; no runtime-critical wired path
- evidence: `docs/wave_g/G2b_provider_gateway/provider_inventory.md`, `docs/wave_g/G2b_provider_gateway/env_key_consumer_map.md`
- normalization_decision: `declared_not_wired`
- rationale: retain as explicit stub; do not treat as active provider surface
- downstream_owner: G2b/G7 provider mapping owner
- blocks_G7: no

### ORPH-001 — Legacy ADG archives

- surface_id: `G6-S012`
- path_or_surface: `artifacts/_legacy_adg_archives/`
- current_role: historical archive store
- observed_usage: no live reader/writer in active runtime
- evidence: `docs/wave_g/G4_storage_infra/storage_catalogue.yaml`
- normalization_decision: `orphan_vestigial`
- rationale: historical leftovers outside active runtime map
- downstream_owner: G4 storage owner
- blocks_G7: no

### ORPH-002 — Redis `bench:*`

- surface_id: `G6-S011`
- path_or_surface: Redis namespace `bench:*`
- current_role: benchmark residue
- observed_usage: orphan keyspace, no current runtime writer
- evidence: `docs/wave_g/G4_storage_infra/redis_namespace_map.md`
- normalization_decision: `orphan_vestigial`
- rationale: not part of active cache architecture
- downstream_owner: G4 storage owner
- blocks_G7: no

### ORPH-003 — Chroma artefact registry

- surface_id: `G6-S010`
- path_or_surface: `artifacts/chromadb/chroma.sqlite3`
- current_role: diagnostic/artefact vector registry
- observed_usage: 2 collections, no live runtime writer
- evidence: `docs/wave_g/G4_storage_infra/vector_collections.md`
- normalization_decision: `orphan_vestigial`
- rationale: vestigial side registry beside canonical vector store
- downstream_owner: G4 storage owner
- blocks_G7: no

### ORPH-004 — `agentic_core/L_CONTRACTS/`

- surface_id: `G6-S001`
- path_or_surface: `agentic_core/L_CONTRACTS/`
- current_role: intended layer-contract boundary
- observed_usage: effectively dead (only archived importer)
- evidence: `docs/wave_g/G2_service_wiring/seam_usage_report.md`
- normalization_decision: `orphan_vestigial`
- rationale: runtime-unwired contract surface should be treated as vestigial until explicit adoption
- downstream_owner: G7 traceability + architecture owner
- blocks_G7: yes
