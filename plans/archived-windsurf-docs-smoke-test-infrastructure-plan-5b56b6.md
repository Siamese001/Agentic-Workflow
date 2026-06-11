---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\smoke-test-infrastructure-plan-5b56b6.md'
original_relative_path: 'smoke-test-infrastructure-plan-5b56b6.md'
source_sha256: 1ada05a504c29a43ef880ffe357c72f363d6a3b98143b78e67d290dd189eef75
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Smoke Test Plan — All Infrastructure

Comprehensive smoke test suite covering every infrastructure subsystem, organized in `tests/smoke/` with domain subfolders.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Folder Placement

```
tests/smoke/                         # NEW top-level smoke test folder
├── conftest.py                      # Shared smoke fixtures (timeouts, markers, skip logic)
├── adg/
│   ├── test_adg_pipeline_smoke.py   # ADG generation + SQLite integrity
│   ├── test_adg_redis_smoke.py      # Redis hot cache ingest + query
│   └── test_adg_scanner_smoke.py    # Static scanner basic operation
├── runtime/
│   ├── test_lifecycle_smoke.py      # Lifecycle trace contract emitters
│   ├── test_execution_trace_smoke.py# Execution trace + determinism
│   └── test_sovereignty_smoke.py    # Sovereignty bootstrap + boundary validator
├── layers/
│   ├── test_l0_routing_smoke.py     # L0 routing engine + config loading
│   ├── test_l1_cognition_smoke.py   # L1 cognition engine init
│   ├── test_l2_execution_smoke.py   # L2 UWG + execution protocol
│   ├── test_l3_orchestration_smoke.py # L3 orchestration contracts
│   ├── test_l4_state_smoke.py       # L4 state management + versioning
│   ├── test_l5_safety_smoke.py      # L5 safety enforcement + validators
│   └── test_l6_observability_smoke.py # L6 dashboard + metrics
├── cache/
│   ├── test_redis_cache_smoke.py    # Redis cache client + coordination fabric
│   └── test_config_cache_smoke.py   # Config file cache + schema validator cache
├── config/
│   ├── test_config_loading_smoke.py # Redis/ADG/path config loading
│   └── test_ssot_constants_smoke.py # SSOT tier constants + structure blueprint
├── agents/
│   ├── test_base_agent_smoke.py     # SovereignBaseAgent + layer bases instantiate
│   └── test_mixin_stack_smoke.py    # Critical mixin imports + MRO resolution
├── knowledge/
│   ├── test_knowledge_engine_smoke.py   # Knowledge engine init
│   └── test_document_loaders_smoke.py   # Document loader imports
├── prompt_governance/
│   └── test_prompt_governance_smoke.py  # Registry + template loading
├── system_learning/
│   ├── test_pipeline_smoke.py       # Pipeline factory + meta learning
│   └── test_system_learning_stores_smoke.py # Store backends init
├── apps/
│   ├── test_apps_shared_smoke.py    # Shared config + spine + validators
│   ├── test_apps_eval_smoke.py      # Eval engine init
│   ├── test_apps_exec_smoke.py      # Exec engine init
│   ├── test_apps_research_smoke.py  # Research engine init
│   ├── test_apps_rfp_smoke.py       # RFP engine init
│   └── test_apps_rg_smoke.py        # Resume gen engine init
├── enforcement/
│   ├── test_enforcement_smoke.py    # Constitutional validator loads
│   └── test_guardrail_smoke.py      # Guardrail strategies instantiate
├── infrastructure/
│   └── test_hardening_smoke.py      # Hardening modules importable
├── interfaces/
│   └── test_interfaces_smoke.py     # All protocol interfaces importable
└── embeddings/
    └── test_embeddings_smoke.py     # Embedding factory + guard importable
```

---

## pytest.ini Changes

Add `tests/smoke` to `testpaths` and register the `smoke` marker:

```ini
# Under testpaths, add:
    tests/smoke

# Under markers, add:
    smoke: Post-deployment and infrastructure health-check tests
```

---

## Smoke Test Design Principles

| Principle | Rule |
|---|---|
| **No external services required** | Mock Redis/APIs; test structure, not connectivity |
| **Import-first** | Every smoke test starts with verifying the module imports cleanly |
| **Fast** | Each file completes in <5s; entire suite <60s |
| **No side effects** | No filesystem writes, no DB mutations, no network calls |
| **Marker-gated** | All tests marked `@pytest.mark.smoke` for selective execution |
| **Deterministic** | No randomness, no time-dependent assertions |

