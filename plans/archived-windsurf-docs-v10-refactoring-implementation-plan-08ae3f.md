---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\v10-refactoring-implementation-plan-08ae3f.md'
original_relative_path: 'v10-refactoring-implementation-plan-08ae3f.md'
source_sha256: bdc7caa3f3ba8af0483d47294456fa4d962b21edf0583e2c803ada43fbb3edda
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# V10 Architectural Transformation Implementation Plan v2.0

A hardened, state-aware approach to the Zero-Loss refactoring of 171 agents with behavioral snapshots, latency budgets, and MRO-safe mixin ordering.

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


## CRITICAL: ZERO-LOSS PROTOCOL RULES

> **These rules are NON-NEGOTIABLE and must be followed for every modification.**

### MRO ORDERING RULE (MANDATORY)
```python
# CORRECT: Safety Mixins ALWAYS precede Base Classes (Left-to-Right)
class MyAgent(AtomicExecutionMixin, CircuitBreakerMixin, L5SafetyBase):
    pass  # MRO: MyAgent → AtomicExecutionMixin → CircuitBreakerMixin → L5SafetyBase → object

# WRONG: Base class before mixin (WILL CAUSE SILENT FAILURES)
class MyAgent(L5SafetyBase, AtomicExecutionMixin):  # ❌ FORBIDDEN
    pass
```

**Why:** Python MRO resolves methods left-to-right. If `L5SafetyBase` comes first, its methods shadow mixin safety features, causing silent failures.

### STATE SNAPSHOT RULE (MANDATORY)
Before modifying ANY agent in L2 (Execution), L3 (Orchestration), or L4 (State):
```bash
# Execute BEFORE code changes
python scripts/state_snapshot.py --wave <N> --agent <AgentName>
```

---

## Overview

| Metric | Value |
|--------|-------|
| **Total Agents** | 171 |
| **Native Agents (Direct Migration)** | 171 |
| **Orphan Agents (Adapter Strategy)** | ~~1~~ **0** (Strategic Pivot) |
| **Existing Mixins** | 29 |
| **Guardian Tests** | 23 |
| **Batch Size** | 5 agents per checkpoint |
| **Latency Budget** | < 50ms overhead per agent |
| **Estimated Duration** | 4- |

---

## WAVE 2: NATIVE MIGRATION (DomainPlannerAgent)

> **STRATEGIC PIVOT:** We are modifying source code directly. The `DomainPlannerAdapter` is **DEPRECATED** and will not be used. Direct inheritance provides cleaner MRO and eliminates bridge complexity.

### Phase 2.1: DomainPlannerAgent Direct Migration
**Priority**: CRITICAL | **Duration**: 1-

#### 2.1.1 State Snapshot (PRE-REQUISITE)
- [ ] **Backup databases**: `cp -r data/*.db data/snapshots/wave2/`
- [ ] **Backup vector store**: `cp -r vector_store/ vector_store_snapshots/wave2/`
- [ ] **Backup memory**: `cp .windsurf/memory.jsonl .windsurf/memory_wave2_backup.jsonl`
- [ ] **Tag git state**: `git tag -a wave-2-pre -m "Pre-Wave 2 state snapshot"`
- **Script**: Create `scripts/state_snapshot.py` if not exists
- **Validation**: Verify all backups exist before proceeding

#### 2.1.2 Capture Golden Output (Behavioral Snapshot)
- [ ] Run `DomainPlannerAgent` with standard test input
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
- **Guardian Check**: `pytest tests/guardian/test_mro_integrity.py -k "DomainPlanner"`

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
- [ ] Run agent with same input as 2.1.2
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
**Priority**: HIGH | **Duration**: 

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
- [ ] Run golden output test for each agent
- **Checkpoint**: `git tag -a wave3-batch1 -m "Wave 3 Batch 1 complete"`
- **Test**: `pytest tests/guardian/test_mro_integrity.py`

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
**Priority**: HIGH | **Duration**: 1-

