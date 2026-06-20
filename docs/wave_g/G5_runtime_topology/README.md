# G5 — Deployment, Ops, and MCP Runtime Topology

## 1. Sub-wave ID, title, one-line purpose

**G5** — *Deployment, Ops, and MCP Runtime Topology*. Map how runtime surfaces are actually launched and operated (process boundaries, startup dependencies, transport modes, env injection classes, health probes, and failure domains).

## 2. Inputs

- ADG precondition verification:
  - `python tools/adg/adg_redis_ingest.py --check`
  - `adg_health`, `adg_status`, `adg_reload`
- ADG snapshot used in this wave:
  - `artifacts/adg/adg_indexed_04182026_0814.sqlite` (timestamp `04182026_0814`)
- Mandatory Wave G planning/runtime baselines:
  - `docs/wave_g/G0_full_runtime_plan/*`
  - `docs/wave_g/G1*/*`
  - `docs/wave_g/G2*/*`
  - `docs/wave_g/G3*/*`
  - `docs/wave_g/G4*/*`
  - `docs/wave_g/G4b_control_plane/*`
- Wave F baseline consumed:
  - `docs/wave_e/99_integration_v14/canonical/*` (preferred baseline present)
- Primary runtime surfaces inspected:
  - `.mcp.json`
  - `.codex/hooks.json`
  - `docs/archive/windsurf/legacy-tree/workflows/*.md`
  - `.codex/governance/scripts/*`
  - `tools/mcp/*`, `tools/adg/*`, `tools/memory/*`, `tools/retrieval/*`, `tools/otel/*`
  - `apps_*/__main__.py`, `apps_rg/bootstrap_runtime.py`, `apps_exec/_optional_agentic_core.py`
  - `.github/workflows/*.yml`, `.pre-commit-config.yaml`, `pytest.ini`
  - `ops_scripts/dev_tools/start_metrics_sidecar.py`

## 3. Outputs

- `README.md` — this index and execution status.
- `process_topology.yaml` — canonical runtime/process topology with required per-entry fields.
- `mcp_server_registry.md` — full 12-server registry, transport split, env classes, lifecycle notes.
- `startup_shutdown_dependencies.md` — startup/shutdown/restart sequencing and dependency ordering.
- `operator_workflows_and_hooks.md` — runtime-affecting workflows, hooks, CI gate surfaces.
- `failure_domains.md` — grouped failure domains and blast-radius boundaries.

## 4. Stop condition

Met.

- All mandatory runtime-topology families are covered:
  1. app runtime entrypoints and launch modes
  2. MCP server registry and transport modes
  3. local supporting services and daemons
  4. process dependency graph
  5. startup/shutdown/restart sequencing
  6. runtime env injection by process class
  7. operator workflows/hooks/CI gate surfaces
  8. health/readiness/freshness probes
  9. failure-domain boundaries
- `process_topology.yaml` includes required fields on every process entry:
  - `id`, `process_name`, `launch_mode`, `entrypoint`, `process_type`, `transport_mode`, `depends_on`, `stores_touched`, `pipelines_touched`, `env_classes_used`, `health_surfaces`, `restart_mode_if_known`, `notes`
- Transport/process distinctions are explicit:
  - in-process runtime
  - python stdio subprocess
  - node stdio subprocess
  - binary subprocess
  - localhost daemon/service
  - pure external endpoint
  - CI/hook/operator trigger surface
- Prior-wave reconciliations are explicitly consumed:
  - 12 MCP servers and `9 stdio / 2 binary / 1 external https` split
  - Redis as bridge dependency
  - ADG/memory/vector/OTel surfaces from G4
  - APP-RG and APP-EXEC bootstrap side-effect surfaces
  - kill-switch and process-start/import-time dependency effects from G4b

## 4a. Reconciled authoritative counts (source-of-truth aligned)

- Process/runtime surfaces (from `process_topology.yaml`): **27**
- MCP registry (from `mcp_server_registry.md`): **12 total**
  - **9** local stdio servers
  - **2** local binary-subprocess launchers
  - **1** pure external HTTPS endpoint
- Failure domains (from `failure_domains.md`): **8**
  - `FD-01` Core app runtime and orchestration
  - `FD-02` ADG canonical graph service
  - `FD-03` Redis bridge/cache
  - `FD-04` Vector retrieval/embedding
  - `FD-05` Observability/runtime-ADG
  - `FD-06` MCP transport/launcher
  - `FD-07` External endpoint
  - `FD-08` Governance/hook/CI enforcement
- Process category vocabulary (canonical from `process_topology.yaml`):
  - `in-process runtime`
  - `python stdio subprocess`
  - `node stdio subprocess`
  - `binary subprocess`
  - `localhost daemon/service`
  - `pure external endpoint`
  - `CI/hook/operator trigger surface`
- Ownership vocabulary reconciliation:
  - **repo-managed** = source-controlled runtime surfaces (repo Python MCPs, hooks/workflows/scripts)
  - **operator-managed** = local daemon lifecycle and external service/account boundary

## 5. Risks encountered during execution

- **Contract shape mismatch in G0**: `output_contracts.md` defines G5 only as `mcp_server_registry.yaml`, while this execution required a broader runtime-topology set and `process_topology.yaml` with stricter fields.
- **Dual-plane runtime ambiguity**: some surfaces exist both in-process and MCP subprocess path (for example, ADG/Redis/memory-related values), requiring explicit boundary labeling.
- **External/opaque subprocess behavior**: GitKraken and remote endpoints expose limited internal lifecycle semantics from repo-owned code.
- **Restart semantics incompleteness**: not every process class has explicit restart contracts in code; unknowns were preserved as `unknown` instead of inferred.

## 6. B7 candidates surfaced, if any

No net-new B7 candidate is introduced in this wave.

G5 records operationally-relevant ambiguity for future tracking but does not alter requirement graph scope.

## 7. Hand-off note for G6 and G7

### G6 hand-off (taxonomy cleanup)

- Use `process_topology.yaml` and `failure_domains.md` to classify and normalize:
  - operator-managed vs repo-managed ownership boundaries,
  - duplicated runtime responsibilities across MCP vs in-process surfaces,
  - bootstrap shim paths versus canonical runtime paths.

### G7 hand-off (integrated runtime map)

- Use this G5 process graph as the deployment/ops layer in `whole_system_runtime_map.md`.
- Bind process entries to v1.4 atoms/edges where relevant in `traceability_matrix.yaml`, especially around:
  - ADG freshness/health,
  - evaluation/exit/UWG path,
  - observability future-run learning boundaries,
  - runtime policy guard enforcement.

## G5 schema note

`output_contracts.md` includes a minimal G5 contract for `mcp_server_registry.yaml` only. Since this wave requires six artifacts and a process-level topology YAML, G5 uses an **extended stable schema** for `process_topology.yaml` with required fields listed in Stop Condition section 4. This extends (does not mutate) the G0 contract and keeps compatibility with existing G5 MCP contract intent.