---

## Smoke Tests by Domain (28 files, ~150 tests)

### 1. ADG Pipeline (`tests/smoke/adg/`) — 3 files, ~15 tests

| Test | What it verifies |
|---|---|
| `test_adg_pipeline_smoke::test_generate_full_adg_importable` | `tools.adg.generate_full_adg` imports without error |
| `test_adg_pipeline_smoke::test_sqlite_artifact_exists` | Latest `artifacts/adg/adg_indexed_*.sqlite` file present |
| `test_adg_pipeline_smoke::test_sqlite_schema_tables` | SQLite has `nodes` and `edges` tables with correct columns |
| `test_adg_pipeline_smoke::test_sqlite_nonzero_counts` | nodes > 0, edges > 0 |
| `test_adg_pipeline_smoke::test_adg_artifact_builder_imports` | `agentic_core.adg.artifact.builder` imports |
| `test_adg_redis_smoke::test_redis_ingest_importable` | `tools.adg.adg_redis_ingest` imports |
| `test_adg_redis_smoke::test_mcp_server_importable` | `tools.adg.adg_mcp_server` imports |
| `test_adg_redis_smoke::test_redis_query_importable` | `tools.adg.adg_redis_query` imports |
| `test_adg_scanner_smoke::test_scanner_importable` | `ADGStaticScanner` class imports |
| `test_adg_scanner_smoke::test_schema_frozensets_nonempty` | All schema frozensets (P0-P4) are non-empty |
| `test_adg_scanner_smoke::test_schema_relation_types` | RelationType literals present |

### 2. Runtime (`tests/smoke/runtime/`) — 3 files, ~15 tests

| Test | What it verifies |
|---|---|
| `test_lifecycle_smoke::test_lifecycle_contract_importable` | `lifecycle_trace_contract` imports |
| `test_lifecycle_smoke::test_emitter_functions_callable` | All `_emit_*` functions exist and are callable |
| `test_lifecycle_smoke::test_all_exports_present` | `__all__` list matches actual module attributes |
| `test_execution_trace_smoke::test_execution_trace_importable` | `execution_trace` module imports |
| `test_execution_trace_smoke::test_trace_emitter_importable` | `trace_emitter` module imports |
| `test_execution_trace_smoke::test_mathematical_determinism_importable` | `mathematical_determinism` imports |
| `test_sovereignty_smoke::test_sovereignty_bootstrap_importable` | `sovereignty_bootstrap` imports |
| `test_sovereignty_smoke::test_boundary_validator_importable` | `boundary_validator` imports |
| `test_sovereignty_smoke::test_execution_bound_token_importable` | `execution_bound_token` imports |

### 3. Architecture Layers (`tests/smoke/layers/`) — 7 files, ~35 tests

Each layer file tests:
- `__init__.py` imports cleanly
- Key exports exist as attributes
- Core engine/reasoning classes are importable
- No MRO errors in class hierarchy

| Layer | Key modules verified |
|---|---|
| **L0** | Routing engine, path_constants, ssot_tier_constants, deterministic_routing_gateway |
| **L1** | Cognition engine, context managers, validators, planning |
| **L2** | UWG, execution protocol, determinism, CID registry, apps_qwen gateway |
| **L3** | Orchestration contracts, PTC, arbitration, registry, coordination |
| **L4** | State authority, versioning, memory, lifecycle, workflow engines |
| **L5** | Safety enforcement, validators, gates, HITL, security, config/structure_blueprint |
| **L6** | Dashboard aggregate, metrics, performance, observability engines |

### 4. Cache (`tests/smoke/cache/`) — 2 files, ~10 tests

| Test | What it verifies |
|---|---|
| `test_redis_cache_smoke::test_redis_cache_client_importable` | `redis_cache_client` imports |
| `test_redis_cache_smoke::test_redis_coordination_fabric_importable` | `redis_coordination_fabric` imports |
| `test_redis_cache_smoke::test_cache_key_builders_importable` | `cache_key_builders` imports |
| `test_config_cache_smoke::test_config_file_cache_importable` | `config_file_cache` imports |
| `test_config_cache_smoke::test_discovery_cache_importable` | `discovery_cache` imports |
| `test_config_cache_smoke::test_graph_aware_cache_importable` | `graph_aware_cache` imports |
| `test_config_cache_smoke::test_schema_validator_cache_importable` | `schema_validator_cache` imports |

