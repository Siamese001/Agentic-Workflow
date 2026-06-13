# AST Gap Analysis: Guardian/Test Coverage of Agentic Repo
**Date:** 2026-02-26
**Method:** AST-based strict exact-import matching (no parent-prefix propagation)
**Scope:** `agentic_core/`, `apps_lic/`, `apps_rg/`, `apps_shared/`, `system_learning/`, `L6_observability/`

---

## Executive Summary

| Metric | Value |
|---|---|
| Source files scanned | 1,970 |
| Test files | 2,615 |
| Test functions | 17,448 |
| Guardian test files | 117 |
| Architecture test files | 17 |
| **Directly covered modules** | **660 (33%)** |
| **Uncovered modules** | **1,310 (67%)** |
| CRITICAL gaps (>5 symbols, no test) | 677 |
| HIGH gaps (2–5 symbols, no test) | 449 |
| LOW gaps (0–1 symbols, no test) | 184 |

**Key finding:** The test suite has 2,615 test files and 17,448 test functions but only 33% of source modules are directly exercised at the exact-import level. The bulk of test coverage is concentrated in `system_learning/` (88–92%) and `agentic_core/L2_execution` (53%), while entire domain layers — `apps_lic/reasoning` (2%), `apps_shared/utils` (1%), `apps_rg/enforcement` (0%) — have essentially no direct test coverage.

Guardian tests are **exclusively** focused on `agentic_core.L0_routing` (289 import refs) with minimal coverage of `L2_execution` (27) and `L5_safety` (22), and zero guardian coverage of 42 out of 51 layer namespaces.

---

## Coverage by Layer — Full Breakdown

### `agentic_core/` — 1,332 files

| Layer | Files | Covered | Uncovered | Cov% | Notes |
|---|---|---|---|---|---|
| L0_routing | 245 | 75 | 170 | **30%** | Guardian-only; 170 modules with no test |
| L1_cognition | 74 | 12 | 62 | **16%** | ZERO guardian coverage |
| L2_execution | 158 | 85 | 73 | **53%** | Best agentic_core layer |
| L3_orchestration | 87 | 33 | 54 | **37%** | |
| L4_state | 86 | 27 | 59 | **31%** | ZERO guardian coverage |
| L5_safety | 337 | 142 | 195 | **42%** | Largest uncovered set: 125 CRITICAL |
| L6_observability | 44 | 17 | 27 | **38%** | ZERO guardian coverage |
| base_agents | 10 | 5 | 5 | **50%** | |
| config | 20 | 2 | 18 | **10%** | Near-zero |
| embeddings | 3 | 2 | 1 | **66%** | |
| enforcement | 5 | 2 | 3 | **40%** | |
| interfaces | 22 | 7 | 15 | **31%** | |
| knowledge | 21 | 15 | 6 | **71%** | Relatively well covered |
| mixins | 73 | 36 | 37 | **49%** | |
| prompt_governance | 37 | 15 | 22 | **40%** | |
| runtime | 56 | 10 | 46 | **17%** | Near-zero; 37 CRITICAL |
| seams | 6 | 6 | 0 | **100%** | Fully covered |
| security | 3 | 2 | 1 | **66%** | |
| system_learning | 12 | 12 | 0 | **100%** | Fully covered |
| utils | 22 | 14 | 8 | **63%** | |

### `apps_lic/` — 140 files

| Layer | Files | Covered | Uncovered | Cov% | Notes |
|---|---|---|---|---|---|
| config | 5 | 2 | 3 | **40%** | |
| enforcement | 1 | 0 | 1 | **0%** | *** ZERO *** |
| engines | 5 | 2 | 3 | **40%** | |
| reasoning | 41 | 1 | 40 | **2%** | *** NEAR ZERO — 40 agents untested *** |
| scripts | 5 | 1 | 4 | **20%** | |
| tools | 48 | 1 | 47 | **2%** | *** NEAR ZERO — 47 tools untested *** |
| types | 20 | 3 | 17 | **15%** | |
| utils | 9 | 1 | 8 | **11%** | |
| validators | 6 | 1 | 5 | **16%** | |

