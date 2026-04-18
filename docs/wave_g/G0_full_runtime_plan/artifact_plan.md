# Wave G — Artifact Plan

Canonical output layout and naming for every G sub-wave. All G artefacts live under `docs/wave_g/`. No G writes occur outside that subtree.

## Directory layout

```
docs/wave_g/
  G0_full_runtime_plan/              (this wave — planning)
    README.md
    runtime_scope_map.md
    repo_surface_inventory.md
    proposed_subwaves.md
    artifact_plan.md                 (this file)
    output_contracts.md
    dependency_and_risk_register.md
    wave_g_execution_plan.md

  G1_core_runtime_inventory/
    README.md
    component_inventory.yaml
    layer_embodiment_map.md
    cross_cutting_classification.md
    unclassified_modules.md

  G1b_apps_inventory/
    README.md
    app_inventory.yaml
    app_to_core_bindings.md
    adapter_patterns.md
    apps_shared_as_library.md

  G2_service_wiring/
    README.md
    import_edge_matrix.md
    canonical_request_walk.md
    seam_usage_report.md
    boundary_violations.md

  G2b_provider_gateway/
    README.md
    provider_inventory.md
    egress_points.yaml
    env_key_consumer_map.md
    mcp_as_transport.md

  G3_pipelines/
    README.md
    pipeline_catalogue.yaml
    state_machines.md
    trigger_matrix.md

  G3b_replay_exit_eval/
    README.md
    trace_contract.md
    exit_gate_path.md
    healing_path.md
    replay_determinism_path.md

  G4_storage_infra/
    README.md
    storage_catalogue.yaml
    redis_namespace_map.md
    vector_collections.md
    artefact_lifecycle.md

  G4b_control_plane/
    README.md
    rules_and_skills_map.md
    config_knob_catalogue.yaml
    env_and_flags.md
    prompt_surface_map.md

  G5_deployment_ops/
    README.md
    mcp_server_registry.yaml
    hooks_map.md
    ops_scripts_inventory.md
    ci_topology.md
    startup_shutdown.md
    operator_playbook_index.md

  G6_taxonomy_cleanup/
    README.md
    special_surface_classification.md
    duplicate_responsibility_register.md
    proposed_consolidation_followups.md

  G7_runtime_map/
    README.md
    whole_system_runtime_map.md
    traceability_matrix.yaml
    b7_candidate_register.md
    operational_flow_walkthrough.md
    open_questions.md
```

## File-type rules

| Extension | Used for | Constraint |
|---|---|---|
| `.md` | Narrative + tables | Markdown only; no embedded HTML unless absolutely required |
| `.yaml` | Structured data (inventories, catalogues, registries, matrices) | Must validate against the per-artefact contract in `output_contracts.md` |

## Required README shape (every sub-wave)

Every `<Gx>/README.md` MUST contain, in order:
1. Sub-wave ID, title, and one-line purpose.
2. Inputs (surfaces inspected, upstream G artefacts consumed, v1.3 / F4 references).
3. Outputs (this directory's files, with one-line purpose each).
4. Stop condition (exact criterion, re-stated verbatim from `proposed_subwaves.md`).
5. Risks encountered during execution (not the pre-planning risks; actual ones).
6. B7 candidates surfaced (if any).
7. Hand-off note (what the next dependent sub-wave can now proceed with).

## Naming discipline

- Sub-wave directory names match the IDs in `proposed_subwaves.md` exactly (`G1_core_runtime_inventory`, `G1b_apps_inventory`, etc.).
- YAML catalogue files use plural, snake_case nouns (`component_inventory.yaml`, `pipeline_catalogue.yaml`).
- No versioning suffixes (`_v2`, `_final`) inside filenames. Rework a file in place.
- B7 candidate references use the format `B7-<Gx>-NN` (e.g., `B7-G2-01`) and are recorded in both the originating sub-wave and the central `G7_runtime_map/b7_candidate_register.md`.

## Cross-referencing discipline

- Within a sub-wave, cite v1.3 atom/edge/source IDs directly (`F09.01`, `INT-F08.04-F09.01-01`, `SRC-ADR-003`).
- When a runtime fact maps to a v1.3 ID, state the mapping explicitly: `embodies: F09.01 (Universal Write Gate)`.
- When no v1.3 ID applies, state: `no v1.3 mapping` and consider a B7 candidate entry.
- Cite concrete code locations as `path/to/module.py:ClassName.method_name` (no line numbers — ADG drift risk).

## Prohibited content

- No edits to `docs/wave_e/` (Wave E/F is closed).
- No edits to `docs/wave_g/G0_full_runtime_plan/` after G0 completes except to correct factual errors (which MUST also record a timestamped erratum in the affected file).
- No atom / edge / source authoring.
- No refactor proposals embedded in G1–G5 artefacts. All consolidation proposals live in `G6_taxonomy_cleanup/proposed_consolidation_followups.md`.
- No secret values, no `.env` contents — only key names.

## Size discipline

Target per artefact:
- YAML catalogues: as large as needed; every entry MUST conform to the contract schema.
- Markdown narratives: keep under ~600 lines; split by concern if larger. Prefer multiple files over mega-documents.
- READMEs: under ~200 lines.

## Regeneration rule

Artefacts in G1–G6 that depend on ADG queries MUST note the ADG snapshot timestamp used (`artifacts/adg/adg_indexed_<ts>.sqlite`). If a subsequent sub-wave re-generates ADG, earlier artefacts do not need re-running unless their specific surface changed.
