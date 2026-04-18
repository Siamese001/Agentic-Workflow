# Wave G — Proposed Sub-Waves

11 sub-waves, executed in the order listed. Every sub-wave is sized to finish in one focused pass, produces a concrete artefact set, and has an explicit stop condition. Sub-wave IDs match the user's requested slicing.

Legend:
- **Scope** — exact boundaries
- **Surfaces** — repo paths that MUST be inspected
- **Outputs** — artefact files (relative to `docs/wave_g/<G-id>/`)
- **Reuses from E/F** — v1.3 canonical / F4 artefacts cited
- **Stop** — explicit stop condition
- **Risks** — top blind spots

---

## G1 — Core runtime component inventory

- **Scope**: Every Python module in `agentic_core/` is classified as one of: `{agent, orchestrator, gate, evaluator, policy, healer, writer, reader, seam, interface, mixin, contract, adapter, runtime-scaffold, util, shim, other}` with its owning layer (L0–L6 or cross-cutting) and top-level entry points (classes / module-level functions / singletons).
- **Surfaces**: `agentic_core/**/*.py` (all files), with ADG MCP used as the primary dependency probe. `agentic_core/L_CONTRACTS/`, `seams/`, `interfaces/`, `runtime/`, `base_agents/`, `agents/`, `mixins/` receive dedicated classification sections.
- **Outputs**:
  - `G1_core_runtime_inventory/README.md`
  - `G1_core_runtime_inventory/component_inventory.yaml` (structured per `output_contracts.md` §Node contract)
  - `G1_core_runtime_inventory/layer_embodiment_map.md` (L0–L6 atoms → concrete modules)
  - `G1_core_runtime_inventory/cross_cutting_classification.md` (runtime, agents, seams, mixins, contracts)
  - `G1_core_runtime_inventory/unclassified_modules.md` (feeds G6)
- **Reuses from E/F**: v1.3 atoms F02.01, F03.01, F05.01, F06.01, F07.01–04, F08.01–05, F09.01–05, F10.01–04, F11.01–07, F12.01–08 cited as embodiment anchors. `SCORE-F<NN>-INTEGRATION.yaml` tables referenced.
- **Stop**: Every `.py` under `agentic_core/` appears exactly once in `component_inventory.yaml` with a layer tag and role tag, OR is explicitly listed in `unclassified_modules.md`.
- **Risks**: (a) L5_safety and L2_execution are very large; role taxonomy must be stable before G2. (b) seams/interfaces may overlap — pick one owning classification per module. (c) agents vs base_agents duplication.

## G1b — apps_* runtime and adapter inventory

- **Scope**: Each of the 8 `apps_*` surfaces is inventoried for: entry points, sub-surface structure (engines / reasoning / integrations / services / spine / outputs / validators / types / tools), binding mechanism into `agentic_core` (direct import / seam / mixin / adapter), and per-app config/data/output paths. Adapter patterns (e.g., `apps_exec/_optional_agentic_core.py`, `apps_rg/bootstrap_runtime.py`) are called out as models.
- **Surfaces**: `apps_eval/**`, `apps_exec/**`, `apps_lic/**`, `apps_research/**`, `apps_rfp/**`, `apps_rg/**`, `apps_shared/**`, `apps_underwriting_ai/**` (code only; test content handled in G5).
- **Outputs**:
  - `G1b_apps_inventory/README.md`
  - `G1b_apps_inventory/app_inventory.yaml` (one entry per app, normalized schema)
  - `G1b_apps_inventory/app_to_core_bindings.md` (every cross-boundary import + seam use)
  - `G1b_apps_inventory/adapter_patterns.md` (bootstrap shims, optional-core shims)
  - `G1b_apps_inventory/apps_shared_as_library.md` (`apps_shared/` treated as library, not app)
