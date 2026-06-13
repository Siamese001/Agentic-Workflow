# RCA: Four Classification Enforcement Gaps in FileClassificationAgent

**Date**: 2026-02-11
**Scope**: `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Summary

Four categories of structural violations were passing undetected through
`FileClassificationAgent.validate_layer_alignment()`. Root cause in each case:
the validation method had no check for the violation type.

---

## BUG 1: Config Files Missing `_config` Suffix

**Trigger**: Files in `config/` directories without `_config` suffix.

**Root Cause**: `validate_layer_alignment()` enforced scripts purity
(no PascalCase in scripts/) but had no analogous check for config/ naming.

**Fix**: Added `CONFIG_SUFFIX_MISSING` check. Flags `.py` files in any `config/`
or `*_configs/` directory whose stem does not end with `_config`, `_settings`,
`_blueprint`, or `_constants`.

**Source files affected** (9 non-test .py):

| File | Directory |
| ---- | --------- |
| `loader.py` | `apps_lic/config/` |
| `ReasoningToggles.py` | `apps_lic/config/` |
| `retry_policy.py` | `apps_lic/config/` |
| `AgentSpec.py` | `apps_rg/config/` |
| `ReasoningToggles.py` | `apps_rg/config/` |
| `unified_config_helper.py` | `apps_shared/config/` |
| `blueprint_compiler.py` | `agentic_core/L5_safety/config/` |
| `capability_gap_types.py` | `agentic_core/runtime/config/` |
| `reasoning_types.py` | `agentic_core/runtime/config/` |

**YAML files also affected** (12 in `agentic_core/config/agent_configs/`):
`ats_compatibility.yaml`, `brand_compliance.yaml`, `campaign_balance.yaml`,
`campaign_planner.yaml`, `content_quality.yaml`, `deliverability.yaml`,
`hop4_routing.yaml`, `hop5_generation.yaml`, `hop6_validation.yaml`,
`hop7_gate_decision.yaml`, `section_balance.yaml`, `unified_agent_schema.yaml`.
These should be renamed to `*_config.yaml`. Not covered by `validate_layer_alignment()`
which gates on `.py` — tracked for separate YAML naming enforcement.

---

## BUG 2: Agent Files Using snake_case Instead of PascalCase

**Trigger**: `neural_autoimmune_agent.py` contains `NeuralAutoImmuneAgent` class.

**Root Cause**: `validate_layer_alignment()` checked for agents outside `reasoning/`
but never checked whether agent files USE the PascalCase naming convention. The
`PascalSovereigntyFixer` agent handles renaming but FileClassificationAgent never
flags the violation.

**Fix**: Added `AGENT_NAMING_SNAKE_CASE` check. Flags `.py` files in `reasoning/`
that are all-lowercase with underscores but contain a ClassDef ending in `Agent`.

**Files affected** (13):

| File | Agent Class | Layer |
| ---- | ----------- | ----- |
| `neural_autoimmune_agent.py` | NeuralAutoImmuneAgent | L5_safety |
| `cached_state_ledger.py` | CachedStateLedgerAgent | L4_state |
| `checkpoint_manager.py` | CheckpointManagerAgent | L4_state |
| `gravity_state_store.py` | GravityStateAgent | L4_state |
| `sub_atomic_registry.py` | SubAtomicRegistryAgent | L2_execution |
| `coverage_engine.py` | CoverageAgent | L3_orchestration |
| `dag_engine.py` | DagEngineAgent | L3_orchestration |
| `domain_planner_engine.py` | DomainPlannerAgent (+4 more) | L3_orchestration |
| `fission_manager.py` | FissionManagerAgent | L3_orchestration |
| `orchestration_handshake.py` | OrchestrationHandshakeAgent | L3_orchestration |
| `state_management_engine.py` | StateManagementAgent | L3_orchestration |
| `integrity_gate_executor.py` | IntegrityGateExecutorAgent | L0_maintenance |
| `routing_decision.py` | RootCustomsAgent | L0_maintenance |

**Note**: `domain_planner_engine.py` contains 5 Agent classes in one file — also
violates one-class-per-file convention.

---

## BUG 3: Dashboard/Observability Files Outside L6_observability

**Trigger**: `validate_dashboard_ssot_util.py` in L5_safety/utils/.

**Root Cause**: `validate_layer_alignment()` had no domain-keyword-to-layer check.
Dashboard, metric, and telemetry files belong in L6_observability per LAYER_OVERRIDES
but no validation enforced this.

**Fix**: Added `OBSERVABILITY_OUTSIDE_L6` check. Flags `.py` files whose stem
contains `dashboard`, `metric`, or `telemetry` that are NOT in L6_observability.

**Files affected** (39 total, key clusters):

- **L0_maintenance/scripts/**: 17 dashboard utility scripts
- **L5_safety/utils/**: `validate_dashboard_ssot_util.py`,
  `validate_dashboard_data_sourcing_util.py`, `guard_observability_footprint_util.py`
- **L5_safety/enforcement/**: `fast_dashboard_e2_e_pipeline.py`
- **L2_execution/enforcement/**: `dashboard_e2_e_pipeline.py`
- **L4_state/**: `telemetry_recorder.py`, `sanitize_telemetry_util.py`
- **L3_orchestration/**: `log_orchestration_metrics.py`
- **L1_cognition/**: `meta_observability.py`, `observability_types.py`

---

## BUG 4: Non-Agent Files in reasoning/ Folders

**Trigger**: `cache_invalidation_utils.py` and `code_tool_runner_core.py` in
L5_safety/reasoning/.

**Root Cause**: `validate_layer_alignment()` checked for agents OUTSIDE reasoning/
(`AGENT_OUTSIDE_REASONING`) but never checked the inverse: non-agent files INSIDE
reasoning/. The reasoning/ subfolder convention requires Agent, Orchestrator, or
Executor classes only.

**Fix**: Added `NON_AGENT_IN_REASONING` check. Flags `.py` files in reasoning/
that contain no ClassDef ending in Agent, Orchestrator, or Executor.

**Files affected** (62 total, key clusters):

- **L1_cognition/reasoning/**: 20 files (engines, managers, caches, clients)
- **L3_orchestration/reasoning/**: 18 files (engines, routers, managers, policies)
- **L5_safety/reasoning/**: 10 files (utils, configs, shims)
- **L2_execution/reasoning/**: 7 files (registries, services, implementations)
- **L0_maintenance/reasoning/**: 1 file (sovereign_healing_engine.py)
- **L6_observability/reasoning/**: 2 files

---

## Root Cause Pattern

All 4 bugs share a common root cause: **validate_layer_alignment() enforced
structural rules only in one direction**. It checked "is X where it shouldn't be?"
but never "is the folder pure for its designated purpose?" Specifically:

| Existing Check | Missing Inverse |
| -------------- | --------------- |
| `AGENT_OUTSIDE_REASONING` (agent not in reasoning/) | `NON_AGENT_IN_REASONING` (non-agent in reasoning/) |
| `SCRIPTS_PURITY_VIOLATION` (PascalCase in scripts/) | `CONFIG_SUFFIX_MISSING` (non-config in config/) |
| `AGENT_LAYER_MISPLACEMENT` (agent in wrong layer) | `OBSERVABILITY_OUTSIDE_L6` (domain file in wrong layer) |
| (none) | `AGENT_NAMING_SNAKE_CASE` (agent file violating PascalCase) |

## Validation Results

All 4 new checks tested:
- **CONFIG_SUFFIX_MISSING**: catches `blueprint_compiler.py` in config/ ✓
- **AGENT_NAMING_SNAKE_CASE**: catches `neural_autoimmune_agent.py` ✓
- **OBSERVABILITY_OUTSIDE_L6**: catches `validate_dashboard_ssot_util.py` ✓
- **NON_AGENT_IN_REASONING**: catches `cache_invalidation_utils.py`, `code_tool_runner_core.py` ✓
- **Negative tests**: `RedisSovereignAgent.py`, `structure_blueprint_config.py` not flagged ✓

## Files Changed

- `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`
  - Added 4 new violation checks to `validate_layer_alignment()`
  - ~95 lines added

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

