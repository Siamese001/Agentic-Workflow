# Comprehensive Agent Integration Migration Plan

**Date:** 2026-02-03
**Last Updated:** 2026-02-03T13:40:00-05:00
**Status:** ✅ FOUNDATION COMPLETE (Phases 1-6 Infrastructure)
**Scope:** All 171 agents across agentic_core, apps_rg, apps_lic
**Method:** AST-verified gap analysis
**Goal:** Full integration with target architecture components

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


## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Agents** | 171 |
| **Foundation Infrastructure** | ✅ COMPLETE |
| **Protocol Interfaces** | ✅ 4 protocols implemented |
| **Feature Flag System** | ✅ Operational |
| **L5 Safety Adapters** | ✅ Protocol-compliant |
| **Domain Integration** | ✅ RG/LIC mixins ready |
| **Total Tests Passing** | **268** |
| **Estimated Remaining** | 8- (agent rollout) |
| **Risk Level** | MEDIUM (foundation de-risks rollout) |

### Infrastructure Completion Status

| Phase | Component | Status | Tests |
|-------|-----------|--------|-------|
| 1 | Interfaces & Primitives | ✅ Complete | 111 |
| 2 | FeatureFlaggedAgentMixin | ✅ Complete | 27 |
| 3 | L5 Safety Adapters | ✅ Complete | 40 |
| 4 | Integration Utilities | ✅ Complete | 36 |
| 5 | Domain Application Mixins | ✅ Complete | 37 |
| 6 | E2E Integration Tests | ✅ Complete | 17 |

---

## AST-Verified Current State

### Layer Distribution
| Layer | Agents | With Healing | Without Healing |
|-------|--------|--------------|-----------------|
| **Apps** | 43 | 43 | 0 |
| **L5 Safety** | 85 | 85 | 0 |
| **L6 Observability** | 11 | 11 | 0 |
| **L3 Orchestration** | 10 | 9 | 1 |
| **L1 Cognition** | 7 | 7 | 0 |
| **L2 Execution** | 6 | 6 | 0 |
| **L4 State** | 5 | 5 | 0 |
| **L0 Maintenance** | 2 | 2 | 0 |
| **Base** | 1 | 1 | 0 |
| **Tests** | 1 | 1 | 0 |

### Current Mixin Usage
| Mixin | Agents Using | % Coverage |
|-------|-------------|------------|
| SovereignBaseAgent | 130 | 76% |
| SubatomicTestingMixin | 89 | 52% |
| LICAgentBase | 16 | 9% |
| RGAgentBase | 13 | 8% |
| MCPHardenedMixin | 6 | 4% |
| HealerMixin | 5 | 3% |
| RedisCacheMixin | 3 | 2% |
| **MetaLearningMixin** | **0** | **0%** |
| **HITLMixin** | **0** | **0%** |
| **AuditTrailMixin** | **0** | **0%** |

### Critical Component Usage (AST Verified)
| Component | Agents Using | Gap |
|-----------|-------------|-----|
| DetectionSignal | 0 | 171 agents |
| VerificationGate | 0 | 171 agents |
| HumanReviewQueue | 0 | 171 agents |
| recall_or_execute | 0 | 171 agents |
| log_audit_event | 0 | 171 agents |

---

## Migration Strategy: Hierarchical Cascade

### Principle: Top-Down Inheritance Propagation

```
Phase 1: Base Agents (1 agent)
    ↓ inheritance propagates
Phase 2: Layer Base Agents (L0-L6 bases)
    ↓ inheritance propagates
Phase 3: Domain Base Agents (RGAgentBase, LICAgentBase)
    ↓ inheritance propagates
Phase 4: Core L5 Safety Agents (85 agents)
    ↓ patterns established
Phase 5: Other Core Layers (L0-L4, L6)
    ↓ patterns replicated
Phase 6: Domain Apps (apps_rg, apps_lic)
```

By fixing base agents first, child agents automatically inherit capabilities.

---

## Phase 1: Foundation Layer ✅ COMPLETE

### 1.1 Protocol Interfaces (111 tests)
**Location:** `agentic_core/interfaces/`
**Status:** ✅ Implemented and tested

