# G2 — Boundary Violations and Dynamic Wiring

Three classes of wiring finding that require attention, drawn from ADG-authoritative views plus literal-string scans for dynamic-import sites.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

## Class 1 — Authority boundary breaches (ADG `mv_authority_boundary_breaches`)

**Total: 137 violations in 2 breach classes.**

### By (src_layer, dst_layer, breach_class)

| src | dst | breach_class | count |
|---|---|---|---:|
| L_APP | L0 | `L_APP_core_bypass` | 58 |
| L_APP | L2 | `L_APP_core_bypass` | 24 |
| L6 | L0 | `L6_downstream_mutation` | 23 |
| L6 | L2 | `L6_downstream_mutation` | 21 |
| L_APP | L1 | `L_APP_core_bypass` | 11 |
| (smaller buckets) | | | 0 |

### `L_APP_core_bypass` (93 violations, 3 app→core pairs)

**Rule broken**: apps should bind to core through sanctioned cross-boundary surfaces (`agentic_core/interfaces/`, `agentic_core/seams/`, or `agentic_core/L_CONTRACTS/` — per G2 `seam_usage_report.md`, only `interfaces/` sees live use). Observed imports reach directly into layer directories (L0 config, L1 types, L2 types) without crossing a declared interface.

**Top offenders** (per app file, descending):

| Importer file | Bypass count |
|---|---:|
| `apps_shared/config/operational_config.py` | 8 |
| `apps_shared/utils/sleeping_giant_util.py` | 4 |
| `apps_eval/engines/scenario_runner.py` | 4 |
| `apps_shared/utils/governed_prompt_adapter.py` | 3 |
| `apps_rg/scripts/migration_executor.py` | 3 |
| `apps_shared/utils/bulkhead_manager_util.py` | 2 |
| `apps_shared/types/reasoning_output.py` | 2 |
| `apps_shared/config/integration_config.py` | 2 |
| `apps_rg/utils/rg_agent_base_util.py` | 2 |
| `apps_rg/scripts/rg_final_audit.py` | 2 |