Target agents (Batch 2):
- `FilesystemSSOTReconcilerAgent`
- `HygieneGuardianAgent`
- `NamingConventionAgent`
- `ImportSafetyAgent`
- `GovernanceAgent`

- [ ] Capture golden outputs for all 5
- [ ] Apply `AtomicExecutionMixin` (FIRST in MRO)
- [ ] Verify golden output matches
- **Checkpoint**: `git tag -a wave3-batch2 -m "Wave 3 Batch 2 complete"`

### Phase 3.3: Critical Safety Agents - Batch 3 (5 agents)
**Priority**: HIGH | **Duration**: 1-

Target agents (Batch 3):
- `PolicyEnforcerAgent`
- `SurgicalCSTHealerMixin` integrations (2 agents)
- 2 additional high-priority validators

- [ ] Same process as Batch 2
- **Checkpoint**: `git tag -a wave3-batch3 -m "Wave 3 Batch 3 complete"`

### Phase 3.4: Remaining L5 Validators (70 agents)
**Priority**: MEDIUM | **Duration**: 5-

#### 3.4.1 Categorize by Risk Level
- [ ] HIGH risk (external_touch=true): 5 agents → Priority
- [ ] MEDIUM risk (mcp_hardened=false): 20 agents
- [ ] LOW risk (has_subatomic=true): 45 agents

#### 3.4.2 Mixin Application by Category
For each **batch of 5 agents**:
1. [ ] Capture golden outputs
2. [ ] Read current inheritance
3. [ ] Add appropriate mixin(s) - **Safety mixins FIRST**
4. [ ] Verify MRO ≤ 3
5. [ ] Run latency test (< 50ms overhead)
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
- [ ] Run latency budget test
- [ ] Run golden output verification
- **Command**: `pytest tests/guardian/ -v --tb=short`
- **Command**: `pytest tests/behavioral/verify_golden.py -v`
- [ ] Generate diff report: `git diff --stat HEAD~5`

---

## WAVE 4: L3 ORCHESTRATION LAYER (10 Agents)

### Phase 4.1: ContextualRouter Hardening
**Priority**: HIGH | **Duration**: 

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
**Priority**: HIGH | **Duration**: 2-

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
**Priority**: MEDIUM | **Duration**: 

#### 5.2.1 IntentAgent & PlanningAgent
- [ ] Verify existing mixins are correct
- [ ] Add `MetaLearningMixin` if not present
- **Files**: `agentic_core/L1_cognition/intent/`, `agentic_core/L1_cognition/planning/`

#### 5.2.2 Thought Engine Agents
- [ ] Add `CognitiveCacheMixin` for reasoning cache
- [ ] Integrate with `WorkingMemory`
- **File**: `agentic_core/L1_cognition/thought_engine/`

---

## WAVE 6: APPS LAYER (43 Agents)

### Phase 6.1: RG Agents (apps_rg)
**Priority**: MEDIUM | **Duration**: 3-

#### 6.1.1 Verify SubatomicTestingMixin
- [ ] All RG agents should have `SubatomicTestingMixin`
- [ ] Run subatomic tests for each
- **Command**: `pytest apps_rg/ -k "subatomic" -v`

#### 6.1.2 Add Missing Mixins
- [ ] Agents without healing → Add `HealerMixin`
- [ ] Agents with external_touch → Add `RateLimitMixin`
- **Guardian Check**: `pytest tests/guardian/test_subatomic_compliance.py`

### Phase 6.2: LIC Agents (apps_lic)
**Priority**: MEDIUM | **Duration**: 2-

Similar process to Phase 6.1.

---

## WAVE 7: REMAINING LAYERS (L0, L4, L6)

### Phase 7.1: L6 Observability (11 agents)
**Priority**: LOW | **Duration**: 1-

- [ ] Verify dashboard agents have proper observability
- [ ] Add `MetricsMixin` where missing
- [ ] Integrate `TelemetryAgent` with `CircuitBreakerMetrics`

### Phase 7.2: L4 State (5 agents)
**Priority**: LOW | **Duration**: 