- **Reuses from E/F**: F06.01 (L2 execution), F09.01 (UWG), F10.02 (L4 reads) — apps bind through these atoms.
- **Stop**: Every app has an entry in `app_inventory.yaml` with at least one entry point, at least one identified binding, and coverage of all sub-surfaces listed in §2 of `repo_surface_inventory.md`.
- **Risks**: (a) `apps_shared/` is not a runtime app — must not get an `__main__`-style entry. (b) `_optional_agentic_core.py` and `_compat/` shims may hide actual bindings. (c) apps may have undocumented direct imports into `L2_execution` / `L4_state` that should round-trip through seams.

## G2 — Service-to-service wiring and connectivity

- **Scope**: The import graph across L0–L6 and across app↔core boundaries, plus call-chain reconstruction for the canonical request lifecycle. Seams and interfaces are traced as the intended passthrough path; direct cross-layer imports are flagged.
- **Surfaces**: ADG MCP (primary), `agentic_core/seams/`, `agentic_core/interfaces/`, `agentic_core/L_CONTRACTS/`, plus ADG nodes for entry points identified in G1 / G1b.
- **Outputs**:
  - `G2_service_wiring/README.md`
  - `G2_service_wiring/import_edge_matrix.md` (layer × layer edge counts; direct-vs-seam breakdown)
  - `G2_service_wiring/canonical_request_walk.md` (admit → plan → route → orchestrate → execute → heal → exit → write)
  - `G2_service_wiring/seam_usage_report.md` (which seams are used, which are unused)
  - `G2_service_wiring/boundary_violations.md` (non-seam cross-layer imports)
- **Reuses from E/F**: v1.3 edges (all 26) cited as the intended wiring normative baseline. Layer-separation atoms (F02.02, F02.04, F02.05, F03.02, F05.02, F05.03, F06.03, F06.04).
- **Stop**: Every layer-to-layer edge in the ADG is classified as expected (covered by a v1.3 edge) / unexpected (candidate B7) / violation (direct cross-layer import bypassing a seam).
- **Risks**: (a) ADG snapshot staleness — re-generate before running via `/adg-redis-refresh`. (b) dynamic imports and `importlib` calls hide edges. (c) `infrastructure/`-mediated cycles.

## G2b — Provider / gateway / egress / auth boundary map

- **Scope**: External-facing boundaries. Every module that opens a socket, calls an LLM provider, signs an auth token, or reads a secret env var is inventoried. MCP servers are dual-classified (egress for providers, ingress for loopback).
- **Surfaces**: `agentic_core/gateway/`, `infrastructure/sdks_mcps/`, `infrastructure/sdks_mcps/client_wrappers.py`, `infrastructure/sdks_mcps/mcp_catalog/`, `tools/mcp/` (transport code), `tools/retrieval/`, `agentic_core/embeddings/`, `.env` key names, every `os.environ[...]` / `os.getenv(...)` read.
- **Outputs**:
  - `G2b_provider_gateway/README.md`
  - `G2b_provider_gateway/provider_inventory.md` (provider → SDK → consumer module)
  - `G2b_provider_gateway/egress_points.yaml` (each egress with protocol, auth mode, retry posture)
  - `G2b_provider_gateway/env_key_consumer_map.md` (env var NAME → consumer modules; no values)
  - `G2b_provider_gateway/mcp_as_transport.md` (MCP loopback analysis)
- **Reuses from E/F**: F01.02 (admission auth), F11.02 (L5 binds L0 routing) for policy binding of gateways.
- **Stop**: Every egress point has protocol + auth mode + retry posture recorded. Every env var read in the codebase appears in the map.
- **Risks**: (a) env vars read deep inside third-party SDK code (out-of-scope; document boundary). (b) silently-swallowed auth errors. (c) dynamic provider selection via feature flag.

## G3 — Pipelines and state transitions

- **Scope**: Named pipelines and state machines are documented end-to-end. Each pipeline has a trigger, an input, a set of stages, outputs, and a terminal state.
- **Surfaces**: `agentic_core/evaluation/`, `apps_eval/spine/`, `agentic_core/L3_orchestration/core/orchestrator_state_retry.py`, `agentic_core/L2_execution/**` healer code, `agentic_core/adg/`, `tools/adg/`, `tools/generate_full_adg.py`, `agentic_core/runtime/engine/`, `agentic_core/evaluation/**` exit-gate code.
- **Outputs**:
  - `G3_pipelines/README.md`
  - `G3_pipelines/pipeline_catalogue.yaml` (one entry per named pipeline)
  - `G3_pipelines/state_machines.md` (orchestrator retry state, healer retry state, exit-gate states)
  - `G3_pipelines/trigger_matrix.md` (CLI, test, hook, CI, operator, MCP)