### `apps_rg/` — 155 files

| Layer | Files | Covered | Uncovered | Cov% | Notes |
|---|---|---|---|---|---|
| config | 4 | 1 | 3 | **25%** | |
| enforcement | 2 | 0 | 2 | **0%** | *** ZERO *** |
| engines | 48 | 4 | 44 | **8%** | Near-zero |
| reasoning | 24 | 1 | 23 | **4%** | *** NEAR ZERO — 23 agents untested *** |
| scripts | 11 | 0 | 11 | **0%** | *** ZERO *** |
| tools | 33 | 1 | 32 | **3%** | *** NEAR ZERO *** |
| types | 16 | 2 | 14 | **12%** | |
| utils | 11 | 0 | 11 | **0%** | *** ZERO *** |
| validators | 5 | 1 | 4 | **20%** | |

### `apps_shared/` — 235 files

| Layer | Files | Covered | Uncovered | Cov% | Notes |
|---|---|---|---|---|---|
| config | 7 | 3 | 4 | **42%** | |
| enforcement | 11 | 0 | 11 | **0%** | *** ZERO — 11 enforcement files *** |
| reasoning | 9 | 1 | 8 | **11%** | |
| scripts | 35 | 4 | 31 | **11%** | |
| spine | 1 | 0 | 1 | **0%** | *** ZERO *** |
| types | 54 | 3 | 51 | **5%** | *** NEAR ZERO — 50 CRITICAL *** |
| utils | 103 | 2 | 101 | **1%** | *** EFFECTIVELY ZERO — 78 CRITICAL *** |
| validators | 14 | 1 | 13 | **7%** | |

### `system_learning/` — 103 files

| Layer | Files | Covered | Uncovered | Cov% | Notes |
|---|---|---|---|---|---|
| config | 2 | 0 | 2 | **0%** | |
| constraints | 3 | 2 | 1 | **66%** | |
| enforcement | 7 | 5 | 2 | **71%** | |
| engines | 52 | 48 | 4 | **92%** | Best covered layer overall |
| pipelines | 3 | 3 | 0 | **100%** | |
| ports | 8 | 5 | 3 | **62%** | |
| runtime | 1 | 0 | 1 | **0%** | |
| snapshots | 2 | 2 | 0 | **100%** | |
| types | 17 | 15 | 2 | **88%** | |
| validators | 7 | 6 | 1 | **85%** | |

### `L6_observability/` — 5 files

| Layer | Files | Covered | Uncovered | Cov% | Notes |
|---|---|---|---|---|---|
| engines | 2 | 2 | 0 | **100%** | |
| types | 2 | 2 | 0 | **100%** | |

---

## Critical Gap Details

### 1. `agentic_core/L5_safety` — 125 CRITICAL + 58 HIGH uncovered (195 total)
The single largest gap. The safety enforcement layer has the most files (337) and the most uncovered (195). Critical examples:

- `agentic_core/L5_safety/enforcement/AdapterBaseFactory.py` — `AdapterContext`, `AdapterResult`, `AdapterBase`
- `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py` — `ArchivalOperation`, `ArchivalResult`, `ArchivalGatekeeper`
- `agentic_core/L5_safety/enforcement/canary_token_defense_strategy.py` — `CanaryToken`, `CanaryDefense`
- `agentic_core/L5_safety/enforcement/circuit_breaker_gate.py` — `CircuitState`, `CircuitBreakerConfig`, `CircuitBreakerMetrics`
- `agentic_core/L5_safety/enforcement/context_session_manager_enforcer.py` — `RiskLevel`, `AttentionState`, `ContextSession`
- `agentic_core/L5_safety/enforcement/deterministic_loop_detector.py` — `ToolBudgetExceededError`, `ToolBudget`
- `agentic_core/L5_safety/enforcement/firecracker_manager.py` — `FirecrackerManager`
- `agentic_core/L5_safety/enforcement/transcript_freezer.py` — `TranscriptMutationViolation`, `FrozenTranscript`
- `agentic_core/L5_safety/config/detection_signal_config.py` — `Severity`, `ImpactScope`, `ImpactAssessment`
- `agentic_core/L5_safety/config/structure_blueprint/enforcement/types.py` — `Violation`, `EnforcementResult`

