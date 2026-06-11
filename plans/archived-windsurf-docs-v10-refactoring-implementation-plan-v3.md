---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\v10-refactoring-implementation-plan-v3.md'
original_relative_path: 'v10-refactoring-implementation-plan-v3.md'
source_sha256: 3949ecab056433eb132c91e37327414218bb190823462442eb46f58c9fa344af
recovered_status: SURVIVED_IN_CURRENT
last_commit: 'c9f7b72fa51'
last_commit_date: '2026-02-15 13:34:42 -0500'
created_date: '2026-02-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# V10 Architectural Transformation Implementation Plan v3.0

A fully deterministic, zero-flake approach to the Zero-Loss refactoring of 171 agents with automated MRO enforcement, deterministic behavioral harnesses, and granular blast-radius control.

---

## CRITICAL: ZERO-LOSS PROTOCOL RULES

> **These rules are NON-NEGOTIABLE and must be followed for every modification.**

### MRO ORDERING RULE (MANDATORY + AUTOMATED)

```python
# CORRECT: Safety Mixins ALWAYS precede Base Classes (Left-to-Right)
class MyAgent(AtomicExecutionMixin, CircuitBreakerMixin, L5SafetyBase):
    pass  # MRO: MyAgent → AtomicExecutionMixin → CircuitBreakerMixin → L5SafetyBase → object

# WRONG: Base class before mixin (WILL CAUSE SILENT FAILURES)
class MyAgent(L5SafetyBase, AtomicExecutionMixin):  # ❌ FORBIDDEN
    pass
```

**Why:** Python MRO resolves methods left-to-right. If `L5SafetyBase` comes first, its methods shadow mixin safety features, causing silent failures.