- **Reuses from E/F**: SRC-ADR-002 (retry), SRC-ADR-003 (eval pipeline), SRC-ADR-005 (replay determinism), SRC-ADR-008 (L3), SRC-ADR-009 (escalation).
- **Stop**: Every pipeline in `pipeline_catalogue.yaml` has all of: trigger, stages (≥2), input/output shapes, terminal condition, source modules.
- **Risks**: (a) pipelines that span core + apps may be double-counted. (b) tests-as-pipelines — only the canonical test harness counts. (c) hidden chaining via subprocess.

## G3b — Replay / exit / evaluation / recovery traceability

- **Scope**: The evaluation-spine → exit-control-gate → UWG path, plus healing recovery and replay determinism. Produces the operator-facing trace contract: given a run_id, what artefacts exist, what paths they took.
- **Surfaces**: `agentic_core/evaluation/`, `apps_eval/spine/`, `apps_eval/services/`, `agentic_core/L5_safety/audit/`, `agentic_core/L6_observability/execution/`, `tools/otel/`, `agentic_core/tracing/`, heal modules under `agentic_core/L2_execution/`.
- **Outputs**:
  - `G3b_replay_exit_eval/README.md`
  - `G3b_replay_exit_eval/trace_contract.md` (per run_id → artefact set)
  - `G3b_replay_exit_eval/exit_gate_path.md` (Exit spine module path)
  - `G3b_replay_exit_eval/healing_path.md` (RetryConfig realization)
  - `G3b_replay_exit_eval/replay_determinism_path.md` (ExecutionTrace / mutation_hash)
- **Reuses from E/F**: SRC-ADR-003, SRC-ADR-005, SRC-ADR-002, SRC-ADR-008, SRC-ADR-009. Atoms F07.01–04, F08.01–05, F09.04–05, F12.01–08. Edges INT-F08.04-F09.01-01, INT-F09.05-F08.04-01 (both now NORMATIVE in v1.4).
- **Stop**: Each of the four paths (exit, healing, replay, evaluation) has a code-grounded walkthrough with entry module, state transitions, and write/record points named.
- **Risks**: (a) `GovernedHandoffAgent` may have multiple implementers — find canonical. (b) ExecutionTrace signing surface scattered.

## G4 — Storage and infrastructure topology

- **Scope**: Every persistent or caching surface: SQLite (ADG + any app-scoped), Redis (namespaces + TTLs + cache policies), vector DBs (collections + embeddings provider), disk artefacts (`artifacts/`, `data/`, `logs/`, `system_learning/`). Each entry records owner, lifetime, invalidation policy, reader/writer modules.
- **Surfaces**: `artifacts/`, `data/`, `logs/`, `test_artifacts/`, `system_learning/`, `agentic_core/L4_state/cache/`, `agentic_core/L4_state/memory/`, `agentic_core/cache/`, `agentic_core/case_memory/`, `agentic_core/knowledge/`, `tools/graphdb/`, `tools/mcp/redis_mcp/`, `tools/mcp/vector_db_server.py`, `tools/retrieval/`, `infrastructure/`, `.backup/`.
- **Outputs**:
  - `G4_storage_infra/README.md`
  - `G4_storage_infra/storage_catalogue.yaml` (one entry per store; shape in `output_contracts.md`)
  - `G4_storage_infra/redis_namespace_map.md`
  - `G4_storage_infra/vector_collections.md`
  - `G4_storage_infra/artefact_lifecycle.md`