**Risk:** Safety layer enforcement code runs in production paths with no test-exercised contract. Any regression in `circuit_breaker_gate`, `archival_gatekeeper_gate`, or `transcript_freezer` is undetectable.

### 2. `agentic_core/L0_routing` — 42 CRITICAL + 49 HIGH uncovered (170 total)
Despite being the primary guardian target, 170 of 245 routing modules have no direct test coverage. Guardian tests concentrate on `execution_gateway`, `traceability_contracts`, and `guardian_contract` but skip:

- All `L0_routing/config/` modules (10+ uncovered)
- Most `L0_routing/engines/` (multiple)
- Most `L0_routing/reasoning/` agents

### 3. `agentic_core/L2_execution` — 47 CRITICAL + 23 HIGH uncovered (73 total)
Key gaps:

- `agentic_core/L2_execution/enforcement/deterministic_loop_detector.py` — `DeterministicLoopDetector`
- `agentic_core/L2_execution/enforcement/transcript_freezer.py` — `FrozenTranscript`
- `agentic_core/L2_execution/enforcement/capability_chokepoint_gate.py` — `CapabilityChokepoint`
- `agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py` — `SovereignFilesystemMcp`
- `agentic_core/L2_execution/engines/tool_registry.py` — `ToolDefinition`, `ToolMatch`, `tool_registry`
- `agentic_core/L2_execution/engines/execute_command_executor.py` — `ExecuteCommandArgs`, `ExecutionTimeoutError`
- `agentic_core/L2_execution/config/mcp_registry.py` — `McpServerMode`, `McpServerConfig`

### 4. `agentic_core/runtime` — 37 CRITICAL + 8 HIGH uncovered (46 total, 17% covered)
Near-zero coverage for all runtime internals:

- `agentic_core/runtime/engine/agent_engine.py` — `AgentEngine`
- `agentic_core/runtime/engine/ast_relocator.py` — `AstRelocator`
- `agentic_core/runtime/mathematical_determinism.py` — `MathematicalDeterminismEngine`, `DeterminismProof`
- `agentic_core/runtime/sovereignty_bootstrap.py` — `SovereigntyBootstrap`
- `agentic_core/runtime/execution_bound_token.py` — `ExecutionBoundToken`, `SecureCapabilityAuthority`
- `agentic_core/runtime/execution_trace.py` — `ExecutionTrace`, `ExecutionTraceManager`
- `agentic_core/runtime/sovereignty_exceptions.py` — `SovereigntyViolationError`, `IsolationViolationError`
- All `agentic_core/runtime/config/` types (14 files): `FeatureFlagManager`, `ModelConfig`, `RAGConfig`, etc.

### 5. `agentic_core/L1_cognition` — 27 CRITICAL + 29 HIGH (62 total, 16% covered, ZERO guardian)
The cognition layer has no guardian tests at all and only 16% direct test coverage. This layer handles agent decision-making and prompt construction.

### 6. `agentic_core/L3_orchestration` — 34 CRITICAL + 20 HIGH (54 total, 37% covered)
Orchestration agents, planning engines, and multi-hop reasoning — only 1 guardian test touches `L3_orchestration`.

### 7. `agentic_core/L4_state` — 30 CRITICAL + 20 HIGH (59 total, 31% covered, ZERO guardian)
State management layer (blackboard, telemetry recorder, prompt version store) — zero guardian coverage.

### 8. `apps_shared/utils` — 78 CRITICAL + 18 HIGH (101 total, 1% covered)
103 utility files with a single module covered. This is the largest absolute gap by file count. Examples:
- `apps_shared/utils/l5_autonomous_orchestrator_util.py`
- `apps_shared/utils/llm_profile_util.py`
- `apps_shared/utils/providers_google_genai_client_util.py`
- `apps_shared/utils/reasoning_prompt_util.py`
- `apps_shared/utils/archive_file_access_deprecated_util.py`

### 9. `apps_shared/types` — 50 CRITICAL (54 total, 5% covered)
Type definitions with virtually no coverage. These are shared contracts used across `apps_lic` and `apps_rg`.