| Interface | File | Purpose |
|-----------|------|----------|
| VerificationGateProtocol | `verification_protocol.py` | Action verification before execution |
| DetectionSignalProtocol | `detection_protocol.py` | Structured violation detection output |
| HumanReviewProtocol | `review_protocol.py` | HITL workflow management |
| MetaLearningProtocol | `meta_learning_protocol.py` | Recall-or-execute patterns |

### 1.2 Primitives (included in 111 tests)
**Location:** `agentic_core/primitives/`
**Status:** ✅ Implemented and tested

| Component | File | Purpose |
|-----------|------|----------|
| FeatureFlagManager | `feature_flags.py` | Centralized flag management with env var support |
| DynamicLoader | `dependency_resolver.py` | Lazy loading to prevent circular dependencies |

### 1.3 Feature Flags Defined
| Flag | Default | Purpose |
|------|---------|----------|
| ENABLE_VERIFICATION_GATE | false | Control verification pre-checks |
| ENABLE_DETECTION_SIGNAL | false | Control structured detection output |
| ENABLE_HITL_WORKFLOW | false | Control human review routing |
| ENABLE_META_LEARNING | false | Control recall-or-execute |
| ENABLE_AUDIT_TRAIL | false | Control cryptographic logging |

---

## Phase 2: FeatureFlaggedAgentMixin ✅ COMPLETE

### 2.1 Core Mixin (27 tests)
**Location:** `agentic_core/base_agents/feature_flagged_agent_mixin.py`
**Status:** ✅ Implemented and tested

| Method | Purpose | Flag Control |
|--------|---------|---------------|
| `is_feature_enabled()` | Check flag status with overrides | All flags |
| `execute_with_flag()` | Execute function if flag enabled | Any flag |
| `verify_action()` | Verification gate integration | ENABLE_VERIFICATION_GATE |
| `emit_detection_signal()` | Detection signal emission | ENABLE_DETECTION_SIGNAL |
| `submit_for_review()` | Human review submission | ENABLE_HITL_WORKFLOW |
| `flagged_recall_or_execute()` | Meta-learning integration | ENABLE_META_LEARNING |
| `log_audit_event()` | Audit trail logging | ENABLE_AUDIT_TRAIL |
| `heal_with_verification()` | Combined healing flow | Multiple flags |
| `get_capability_report()` | Status reporting | N/A |

### 2.2 Graceful Degradation
All methods gracefully degrade when:
- Feature flag is disabled → Returns fallback result
- Implementation unavailable → Returns fallback result
- Legacy signature mismatch → Falls back to legacy call

---

## Phase 3: L5 Safety Adapters ✅ COMPLETE

### 3.1 Protocol-Compliant Adapters (40 tests)
**Location:** `agentic_core/L5_safety/adapters/`
**Status:** ✅ Implemented and tested

| Adapter | File | Protocol |
|---------|------|----------|
| VerificationGateAdapter | `verification_gate_adapter.py` | VerificationGateProtocol |
| HumanReviewAdapter | `human_review_adapter.py` | HumanReviewProtocol |

### 3.2 VerificationGateAdapter Features
- Wraps legacy `VerificationGate` class
- Full protocol compliance
- Feature flag integration
- Cache management
- Supported actions: modify_function, delete_import, remove_class, modify_method, modify_variable

### 3.3 HumanReviewAdapter Features
- Full review workflow: submit → pending → approve/reject
- Queue depth tracking
- Agent-filtered pending review retrieval
- Auto-approve when HITL disabled

### 3.4 Remaining L5 Agent Rollout (PENDING)
**Target:** `agentic_core/L5_safety/validators/` (50+ agents)

| Agent Category | Count | Status |
|----------------|-------|--------|
| Critical Validators | 5 | Pending |
| Structural Validators | 4 | Pending |
| Code Quality Validators | 4 | Pending |

### 3.5 Guardrails Sub-Phase (PENDING)
**Target:** `agentic_core/L5_safety/guardrails/` (30+ agents)

| Agent Category | Count | Status |
|----------------|-------|--------|
| Security Guardrails | 4 | Pending |
| Quality Guardrails | 4 | Pending |

### 3.6 Healers Sub-Phase (PENDING)
**Target:** All healing agents

| Agent | Status |
|-------|--------|
| CodeHealerAgent | Pending |
| StructureHealerAgent | Pending |
| SurgicalCSTHealer | Pending |

