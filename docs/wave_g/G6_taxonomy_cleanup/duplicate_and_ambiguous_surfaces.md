# G6 — Duplicate and Ambiguous Surfaces

wave: G6
produced_at: 2026-04-18
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
adg_snapshot_timestamp: "04182026_0814"

## Scope

This file captures surfaces classified as:

- `duplicate_needing_resolution`
- `ambiguous_needing_followup`

## Duplicate surfaces

### DUP-001 — Execution trace type duplication

- surface_id: `G6-S006`
- path_or_surface:
  - `agentic_core/L2_execution/types/execution_trace_types.py`
  - `agentic_core/L3_orchestration/types/execution_trace_types.py`
- current_role: execution trace contract/type surfaces
- observed_usage: both live in active layer trees
- evidence: `docs/wave_g/G2_service_wiring/seam_usage_report.md`
- normalization_decision: `duplicate_needing_resolution`
- rationale: parallel type-contract surfaces increase cross-layer ambiguity for G7 traceability
- downstream_owner: L2/L3 owners + G7 traceability owner
- blocks_G7: yes

### DUP-002 — Memory SQLite triplet

- surface_id: `G6-S009`
- path_or_surface:
  - `artifacts/memory/knowledge_graph.sqlite`
  - `data/memory/knowledge_graph.sqlite`
  - `data/memory/unified_memory.db`
- current_role: persistent memory store family
- observed_usage: canonical default plus duplicate and ambiguous third db path
- evidence: `docs/wave_g/G4_storage_infra/storage_catalogue.yaml`, `docs/wave_g/G4_storage_infra/artefact_lifecycle.md`
- normalization_decision: `duplicate_needing_resolution`
- rationale: multiple candidate persistent stores for one conceptual surface
- downstream_owner: memory owner + G4b config owner
- blocks_G7: yes

## Ambiguous surfaces

### AMB-001 — G1 cross-cutting `role=other` clusters

- surface_id: `G6-S013`
- path_or_surface: 337 modules across 99 clusters from `unclassified_modules.md`
- current_role: unresolved cross-cutting taxonomy
- observed_usage: broad residual `other` role bucket
- evidence: `docs/wave_g/G1_core_runtime_inventory/unclassified_modules.md`
- normalization_decision: `ambiguous_needing_followup`
- rationale: insufficiently granular classification to close whole-system taxonomy cleanly without deeper decomposition
- downstream_owner: G6/G7 taxonomy owner
- blocks_G7: yes

### AMB-002 — Operator-managed vs repo-managed ownership boundaries

- surface_id: `G6-S014`
- path_or_surface: G5 ownership splits across Redis daemon, external endpoints, GitKraken, repo MCP/hooks
- current_role: runtime ownership boundary model
- observed_usage: split is documented but requires final map-level formalization to avoid overlap
- evidence: `docs/wave_g/G5_runtime_topology/README.md`, `mcp_server_registry.md`, `operator_workflows_and_hooks.md`
- normalization_decision: `ambiguous_needing_followup`
- rationale: ownership boundary remains partly narrative; requires explicit per-surface ownership tags in G7 integrated map
- downstream_owner: G7 runtime map owner
- blocks_G7: yes
