# G4b — Control Plane and Config-Knob Catalogue

## 1. Sub-wave ID, title, one-line purpose

**G4b** — *Control Plane and Config-Knob Catalogue*. Map runtime behavior controls (env keys, flags, tunables, path overrides, store binders, MCP-injected runtime env) with observable defaults, read-time, reload semantics, risk ranking, and cross-links to G3 pipelines and G4 stores.

## 2. Inputs

- ADG health/status probes: `adg_health` + `adg_status` + Redis hot sentinel check.
- ADG snapshot used throughout: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (`04172026_0611`).
- G0 contracts and planning: especially `output_contracts.md` (G4b schema baseline) and scope map.
- G2b baselines: `env_key_consumer_map.md`, `provider_inventory.md`, `egress_points.yaml`, `mcp_as_transport.md`.
- G3 baselines: `pipeline_catalogue.yaml`, `trigger_matrix.md`, `state_machines.md`, `reconciliation_report.md`.
- G4 baselines: `storage_catalogue.yaml`, `redis_namespace_map.md`, `vector_collections.md`, `artefact_lifecycle.md`.
- Source readers for defaults/read semantics:
  - `tools/retrieval/vector_config.py`
  - `tools/memory/{adg_memory_server.py, sqlite_memory_store.py, purge_sync.py}`
  - `tools/adg/{adg_redis_ingest.py, core/service.py}`
  - `agentic_core/L2_execution/enforcement/network_egress_guard.py`
  - `agentic_core/L0_routing/enforcement/runtime_mutation_guard.py`
  - `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py`
  - `agentic_core/config/constants_config.py`
  - `.windsurf/mcp_config.json`

## 3. Outputs

- `config_knob_catalogue.yaml` — canonical knob catalogue (required G4b artifact).
- `defaults_and_reload_policy.md` — observable defaults + reload semantics.
- `kill_switches_and_risk.md` — ranked kill-switch and policy-bypass risk map.
- `secret_and_auth_binding_map.md` — secret/auth key bindings and hygiene map.
- `README.md` — this index.

## 4. Stop condition

Met.

- Major runtime control families are catalogued:
  - provider config
  - secret/auth binding
  - runtime tunables/thresholds
  - feature flags/kill-switches
  - path/store-binding overrides
  - bootstrap/import-time toggles
  - MCP-injected runtime env
- Required hand-off keys from G4 are explicitly covered: `MEMORY_DB`, `VECTOR_DB_CHROMA_PATH`, `REDIS_HOST/PORT/DB/PASSWORD/URL`, `ADG_REDIS_URL`, `ADG_DIR`, `ADG_SKIP_REDIS`, `ADG_SKIP_GIT`, `ADG_SKIP_SELF_TEST`, `VECTOR_DB_ALLOW_MODEL_DOWNLOAD`, `HF_HUB_OFFLINE`, `BGE_ALLOW_MODEL_DOWNLOAD`, and the `VECTOR_DB_*` timeout/budget knobs.
- G2b risk keys are explicitly covered: `EGRESS_GUARD_DISABLED`, `DISABLE_RUNTIME_MUTATION_GUARD`, `SOVEREIGN_AUTO_APPROVE`, Pinecone declared-not-wired surface.
- Every catalogue entry records required fields: `id`, `key_name`, `class`, `default_value_if_observable`, `consumer_modules`, `affects_pipelines`, `affects_stores`, `read_time`, `reload_behavior`, `risk_level`, `notes`.
- Reload semantics are classified using required enum: `import_time`, `process_start`, `per_call`, `lazy_first_use`, `unknown`.
- G3 pipeline IDs and G4 store IDs are cross-linked in the catalogue.

## 5. Risks encountered during execution

- **Default observability is uneven**: many keys are listed in G2b env map but not read via direct `os.getenv("KEY", default)` in the same module; some defaults remain `unknown` by design.
- **Dual execution planes**: a subset of keys exists both as in-process readers and MCP subprocess env injection (`MEMORY_DB`, `VECTOR_DB_CHROMA_PATH`, `ADG_REDIS_URL`), so effective behavior depends on where the call executes.
- **Kill-switch asymmetry**: `SOVEREIGN_AUTO_APPROVE` is ignored by `hitl_gate.py` / `exit_control_hitl.py` but active in `archival_gatekeeper_gate.py`; this requires operator clarity.
- **Store-binding ambiguity inherited from G4**: `MEMORY_DB` can point to three SQLite candidates (B7-G4-03).
- **Declared-not-wired controls**: Pinecone key is present as config stub but no runtime import path.

## 6. B7 candidates surfaced, if any

No net-new B7 candidate introduced in G4b.

This wave operationalizes existing items only:
- `B7-G2b-06` (`EGRESS_GUARD_DISABLED` audit gap)
- `B7-G4-03` (`MEMORY_DB` multi-store ambiguity)
- `B7-G4-07` (Redis posture/discipline context)

## 7. Hand-off note for G5 and G6

### G5 hand-off (deployment/MCP ops)

- Use `config_knob_catalogue.yaml` to derive deployment-time variable matrix (required/optional per process).
- Prioritize enforcement controls for critical keys: `EGRESS_GUARD_DISABLED`, `DISABLE_RUNTIME_MUTATION_GUARD`, `SOVEREIGN_AUTO_APPROVE`, `MEMORY_DB`, `VECTOR_DB_CHROMA_PATH`, `ADG_REDIS_URL`.
- Add startup validation checks for unknown-default high-risk keys and secrets presence.

### G6 hand-off (special-surface normalization)

- Use ambiguous/unknown-default keys as investigation seeds (especially provider/model selectors and secondary embedding toggles).
- Verify test-only keys remain test-scoped (`OTEL_MCP_ALLOW_MOCK_TRACES`, mutation guard test overrides) and do not bleed into production runtime runs.

## Schema note

`output_contracts.md` defines a minimal G4b schema (`id`, `plane`, `source`, `key_path`, `default`, `consumers`, `scope`, `reload_policy`, ...).
To satisfy this wave’s stricter hard requirements, `config_knob_catalogue.yaml` keeps that baseline shape via compatibility fields (`plane/source/key_path/default/consumers/scope/reload_policy`) **and** adds mandatory G4b fields (`key_name/class/default_value_if_observable/consumer_modules/affects_pipelines/affects_stores/read_time/reload_behavior/risk_level`).