### 10. `apps_shared/enforcement` — 11 CRITICAL (11 total, 0% covered)
Strategy enforcement layer completely untested:
- `AdaptiveretrievalgateStrategy.py`
- `CircuitbreakerStrategy.py`
- `DecomposedqueryagentStrategy.py`
- All 8 strategy files

### 11. `apps_lic/reasoning` and `apps_lic/tools` — 2% and 2% covered
40 of 41 reasoning agents untested. 47 of 48 tool files untested. These are the primary domain execution paths.

Key untested agents: `ArchitectureVisualizerAgent`, `CampaignBalanceAgent`, `CulturalDecoderAgent`, `DeliverabilityAgent`, `HOP3SenderGroundingAgent`–`HOP9IntegrationAgent`, `LicS2SupervisorAgent`, `MessageArchitectAgent`, `PreMortemAgent`, `TwoPhaseDeduplicationAgent`

### 12. `apps_rg/reasoning` (4%) and `apps_rg/engines` (8%)
23 of 24 reasoning agents untested. 44 of 48 engine files untested. Core resume generation paths.

Key untested agents: `ATSCompatibilityAgent`, `BrandComplianceAgent`, `CampaignPlannerAgent`, `ContentStrategyAgent`, `FactCheckAgent`, `RgStrategicPlannerAgent`

---

## Guardian Test Scope Analysis

Guardian tests (117 files) are **narrowly scoped** to `agentic_core.L0_routing`:

| Layer | Guardian Import Refs | Coverage Status |
|---|---|---|
| `agentic_core.L0_routing` | 289 | Primary guardian target |
| `agentic_core.L2_execution` | 27 | Partial |
| `agentic_core.L5_safety` | 22 | Partial |
| `agentic_core.base_agents` | 4 | Minimal |
| `agentic_core.L3_orchestration` | 1 | Token only |
| `agentic_core.mixins` | 1 | Token only |
| `agentic_core.utils` | 1 | Token only |
| `apps_lic.engines` | 2 | Minimal |
| `system_learning.enforcement` | 1 | Token only |

### Layers with ZERO guardian coverage (42 total):

**agentic_core sub-layers with no guardian tests:**
- `agentic_core.L1_cognition` (74 modules)
- `agentic_core.L4_state` (86 modules)
- `agentic_core.L6_observability` (44 modules)
- `agentic_core.config` (20 modules)
- `agentic_core.interfaces` (22 modules)
- `agentic_core.knowledge` (21 modules)
- `agentic_core.mixins` (significant portion — only 1 ref total)
- `agentic_core.prompt_governance` (37 modules)
- `agentic_core.runtime` (56 modules)
- `agentic_core.embeddings` (3 modules)
- `agentic_core.enforcement` (5 modules)
- `agentic_core.security` (3 modules)

**Apps layers — entirely absent from guardian tests:**
- `apps_lic.config`, `apps_lic.reasoning`, `apps_lic.scripts`, `apps_lic.tools`, `apps_lic.types`, `apps_lic.utils`, `apps_lic.validators`
- `apps_rg.config`, `apps_rg.enforcement`, `apps_rg.engines`, `apps_rg.reasoning`, `apps_rg.scripts`, `apps_rg.tools`, `apps_rg.types`, `apps_rg.utils`, `apps_rg.validators`
- `apps_shared.*` (all 8 sub-layers)

**system_learning sub-layers — absent from guardian tests:**
- `system_learning.constraints`, `system_learning.engines`, `system_learning.pipelines`, `system_learning.ports`, `system_learning.types`, `system_learning.validators`

---

## Architecture Test Scope (`tests/architecture/` — 17 files)

Architecture tests cover narrow structural invariants:

