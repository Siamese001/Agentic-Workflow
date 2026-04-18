# G6 — Normalization Matrix

wave: G6
produced_at: 2026-04-18
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
adg_snapshot_timestamp: "04182026_0814"

## Canonical decision enum

- `canonical`
- `tolerated_special_case`
- `dormant_but_intentional`
- `declared_not_wired`
- `duplicate_needing_resolution`
- `orphan_vestigial`
- `ambiguous_needing_followup`

## Candidate matrix

| surface_id | path_or_surface | current_role | observed_usage | evidence | normalization_decision | rationale | downstream_owner | blocks_G7 |
|---|---|---|---|---|---|---|---|---|
| G6-S001 | `agentic_core/L_CONTRACTS/` | layer-contract surface | 4 modules, only 1 archived importer, 0 live app/core import path | `docs/wave_g/G2_service_wiring/seam_usage_report.md` | orphan_vestigial | Runtime-effective dead surface in current topology; should not be treated as live boundary seam until wired | G7 traceability + architecture owner | yes |
| G6-S002 | `agentic_core/interfaces/` (dormant subset) | boundary interface surface | 38 modules, heavy usage concentrated in 3 files (`gateway.py`, `mixins.py`, `spine.py`) | `docs/wave_g/G2_service_wiring/seam_usage_report.md` | dormant_but_intentional | Surface contains a live core plus dormant declarations; retain but mark dormant remainder explicitly | G6 follow-up taxonomy owner | no |
| G6-S003 | `agentic_core/seams/` | core-internal seam surface | 41 inbound imports, 0 app imports | `docs/wave_g/G2_service_wiring/seam_usage_report.md` | canonical | Current intended runtime role is core-internal cross-layer seam, not app boundary | G7 runtime map owner | no |
| G6-S004 | `apps_exec/_optional_agentic_core.py` | compatibility shim | Activated only when `agentic_core` unavailable; synthesizes modules in `sys.modules` | `docs/wave_g/G1b_apps_inventory/adapter_patterns.md` | tolerated_special_case | Required for standalone compatibility posture; explicitly non-canonical for full-stack runtime | APP-EXEC owner | no |
| G6-S005 | `apps_rg/bootstrap_runtime.py` | bootstrap shim | startup import side-effect path used before main dispatch | `docs/wave_g/G1b_apps_inventory/adapter_patterns.md`, `docs/wave_g/G5_runtime_topology/process_topology.yaml` | tolerated_special_case | Additive environment bootstrap for flagship app; keep with explicit label as special-case startup path | APP-RG owner | no |
| G6-S006 | `agentic_core/L2_execution/types/execution_trace_types.py` + `agentic_core/L3_orchestration/types/execution_trace_types.py` | execution-trace contract duplication | both live; duplicate semantic surface | `docs/wave_g/G2_service_wiring/seam_usage_report.md` | duplicate_needing_resolution | Duplicate contract surfaces increase taxonomy ambiguity and traceability friction | G7 traceability + L2/L3 owners | yes |
| G6-S007 | lifecycle-trace compatibility surfaces (`apps_rfp/_compat/lifecycle_trace.py`, `apps_shared/_compat/agentic_core_shim.py`) | compatibility trace facade | used only in compatibility/standalone branch | `docs/wave_g/G1b_apps_inventory/adapter_patterns.md` | tolerated_special_case | Necessary for standalone mode; must remain labeled as compatibility-only | APP-RFP + APPS_SHARED owners | no |
| G6-S008 | `PINECONE_INDEX_NAME` + `EGRESS-PINECONE-STUB-01` | declared provider stub | key declared in config maps; no active wired runtime pipeline | `docs/wave_g/G2b_provider_gateway/provider_inventory.md`, `docs/wave_g/G2b_provider_gateway/env_key_consumer_map.md` | declared_not_wired | Explicitly declared-but-not-wired surface; keep as stub, do not classify as active egress | G2b/G7 provider mapping owner | no |
| G6-S009 | memory SQLite triplet (`artifacts/memory/knowledge_graph.sqlite`, `data/memory/knowledge_graph.sqlite`, `data/memory/unified_memory.db`) | persistent memory store family | canonical + duplicate + ambiguous third file | `docs/wave_g/G4_storage_infra/storage_catalogue.yaml`, `artefact_lifecycle.md` | duplicate_needing_resolution | Multiple candidate files for same role create topology ambiguity for G7 mapping | G4b config owner + memory owner | yes |
| G6-S010 | `artifacts/chromadb/chroma.sqlite3` (artefact registry) | diagnostic vector registry | 2 collections (`docs`, `traces`), no live runtime writer | `docs/wave_g/G4_storage_infra/vector_collections.md` | orphan_vestigial | Vestigial registry separate from canonical `data/cache/chromadb`; keep flagged for cleanup wave | G4 storage owner | no |
| G6-S011 | Redis namespace `bench:*` | benchmark namespace residue | orphan keyspace; no current runtime writer | `docs/wave_g/G4_storage_infra/redis_namespace_map.md` | orphan_vestigial | Legacy benchmark residue; should not be counted as runtime cache contract | G4 storage owner | no |
| G6-S012 | `artifacts/_legacy_adg_archives/` | historical ADG archive | no live readers/writers in active runtime | `docs/wave_g/G4_storage_infra/storage_catalogue.yaml` | orphan_vestigial | Legacy archive surface kept as historical storage only; exclude from active runtime taxonomy | G4 storage owner | no |
| G6-S013 | G1 `role=other` cross-cutting clusters (337 modules across 99 clusters) | unresolved cross-cutting taxonomy | broad residual taxonomy bucket remains | `docs/wave_g/G1_core_runtime_inventory/unclassified_modules.md` | ambiguous_needing_followup | Too broad to normalize without downstream per-cluster decomposition; keep explicit follow-up ownership | G6/G7 taxonomy owner | yes |
| G6-S014 | operator-managed vs repo-managed boundaries (Redis daemon, external endpoints, GitKraken binary) | ownership boundary surface | split documented but still mixed wording across waves | `docs/wave_g/G5_runtime_topology/*.md` | ambiguous_needing_followup | Needs final G7 map-level explicit ownership tags to avoid operational responsibility drift | G7 runtime map owner | yes |

## Decision tally

| normalization_decision | count |
|---|---:|
| canonical | 1 |
| tolerated_special_case | 3 |
| dormant_but_intentional | 1 |
| declared_not_wired | 1 |
| duplicate_needing_resolution | 2 |
| orphan_vestigial | 4 |
| ambiguous_needing_followup | 2 |
| **total** | **14** |
