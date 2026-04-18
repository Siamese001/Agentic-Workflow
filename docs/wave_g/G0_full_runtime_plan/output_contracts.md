# Wave G — Output Contracts

Minimum schema/shape every G artefact must satisfy. YAML catalogues MUST validate against the schemas below before a sub-wave is considered complete.

## Universal requirements

Every artefact (YAML or Markdown) MUST state at the top:

```
wave: <G-sub-wave-id>
produced_at: <ISO-8601 date>
adg_snapshot: artifacts/adg/adg_indexed_<ts>.sqlite   # if ADG was used
upstream_artefacts:
  - <path to any G artefact this depends on>
```

## Component inventory schema (G1)

File: `G1_core_runtime_inventory/component_inventory.yaml`

```yaml
wave: G1
produced_at: YYYY-MM-DD
adg_snapshot: artifacts/adg/adg_indexed_<ts>.sqlite
components:
  - id: C-L1-00001                      # C-<layer>-<nnnnn>; stable within G1
    path: agentic_core/L1_cognition/reasoning/context_assembler.py
    layer: L1                           # L0..L6 or CROSS_CUTTING
    role: reasoner                      # see role enum below
    entry_points:
      - ContextAssembler.assemble_context
    exports: [ContextAssembler]
    imports_summary:
      intra_layer: 4
      cross_layer: [L0, L4]             # layers directly imported
      external: [infrastructure]
    seams_used: [SEAM-L1-CONTEXT]       # seam IDs from G1 seam registry
    embodies:
      atoms: [F04.01, F04.02, F04.03, F04.04]
      edges: []
      sources: [SRC-ADR-007]
    notes: ""
```

Role enum (exact values):
`agent | orchestrator | gate | evaluator | policy | healer | writer | reader | seam | interface | mixin | contract | adapter | runtime-scaffold | reasoner | validator | registry | util | shim | other`

Layer enum: `L0 | L1 | L2 | L3 | L4 | L5 | L6 | CROSS_CUTTING`

## App inventory schema (G1b)

File: `G1b_apps_inventory/app_inventory.yaml`

```yaml
wave: G1b
apps:
  - id: APP-RG
    path: apps_rg
    is_library_only: false             # apps_shared → true
    entry_points:
      - path: apps_rg/__main__.py
        kind: cli
      - path: apps_rg/bootstrap_runtime.py
        kind: runtime_bootstrap
    sub_surfaces:
      engines: apps_rg/engines
      reasoning: apps_rg/reasoning
      integrations: apps_rg/integrations
      services: null                    # if absent
      spine: null
      outputs: apps_rg/outputs
      validators: apps_rg/validators
      types: apps_rg/types
      tools: apps_rg/tools
      config: apps_rg/config
      tests: apps_rg/tests
    core_bindings:
      direct_imports_from:
        - agentic_core.L1_cognition.reasoning
        - agentic_core.L4_state.cache
      seam_uses:
        - SEAM-L1-CONTEXT
      adapter_shims:
        - apps_rg/bootstrap_runtime.py
    apps_shared_uses:
      - apps_shared.services.<module>
    data_and_outputs_paths:
      - apps_rg/outputs
    notes: ""
```

## Egress point schema (G2b)

File: `G2b_provider_gateway/egress_points.yaml`

```yaml
wave: G2b
egress_points:
  - id: EGRESS-OPENAI-01
    provider: openai                    # openai | anthropic | azure | local | ... | mcp-loopback
    protocol: https                     # https | ws | grpc | stdio | ipc
    module_path: infrastructure/sdks_mcps/client_wrappers.py
    consumer_modules:
      - agentic_core/L1_cognition/<...>
    auth_mode: api_key_env
    env_keys:                           # names only
      - OPENAI_API_KEY
    retry_posture:
      max_attempts: 3                   # per SRC-ADR-002 when applicable
      backoff: exponential
      circuit_breaker: false
    rate_limit_known: true
    notes: ""
```

## Pipeline catalogue schema (G3)

File: `G3_pipelines/pipeline_catalogue.yaml`

```yaml
wave: G3
pipelines:
  - id: PIPE-ADG-GEN
    title: "ADG full graph regeneration"
    triggers:
      - kind: cli
        command: python tools/generate_full_adg.py
      - kind: workflow
        name: /adg-redis-refresh
    inputs:
      - repo python source tree
    stages:
      - scan_repo
      - build_nodes
      - build_edges
      - write_sqlite
      - redis_ingest
    outputs:
      - artifacts/adg/adg_indexed_<ts>.sqlite
      - redis: adg:node:*
    terminal_condition: "sqlite snapshot written and adg_health returns healthy"
    source_modules:
      - tools/generate_full_adg.py
      - tools/adg/**
    embodies_atoms: []
    embodies_edges: []
    notes: ""
```

