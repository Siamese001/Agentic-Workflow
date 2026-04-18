# G6 — Special Surface Decisions

wave: G6
produced_at: 2026-04-18
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
adg_snapshot_timestamp: "04182026_0814"

## Scope

This file captures surfaces classified as:

- `canonical`
- `tolerated_special_case`

## Canonical decision

### SPEC-001 — `agentic_core/seams/` as core-internal seam system

- surface_id: `G6-S003`
- path_or_surface: `agentic_core/seams/`
- current_role: cross-layer seam contract within core runtime
- observed_usage: 41 inbound imports, 0 app imports
- evidence: `docs/wave_g/G2_service_wiring/seam_usage_report.md`
- normalization_decision: `canonical`
- rationale: current runtime architecture uses seams as internal core boundary, not app-facing boundary
- downstream_owner: G7 runtime map owner
- blocks_G7: no

## Tolerated special cases

### SPEC-002 — APP-EXEC optional agentic_core shim

- surface_id: `G6-S004`
- path_or_surface: `apps_exec/_optional_agentic_core.py`
- current_role: standalone compatibility shim
- observed_usage: activated when core package unavailable; synthesizes selected modules in `sys.modules`
- evidence: `docs/wave_g/G1b_apps_inventory/adapter_patterns.md`
- normalization_decision: `tolerated_special_case`
- rationale: intentional compatibility path for standalone operation
- downstream_owner: APP-EXEC owner
- blocks_G7: no

### SPEC-003 — APP-RG bootstrap runtime shim

- surface_id: `G6-S005`
- path_or_surface: `apps_rg/bootstrap_runtime.py`
- current_role: startup bootstrap and compatibility preparation
- observed_usage: import side-effect prior to main dispatch
- evidence: `docs/wave_g/G1b_apps_inventory/adapter_patterns.md`, `docs/wave_g/G5_runtime_topology/process_topology.yaml`
- normalization_decision: `tolerated_special_case`
- rationale: additive bootstrap complexity accepted as app-specific runtime prerequisite
- downstream_owner: APP-RG owner
- blocks_G7: no

### SPEC-004 — Lifecycle trace compatibility facades

- surface_id: `G6-S007`
- path_or_surface:
  - `apps_rfp/_compat/lifecycle_trace.py`
  - `apps_shared/_compat/agentic_core_shim.py`
- current_role: compatibility fallback trace interface
- observed_usage: fallback branch in standalone/compat mode
- evidence: `docs/wave_g/G1b_apps_inventory/adapter_patterns.md`
- normalization_decision: `tolerated_special_case`
- rationale: preserve compatibility without treating as canonical runtime contract owner
- downstream_owner: APP-RFP + APPS_SHARED owners
- blocks_G7: no