- **Reuses from E/F**: F09.01–05 (UWG sole writer), F10.01–04 (L4 authority), INT-F10.03-F09.01-01.
- **Stop**: Every store has owner, schema-or-shape, lifecycle, readers, writers named. No store is classified as "?".
- **Risks**: (a) transient on-disk SQLite files (per-test) may skew counts. (b) Redis namespaces overlap. (c) `system_learning/` shape is under-documented.

## G4b — Config / prompts / rules / env / feature-flag control plane

- **Scope**: Every knob that tunes runtime behaviour at start or request time. Organized into four planes: (i) constitutional rules + AGENTS.md, (ii) config files (YAML/JSON/TOML), (iii) env vars + feature flags, (iv) prompts / prompt-governance surfaces.
- **Surfaces**: `.windsurf/rules/`, `.windsurf/skills/`, `AGENTS.md`, `config/`, `agentic_core/config/`, `agentic_core/runtime/config/`, `apps_*/config/`, `.env` (key names), `agentic_core/prompt_governance/`, `apps_shared/prompts/`, any `os.getenv` consumer surfaced by G2b.
- **Outputs**:
  - `G4b_control_plane/README.md`
  - `G4b_control_plane/rules_and_skills_map.md` (rule → enforcer)
  - `G4b_control_plane/config_knob_catalogue.yaml` (one entry per knob; plane, default, consumer, scope, reload policy)
  - `G4b_control_plane/env_and_flags.md` (env keys + feature flags with consumers)
  - `G4b_control_plane/prompt_surface_map.md` (prompt files + governance rules)
- **Reuses from E/F**: F11.01 (L5 authority), F11.04 (L5 binds UWG), SRC-RULE-001 / SRC-RULE-002 / SRC-INT-001 / SRC-INT-004.
- **Stop**: Every rule in `.windsurf/rules/` is mapped to an enforcer. Every top-level config file has consumers listed. Every `.env` key name appears in `env_and_flags.md`.
- **Risks**: (a) prompt governance may be distributed across core and apps. (b) some rules are doctrine-only with no code enforcer — flag explicitly. (c) env vars used only in CI workflows.

## G5 — Deployment / MCP / hooks / ops-scripts / CI topology

- **Scope**: The operational envelope: MCP servers (process lifecycle), hooks, ops scripts, CI workflows, pre-commit, pytest orchestration. Deployment here is "what runs where when an operator starts the system", not cloud IaC.
- **Surfaces**: `tools/mcp/`, `tools/adg/mcp/`, `.windsurf/mcp_config.json`, `.windsurf/hooks.json`, `.windsurf/scripts/`, `.windsurf/workflows/`, `ops_scripts/`, `.github/`, `pyproject.toml`, `pytest.ini`, `conftest.py`, `.pre-commit-config.yaml`.
- **Outputs**:
  - `G5_deployment_ops/README.md`
  - `G5_deployment_ops/mcp_server_registry.yaml` (server → transport → launch cmd → env → lifecycle)
  - `G5_deployment_ops/hooks_map.md`
  - `G5_deployment_ops/ops_scripts_inventory.md` (grouped by `ops_scripts/*` subfolder; role per script)
  - `G5_deployment_ops/ci_topology.md` (GitHub Actions + pre-commit + pytest + guardian gates)
  - `G5_deployment_ops/startup_shutdown.md` (process start → health → shutdown)
  - `G5_deployment_ops/operator_playbook_index.md` (workflow slash-commands)
- **Reuses from E/F**: SRC-RULE-001 / SRC-RULE-002 + any ADR-003 wiring touching CI.
- **Stop**: Every MCP server in `.windsurf/mcp_config.json` appears in `mcp_server_registry.yaml` with transport and launch command. Every `ops_scripts/*` script has a one-line role.
- **Risks**: (a) global MCP config is ~/.codeium shadow; in-repo is source — note this divergence explicitly. (b) hooks.json vs .bak; ignore .bak. (c) some ops scripts are orphaned — mark "no known caller".

## G6 — Taxonomy cleanup / special-surface normalization