### 3.7 Pattern: Healing with Verification (IMPLEMENTED)
```python
# From FeatureFlaggedAgentMixin.heal_with_verification()
def heal_with_verification(self, violation, heal_fn):
    # 1. Verify target exists (if flag enabled)
    verification = self.verify_action(
        file_path=violation.get('file_path'),
        action_type=violation.get('fix_type'),
        target_node=violation.get('target')
    )
    if not verification.get('success'):
        return {'status': 'skipped', 'reason': verification.get('reason')}

    # 2. Check risk level and route to HITL if needed
    risk = self._classify_risk(violation)
    if risk == 'high':
        review = self.submit_for_review(
            agent_name=self.__class__.__name__,
            action_type=violation.get('fix_type'),
            target_file=violation.get('file_path'),
            description=violation.get('message'),
            risk_level=risk
        )
        if review.get('status') == 'pending':
            return {'status': 'pending_review', 'request_id': review.get('request_id')}

    # 3. Execute healing function
    result = heal_fn(violation)

    # 4. Log audit event
    self.log_audit_event('heal_executed', {...})

    return result
```

---

## Phase 4: Integration Utilities ✅ COMPLETE

### 4.1 Component Factory (36 tests)
**Location:** `agentic_core/integration/component_factory.py`
**Status:** ✅ Implemented and tested

| Method | Purpose |
|--------|----------|
| `get_verification_gate()` | Cached protocol-compliant gate |
| `get_human_review_queue()` | Cached protocol-compliant queue |
| `get_detection_emitter()` | Cached detection emitter |
| `get_meta_learning_service()` | Cached ML service |
| `get_component_status()` | Status of all components |
| `clear_instances()` | Clear cached instances |

### 4.2 Migration Helper (included in 36 tests)
**Location:** `agentic_core/integration/migration_helper.py`
**Status:** ✅ Implemented and tested

| Method | Purpose |
|--------|----------|
| `check_agent_compliance()` | Verify agent implements required interfaces |
| `get_migration_status()` | Aggregate compliance statistics |
| `generate_migration_report()` | Human-readable compliance report |

### 4.3 Core Layers Agent Rollout (PENDING)

| Layer | Agents | Status |
|-------|--------|--------|
| L6 Observability | 11 | Pending |
| L3 Orchestration | 10 | Pending |
| L1 Cognition | 7 | Pending |
| L2 Execution | 6 | Pending |
| L4 State | 5 | Pending |
| L0 Maintenance | 2 | Pending |

---

## Phase 5: Domain Application Mixins ✅ COMPLETE

### 5.1 Domain Integration Module (37 tests)
**Location:** `apps_shared/integration/`
**Status:** ✅ Implemented and tested

| Component | File | Purpose |
|-----------|------|----------|
| DomainAgentMixin | `domain_agent_mixin.py` | Domain-aware FeatureFlaggedAgentMixin |
| RGDomainMixin | `domain_agent_mixin.py` | Resume Generation specific |
| LICDomainMixin | `domain_agent_mixin.py` | LinkedIn Canonical specific |
| IntegrationConfig | `integration_config.py` | Domain configuration |

### 5.2 Domain Mixin Features
| Feature | RG | LIC |
|---------|-----|-----|
| Similarity Threshold | 0.85 | 0.92 (stricter) |
| TTL (seconds) | 3600 | 7200 (longer) |
| Rate Limit (req/min) | 100 | 50 (conservative) |
| HITL Required | Optional | **Mandatory** |
| Domain Isolation | ✅ | ✅ |

### 5.3 Domain-Specific Methods
| Method | RG | LIC |
|--------|-----|-----|
| `store_resume_pattern()` | ✅ | - |
| `store_campaign_pattern()` | - | ✅ |
| `get_rg_context()` | ✅ | - |
| `get_lic_context()` | - | ✅ |
| `domain_heal_with_verification()` | ✅ | ✅ |
| `domain_log_audit_event()` | ✅ | ✅ |
| `validate_domain_pattern()` | ✅ | ✅ |

### 5.4 Domain Agent Rollout (PENDING)

| Domain | Agents | Status |
|--------|--------|--------|
| apps_rg | 21 | Ready for mixin adoption |
| apps_lic | 22 | Ready for mixin adoption |