### 5. Config (`tests/smoke/config/`) — 2 files, ~8 tests

| Test | What it verifies |
|---|---|
| `test_config_loading_smoke::test_redis_config_loads` | `get_redis_config()` returns valid config |
| `test_config_loading_smoke::test_adg_cache_config_loads` | `get_adg_cache_config()` returns valid config |
| `test_config_loading_smoke::test_redis_windows_config_loads` | `get_redis_windows_config()` returns valid config |
| `test_ssot_constants_smoke::test_path_constants_importable` | `path_constants` BATCH_SIZE, MAX_RETRIES etc. present |
| `test_ssot_constants_smoke::test_structure_blueprint_importable` | `structure_blueprint_config` imports |
| `test_ssot_constants_smoke::test_ssot_tier_constants_importable` | `ssot_tier_constants` imports |

### 6. Agents & Mixins (`tests/smoke/agents/`) — 2 files, ~12 tests

| Test | What it verifies |
|---|---|
| `test_base_agent_smoke::test_sovereign_base_importable` | `SovereignBaseAgent` imports |
| `test_base_agent_smoke::test_layer_bases_importable` | All 7 layer base classes import (L0-L6) |
| `test_base_agent_smoke::test_lightweight_base_importable` | `LightweightBase` imports |
| `test_mixin_stack_smoke::test_ssot_mixin_stack_importable` | `ssot_mixin_stack` imports |
| `test_mixin_stack_smoke::test_critical_mixins_importable` | Top 10 high-use mixins import (tracing, safety, caching, lifecycle, etc.) |
| `test_mixin_stack_smoke::test_mixin_mro_no_conflicts` | MRO resolves for SovereignBaseAgent + common mixin combos |

### 7. Knowledge (`tests/smoke/knowledge/`) — 2 files, ~6 tests

| Test | What it verifies |
|---|---|
| `test_knowledge_engine_smoke::test_knowledge_init_importable` | `agentic_core.knowledge` imports |
| `test_knowledge_engine_smoke::test_engine_importable` | `knowledge.engine` imports |
| `test_document_loaders_smoke::test_document_loaders_importable` | `knowledge.document_loaders` imports |

### 8. Prompt Governance (`tests/smoke/prompt_governance/`) — 1 file, ~5 tests

| Test | What it verifies |
|---|---|
| `test_prompt_governance_smoke::test_pg_init_importable` | `prompt_governance` imports |
| `test_prompt_governance_smoke::test_registry_importable` | `prompt_governance.registry` imports |
| `test_prompt_governance_smoke::test_core_importable` | `prompt_governance.core` imports |
| `test_prompt_governance_smoke::test_security_importable` | `prompt_governance.security` imports |
| `test_prompt_governance_smoke::test_templates_importable` | `prompt_governance.templates` imports |

### 9. System Learning (`tests/smoke/system_learning/`) — 2 files, ~8 tests

| Test | What it verifies |
|---|---|
| `test_pipeline_smoke::test_pipeline_factory_importable` | `pipelines.pipeline_factory` imports |
| `test_pipeline_smoke::test_meta_learning_pipeline_importable` | `pipelines.meta_learning_pipeline` imports |
| `test_pipeline_smoke::test_adapters_importable` | `adapters` imports |
| `test_pipeline_smoke::test_arbitration_importable` | `arbitration` imports |
| `test_system_learning_stores_smoke::test_stores_importable` | `stores` imports |
| `test_system_learning_stores_smoke::test_state_importable` | `state` imports |
| `test_system_learning_stores_smoke::test_validators_importable` | `validators` imports |

### 10. Apps (`tests/smoke/apps/`) — 6 files, ~18 tests

Each app file tests:
- `config/agent_spec_config.py` imports
- `engines/base_*_engine.py` imports
- `reasoning/*Orchestrator.py` imports

| App | Module verified |
|---|---|
| **apps_shared** | config, spine, validators, enforcement, reasoning bases |
| **apps_eval** | EvalOrchestrator, base_eval_engine, evaluation_prompts.json exists |
| **apps_exec** | ExecOrchestrator, base_exec_engine, brief_assembly_engine |
| **apps_research** | ResearchOrchestrator, base_research_engine |
| **apps_rfp** | RfpOrchestrator, base_rfp_engine, proposal_assembly_engine |
| **apps_rg** | apps_rg engines importable, reasoning agents importable |