- [ ] Verify `LedgerAgent` has audit trail
- [ ] Add `PersistenceMixin` where needed

### Phase 7.3: L0 Maintenance (2 agents)
**Priority**: LOW | **Duration**: 

- [ ] Verify bootstrap sequence is V10 compliant
- [ ] No additional mixins needed (foundation layer)

---

## WAVE 8: INTEGRATION & REGRESSION TESTING

### Phase 8.1: Full Guardian Suite
**Priority**: CRITICAL | **Duration**: 1-

- [ ] `pytest tests/guardian/ -v --tb=long`
- [ ] All 23 guardian tests must pass
- [ ] Generate coverage report

### Phase 8.2: End-to-End Scenarios
- [ ] Mental sandbox simulation (from audit report)
- [ ] Legacy agent failure path
- [ ] CircuitBreaker escalation to Human Review
- [ ] Full healing cycle with rollback

### Phase 8.3: Performance Benchmarks
- [ ] Measure MRO resolution time
- [ ] Measure CircuitBreaker overhead
- [ ] Measure AtomicExecution transaction cost

---

## TESTING STRATEGY

### Per-Agent Test Template
```bash
# 1. Before modification
git diff HEAD -- <file_path>
pytest tests/unit/<layer>/<agent_test>.py -v

# 2. After modification
pytest tests/unit/<layer>/<agent_test>.py -v
pytest tests/guardian/test_mro_integrity.py -k "<AgentName>"
pytest tests/guardian/test_ssot_compliance.py

# 3. Commit
git add <file_path>
git commit -m "feat(<layer>): Add <Mixin> to <AgentName>

- MRO depth: X (was Y)
- Guardian tests: PASS
- Unit tests: X/Y PASS"
```

### Guardian Test Coverage

| Test File | Purpose | Run After |
|-----------|---------|-----------|
| `test_mro_integrity.py` | MRO depth ≤ 3 | Every mixin addition |
| `test_ssot_compliance.py` | Structure blueprint | File moves/renames |
| `test_import_safety.py` | No circular imports | Import changes |
| `test_orphan_agent_detection.py` | Orphan detection | Inheritance changes |
| `test_anti_patterns.py` | Code quality | All changes |
| `test_agent_validation.py` | Agent rules | All changes |

---

## BEHAVIORAL SNAPSHOTS (Golden Output Testing)

> **Purpose:** Ensure V10 Mixins don't alter the functional logic of agents. This is the "Zero-Loss" verification.

### Protocol

#### Before Refactor (Capture Phase)
```bash
# For each agent being modified:
python -m pytest tests/behavioral/capture_golden.py -k "<AgentName>" --capture-output

# Output saved to:
# tests/snapshots/golden_<AgentName>.json
```

#### After Refactor (Verify Phase)
```bash
# Assert output matches golden snapshot:
python -m pytest tests/behavioral/verify_golden.py -k "<AgentName>"

# If mismatch detected:
# 1. STOP refactoring
# 2. Investigate functional change
# 3. Either fix the mixin or update the golden (with justification)
```

### Golden Snapshot Schema
```json
{
  "agent": "DomainPlannerAgent",
  "input": { "task": "...", "context": "..." },
  "output": { "plan": [...], "confidence": 0.85 },
  "metadata": {
    "captured_at": "2026-02-03T19:00:00Z",
    "version": "pre-v10",
    "mro_depth": 2
  }
}
```

### Test File Structure
```
tests/
├── behavioral/
│   ├── capture_golden.py      # Captures golden outputs
│   ├── verify_golden.py       # Verifies against golden
│   └── conftest.py            # Shared fixtures
├── snapshots/
│   ├── golden_DomainPlannerAgent.json
│   ├── golden_CodeHealerAgent.json
│   └── ...                    # One per agent
└── stress/
    └── test_atomic_concurrency.py  # Concurrency stress tests
```

---

## LATENCY BUDGET (Performance Constraint)

> **Constraint:** Agents with >2 Mixins must have execution overhead **< 50ms**.

### Measurement Protocol