| Test File | Source Modules Covered | Tests |
|---|---|---|
| `test_apps_ssot_shared_enforcement.py` | `agentic_core.L5_safety.reasoning.FileClassificationAgent` | 8 |
| `test_classification_hardening.py` | `agentic_core.L5_safety.core_kernel.classification_kernel` | 10 |
| `test_compile_time_frozen_governance.py` | `agentic_core.L2_execution.healers.*`, `agentic_core.agents.*` | 12 |
| `test_environment_independence.py` | `agentic_core.L2_execution.healers.*` | 11 |
| `test_invariants.py` | `agentic_core.L0_routing.*`, `agentic_core.L2_execution.*`, `system_learning.pipelines.*` | 3 |
| `test_mathematical_determinism.py` | `agentic_core.L2_execution.healers.*` | 8 |
| `test_prompt_governance_no_orphans.py` | None (filesystem scan) | 1 |
| `test_artifacts_guard.py`, `test_cache_guard.py`, `test_docs_structure_guard.py`, `test_logs_guard.py`, etc. | None (filesystem/structural) | 2 each |

Architecture tests do NOT cover: `apps_lic`, `apps_rg`, `apps_shared`, `system_learning` internals, `L6_observability`, `L1_cognition`, `L4_state`.

---

## Prioritized Gap Remediation Plan

### Priority 1 — CRITICAL SAFETY REGRESSIONS (immediate risk)

These enforcement/safety modules are on hot paths with no tests:

1. **`agentic_core/L5_safety/enforcement/circuit_breaker_gate.py`** — `CircuitBreakerGate` controls production fault isolation
2. **`agentic_core/L5_safety/enforcement/transcript_freezer.py`** — `FrozenTranscript` prevents mutation attacks
3. **`agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py`** — `ArchivalGatekeeper` controls data archival
4. **`agentic_core/L2_execution/enforcement/deterministic_loop_detector.py`** — prevents runaway tool budgets
5. **`agentic_core/L2_execution/enforcement/capability_chokepoint_gate.py`** — `CapabilityChokepoint`
6. **`agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py`** — filesystem access control
7. **`apps_shared/enforcement/*`** — 11 strategy enforcement files, all untested (0%)

### Priority 2 — GUARDIAN BLIND SPOTS (architectural integrity risk)

Add guardian tests for layers currently missing:

1. **`agentic_core.L4_state`** — 86 modules, 0 guardian tests; state corruption has no invariant gate
2. **`agentic_core.L1_cognition`** — 74 modules, 0 guardian tests; cognition pipeline unguarded
3. **`agentic_core.runtime`** — 56 modules, 17% coverage; `AgentEngine`, `SovereigntyBootstrap` unguarded
4. **`agentic_core.L6_observability`** — 44 modules, 0 guardian tests; observability/DPO pipeline unguarded
5. **`agentic_core.prompt_governance`** — 37 modules, 40% coverage; prompt injection unguarded

### Priority 3 — DOMAIN AGENT COVERAGE (regression detection)

Add unit tests for `apps_lic` and `apps_rg` reasoning agents:

1. **`apps_lic/reasoning/`** — 40/41 agents untested; no regression detection for HOP1–HOP9 pipeline
2. **`apps_rg/reasoning/`** — 23/24 agents untested; no regression for resume generation pipeline
3. **`apps_rg/engines/`** — 44/48 engines untested (8%)
4. **`apps_lic/tools/`** — 47/48 tools untested (2%)

### Priority 4 — SHARED INFRASTRUCTURE (support risk)

1. **`apps_shared/types/`** — 50 CRITICAL; shared contracts used by both apps with no tests
2. **`apps_shared/utils/`** — 78 CRITICAL; 101 utilities, 1% coverage
3. **`agentic_core/config/`** — 10% coverage; configuration modules lack contract tests
4. **`agentic_core/runtime/config/`** — all 14 config types uncovered

### Priority 5 — SYSTEM_LEARNING REMAINING GAPS

1. `system_learning/config/embedding_storage_layout.py` — `EmbeddingStorageLayout` (13 methods, no test)
2. `system_learning/enforcement/boundary_guard.py` — `_BoundaryVisitor` (6 methods, no test)
3. `system_learning/engines/retrieval_profile_invariant_checker.py` — `RetrievalProfileInvariantChecker`
4. `system_learning/engines/retrieval_profile_replay_check.py` — `RetrievalProfileReplayChecker`
5. `system_learning/validators/readonly_access.py` — `check_system_learning_readonly`