> **v3.0 ENFORCEMENT:** This rule is now enforced by `test_mro_mixin_order.py` which **BLOCKS COMMITS** on violation. See [Automated MRO Guard](#automated-mro-guard-commit-blocking).

### STATE SNAPSHOT RULE (MANDATORY)

Before modifying ANY agent in L2 (Execution), L3 (Orchestration), or L4 (State):

```bash
# Execute BEFORE code changes
python scripts/state_snapshot.py --wave <N> --agent <AgentName>
```

### DETERMINISTIC TESTING RULE (MANDATORY)

> **v3.0 NEW:** All behavioral tests MUST use the Deterministic Harness to prevent flaky tests.

```python
# All behavioral/golden tests MUST use this fixture
@pytest.fixture
def deterministic_harness():
    # See DETERMINISTIC BEHAVIORAL HARNESS section
    ...
```

---

## Overview

| Metric | Value |
|--------|-------|
| **Total Agents** | 171 |
| **Native Agents (Direct Migration)** | 171 |
| **Orphan Agents (Adapter Strategy)** | ~~1~~ **0** (Strategic Pivot) |
| **Existing Mixins** | 29 |
| **Guardian Tests** | 24 (was 23, +1 MRO Guard) |
| **Batch Size** | 5 agents per checkpoint |
| **Wave 6 Batches** | 9 (was 1) |
| **Latency Budget** | < 50ms overhead per agent |
| **Estimated Duration** | 4-6 weeks |

---

## WAVE 2: NATIVE MIGRATION (DomainPlannerAgent)

> **STRATEGIC PIVOT:** We are modifying source code directly. The `DomainPlannerAdapter` is **DEPRECATED** and will not be used. Direct inheritance provides cleaner MRO and eliminates bridge complexity.

### Phase 2.1: DomainPlannerAgent Direct Migration

**Priority**: CRITICAL | **Duration**: 1-2 days

#### 2.1.1 State Snapshot (PRE-REQUISITE)

- [ ] **Backup databases**: `cp -r data/*.db data/snapshots/wave2/`
- [ ] **Backup vector store**: `cp -r vector_store/ vector_store_snapshots/wave2/`
- [ ] **Backup memory**: `cp .windsurf/memory.jsonl .windsurf/memory_wave2_backup.jsonl`
- [ ] **Tag git state**: `git tag -a wave-2-pre -m "Pre-Wave 2 state snapshot"`
- **Script**: Create `scripts/state_snapshot.py` if not exists
- **Validation**: Verify all backups exist before proceeding

#### 2.1.2 Capture Golden Output (Behavioral Snapshot)

- [ ] Run `DomainPlannerAgent` with standard test input **using Deterministic Harness**
- [ ] Save output to `tests/snapshots/golden_DomainPlannerAgent.json`
- [ ] Document input parameters used for reproducibility
- **Command**: `python -m pytest tests/behavioral/capture_golden.py -k "DomainPlanner"`

#### 2.1.3 Direct Inheritance Migration

- [ ] **Change inheritance** (MRO-SAFE ORDER):

```python
# BEFORE
class DomainPlannerAgent(SovereignBaseAgent):

# AFTER (AtomicExecutionMixin MUST be first)
class DomainPlannerAgent(AtomicExecutionMixin, L3OrchestrationBase):
```

- [ ] Update imports: Add `from agentic_core.base_agents.atomic_execution_mixin import AtomicExecutionMixin`
- [ ] Update imports: Add `from agentic_core.base_agents.L3OrchestrationBase import L3OrchestrationBase`
- [ ] Verify MRO depth = 3 (Agent → Mixin → Base → object)
- **File**: `agentic_core/L3_orchestration/workflow_engines/DomainPlannerAgent.py`
- **Guardian Check**: `pytest tests/guardian/test_mro_mixin_order.py -k "DomainPlanner"`

#### 2.1.4 Add heal_repository() Method

- [ ] Implement `heal_repository()` returning canonical schema:

```python
def heal_repository(self) -> dict:
    return {
        "violations_found": 0,
        "violations_fixed": 0,
        "errors": [],
        "skipped": []
    }
```

- [ ] Do NOT modify existing `run_async()` logic
- **Test**: `pytest -k "test_domain_planner_healing"`

#### 2.1.5 Behavioral Verification (Golden Output Test)

- [ ] Run agent with same input as 2.1.2 **using Deterministic Harness**
- [ ] Assert output matches `golden_DomainPlannerAgent.json`
- [ ] If mismatch: **STOP** and investigate before proceeding
- **Command**: `python -m pytest tests/behavioral/verify_golden.py -k "DomainPlanner"`

#### 2.1.6 Deprecate DomainPlannerAdapter

- [ ] Add deprecation warning to `domain_planner_adapter.py`:

```python
import warnings
warnings.warn("DomainPlannerAdapter is deprecated. Use DomainPlannerAgent directly.", DeprecationWarning)
```

- [ ] Do NOT delete file (maintain backward compatibility)
- **File**: `agentic_core/L5_safety/adapters/domain_planner_adapter.py`

---

## WAVE 3: L5 SAFETY LAYER MIXIN ROLLOUT (85 Agents)

> **BATCH SIZE: 5 agents per checkpoint** (reduced from 10 for safer rollback granularity)

### Phase 3.1: Critical Safety Agents - Batch 1 (5 agents)

**Priority**: HIGH | **Duration**: 2 days

#### 3.1.1 VerificationGate Enhancement

- [ ] Add `AtomicExecutionMixin` for rollback capability (MUST be first in MRO)
- [ ] Integrate `HallucinationDetectionMixin`
- [ ] Wire to `GuardianSignalBus`
- **Files**:
  - `agentic_core/L5_safety/security/verification_gate.py`
- **Test**: `pytest tests/unit/L5_safety/security/test_verification_gate.py`

#### 3.1.2 CodeHealerAgent Enhancement

- [ ] Add `AtomicExecutionMixin`
- [ ] Verify `VerificationGate` integration
- [ ] Add `CircuitBreakerMixin` for timeout protection
- **File**: `agentic_core/L5_safety/policy_engine/code_healer_agent.py`
- **MRO Check**: Ensure depth ≤ 3 after mixin addition

#### 3.1.3 LocationAgent Enhancement

- [ ] Add `AtomicExecutionMixin`
- [ ] Validate constitutional rule enforcement (base agents location)
- **File**: `agentic_core/L5_safety/validators/location_agent.py`
- **Guardian Check**: `pytest tests/guardian/test_ssot_compliance.py`

#### 3.1.4 Batch Safety Validators - Batch 1 (5 agents)

Target agents (Batch 1):

- `HierarchyAgent`
- `FileClassificationAgent`
- `StructureHealerAgent`
- `CompositeGuardrailAgent`
- `ASTValidatorAgent`

**Strategy per agent** (MRO-SAFE):

```python
# Before
class MyAgent(L5SafetyBase):
    pass

# After (Safety Mixin MUST be first)
class MyAgent(AtomicExecutionMixin, L5SafetyBase):
    pass
```

- [ ] Apply `AtomicExecutionMixin` to all 5 agents
- [ ] Verify MRO order: `Mixin → Base → object`
- [ ] Run golden output test for each agent **using Deterministic Harness**
- **Checkpoint**: `git tag -a wave3-batch1 -m "Wave 3 Batch 1 complete"`
- **Test**: `pytest tests/guardian/test_mro_mixin_order.py`

#### 3.1.5 Concurrency Stress Test (HIGH-TRAFFIC AGENTS)

> **CRITICAL:** Before finalizing `AtomicExecutionMixin` on Healer agents, verify file locking works under concurrent access.

- [ ] Create test: `tests/stress/test_atomic_concurrency.py`
- [ ] Spawn **5 threads** targeting the same file simultaneously
- [ ] Verify file locking prevents race conditions
- [ ] Verify rollback works when one thread fails
- **Test Command**:

```bash
python -m pytest tests/stress/test_atomic_concurrency.py -v --tb=long
```

- **Pass Criteria**: Zero data corruption, all threads complete or rollback cleanly

### Phase 3.2: Critical Safety Agents - Batch 2 (5 agents)

**Priority**: HIGH | **Duration**: 1-2 days

Target agents (Batch 2):

- `FilesystemSSOTReconcilerAgent`
- `HygieneGuardianAgent`
- `NamingConventionAgent`
- `ImportSafetyAgent`
- `GovernanceAgent`

- [ ] Capture golden outputs for all 5 **using Deterministic Harness**
- [ ] Apply `AtomicExecutionMixin` (FIRST in MRO)
- [ ] Verify golden output matches
- **Checkpoint**: `git tag -a wave3-batch2 -m "Wave 3 Batch 2 complete"`

### Phase 3.3: Critical Safety Agents - Batch 3 (5 agents)

**Priority**: HIGH | **Duration**: 1-2 days

Target agents (Batch 3):

- `PolicyEnforcerAgent`
- `SurgicalCSTHealerMixin` integrations (2 agents)
- 2 additional high-priority validators

- [ ] Same process as Batch 2
- **Checkpoint**: `git tag -a wave3-batch3 -m "Wave 3 Batch 3 complete"`

### Phase 3.4: Remaining L5 Validators (70 agents)

**Priority**: MEDIUM | **Duration**: 5-7 days

#### 3.4.1 Categorize by Risk Level

- [ ] HIGH risk (external_touch=true): 5 agents → Priority
- [ ] MEDIUM risk (mcp_hardened=false): 20 agents
- [ ] LOW risk (has_subatomic=true): 45 agents

#### 3.4.2 Mixin Application by Category

For each **batch of 5 agents**:

1. [ ] Capture golden outputs **using Deterministic Harness**
2. [ ] Read current inheritance
3. [ ] Add appropriate mixin(s) - **Safety mixins FIRST**
4. [ ] Verify MRO ≤ 3
5. [ ] Run latency test (< 50ms overhead) **using Deterministic Harness**
6. [ ] Verify golden output matches
7. [ ] Commit with descriptive message
8. [ ] Create checkpoint tag

**Mixins to apply** (MRO Order):

| Agent Category | Mixin Order (Left-to-Right) |
|----------------|----------|
| Healers | `AtomicExecutionMixin`, `AuditTrailMixin`, `BaseAgent` |
| Validators | `HallucinationDetectionMixin`, `BaseAgent` |
| MCP-touching | `CircuitBreakerMixin`, `MCPHardenedMixin`, `RateLimitMixin`, `BaseAgent` |
| Memory-using | `RedisCacheMixin`, `SemanticCacheMixin`, `BaseAgent` |

#### 3.4.3 Checkpoint Testing (Every 5 Agents)

- [ ] After every 5 agents, run full guardian suite
- [ ] Run latency budget test **with Deterministic Harness**
- [ ] Run golden output verification
- **Command**: `pytest tests/guardian/ -v --tb=short`
- **Command**: `pytest tests/behavioral/verify_golden.py -v`
- [ ] Generate diff report: `git diff --stat HEAD~5`

---

## WAVE 4: L3 ORCHESTRATION LAYER (10 Agents)

### Phase 4.1: ContextualRouter Hardening

**Priority**: HIGH | **Duration**: 2 days

#### 4.1.1 CircuitBreaker Integration

- [ ] Verify `CircuitBreakerMixin` is applied
- [ ] Test all `RouteDecision` paths
- [ ] Validate `GuardianSignalBus` connection
- **File**: `agentic_core/L3_orchestration/contextual_router.py`

#### 4.1.2 WorkflowEngine Enhancement

- [ ] Add `AtomicExecutionMixin` for transaction safety
- [ ] Integrate with `ContextSession` for state tracking
- **Files**: `agentic_core/L3_orchestration/workflow_engines/*.py`

#### 4.1.3 Orchestration Agent Migration

Target agents:

- `WorkflowCoordinatorAgent`
- `TaskSchedulerAgent`
- `EventDispatcherAgent`
- `StateManagerAgent`
- `RecoveryAgent`
- `SynchronizationAgent`
- `DependencyResolverAgent`
- `ResourceAllocatorAgent`

- [ ] Apply `CircuitBreakerMixin` to all
- [ ] Verify timeout handling
- **Test**: `pytest tests/unit/L3_orchestration/ -v`

---

## WAVE 5: L2 EXECUTION & L1 COGNITION (13 Agents)

### Phase 5.1: L2 MCP Hardening (6 agents)

**Priority**: HIGH | **Duration**: 2-3 days

#### 5.1.1 ToolRegistryAgent

- [ ] Add `MCPHardenedMixin`
- [ ] Add `RateLimitMixin` for API protection
- [ ] Verify tool registration flow
- **File**: `agentic_core/L2_execution/tool_registry/`

#### 5.1.2 MCPAgent Enhancement

- [ ] Add `CircuitBreakerMixin` for external call protection
- [ ] Add `CachingMixin` for response caching
- [ ] Validate MCP protocol compliance
- **File**: `agentic_core/L2_execution/mcp/`

#### 5.1.3 Remaining L2 Agents

- `ExecutionAgent`
- `ActionHandlerAgent`
- `ResponseFormatterAgent`
- `ErrorRecoveryAgent`

### Phase 5.2: L1 Cognition Enhancement (7 agents)

**Priority**: MEDIUM | **Duration**: 2 days

#### 5.2.1 IntentAgent & PlanningAgent

- [ ] Verify existing mixins are correct
- [ ] Add `MetaLearningMixin` if not present
- **Files**: `agentic_core/L1_cognition/intent/`, `agentic_core/L1_cognition/planning/`

#### 5.2.2 Thought Engine Agents

- [ ] Add `CognitiveCacheMixin` for reasoning cache
- [ ] Integrate with `WorkingMemory`
- **File**: `agentic_core/L1_cognition/thought_engine/`

---

## WAVE 6: APPS LAYER (43 Agents) - GRANULAR BATCHES

> **v3.0 RESTRUCTURE:** Wave 6 is now split into **9 granular batches** to minimize blast radius. Each batch is an independent rollback unit.

### Wave 6 Batch Overview

| Batch | Agents | App | Checkpoint Tag |
|-------|--------|-----|----------------|
| 6.1 | 5 | apps_rg | `wave6-batch1` |
| 6.2 | 5 | apps_rg | `wave6-batch2` |
| 6.3 | 5 | apps_rg | `wave6-batch3` |
| 6.4 | 5 | apps_rg | `wave6-batch4` |
| 6.5 | 5 | apps_lic | `wave6-batch5` |
| 6.6 | 5 | apps_lic | `wave6-batch6` |
| 6.7 | 5 | apps_lic | `wave6-batch7` |
| 6.8 | 5 | apps_lic | `wave6-batch8` |
| 6.9 | 3 | mixed | `wave6-batch9` |

### Phase 6.1: RG Agents - Batch 1 (5 agents)

**Priority**: MEDIUM | **Duration**: 0.5 days

#### 6.1.1 Pre-Batch Protocol

- [ ] Capture golden outputs for all 5 agents **using Deterministic Harness**
- [ ] Document current MRO for each agent
- [ ] Create state snapshot: `git tag -a wave6-batch1-pre -m "Pre-Wave 6 Batch 1"`

#### 6.1.2 Mixin Application

Target agents (select first 5 from `apps_rg/`):

- Agent 1: `[TBD from discovery]`
- Agent 2: `[TBD from discovery]`
- Agent 3: `[TBD from discovery]`
- Agent 4: `[TBD from discovery]`
- Agent 5: `[TBD from discovery]`

For each agent:

- [ ] Add `SubatomicTestingMixin` if missing
- [ ] Add `HealerMixin` if no healing capability
- [ ] Add `RateLimitMixin` if external_touch=true
- [ ] Verify MRO order with `test_mro_mixin_order.py`

#### 6.1.3 Post-Batch Verification

- [ ] Run golden output verification **using Deterministic Harness**
- [ ] Run latency budget test **using Deterministic Harness**
- [ ] Run guardian suite: `pytest tests/guardian/ -v`
- [ ] **Checkpoint**: `git tag -a wave6-batch1 -m "Wave 6 Batch 1 complete"`

### Phase 6.2: RG Agents - Batch 2 (5 agents)

**Priority**: MEDIUM | **Duration**: 0.5 days

- [ ] Same protocol as Phase 6.1
- [ ] Target next 5 agents from `apps_rg/`
- [ ] **Checkpoint**: `git tag -a wave6-batch2 -m "Wave 6 Batch 2 complete"`

### Phase 6.3: RG Agents - Batch 3 (5 agents)

**Priority**: MEDIUM | **Duration**: 0.5 days

- [ ] Same protocol as Phase 6.1
- [ ] Target next 5 agents from `apps_rg/`
- [ ] **Checkpoint**: `git tag -a wave6-batch3 -m "Wave 6 Batch 3 complete"`

### Phase 6.4: RG Agents - Batch 4 (5 agents)

**Priority**: MEDIUM | **Duration**: 0.5 days

- [ ] Same protocol as Phase 6.1
- [ ] Target remaining agents from `apps_rg/`
- [ ] **Checkpoint**: `git tag -a wave6-batch4 -m "Wave 6 Batch 4 complete"`

### Phase 6.5: LIC Agents - Batch 5 (5 agents)

**Priority**: MEDIUM | **Duration**: 0.5 days

- [ ] Same protocol as Phase 6.1
- [ ] Target first 5 agents from `apps_lic/`
- [ ] **Checkpoint**: `git tag -a wave6-batch5 -m "Wave 6 Batch 5 complete"`

### Phase 6.6: LIC Agents - Batch 6 (5 agents)

**Priority**: MEDIUM | **Duration**: 0.5 days

- [ ] Same protocol as Phase 6.1
- [ ] Target next 5 agents from `apps_lic/`
- [ ] **Checkpoint**: `git tag -a wave6-batch6 -m "Wave 6 Batch 6 complete"`

### Phase 6.7: LIC Agents - Batch 7 (5 agents)

**Priority**: MEDIUM | **Duration**: 0.5 days

- [ ] Same protocol as Phase 6.1
- [ ] Target next 5 agents from `apps_lic/`
- [ ] **Checkpoint**: `git tag -a wave6-batch7 -m "Wave 6 Batch 7 complete"`

### Phase 6.8: LIC Agents - Batch 8 (5 agents)

**Priority**: MEDIUM | **Duration**: 0.5 days

- [ ] Same protocol as Phase 6.1
- [ ] Target next 5 agents from `apps_lic/`
- [ ] **Checkpoint**: `git tag -a wave6-batch8 -m "Wave 6 Batch 8 complete"`

### Phase 6.9: Remaining Agents - Batch 9 (3 agents)

**Priority**: MEDIUM | **Duration**: 0.5 days

- [ ] Same protocol as Phase 6.1
- [ ] Target remaining 3 agents from both apps
- [ ] **Checkpoint**: `git tag -a wave6-batch9 -m "Wave 6 Batch 9 complete - Wave 6 DONE"`

### Wave 6 Rollback Protocol

If ANY batch fails:

1. Rollback ONLY that batch: `git reset --hard wave6-batchN-pre`
2. Do NOT rollback other batches
3. Investigate and fix before retrying
4. Maximum blast radius: **5 agents** (not 43)

---

## WAVE 7: REMAINING LAYERS (L0, L4, L6)

### Phase 7.1: L6 Observability (11 agents)

**Priority**: LOW | **Duration**: 1-2 days

- [ ] Verify dashboard agents have proper observability
- [ ] Add `MetricsMixin` where missing
- [ ] Integrate `TelemetryAgent` with `CircuitBreakerMetrics`

### Phase 7.2: L4 State (5 agents)

**Priority**: LOW | **Duration**: 1 day

- [ ] Verify `LedgerAgent` has audit trail
- [ ] Add `PersistenceMixin` where needed

### Phase 7.3: L0 Maintenance (2 agents)

**Priority**: LOW | **Duration**: 0.5 days

- [ ] Verify bootstrap sequence is V10 compliant
- [ ] No additional mixins needed (foundation layer)

---

## WAVE 8: INTEGRATION & REGRESSION TESTING

### Phase 8.1: Full Guardian Suite

**Priority**: CRITICAL | **Duration**: 1-2 days

- [ ] `pytest tests/guardian/ -v --tb=long`
- [ ] All **24** guardian tests must pass (was 23, +1 MRO Guard)
- [ ] Generate coverage report

### Phase 8.2: End-to-End Scenarios

- [ ] Mental sandbox simulation (from audit report)
- [ ] Legacy agent failure path
- [ ] CircuitBreaker escalation to Human Review
- [ ] Full healing cycle with rollback

### Phase 8.3: Performance Benchmarks

- [ ] Measure MRO resolution time **using Deterministic Harness**
- [ ] Measure CircuitBreaker overhead **using Deterministic Harness**
- [ ] Measure AtomicExecution transaction cost **using Deterministic Harness**

---

## TESTING STRATEGY

### Per-Agent Test Template

```bash
# 1. Before modification
git diff HEAD -- <file_path>
pytest tests/unit/<layer>/<agent_test>.py -v

# 2. After modification
pytest tests/unit/<layer>/<agent_test>.py -v
pytest tests/guardian/test_mro_mixin_order.py -k "<AgentName>"
pytest tests/guardian/test_ssot_compliance.py

# 3. Commit
git add <file_path>
git commit -m "feat(<layer>): Add <Mixin> to <AgentName>

- MRO depth: X (was Y)
- Guardian tests: PASS
- Unit tests: X/Y PASS"
```

### Guardian Test Coverage

| Test File | Purpose | Run After | Blocks Commit |
|-----------|---------|-----------|---------------|
| `test_mro_mixin_order.py` | **MRO mixin ordering** | Every mixin addition | **YES** |
| `test_mro_integrity.py` | MRO depth ≤ 3 | Every mixin addition | YES |
| `test_ssot_compliance.py` | Structure blueprint | File moves/renames | YES |
| `test_import_safety.py` | No circular imports | Import changes | YES |
| `test_orphan_agent_detection.py` | Orphan detection | Inheritance changes | YES |
| `test_anti_patterns.py` | Code quality | All changes | NO |
| `test_agent_validation.py` | Agent rules | All changes | YES |

---

## AUTOMATED MRO GUARD (COMMIT-BLOCKING)

> **v3.0 NEW:** Automated enforcement of MRO ordering rule. Humans will forget the left-to-right rule. This test catches violations before they reach production.

### Test Implementation

**File**: `tests/guardian/test_mro_mixin_order.py`

```python
"""
Automated MRO Mixin Order Guardian Test.

This test BLOCKS COMMITS if any agent has incorrect mixin ordering.
Safety mixins (AtomicExecutionMixin, CircuitBreakerMixin) MUST precede
base agent classes in the inheritance list.

v3.0: Added to prevent silent MRO shadowing failures.
"""

import pytest
import inspect
from pathlib import Path
from typing import List, Type

# Import all agents dynamically
from agentic_core.utils.ssot_discovery import discover_all_agents

# Define safety mixins that MUST precede base classes
SAFETY_MIXINS = [
    "AtomicExecutionMixin",
    "CircuitBreakerMixin",
    "HallucinationDetectionMixin",
    "MCPHardenedMixin",
]

# Define base agent classes
BASE_AGENT_CLASSES = [
    "SovereignBaseAgent",
    "L0MaintenanceBaseAgent",
    "L1CognitionBase",
    "L2ExecutionBase",
    "L3OrchestrationBase",
    "L4StateBase",
    "L5SafetyBase",
    "L6ObservabilityBase",
]


def get_mro_class_names(agent_class: Type) -> List[str]:
    """Get list of class names in MRO order."""
    return [cls.__name__ for cls in agent_class.__mro__]


def check_mixin_order(agent_class: Type) -> tuple[bool, str]:
    """
    Check if safety mixins precede base classes in MRO.

    Returns:
        (is_valid, error_message)
    """
    mro_names = get_mro_class_names(agent_class)

    for mixin in SAFETY_MIXINS:
        if mixin not in mro_names:
            continue  # Mixin not used, skip

        mixin_index = mro_names.index(mixin)

        for base in BASE_AGENT_CLASSES:
            if base not in mro_names:
                continue  # Base not used, skip

            base_index = mro_names.index(base)

            if mixin_index > base_index:
                return (
                    False,
                    f"MRO VIOLATION: {agent_class.__name__} has {mixin} "
                    f"(index {mixin_index}) AFTER {base} (index {base_index}). "
                    f"Safety mixins MUST come BEFORE base classes."
                )

    return (True, "")


class TestMROMixinOrder:
    """Guardian test for MRO mixin ordering."""

    @pytest.fixture(scope="class")
    def all_agents(self):
        """Discover all agents in the codebase."""
        return discover_all_agents()

    def test_all_agents_have_correct_mro_order(self, all_agents):
        """
        COMMIT-BLOCKING TEST.

        Verifies that ALL agents with safety mixins have them
        positioned BEFORE base agent classes in the inheritance list.
        """
        violations = []

        for agent_class in all_agents:
            is_valid, error_msg = check_mixin_order(agent_class)
            if not is_valid:
                violations.append(error_msg)

        if violations:
            violation_report = "\n".join(violations)
            pytest.fail(
                f"MRO ORDERING VIOLATIONS DETECTED!\n\n"
                f"The following agents have incorrect mixin ordering:\n\n"
                f"{violation_report}\n\n"
                f"FIX: Move safety mixins to the LEFT of base classes:\n"
                f"  WRONG: class MyAgent(L5SafetyBase, AtomicExecutionMixin)\n"
                f"  RIGHT: class MyAgent(AtomicExecutionMixin, L5SafetyBase)\n\n"
                f"This commit is BLOCKED until all violations are fixed."
            )

    @pytest.mark.parametrize("mixin_name", SAFETY_MIXINS)
    def test_specific_mixin_ordering(self, all_agents, mixin_name):
        """Test each safety mixin individually for better error reporting."""
        violations = []

        for agent_class in all_agents:
            mro_names = get_mro_class_names(agent_class)

            if mixin_name not in mro_names:
                continue

            mixin_index = mro_names.index(mixin_name)

            for base in BASE_AGENT_CLASSES:
                if base not in mro_names:
                    continue

                base_index = mro_names.index(base)

                if mixin_index > base_index:
                    violations.append(
                        f"{agent_class.__name__}: {mixin_name} @ {mixin_index}, "
                        f"{base} @ {base_index}"
                    )

        if violations:
            pytest.fail(
                f"{mixin_name} ordering violations:\n" + "\n".join(violations)
            )
```

### Pre-Commit Hook Integration

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: mro-mixin-order-guard
      name: MRO Mixin Order Guard
      entry: pytest tests/guardian/test_mro_mixin_order.py -v --tb=short
      language: system
      pass_filenames: false
      always_run: true
      stages: [commit]
```

---

## DETERMINISTIC BEHAVIORAL HARNESS

> **v3.0 NEW:** All behavioral tests MUST use this harness to prevent flaky tests caused by timestamps, UUIDs, and system load variance.

### The Problem

Agent outputs contain volatile fields:

- `created_at`: Changes every run
- `trace_id`: Random UUID
- `elapsed_time`: Varies with system load
- `request_id`: Random UUID

Simple JSON comparison will **ALWAYS FAIL**.

### The Solution: Deterministic Fixture

**File**: `tests/behavioral/conftest.py`

```python
"""
Deterministic Behavioral Test Harness.

v3.0: All behavioral/golden tests MUST use this fixture to ensure
deterministic, reproducible outputs.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from typing import Any, Dict
import uuid
import copy


# Frozen timestamp for all tests
FROZEN_TIMESTAMP = datetime(2026, 1, 1, 0, 0, 0)
FROZEN_TIMESTAMP_ISO = "2026-01-01T00:00:00Z"

# Deterministic UUID sequence
UUID_SEQUENCE = [
    "00000000-0000-0000-0000-000000000001",
    "00000000-0000-0000-0000-000000000002",
    "00000000-0000-0000-0000-000000000003",
    "00000000-0000-0000-0000-000000000004",
    "00000000-0000-0000-0000-000000000005",
    "00000000-0000-0000-0000-000000000006",
    "00000000-0000-0000-0000-000000000007",
    "00000000-0000-0000-0000-000000000008",
    "00000000-0000-0000-0000-000000000009",
    "00000000-0000-0000-0000-000000000010",
]

# Fields to strip from output before comparison
VOLATILE_FIELDS = [
    "created_at",
    "updated_at",
    "timestamp",
    "elapsed_time",
    "execution_time",
    "duration",
    "trace_id",
    "request_id",
    "session_id",
    "correlation_id",
    "span_id",
]


class DeterministicUUIDGenerator:
    """Generates UUIDs in a deterministic sequence."""

    def __init__(self):
        self.index = 0

    def __call__(self) -> uuid.UUID:
        if self.index >= len(UUID_SEQUENCE):
            self.index = 0  # Wrap around
        result = uuid.UUID(UUID_SEQUENCE[self.index])
        self.index += 1
        return result

    def reset(self):
        self.index = 0


def strip_volatile_fields(obj: Any, fields: list = None) -> Any:
    """
    Recursively strip volatile fields from a dictionary or list.

    Args:
        obj: The object to strip fields from
        fields: List of field names to strip (defaults to VOLATILE_FIELDS)

    Returns:
        A copy of the object with volatile fields removed
    """
    if fields is None:
        fields = VOLATILE_FIELDS

    if isinstance(obj, dict):
        return {
            k: strip_volatile_fields(v, fields)
            for k, v in obj.items()
            if k not in fields
        }
    elif isinstance(obj, list):
        return [strip_volatile_fields(item, fields) for item in obj]
    else:
        return obj


@pytest.fixture
def deterministic_harness():
    """
    Pytest fixture that provides a deterministic test environment.

    Usage:
        def test_my_agent(deterministic_harness):
            with deterministic_harness:
                result = my_agent.execute(input)
                # result will have frozen timestamps and deterministic UUIDs

    The harness:
    1. Freezes datetime.utcnow() to 2026-01-01T00:00:00Z
    2. Seeds uuid.uuid4() to return deterministic sequence
    3. Provides strip_volatile_fields() for output comparison
    """

    class DeterministicContext:
        def __init__(self):
            self.uuid_generator = DeterministicUUIDGenerator()
            self.patches = []

        def __enter__(self):
            # Freeze time
            time_patch = patch('datetime.datetime')
            mock_datetime = time_patch.start()
            mock_datetime.utcnow.return_value = FROZEN_TIMESTAMP
            mock_datetime.now.return_value = FROZEN_TIMESTAMP
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            self.patches.append(time_patch)

            # Also patch common time modules
            for module in [
                'agentic_core.utils.datetime',
                'agentic_core.L4_state.ledger.datetime',
            ]:
                try:
                    p = patch(f'{module}.datetime')
                    m = p.start()
                    m.utcnow.return_value = FROZEN_TIMESTAMP
                    m.now.return_value = FROZEN_TIMESTAMP
                    self.patches.append(p)
                except ModuleNotFoundError:
                    pass

            # Seed UUID
            uuid_patch = patch('uuid.uuid4', self.uuid_generator)
            uuid_patch.start()
            self.patches.append(uuid_patch)

            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            for p in self.patches:
                p.stop()
            self.uuid_generator.reset()

        def strip_volatile(self, obj: Any) -> Any:
            """Strip volatile fields from output for comparison."""
            return strip_volatile_fields(obj)

        @property
        def frozen_timestamp(self) -> datetime:
            return FROZEN_TIMESTAMP

        @property
        def frozen_timestamp_iso(self) -> str:
            return FROZEN_TIMESTAMP_ISO

    return DeterministicContext()


@pytest.fixture
def golden_snapshot_path(request, tmp_path):
    """
    Fixture that provides the path to the golden snapshot file.

    Uses the test name to determine the snapshot filename.
    """
    test_name = request.node.name
    agent_name = test_name.replace("test_", "").replace("_golden", "")
    return Path("tests/snapshots") / f"golden_{agent_name}.json"
```

### Usage Example

```python
# tests/behavioral/test_domain_planner_golden.py

import json
import pytest
from pathlib import Path

from agentic_core.L3_orchestration.workflow_engines.DomainPlannerAgent import (
    DomainPlannerAgent
)


class TestDomainPlannerGolden:
    """Golden output tests for DomainPlannerAgent."""

    GOLDEN_PATH = Path("tests/snapshots/golden_DomainPlannerAgent.json")

    @pytest.fixture
    def standard_input(self):
        """Standard test input for reproducibility."""
        return {
            "task": "Plan repository healing",
            "context": {"violations": 5, "layer": "L5"}
        }

    def test_capture_golden(self, deterministic_harness, standard_input):
        """Capture golden output (run once, then skip)."""
        if self.GOLDEN_PATH.exists():
            pytest.skip("Golden snapshot already exists")

        with deterministic_harness:
            agent = DomainPlannerAgent()
            result = agent.execute(standard_input)

            # Strip volatile fields before saving
            clean_result = deterministic_harness.strip_volatile(result)

            golden = {
                "agent": "DomainPlannerAgent",
                "input": standard_input,
                "output": clean_result,
                "metadata": {
                    "captured_at": deterministic_harness.frozen_timestamp_iso,
                    "version": "pre-v10",
                    "harness_version": "3.0"
                }
            }

            self.GOLDEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            self.GOLDEN_PATH.write_text(json.dumps(golden, indent=2))

    def test_verify_golden(self, deterministic_harness, standard_input):
        """Verify output matches golden snapshot."""
        if not self.GOLDEN_PATH.exists():
            pytest.fail(f"Golden snapshot not found: {self.GOLDEN_PATH}")

        golden = json.loads(self.GOLDEN_PATH.read_text())

        with deterministic_harness:
            agent = DomainPlannerAgent()
            result = agent.execute(standard_input)

            # Strip volatile fields before comparison
            clean_result = deterministic_harness.strip_volatile(result)

            assert clean_result == golden["output"], (
                f"Output mismatch!\n"
                f"Expected: {json.dumps(golden['output'], indent=2)}\n"
                f"Got: {json.dumps(clean_result, indent=2)}"
            )
```

---

## LATENCY BUDGET (Performance Constraint)

> **Constraint:** Agents with >2 Mixins must have execution overhead **< 50ms**.

> **v3.0 REFINEMENT:** All latency tests MUST use the **Deterministic Harness** to eliminate variance caused by system load, I/O, and non-deterministic operations.

### Measurement Protocol

#### Per-Agent Latency Test (Deterministic)

**File**: `tests/performance/test_latency_budget.py`

```python
"""
Latency Budget Tests with Deterministic Harness.

v3.0: Uses deterministic harness to eliminate system load variance.
"""

import pytest
import time
from typing import Type

from tests.behavioral.conftest import deterministic_harness


class TestLatencyBudget:
    """Latency budget tests for agents with multiple mixins."""

    # Latency thresholds (in milliseconds)
    THRESHOLD_1_MIXIN = 20
    THRESHOLD_2_MIXINS = 35
    THRESHOLD_3_PLUS_MIXINS = 50

    # Number of iterations for averaging
    ITERATIONS = 10

    def get_mixin_count(self, agent_class: Type) -> int:
        """Count the number of V10 mixins in agent's MRO."""
        mixin_names = [
            "AtomicExecutionMixin",
            "CircuitBreakerMixin",
            "AuditTrailMixin",
            "HallucinationDetectionMixin",
            "MCPHardenedMixin",
            "RateLimitMixin",
        ]
        mro_names = [cls.__name__ for cls in agent_class.__mro__]
        return sum(1 for m in mixin_names if m in mro_names)

    def measure_execution_time(
        self,
        agent_class: Type,
        test_input: dict,
        deterministic_harness
    ) -> float:
        """
        Measure average execution time over multiple iterations.

        Uses deterministic harness to eliminate non-deterministic variance.
        """
        times = []

        with deterministic_harness:
            agent = agent_class()

            # Warm-up run (not counted)
            agent.execute(test_input)

            # Measured runs
            for _ in range(self.ITERATIONS):
                start = time.perf_counter()
                agent.execute(test_input)
                elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
                times.append(elapsed)

        # Return average, excluding outliers
        times.sort()
        trimmed = times[1:-1]  # Remove fastest and slowest
        return sum(trimmed) / len(trimmed) if trimmed else times[0]

    def test_agent_latency_budget(
        self,
        agent_class: Type,
        test_input: dict,
        deterministic_harness
    ):
        """
        Verify mixin overhead is within budget.

        Thresholds:
        - 1 mixin: < 20ms
        - 2 mixins: < 35ms
        - 3+ mixins: < 50ms (HARD FAIL)
        """
        mixin_count = self.get_mixin_count(agent_class)

        if mixin_count == 0:
            pytest.skip("No mixins to test")

        avg_time = self.measure_execution_time(
            agent_class, test_input, deterministic_harness
        )

        # Determine threshold
        if mixin_count >= 3:
            threshold = self.THRESHOLD_3_PLUS_MIXINS
            severity = "FAIL"
        elif mixin_count == 2:
            threshold = self.THRESHOLD_2_MIXINS
            severity = "WARNING"
        else:
            threshold = self.THRESHOLD_1_MIXIN
            severity = "WARNING"

        if avg_time > threshold:
            msg = (
                f"LATENCY BUDGET {severity}: {agent_class.__name__}\n"
                f"  Mixin count: {mixin_count}\n"
                f"  Average time: {avg_time:.2f}ms\n"
                f"  Threshold: {threshold}ms\n"
            )

            if severity == "FAIL":
                pytest.fail(msg + "  Action: Optimize or remove mixin")
            else:
                pytest.warns(UserWarning, match=msg)
```

### Latency Budget by Mixin Count

| Mixin Count | Max Overhead | Action if Exceeded |
|-------------|--------------|-------------------|
| 1 | 20ms | Warning |
| 2 | 35ms | Warning |
| 3+ | 50ms | **FAIL** - Optimize or remove mixin |

### Why Deterministic Harness for Latency?

Without the harness, latency tests are **flaky** because:

1. **I/O variance**: File system operations vary by 10-50ms
2. **UUID generation**: Crypto-secure UUIDs add ~1ms per call
3. **Timestamp operations**: System clock calls add variance
4. **Background processes**: System load affects timing

The harness mocks these operations, isolating **mixin overhead only**.

---

## BEHAVIORAL SNAPSHOTS (Golden Output Testing)

> **Purpose:** Ensure V10 Mixins don't alter the functional logic of agents. This is the "Zero-Loss" verification.

> **v3.0 MANDATE:** All golden tests MUST use the **Deterministic Harness**.

### Protocol

#### Before Refactor (Capture Phase)

```bash
# For each agent being modified (uses Deterministic Harness automatically):
python -m pytest tests/behavioral/capture_golden.py -k "<AgentName>" --capture-output

# Output saved to:
# tests/snapshots/golden_<AgentName>.json
```

#### After Refactor (Verify Phase)

```bash
# Assert output matches golden snapshot (uses Deterministic Harness automatically):
python -m pytest tests/behavioral/verify_golden.py -k "<AgentName>"

# If mismatch detected:
# 1. STOP refactoring
# 2. Investigate functional change
# 3. Either fix the mixin or update the golden (with justification)
```

### Golden Snapshot Schema (v3.0)

```json
{
  "agent": "DomainPlannerAgent",
  "input": { "task": "...", "context": "..." },
  "output": {
    "plan": ["step1", "step2"],
    "confidence": 0.85
  },
  "metadata": {
    "captured_at": "2026-01-01T00:00:00Z",
    "version": "pre-v10",
    "harness_version": "3.0",
    "mro_depth": 2,
    "volatile_fields_stripped": [
      "created_at",
      "trace_id",
      "elapsed_time"
    ]
  }
}
```

### Test File Structure

```
tests/
├── behavioral/
│   ├── conftest.py            # Deterministic Harness fixture
│   ├── capture_golden.py      # Captures golden outputs
│   ├── verify_golden.py       # Verifies against golden
│   └── test_*_golden.py       # Per-agent golden tests
├── snapshots/
│   ├── golden_DomainPlannerAgent.json
│   ├── golden_CodeHealerAgent.json
│   └── ...                    # One per agent
├── performance/
│   └── test_latency_budget.py # Latency tests (uses harness)
├── guardian/
│   ├── test_mro_mixin_order.py  # NEW: MRO Guard
│   └── ...
└── stress/
    └── test_atomic_concurrency.py
```

---

## ROLLBACK STRATEGY (State-Aware)

> **CRITICAL:** `git revert` alone does NOT revert Database/Vector schemas. State corruption can cause crash loops.

### Three-Layer Rollback Protocol

#### Layer 1: Code Rollback (Standard)

```bash
# Tag before each wave
git tag -a wave-X-pre -m "Pre-Wave X state"

# If issues occur - Code only
git revert HEAD~N..HEAD
```

#### Layer 2: State Rollback (L2/L3/L4 Agents)

If the wave involved **L2 (Execution), L3 (Orchestration), or L4 (State)** agents:

```bash
# Restore database snapshots
cp -r data/snapshots/wave<X>/*.db data/

# Restore vector store
rm -rf vector_store/
cp -r vector_store_snapshots/wave<X>/ vector_store/

# Verify integrity
python scripts/verify_state_integrity.py
```

#### Layer 3: IDE State Rollback (L1 Memory Agents)

If reverting **L1 Memory agents**, prevent context poisoning:

```bash
# Nuke Windsurf memory to prevent stale context
rm .windsurf/memory.jsonl

# Restore from backup (if exists)
cp .windsurf/memory_wave<X>_backup.jsonl .windsurf/memory.jsonl
```

### Rollback Decision Matrix (Updated for Wave 6 Batches)

| Wave | Layers Affected | Rollback Actions | Max Blast Radius |
|------|-----------------|------------------|------------------|
| Wave 2 | L3 | Code + DB Snapshot | 1 agent |
| Wave 3 | L5 | Code only | 5 agents |
| Wave 4 | L3 | Code + DB Snapshot | 10 agents |
| Wave 5 | L2, L1 | Code + DB + Memory.jsonl | 13 agents |
| Wave 6.1-6.9 | Apps | Code only | **5 agents** |
| Wave 7 | L4, L6 | Code + DB Snapshot | 18 agents |

### Emergency Recovery Script

```bash
#!/bin/bash
# scripts/emergency_rollback.sh

WAVE=$1

echo "Rolling back Wave $WAVE..."

# 1. Code rollback
git reset --hard wave-${WAVE}-pre

# 2. State rollback (if needed)
if [[ "$WAVE" =~ ^(2|4|5|7)$ ]]; then
    echo "Restoring state snapshots..."
    cp -r data/snapshots/wave${WAVE}/*.db data/
    cp -r vector_store_snapshots/wave${WAVE}/ vector_store/
fi

# 3. Memory rollback (Wave 5 only)
if [[ "$WAVE" == "5" ]]; then
    echo "Restoring IDE memory..."
    rm -f .windsurf/memory.jsonl
    cp .windsurf/memory_wave5_backup.jsonl .windsurf/memory.jsonl 2>/dev/null || true
fi

# 4. Verify
python scripts/verify_state_integrity.py
pytest tests/guardian/ -v --tb=short

echo "Rollback complete. Verify manually before proceeding."
```

---

## FILE DIFF TRACKING

### Automated Diff Report

After each wave, generate:

```bash
git diff wave-X-start..HEAD --stat > docs/reports/wave-X-diff-report.txt
git log wave-X-start..HEAD --oneline > docs/reports/wave-X-commits.txt
```

### Expected File Changes by Wave

| Wave | Files Modified | Lines Changed (Est.) |
|------|----------------|----------------------|
| Wave 2 | 3-5 | ~200 |
| Wave 3 | 85-100 | ~2,000 |
| Wave 4 | 10-15 | ~500 |
| Wave 5 | 13-18 | ~600 |
| Wave 6.1 | 5-7 | ~150 |
| Wave 6.2 | 5-7 | ~150 |
| Wave 6.3 | 5-7 | ~150 |
| Wave 6.4 | 5-7 | ~150 |
| Wave 6.5 | 5-7 | ~150 |
| Wave 6.6 | 5-7 | ~150 |
| Wave 6.7 | 5-7 | ~150 |
| Wave 6.8 | 5-7 | ~150 |
| Wave 6.9 | 3-5 | ~100 |
| Wave 7 | 18-25 | ~400 |
| Wave 8 | 0 (tests only) | ~100 |

---

## SUCCESS CRITERIA

### Per-Wave Gates

- [ ] All guardian tests pass (including `test_mro_mixin_order.py`)
- [ ] No MRO depth > 3
- [ ] No MRO ordering violations (Safety Mixins before Base Classes)
- [ ] No import cycles introduced
- [ ] All unit tests pass
- [ ] Golden output tests pass (using Deterministic Harness)
- [ ] Latency budget tests pass (using Deterministic Harness)
- [ ] Commit messages follow convention

### Final Acceptance

- [ ] 171/171 agents V10 compliant
- [ ] **24/24** guardian tests pass (was 23, +1 MRO Guard)
- [ ] Zero regression in existing functionality
- [ ] Zero flaky tests (Deterministic Harness enforced)
- [ ] Documentation updated
- [ ] Diff reports generated for all waves

---

## APPENDIX: MIXIN REFERENCE

### Available V10 Mixins (29 total)

| Mixin | Purpose | Apply To |
|-------|---------|----------|
| `AtomicExecutionMixin` | Rollback on failure | Healers, Validators |
| `AuditTrailMixin` | Audit logging | All agents |
| `CircuitBreakerMixin` | Timeout protection | External calls |
| `HallucinationDetectionMixin` | Verify targets exist | Healers |
| `MCPHardenedMixin` | MCP protocol safety | L2 agents |
| `RateLimitMixin` | API rate limiting | External touch |
| `RedisCacheMixin` | Redis caching | Memory agents |
| `SubatomicTestingMixin` | Built-in tests | All agents |
| `MetaLearningMixin` | Learn from outcomes | L1 agents |
| `TracingMixin` | Distributed tracing | All agents |

---

**Plan Version**: 3.0
**Created**: 2026-02-03
**Updated**: 2026-02-03 (v3.0 - Zero-Flake Hardening)
**Based On**: `docs/reports/PHASE_1_AUDIT_REPORT.md` + Grok Risk Assessment + Flaky Test Analysis
**Branch**: `healing-resolution-dev-2`

---

## CHANGELOG

### v3.0 (2026-02-03) - ZERO-FLAKE HARDENING

**Based on Flaky Test Analysis & Blast Radius Review**

#### Fixed Fatal Flaws

1. **Non-Determinism Trap:** Added Deterministic Behavioral Harness (freezes time, seeds UUIDs, strips volatile fields)
2. **Human Error Gap:** Added Automated MRO Guard (`test_mro_mixin_order.py`) that BLOCKS COMMITS
3. **Wave 6 Blast Radius:** Split 43 agents into 9 granular batches (max 5 agents per rollback unit)

#### New Protocols Added

- **DETERMINISTIC BEHAVIORAL HARNESS** - Pytest fixture for reproducible golden tests
- **AUTOMATED MRO GUARD** - Commit-blocking test for mixin ordering
- **GRANULAR WAVE 6 BATCHES** - 9 batches instead of 1

#### Changes to Sections

- **Behavioral Snapshots:** Now mandates Deterministic Harness
- **Latency Budget:** Now mandates Deterministic Harness
- **Guardian Test Coverage:** Added `test_mro_mixin_order.py` (24 tests, was 23)
- **Wave 6:** Restructured into 9 independent batches

### v2.0 (2026-02-03) - HARDENED RELEASE

**Based on Deep Architectural Review & Grok Risk Assessment**

#### Fixed Fatal Flaws

1. **Architectural Conflict (Wave 2):** Removed Adapter strategy. Now using Direct Native Migration.
2. **State Corruption Risk:** Added State-Aware Rollback with DB/Vector snapshots.
3. **MRO Shadowing:** Added explicit MRO Ordering Rule - Safety Mixins MUST precede Base Classes.

#### New Sections Added

- **CRITICAL: ZERO-LOSS PROTOCOL RULES** - Non-negotiable MRO and State Snapshot rules
- **BEHAVIORAL SNAPSHOTS** - Golden Output Testing protocol
- **LATENCY BUDGET** - <50ms overhead constraint for agents with >2 mixins
- **STATE-AWARE ROLLBACK** - Three-layer rollback (Code + State + Memory)

#### Changes to Waves

- **Wave 2:** Removed `DomainPlannerAdapter` usage, added State Snapshot step, Direct Inheritance only
- **Wave 3:** Reduced batch size from 10 to **5 agents** per checkpoint
- **Wave 3:** Added Concurrency Stress Test (3.1.5) for file locking verification

### v1.0 (2026-02-03) - Initial Draft

- Basic wave structure
- Per-agent testing template
- Guardian test coverage mapping