## Storage catalogue schema (G4)

File: `G4_storage_infra/storage_catalogue.yaml`

```yaml
wave: G4
stores:
  - id: STORE-ADG-SQLITE
    kind: sqlite                        # sqlite | redis | vector | disk_artefact | in_process_cache | other
    path_or_location: artifacts/adg/adg_indexed_<ts>.sqlite
    owner_module: tools/adg/mcp/server.py
    readers:
      - agentic_core/adg/**
      - mcp1_adg_* tools
    writers:
      - tools/generate_full_adg.py
    lifecycle:
      creation: "per ADG regeneration"
      retention: "latest N snapshots"
      invalidation: "full regeneration"
    schema_or_shape_ref: "tools/adg/schema.sql"  # or inline if small
    embodies_atoms: [F10.01, F10.02]
    notes: ""
```

## Config knob catalogue schema (G4b)

File: `G4b_control_plane/config_knob_catalogue.yaml`

```yaml
wave: G4b
knobs:
  - id: KNOB-TOKEN-BUDGET-DEFAULT
    plane: config_file                  # rule | config_file | env | flag | prompt
    source: config/token_budget.yaml
    key_path: default.max_tokens
    default: 16000
    consumers:
      - agentic_core/runtime/config/**
    scope: process
    reload_policy: restart
    embodies_atoms: []
    notes: ""
```

## MCP server registry schema (G5)

File: `G5_deployment_ops/mcp_server_registry.yaml`

```yaml
wave: G5
mcp_servers:
  - id: MCP-ADG-SQLITE
    stable_server_id: adg_sqlite
    transport: stdio                    # stdio | http | ws
    launch_command: "python -u -m tools.adg.mcp.server"
    env:
      ADG_DIR: ${AGENTIC_REPO_ROOT}/artifacts/adg
      ADG_REDIS_URL: redis://localhost:6379/0
    in_repo_source: tools/adg/mcp/server.py
    lifecycle:
      start: "Windsurf boots server from ~/.codeium/windsurf/mcp_config.json"
      health_probe: adg_health
      shutdown: "process exit"
    dependencies:
      - artifacts/adg/adg_indexed_<ts>.sqlite
      - redis (optional)
    hooks_related:
      - pre_mcp_gate
    notes: ""
```

## Traceability matrix schema (G7)

File: `G7_runtime_map/traceability_matrix.yaml`

```yaml
wave: G7
atoms_to_modules:
  - atom_id: F09.01
    embodying_modules:
      - agentic_core/L5_safety/<handoff>.py
      - agentic_core/L4_state/<uwg>.py
    gaps: []
edges_to_callchains:
  - edge_id: INT-F08.04-F09.01-01
    callchain:
      - agentic_core/evaluation/**
      - agentic_core/L5_safety/<GovernedHandoffAgent>
      - agentic_core/L4_state/<uwg write>
    gaps: []
unmatched:
  atoms: []                             # should be empty at G7 completion
  edges: []                             # should be empty at G7 completion
```

## B7 candidate register schema

File: `G7_runtime_map/b7_candidate_register.md` contains a table; one row per candidate:

| Candidate ID | Surfaced in sub-wave | Observed interaction | Proposed atom/edge | Surfaces |
|---|---|---|---|---|
| B7-G2-01 | G2 | apps_rg → L4_state direct read bypassing seam | New edge APP-RG→F10.02 | apps_rg/engines/X.py |

Candidate ID format: `B7-<sub-wave-id>-<NN>`.

## Validation checklist (per sub-wave)

Before a sub-wave is considered done, the owner MUST verify:

1. Every YAML file validates against its schema above (IDs unique; enum values valid; required fields present).
2. Every v1.3 atom/edge/source citation resolves to a real ID in `docs/wave_e/99_integration_v13/canonical/`.
3. Every file path citation resolves on disk.
4. The sub-wave README covers all 7 required sections.
5. Any surface deferred to G6 is listed in `unclassified_modules.md` (G1) / equivalent file (G1b) / `special_surface_classification.md` (G6).
6. ADG snapshot timestamp is recorded if ADG was used.
7. B7 candidates, if any, are cross-posted to `G7_runtime_map/b7_candidate_register.md` at the end of G7.