---

## Phase 6: E2E Integration Testing ✅ COMPLETE

### 6.1 E2E Test Coverage (17 tests)
**Location:** `tests/integration/test_migration_e2e.py`
**Status:** ✅ All passing

| Test Suite | Coverage |
|------------|----------|
| Feature Flag Integration | Flags control component availability |
| Verification Gate Flow | Disabled allows all, enabled validates |
| Human Review Flow | Auto-approve when disabled, full workflow when enabled |
| Domain Agent Integration | RG/LIC inherit all capabilities |
| Migration Compliance | Legacy vs migrated agent detection |
| Complete Healing Workflow | All safety checks combined |
| Configuration Integration | Domain configs match mixin defaults |

### 6.2 Feature Flags (Implemented)
| Flag | Default | Purpose |
|------|---------|----------|
| ENABLE_VERIFICATION_GATE | false | Target verification pre-checks |
| ENABLE_DETECTION_SIGNAL | false | Structured detection output |
| ENABLE_HITL_WORKFLOW | false | Human review routing |
| ENABLE_META_LEARNING | false | Recall-or-execute caching |
| ENABLE_AUDIT_TRAIL | false | Cryptographic audit logging |

### 6.3 Production Rollout (PENDING)
| Metric | Target | Current |
|--------|--------|----------|
| Tests Passing | 100% | ✅ 268/268 |
| Infrastructure Ready | Yes | ✅ Complete |
| Agent Rollout | 171 | 0 (pending) |

---

## Phase 7: Agent Rollout (REMAINING WORK)

### 7.1 Rollout Strategy
With infrastructure complete, agents can now adopt the mixins:

```python
# Example: Migrating an existing agent
from apps_shared.integration import RGDomainMixin

class MyRGAgent(RGDomainMixin, ExistingBase):
    def __init__(self):
        super().__init__()

    def heal(self, violation):
        # Use pre-built healing flow
        return self.domain_heal_with_verification(
            violation,
            heal_fn=self._do_heal
        )
```

### 7.2 Remaining Agent Count by Layer
| Layer | Agents | Mixin to Use |
|-------|--------|---------------|
| L5 Safety | 85 | FeatureFlaggedAgentMixin |
| apps_rg | 21 | RGDomainMixin |
| apps_lic | 22 | LICDomainMixin |
| L6 Observability | 11 | FeatureFlaggedAgentMixin |
| L3 Orchestration | 10 | FeatureFlaggedAgentMixin |
| L1 Cognition | 7 | FeatureFlaggedAgentMixin |
| L2 Execution | 6 | FeatureFlaggedAgentMixin |
| L4 State | 5 | FeatureFlaggedAgentMixin |
| L0 Maintenance | 2 | FeatureFlaggedAgentMixin |
| **Total** | **169** | - |

### 7.3 Documentation (Delivered)
- Protocol interfaces documented in docstrings
- Mixin usage via comprehensive test examples
- E2E tests serve as integration patterns guide

---

## Risk Mitigation Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| MRO Conflicts | MEDIUM | HIGH | Test each mixin combination |
| Performance Degradation | MEDIUM | MEDIUM | Feature flags, lazy loading |
| Human Review Bottleneck | LOW | HIGH | Auto-approve low-risk |
| Meta-Learning False Positives | MEDIUM | MEDIUM | Confidence thresholds |
| Infrastructure Dependency | LOW | HIGH | Graceful degradation |
| Breaking Changes | MEDIUM | HIGH | Incremental rollout |

---

## Success Metrics

| Milestone | Status | Tests | Coverage |
|-----------|--------|-------|----------|
| Phase 1: Interfaces & Primitives | ✅ Complete | 111 | Foundation |
| Phase 2: FeatureFlaggedAgentMixin | ✅ Complete | 27 | Core mixin |
| Phase 3: L5 Safety Adapters | ✅ Complete | 40 | Protocol adapters |
| Phase 4: Integration Utilities | ✅ Complete | 36 | Factory & helper |
| Phase 5: Domain Mixins | ✅ Complete | 37 | RG/LIC ready |
| Phase 6: E2E Testing | ✅ Complete | 17 | Full validation |
| **Infrastructure Total** | **✅ Complete** | **268** | **100%** |
| Phase 7: Agent Rollout | 🔄 Pending | - | 0/169 agents |