- `apps_shared/` accounts for the majority of bypasses (expected — it's the library layer wrapping core; its internals legitimately reach deep).
- `apps_rg/` is the flagship runtime app; its bypasses are in `scripts/` (admin) and `utils/` (app-internal) — not in the main request path.
- `apps_eval/engines/scenario_runner.py` is a runtime binding (scenario runner → L0) that is on the operational path. **Highest-value review candidate**.

### `L6_downstream_mutation` (44 violations, 2 L6→core pairs)

**Rule broken**: L6 is observability — it should observe / record, NOT import from lower layers to drive behaviour.

**Top offenders**:

| Importer file | Target |
|---|---|
| `agentic_core/L6_observability/__init__.py` | `agentic_core/L0_routing/config/path_constants.py` (≥ 8 direct import statements) |
| `agentic_core/L6_observability/enforcement/reasoning_streamer.py` | `L0_routing/config/path_constants.py` |
| `agentic_core/L6_observability/types/vigilance_event_types.py` | `L0_routing/types/determinism_types.py` |
| `agentic_core/L6_observability/utils/engines/TieredVigilanceEmitter.py` | `L0_routing/types/determinism_types.py` |
| `agentic_core/L6_observability/utils/evaluation/golden/__init__.py` | `L0_routing/config/path_constants.py` |

- Most breaches resolve to **L6 → `L0/config/path_constants.py`** (a shared-paths module) and **L6 → `L0/types/determinism_types.py`**.
- Reading shared constants from L0 is arguably benign, but ADG has already classified it as a violation.
- **B7-G2-03**: either v1.4 missing an edge "L6 MAY read L0 shared constants" or a real cleanup target.

## Class 2 — Write sovereignty bypasses (ADG `mv_write_sovereignty_paths`)

**Total: 1,821 write sites; 56 critical (`is_direct_infra_write=1`).**

### By layer and severity

| writer_layer | severity | UWG-routed | Direct infra write |
|---|---|---:|---:|
| **L0** | ok | 21 | 0 |
| **L2** | ok | 39 | 0 |
| **L2** | critical | 0 | **1** — `agentic_core/L2_execution/reasoning/RedisSovereignAgent.py` (writes `ExecutionContext.create` directly) |
| **L4** | ok | 5 | 0 |
| **L4** | critical | 0 | **7** — see below |
| **L5** | ok | 16 | 0 |
| **L6** | warning | 0 | 0 |
| **L_SHARED** | critical | 0 | **1** |
| **L_INFRA** | critical | 0 | **4** |
| **L_TOOLS** | critical | 0 | **25** |
| **L_UNKNOWN** | critical | 0 | **24** |

### L4 critical bypasses (architecturally important)

| File | Write symbol | Line |
|---|---|---|
| `agentic_core/L4_state/cache/gptcache_client.py` | `self.cache_dir.mkdir` | 69 |
| `agentic_core/L4_state/reasoning/retrieval_layers.py` | `persist_dir.mkdir` | 227 |
| `agentic_core/L4_state/utils/memory/chunk_manifest_registry.py` | `parent.mkdir` | 101 |
| `agentic_core/L4_state/utils/memory/completeness_snapshot_registry.py` | `parent.mkdir` | 114 |
| `agentic_core/L4_state/utils/memory/graph_knowledge_store.py` | `current_nodes.copy` | 282 |
| `agentic_core/L4_state/utils/memory/graph_knowledge_store.py` | `current_rels.copy` | 283 |
| `agentic_core/L4_state/utils/memory/retrieval_eval_registry.py` | `parent.mkdir` | 96 |

All seven are either directory-creation (`mkdir`) or in-memory dict copies (`copy`). Most are scaffolding for durable-state files (cache dirs, manifest parents), not payload writes. However:

- F09.01 asserts UWG is the sole durable-write path. `mkdir` is technically a filesystem mutation — F09.02 scheme compliance may or may not require UWG mediation for directory creation. Deferred to G4 storage topology + G7 traceability.
- `graph_knowledge_store.py` `copy()` calls are in-memory only (not persistent). These may be false positives in ADG's write-sovereignty classifier; ok for now.

### L_TOOLS critical (25) — expected

Tools legitimately write artefacts outside UWG (ADG snapshots, reports, caches). Classified `expected`.

### L_UNKNOWN critical (24) — **investigate**

Modules ADG could not layer-assign that write directly to infra. G1 unclassified_modules + G6 should inspect.

## Class 3 — Dynamic-import / synthetic-wiring sites

Enumerated via literal-string grep (allowed per constitutional Quick Gates §"grep_search permitted only to confirm literals"). These are wiring sites invisible to the ADG static import graph.

### `importlib.import_module(` — 59 matches in 37 files

| Category | Files | Notable |
|---|---:|---|
| L0 enforcement seams | 5 | `safety_reasoning_seam.py` (8), `safety_validators_seam.py` (6), `safety_enforcement_seam.py` (4), `safety_kernel_seam.py` (1), `vigilance_seam.py` (1) — these dispatch to L5 validators dynamically |
| L0 utils seams | 4 | `canonical_truth_seam.py`, `layer_emission_seam.py`, `observability_seam.py`, + 1 more |
| L5 validators / enforcement | 7 | `silent_degradation_validator.py` (4), `mission_utils_enforcer.py`, `priority_violation_guard.py`, `import_guard.py`, `canary_token_defense_strategy.py`, `signature_verifier.py`, `ddd_alignment_validator.py` |
| L2 enforcement / reasoning / utils | 6 | `static_dispatch_registry.py` (3), `preventative_sandbox.py` (2), `SubAtomicRegistryAgent.py`, `archive_util.py`, `factory_util.py`, + 1 |
| L3 reasoning / engines | 3 | `DagRuntimeInspectorAgent.py`, `AgentFactory.py`, `orchestrator_engine.py` |
| L4 enforcement / reasoning | 2 | `graph_memory_bridge.py`, `l4_tool_registry.py` |
| L5 reasoning | 2 | `GenerativeGuardAgent.py`, `GovernanceAgent.py` |
| adg runtime + extraction | 4 | `dynamic_invocation.py` (2), `contracts/schema.py`, `contracts/schema_util.py`, `extraction/static_scanner.py`, `extraction/visitors/dynamic.py` |
| L1 | 1 | `prompt_artifact_cache.py` |
| core / mixins / runtime | 3 | `core/frameworks/dependency_manager.py`, `mixins/subatomic_testing_mixin.py`, `runtime/utils/dynamic_loader_util.py` |
| Apps | 3 | `apps_eval/integrations/governed_eval_exception.py`, `apps_research/__main__.py`, `apps_underwriting_ai/integrations/governed_uw_exception.py` |

**Architectural reading**: L0 seams dispatch to L5 validators dynamically (expected pattern — seam boundary explicitly uses runtime dispatch to decouple). L3 engines use `importlib` for factory / DAG inspection. L5 uses `importlib` for guard / validator dispatch. None of these are captured by the ADG static import graph.

**Three apps** have `importlib.import_module` calls:
- `apps_eval/integrations/governed_eval_exception.py` — governed exception handler loads handlers dynamically.
- `apps_research/__main__.py` — research entry point dynamic-loads a runner.
- `apps_underwriting_ai/integrations/governed_uw_exception.py` — same pattern as eval.

### `__import__(` — 19 matches in 15 files

| File | Matches | Category |
|---|---:|---|
| `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` | 3 | healer dispatch |
| `agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py` | 3 | pre-commit dispatch |
| L0 / L3 / L4 / L5 enforcement, types, utils | 1 each | guard / registry / validator wiring |
| `apps_shared/_compat/agentic_core_shim.py` | 1 | **shim** (per G1b adapter pattern B) |
| `apps_shared/utils/collected_item_util.py` | 1 | app-internal |
| `apps_shared/utils/sdk_category_util.py` | 1 | app-internal |

### `sys.modules[` write sites — 245 matches in 123 files

- **93 matches are inside `agentic_core/adg/_compat/`** (the adg compatibility shim package). These are synthetic module substitutions, not runtime dispatch. Excluded from "real runtime wiring".
- Remaining **~30 sites** are real runtime dispatch or explicit module-table manipulation:
  - `apps_exec/_optional_agentic_core.py` (G1b adapter pattern B)
  - `apps_shared/_compat/agentic_core_shim.py` (G1b adapter pattern B)
  - `apps_rg/bootstrap_runtime.py` (G1b adapter pattern D)
  - `agentic_core/runtime/utils/dynamic_loader_util.py`
  - various guard / enforcer modules that sentinel-install fallback symbols
- **These sites produce synthetic-looking `agentic_core.*` entries in `sys.modules`** — G2 explicitly does NOT count them as real agentic_core bindings. Per G1b, real agentic_core imports were resolved AFTER excluding shim synthesis; 0 unresolved bindings remain across 8 apps.

## Class 4 — Bridge candidates and hubs

From `mv_graph_chokepoint_bridges` (top bridge_score):

| Module | Layer | fan_in | fan_out | Purpose |
|---|---|---:|---:|---|
| `agentic_core/cache/redis_cache_client.py` | L_SHARED | 70 | 70 | **Redis bridge** — primary external dependency bridge |
| `tools/generate/validation/__init__.py` | L_TOOLS | 53 | 53 | generator validation init |
| `agentic_core/L0_routing/types/guardian_contract_types.py` | L0 | 103 | 99 | Guardian contract types bridge |
| `agentic_core/L2_execution/utils/write_gateway.py` | L2 | 94 | 98 | L2 write gateway |
| `agentic_core/adg/extraction/visitors/__init__.py` | L_TOOLS | 53 | 56 | ADG visitor init |
| `agentic_core/L5_safety/config/structure_blueprint/__init__.py` | L5 | 96 | 122 | structure blueprint init |
| `agentic_core/base_agents/SovereignBaseAgent.py` | L_SHARED | 136 | 101 | **Base agent** — largest in/out combined |
| `agentic_core/adg/extraction/static_scanner.py` | L_TOOLS | 289 | 158 | ADG static scanner |
| `agentic_core/L0_routing/config/__init__.py` | L0 | 248 | 122 | L0 config root |
| `apps_rg/engines/base_rg_engine.py` | L_APP | 45 | 79 | APP-RG base engine |

Bridge candidates carry the majority of cross-layer flow. Any refactor that touches one of these triggers wide blast-radius — G6 / G7 must record this.

## Summary

| Class | Count | Severity |
|---|---:|---|
| Authority boundary breaches (`mv_authority_boundary_breaches`) | 137 | High — pre-classified as breaches |
| Write-sovereignty direct writes (`is_direct_infra_write=1`) | 56 | 8 concerning (L4 + L2 + L_SHARED); 25 expected (L_TOOLS); 24 unclassified (L_UNKNOWN) |
| `importlib.import_module` dynamic sites | 59 matches / 37 files | Medium — 34 inside core (seams, guards, factories), 3 in apps |
| `__import__(` dynamic sites | 19 matches / 15 files | Low — mostly healer/guard dispatch + 1 shim |
| `sys.modules[` write sites (non-shim) | ~30 | Medium — must be tracked to avoid false positives in G7 |
| Bridge hubs (top-10) | 10 modules | Architectural — refactor risk concentrators |

All items are catalogued. No G2-owned closure; handed off to G6 (taxonomy/duplicates), G7 (B7 register + traceability), and the parked B7 interaction-completeness wave.