#### Per-Agent Latency Test
```python
# tests/performance/test_latency_budget.py

import time

def test_agent_latency_budget(agent_class):
    """Verify mixin overhead is < 50ms."""
    # Baseline: Agent with no mixins
    baseline_agent = create_baseline_agent(agent_class)
    start = time.perf_counter()
    baseline_agent.execute(test_input)
    baseline_time = time.perf_counter() - start

    # With Mixins: Agent with V10 mixins
    mixin_agent = create_mixin_agent(agent_class)
    start = time.perf_counter()
    mixin_agent.execute(test_input)
    mixin_time = time.perf_counter() - start

    # Overhead calculation
    overhead = (mixin_time - baseline_time) * 1000  # Convert to ms
    assert overhead < 50, f"Overhead {overhead}ms exceeds 50ms budget"
```

### Latency Budget by Mixin Count

| Mixin Count | Max Overhead | Action if Exceeded |
|-------------|--------------|-------------------|
| 1 | 20ms | Warning |
| 2 | 35ms | Warning |
| 3+ | 50ms | **FAIL** - Optimize or remove mixin |

### Agents Requiring Latency Tests
- All agents with `>2` mixins in inheritance
- All agents in L2 (Execution) layer
- All agents with `external_touch=true`

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

### Rollback Decision Matrix

| Wave | Layers Affected | Rollback Actions |
|------|-----------------|------------------|
| Wave 2 | L3 | Code + DB Snapshot |
| Wave 3 | L5 | Code only |
| Wave 4 | L3 | Code + DB Snapshot |
| Wave 5 | L2, L1 | Code + DB + Memory.jsonl |
| Wave 6 | Apps | Code only |
| Wave 7 | L4, L6 | Code + DB Snapshot |

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
| Wave 6 | 43-50 | ~1,500 |
| Wave 7 | 18-25 | ~400 |
| Wave 8 | 0 (tests only) | ~100 |

---

## SUCCESS CRITERIA

### Per-Wave Gates
- [ ] All guardian tests pass
- [ ] No MRO depth > 3
- [ ] No import cycles introduced
- [ ] All unit tests pass
- [ ] Commit messages follow convention

### Final Acceptance
- [ ] 171/171 agents V10 compliant
- [ ] 23/23 guardian tests pass
- [ ] Zero regression in existing functionality
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

**Plan Version**: 2.0
**Created**: 2026-02-03
**Updated**: 2026-02-03 (v2.0 - Hardened)
**Based On**: `docs/reports/PHASE_1_AUDIT_REPORT.md` + Grok Risk Assessment
**Branch**: `healing-resolution-dev-2`

---

## CHANGELOG

### v2.0 (2026-02-03) - HARDENED RELEASE
**Based on Deep Architectural Review & Grok Risk Assessment**

#### Fixed Fatal Flaws:
1. **Architectural Conflict (Wave 2):** Removed Adapter strategy. Now using Direct Native Migration.
2. **State Corruption Risk:** Added State-Aware Rollback with DB/Vector snapshots.
3. **MRO Shadowing:** Added explicit MRO Ordering Rule - Safety Mixins MUST precede Base Classes.

#### New Sections Added:
- **CRITICAL: ZERO-LOSS PROTOCOL RULES** - Non-negotiable MRO and State Snapshot rules
- **BEHAVIORAL SNAPSHOTS** - Golden Output Testing protocol
- **LATENCY BUDGET** - <50ms overhead constraint for agents with >2 mixins
- **STATE-AWARE ROLLBACK** - Three-layer rollback (Code + State + Memory)

#### Changes to Waves:
- **Wave 2:** Removed `DomainPlannerAdapter` usage, added State Snapshot step, Direct Inheritance only
- **Wave 3:** Reduced batch size from 10 to **5 agents** per checkpoint
- **Wave 3:** Added Concurrency Stress Test (3.1.5) for file locking verification

### v1.0 (2026-02-03) - Initial Draft
- Basic wave structure
- Per-agent testing template
- Guardian test coverage mapping

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