- **Scope**: Surfaces that didn't fit cleanly in G1–G5. Each surface is classified (runtime / infra / legacy / compat / scratch / doc-only). Duplicated-responsibility pairs are flagged with a proposed canonical owner — *without* refactoring.
- **Surfaces**: `agentic_core/cloud_native/`, `agentic_core/case_memory/`, `agentic_core/embeddings/`, `agentic_core/visualization/`, `agentic_core/utils/`, `agentic_core/_compat/`, `agentic_core/core/`, `tools/debug/`, `.backup/`, `templates/`, `_compat/` directories across apps, `unclassified_modules.md` carry-over from G1 and G1b.
- **Outputs**:
  - `G6_taxonomy_cleanup/README.md`
  - `G6_taxonomy_cleanup/special_surface_classification.md`
  - `G6_taxonomy_cleanup/duplicate_responsibility_register.md`
  - `G6_taxonomy_cleanup/proposed_consolidation_followups.md` (proposals only; no edits)
- **Reuses from E/F**: none directly; references the v1.3 layer model only.
- **Stop**: Every surface deferred by an earlier sub-wave has a classification verdict. Every duplicate-responsibility pair has a proposed canonical owner documented.
- **Risks**: (a) temptation to consolidate during cleanup — forbidden here. (b) `_compat/` may hide dead code. (c) `system_learning/` straddles G4 and G6.

## G7 — Final integrated whole-system runtime map

- **Scope**: Integration artefact. Combines outputs of G1–G6 into a single walkable map of the whole runtime: operator trigger → admit → plan → route → orchestrate → execute → heal → evaluate → exit → UWG → L4 persist → L6 observe → memory write-back, overlaid with the component inventory (G1/G1b), wiring (G2/G2b), pipelines (G3/G3b), storage (G4), control plane (G4b), and ops envelope (G5).
- **Surfaces**: No fresh code inspection; integrates G1–G6 artefacts plus v1.3 canonical + F4 cleanup.
- **Outputs**:
  - `G7_runtime_map/README.md`
  - `G7_runtime_map/whole_system_runtime_map.md` (the integrated map, prose + diagram-in-markdown)
  - `G7_runtime_map/traceability_matrix.yaml` (v1.3 atom ID → embodying modules; v1.3 edge ID → embodying call-chain)
  - `G7_runtime_map/b7_candidate_register.md` (B7 candidates surfaced across G1–G6)
  - `G7_runtime_map/operational_flow_walkthrough.md` (end-to-end walk with code citations)
  - `G7_runtime_map/open_questions.md` (anything still unresolved)
- **Reuses from E/F**: v1.3 full atom/edge set; F4 edge upgrades (all NORMATIVE in v1.4).
- **Stop**: The traceability matrix covers every v1.3 atom and every v1.3 edge. The operational flow walkthrough cites concrete modules from G1/G1b for each stage. B7 candidate register captures every B7 signal noted in earlier sub-waves.
- **Risks**: (a) risk of theory drift in the final prose — enforce "every claim cites a G1–G6 artefact or a v1.3 ID". (b) B7 candidates get quietly absorbed into theory — they must stay labelled. (c) diagram complexity; prefer multiple simple maps over one mega-diagram.

---

## Minimum-set answer

**All 11 sub-waves are mandatory.** Cutting any one leaves a concrete gap against the user's listed dimensions:

| User dimension | Sub-wave |
|---|---|
| 1. Runtime component inventory (core) | G1 |
| 2. apps_* inventory | G1b |
| 3. Service-to-service wiring | G2 |
| 4. Provider / gateway / egress / auth | G2b |
| 5. Pipelines and state transitions | G3 |
| 6. Replay / exit / eval / recovery | G3b |
| 7. Storage and infra topology | G4 |
| 8. Config / prompts / rules / env / flags | G4b |
| 9. Deployment / MCP / hooks / ops / CI | G5 |
| 10. Unknown taxonomy / special surfaces | G6 |
| 11. Final integrated map | G7 |

No sub-wave may be skipped. Merging G1+G1b, G2+G2b, G3+G3b, or G4+G4b is rejected — each pair has distinct surfaces and distinct skill requirements. G6 is mandatory because G1 and G1b will produce non-empty `unclassified_modules.md`.