---

## Appendix A: Integration Pattern Templates

### A.1 Standard Agent Integration
```python
class MyAgent(
    MetaLearningMixin,       # P0 - recall_or_execute
    AuditTrailMixin,         # P1 - cryptographic logging
    CostGuardrailMixin,      # P1 - budget enforcement
    SovereignBaseAgent
):
    def __init__(self):
        super().__init__()
        self.verification_gate = VerificationGate()
        self.review_queue = HumanReviewQueue()

    def execute(self, task) -> DetectionSignal:
        return self.recall_or_execute(
            context=f"{self.__class__.__name__}:{task.hash}",
            execution_fn=lambda: self._do_execute(task)
        )
```

### A.2 Healing Agent Integration
```python
class MyHealer(
    MetaLearningMixin,
    AuditTrailMixin,
    HealerMixin,
    SovereignBaseAgent
):
    def heal(self, violation: dict) -> dict:
        # Pre-check
        if not self.verification_gate.verify_action(...):
            return {'status': 'skipped'}

        # Risk routing
        signal = DetectionSignal.from_violation(violation)
        if signal.classify_risk_level() == 'high':
            return self.submit_for_review(violation)

        # Execute with learning
        return self.recall_or_execute(
            context=f"heal:{violation['type']}",
            execution_fn=lambda: self._do_heal(violation)
        )
```

---

## Appendix B: Agent Inventory by Phase

### Phase 1 Agents (1)
- SovereignBaseAgent

### Phase 2 Agents (7)
- L0MaintenanceBaseAgent, L1CognitionBase, L2ExecutionBase
- L3OrchestrationBase, L4StateBase, L5SafetyBase
- L6ObservabilityBase

### Phase 3 Agents (85)
- All agents in `agentic_core/L5_safety/`

### Phase 4 Agents (41)
- L0: 2 agents, L1: 7 agents, L2: 6 agents
- L3: 10 agents, L4: 5 agents, L6: 11 agents

### Phase 5 Agents (43)
- apps_rg: 21 agents
- apps_lic: 22 agents

---

---

## Files Delivered

### Interfaces (`agentic_core/interfaces/`)
- `__init__.py` - Module exports
- `verification_protocol.py` - VerificationGateProtocol
- `detection_protocol.py` - DetectionSignalProtocol
- `review_protocol.py` - HumanReviewProtocol
- `meta_learning_protocol.py` - MetaLearningProtocol

### Primitives (`agentic_core/primitives/`)
- `__init__.py` - Module exports
- `feature_flags.py` - FeatureFlagManager
- `dependency_resolver.py` - DynamicLoader

### Base Agents (`agentic_core/base_agents/`)
- `feature_flagged_agent_mixin.py` - FeatureFlaggedAgentMixin

### L5 Safety Adapters (`agentic_core/L5_safety/adapters/`)
- `__init__.py` - Module exports
- `verification_gate_adapter.py` - VerificationGateAdapter
- `human_review_adapter.py` - HumanReviewAdapter

### Integration (`agentic_core/integration/`)
- `__init__.py` - Module exports
- `component_factory.py` - ComponentFactory
- `migration_helper.py` - MigrationHelper

### Domain Integration (`apps_shared/integration/`)
- `__init__.py` - Module exports
- `domain_agent_mixin.py` - DomainAgentMixin, RGDomainMixin, LICDomainMixin
- `integration_config.py` - IntegrationConfig, RG_CONFIG, LIC_CONFIG

### Tests
- `tests/unit/agentic_core/interfaces/` - 4 test files
- `tests/unit/agentic_core/primitives/` - 2 test files
- `tests/unit/agentic_core/base_agents/test_feature_flagged_agent_mixin.py`
- `tests/unit/agentic_core/L5_safety/adapters/` - 2 test files
- `tests/unit/agentic_core/integration/` - 2 test files
- `tests/unit/apps_shared/integration/` - 2 test files
- `tests/integration/test_migration_e2e.py`

---

**Report Generated:** 2026-02-03T10:15:00-05:00
**Last Updated:** 2026-02-03T13:40:00-05:00
**Analysis Method:** AST-based pattern matching with full file reads
**Confidence:** HIGH (verified via 268 passing tests)

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