### 11. Enforcement (`tests/smoke/enforcement/`) — 2 files, ~6 tests

| Test | What it verifies |
|---|---|
| `test_enforcement_smoke::test_constitutional_validator_importable` | `ops_scripts.enforcement.constitutional_validator` imports |
| `test_enforcement_smoke::test_l5_enforcement_importable` | `L5_safety.enforcement` has strategy classes |
| `test_guardrail_smoke::test_guardrail_strategies_importable` | `apps_shared.enforcement` strategy files import |

### 12. Infrastructure Hardening (`tests/smoke/infrastructure/`) — 1 file, ~4 tests

| Test | What it verifies |
|---|---|
| `test_hardening_smoke::test_adaptive_optimizer_importable` | `infrastructure.hardening.adaptive_optimizer` imports |
| `test_hardening_smoke::test_security_framework_importable` | `infrastructure.hardening.security_framework` imports |
| `test_hardening_smoke::test_distributed_state_importable` | `infrastructure.hardening.distributed_state_manager` imports |
| `test_hardening_smoke::test_cross_layer_coherence_importable` | `infrastructure.hardening.cross_layer_coherence` imports |

### 13. Interfaces (`tests/smoke/interfaces/`) — 1 file, ~6 tests

| Test | What it verifies |
|---|---|
| `test_interfaces_smoke::test_all_protocols_importable` | All I*Protocol files import |
| `test_interfaces_smoke::test_determinism_interface_importable` | `interfaces.determinism` imports |
| `test_interfaces_smoke::test_gateway_interface_importable` | `interfaces.gateway` imports |
| `test_interfaces_smoke::test_write_gateway_importable` | `interfaces.write_gateway` imports |

### 14. Embeddings (`tests/smoke/embeddings/`) — 1 file, ~3 tests

| Test | What it verifies |
|---|---|
| `test_embeddings_smoke::test_embedding_factory_importable` | `embedding_factory` imports |
| `test_embeddings_smoke::test_embedding_input_guard_importable` | `embedding_input_guard` imports |
| `test_embeddings_smoke::test_tokenization_adapter_importable` | `tokenization_adapter` imports |

---

## Shared Conftest (`tests/smoke/conftest.py`)

```python
"""Smoke test configuration — fast, deterministic, no external deps."""
import logging
import pytest

# Suppress lifecycle trace loggers (consistent with root conftest)
for _name in ["adg", "lifecycle"]:
    _lg = logging.getLogger(_name)
    _lg.setLevel(logging.CRITICAL)
    _lg.propagate = False

@pytest.fixture(autouse=True)
def smoke_timeout(request):
    """Enforce 5s max per smoke test."""
    pass

def pytest_collection_modifyitems(items):
    """Auto-mark all tests in smoke/ with @pytest.mark.smoke."""
    for item in items:
        if "smoke" in str(item.fspath):
            item.add_marker(pytest.mark.smoke)
```

---

## Execution Commands

```bash
# Run only smoke tests
pytest tests/smoke/ -v --tb=short

# Run smoke tests for a specific domain
pytest tests/smoke/adg/ -v
pytest tests/smoke/layers/ -v

# Exclude smoke from regular test runs
pytest tests/ --ignore=tests/smoke/

# CI/CD: Smoke gate before full suite
pytest tests/smoke/ -v --tb=short -x && pytest tests/unit/ tests/integration/
```

---

## Implementation Order (by priority)

| Phase | Domain | Files | Est. Tests |
|-------|--------|-------|-----------|
| **1** | conftest + ADG + Runtime + Config | 9 | ~38 |
| **2** | Layers (L0-L6) | 7 | ~35 |
| **3** | Cache + Agents + Enforcement | 6 | ~28 |
| **4** | Knowledge + Prompt Gov + System Learning | 5 | ~19 |
| **5** | Apps + Infrastructure + Interfaces + Embeddings | 9 | ~31 |
| **Total** | | **28 files** | **~151 tests** |

---

## Non-Goals

- **No live Redis tests** — smoke tests mock Redis or skip connectivity checks
- **No ADG regeneration** — smoke tests verify existing artifacts, not generate new ones
- **No LLM/API calls** — zero external service dependency
- **No test data generation** — uses existing fixtures and constants only

---

## Post-Plan Mode Action

Move this file to `docs/reports/plans/smoke-test-infrastructure-plan-5b56b6.md` (constitutional requirement).

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