---

## Coverage Anomalies

1. **2,615 test files but only 33% module coverage** — The test suite is very large but concentrated. Many test files import only indirectly (via shared fixtures, conftest.py) rather than targeting specific modules.

2. **`apps_shared/utils` has 103 files but 2 covered (1%)** — Despite a `tests/apps_shared/` directory with 284 test files, the import index shows they don't directly reference `apps_shared.utils.*` modules — they likely test via higher-level integrations.

3. **Guardian tests are version-locked to L0_routing** — The v15 guardian test suite (test_v15_p*) exclusively exercises `execution_gateway`, `traceability_contracts`, and `guardian_contract`. No guardian validates L1–L4 or L6 behavior.

4. **`agentic_core/system_learning` sub-namespace is 100% covered** — This is the `agentic_core/system_learning/` shim layer (12 files) which acts as a re-export; the actual `system_learning/` package is independently well-covered.

---

## Artifacts

- **AST scan script:** `ops_scripts/ci/ast_gap_analysis.py`
- **Strict coverage script:** `ops_scripts/ci/ast_gap_strict.py`
- **Raw JSON results:** `ops_scripts/ci/ast_gap_strict_results.json`
- **Deep layer script:** `ops_scripts/ci/ast_gap_deep.py`

---

## Guardian Test Recommendations — Delivered

Five new guardian test files have been written to `tests/guardian/`. Each follows the existing guardian pattern exactly: `pytestmark = pytest.mark.guardian`, uses `GuardianTestBase` AST utilities, autouse `_reset` fixtures for isolation, and mixes structural (AST-only) and runtime (import + call) tests.

### Files Delivered

| File | Guardian ID | Target | Tests |
|---|---|---|---|
| `tests/guardian/test_circuit_breaker_gate.py` | G-CB-1 | `agentic_core/L5_safety/enforcement/circuit_breaker_gate.py` | 13 |
| `tests/guardian/test_deterministic_loop_detector.py` | G-DLD-1 | `agentic_core/L2_execution/enforcement/deterministic_loop_detector.py` | 16 |
| `tests/guardian/test_sovereignty_runtime_contract.py` | G-SRC-1 | `agentic_core/runtime/sovereignty_bootstrap.py` + `sovereignty_exceptions.py` | 17 |
| `tests/guardian/test_l4_state_write_sovereignty.py` | G-L4S-1 | `agentic_core/L4_state/` (full layer, AST scan) | 9 |
| `tests/guardian/test_l1_cognition_purity_contract.py` | G-L1C-1 | `agentic_core/L1_cognition/` (full layer, AST scan) | 16 |

**Total new guardian tests: 71**

### Run Command

```bash
python -m pytest tests/guardian/test_circuit_breaker_gate.py \
  tests/guardian/test_deterministic_loop_detector.py \
  tests/guardian/test_sovereignty_runtime_contract.py \
  tests/guardian/test_l4_state_write_sovereignty.py \
  tests/guardian/test_l1_cognition_purity_contract.py \
  -m guardian --tb=short
```

### Test Results: 65 Pass / 6 Fail

The 6 failures are **real architectural violations** uncovered by the new tests, not test bugs:

#### Confirmed Violations (require remediation)

**G-L4S-1 — L4_state layer violations (4 failures):**

1. **Missing `__init__.py`** — `agentic_core/L4_state/__init__.py` does not exist; layer is not a proper Python package.

2. **Unguarded raw write** — `agentic_core/L4_state/storage/filesystem_store.py:115` calls `write_text()` without going through `UniversalWriteGateway`. Violates write-sovereignty contract.

3. **Forbidden layer imports (11 files)** — `L4_state` imports from `agentic_core.L2_execution.tools` in 11 files including `mission_historian.py`, `blob_storage_provider.py`, `runtime_state_guard.py`, `cycle_types.py`, `validation_context_types.py`, and 6 others. Direct L4→L2 imports are a layer inversion.

4. **Agent classes in state layer (5 files)** — `CachedStateLedgerAgent`, `CheckpointManagerAgent`, `GravityStateAgent`, `PineconeSovereignAgent`, `RedisSovereignAgent` are defined under `L4_state/reasoning/`. These belong in `L3_orchestration/reasoning/` or `apps_*/reasoning/`.

**G-L1C-1 — L1_cognition layer violations (2 failures):**

5. **Missing `__init__.py`** — `agentic_core/L1_cognition/__init__.py` does not exist; layer is not a proper Python package.

6. **Forbidden layer imports (4 files)** — `L1_cognition` imports from higher layers in violation of the layer hierarchy:
   - `cognitive_engine.py` → `agentic_core.L3_orchestration.engines.action_router` (L1→L3 inversion)
   - `memory_embedder.py` → `agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent` (L1→L2 inversion)
   - `meta_client.py` → `agentic_core.L4_state.reasoning.RedisSovereignAgent` + `PineconeSovereignAgent` + `L2_execution.reasoning.EmbeddingSovereignAgent` (L1→L4, L1→L2 inversions)
   - `ASTValidatorAgent.py` → `agentic_core.L5_safety.validators.unified_cst_healer` (L1→L5 inversion)

### What Each Guardian Test Enforces

**`test_circuit_breaker_gate.py`** (G-CB-1):
- AST: `CircuitBreaker`, `CircuitBreakerOpenError`, `CircuitState`, `get_breaker`, `reset_registry` present
- Runtime: CLOSED state allows requests; `record_failure()` × N opens breaker; OPEN state rejects `allow_request()`; `reset_registry()` clears all breakers

**`test_deterministic_loop_detector.py`** (G-DLD-1):
- AST: required classes + methods present; **no `time`/`datetime` imports** (clock-free determinism contract)
- Runtime: raises `ToolBudgetExceededError` at exactly `max_steps`; separate `trace_id` values are isolated; `reset_trace()` clears without affecting other traces

**`test_sovereignty_runtime_contract.py`** (G-SRC-1):
- AST: `SovereigntyBootstrap`, 4 exception classes, `bootstrap()` + `seal_and_finalize()` methods present; no layer inversions in exceptions module; bootstrap docstring enumerates step order
- Runtime: double-call raises `RuntimeError`; `seal_and_finalize()` before `bootstrap()` raises `RuntimeError`; all 4 exception classes are importable and carry messages

**`test_l4_state_write_sovereignty.py`** (G-L4S-1):
- AST: no raw `write_text()`/`open(write)` without gateway; no imports from L2/L5; no Agent class definitions; expected sub-layers exist
- **Detects 4 real violations** (see above)

**`test_l1_cognition_purity_contract.py`** (G-L1C-1):
- AST: no imports from L2/L3/L4/L5; no raw writes; `assert_l1_purity()` importable; `compute_event_hash` uses `hashlib` not `random`; `MetaLearningGuardrails`/`CacheGuardrails` present
- Runtime: `assert_l1_purity(instance)` passes clean objects, raises on `redis`/`subprocess` attributes
- **Detects 2 real violations** (see above)

### Pre-existing Conftest Fix

`tests/guardian/conftest.py` line 33 had a broken import (`tests._helpers.robust_fs`) — fixed to `tests.helpers.robust_fs` (the actual module path). This was blocking all direct `tests/guardian/` runs.

### Recommended Next Guardian Tests (backlog)

Based on the gap analysis, the next highest-value guardian tests to write:

| Priority | File | Contract to enforce |
|---|---|---|
| P1 | `test_transcript_freezer.py` | `FrozenTranscript` immutability; mutation raises `TranscriptMutationViolation` |
| P2 | `test_archival_gatekeeper.py` | `ArchivalGatekeeper` fail-closed; missing auth raises; AST structural |
| P3 | `test_l6_observability_write_contract.py` | L6 must not write (§ constitutional rule); AST scan |
| P4 | `test_apps_shared_enforcement_contracts.py` | All 11 `apps_shared/enforcement/` strategies importable + have required interface methods |
| P5 | `test_apps_rg_engine_contracts.py` | `apps_rg/engines/` have required `run()`/`execute()` methods; no direct LLM SDK imports |

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

