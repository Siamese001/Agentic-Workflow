---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\comprehensive-guardian-test-scope-enhancement-21b1fb.md'
original_relative_path: 'comprehensive-guardian-test-scope-enhancement-21b1fb.md'
source_sha256: 214daf03870dbb5375d25f69d6fd99e940d5e9ad14947e94087be53bfe1b4bfa
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Comprehensive Guardian/Test Scope Enhancement Plan

This plan analyzes the current agentic functionality and proposes additional guardian/test scope to ensure comprehensive coverage across all architectural layers, governance invariants, and operational boundaries.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State Analysis

### Existing Guardian Coverage
- **8 registered guardians** in `agentic_core.L0_routing.types.guardian_registry`:
  - `location_alignment` (slow) - File placement validation
  - `hygiene` (fast) - Temp artifacts, empty folders, init-only folders
  - `manifest_integrity` (fast) - Manifest existence, lock files, checksums
  - `drift_detection` (fast) - Root drift detection
  - `architecture_governance` (slow) - Import compliance, layer gravity
  - `classification_compliance` (slow) - Naming compliance, territory compliance
  - `hierarchy_compliance` (fast) - Missing structure, subfolder compliance
  - `contract_integrity` (fast) - Meta-guardian for script integrity

### Current Test Distribution
- **Guardian tests**: 80+ test files in `tests/guardian/`
- **Governance tests**: 60+ test files in `tests/governance/`
- **Markers**: `guardian`, `governance`, `security`, `constitutional`, `ssot`

## Identified Gaps & Proposed Enhancements

### 1. **Runtime Behavior Guardians** (NEW)

#### Gap: No guardians monitor actual runtime behavior
- Current guardians focus on static analysis
- Missing: Runtime contract enforcement, performance boundaries, resource limits

**Proposed Guardians:**
```python
# Runtime Contract Guardian
guardian_id="runtime_contract"
entrypoint="agentic_core.L5_safety.scripts.run_runtime_contract_guardian"
check_ids=("method_signature_drift", "interface_contract_violations", "return_type_mismatch")

# Performance Boundary Guardian
guardian_id="performance_boundary"
entrypoint="agentic_core.L5_safety.scripts.run_performance_boundary_guardian"
check_ids=("execution_time_exceeded", "memory_limit_breach", "cpu_threshold_violation")

# Resource Isolation Guardian
guardian_id="resource_isolation"
entrypoint="agentic_core.L5_safety.scripts.run_resource_isolation_guardian"
check_ids=("file_handle_leak", "network_connection_exhaustion", "temp_file_accumulation")
```

### 2. **Data Flow Integrity Guardians** (NEW)

#### Gap: No validation of data flow contracts between layers
- Missing: Data transformation validation, pipeline integrity, state consistency

**Proposed Guardians:**
```python
# Data Pipeline Guardian
guardian_id="data_pipeline_integrity"
entrypoint="agentic_core.L4_state.scripts.run_data_pipeline_guardian"
check_ids=("pipeline_break", "data_corruption", "schema_drift")

# State Consistency Guardian
guardian_id="state_consistency"
entrypoint="agentic_core.L4_state.scripts.run_state_consistency_guardian"
check_ids=("state_divergence", "concurrent_mutation", "rollback_failure")

# Serialization Contract Guardian
guardian_id="serialization_contract"
entrypoint="agentic_core.L4_state.scripts.run_serialization_guardian"
check_ids=("serialization_drift", "version_mismatch", "circular_reference")
```

### 3. **Security & Boundary Guardians** (NEW)

#### Gap: Limited security coverage beyond import safety
- Missing: Access control, privilege escalation, data exfiltration prevention

**Proposed Guardians:**
```python
# Access Control Guardian
guardian_id="access_control"
entrypoint="agentic_core.L5_safety.scripts.run_access_control_guardian"
check_ids=("privilege_escalation", "unauthorized_file_access", "sensitive_data_exposure")

# Cryptographic Integrity Guardian
guardian_id="cryptographic_integrity"
entrypoint="agentic_core.L5_safety.scripts.run_crypto_integrity_guardian"
check_ids=("weak_cryptography", "key_management_violation", "hash_collision")

# Network Boundary Guardian
guardian_id="network_boundary"
entrypoint="agentic_core.L5_safety.scripts.run_network_boundary_guardian"
check_ids=("unauthorized_network_access", "data_exfiltration", "command_injection")
```

### 4. **Agent Lifecycle Guardians** (NEW)

#### Gap: No validation of agent lifecycle contracts
- Missing: Agent initialization, state transitions, cleanup protocols

**Proposed Guardians:**
```python
# Agent Lifecycle Guardian
guardian_id="agent_lifecycle"
entrypoint="agentic_core.L2_execution.scripts.run_agent_lifecycle_guardian"
check_ids=("initialization_failure", "state_transition_violation", "cleanup_incomplete")

# Agent Communication Guardian
guardian_id="agent_communication"
entrypoint="agentic_core.L3_orchestration.scripts.run_agent_communication_guardian"
check_ids=("message_protocol_violation", "deadlock_detection", "circular_dependency")

# Agent Resource Guardian
guardian_id="agent_resource"
entrypoint="agentic_core.L2_execution.scripts.run_agent_resource_guardian"
check_ids=("resource_exhaustion", "memory_leak", "file_descriptor_leak")
```

## Enhanced Test Cases Implementation

### Test Case Categories

#### **A. Structural Integrity Tests**
```python
# tests/guardian/structural/test_layer_boundary_invariants.py
class TestLayerBoundaryInvariants:
    def test_no_upward_imports_from_lower_layers(self):
        """AST-based validation that lower layers never import higher layers."""

    def test_layer_gravity_compliance(self):
        """Validate gravity leak prevention across all layer boundaries."""

    def test_sovereign_territory_isolation(self):
        """Ensure sovereign territories maintain strict isolation."""
```

#### **B. Runtime Contract Tests**
```python
# tests/guardian/runtime/test_runtime_contract_compliance.py
class TestRuntimeContractCompliance:
    def test_method_signature_stability(self):
        """Verify method signatures don't drift across versions."""

    def test_interface_contract_enforcement(self):
        """Validate interface contracts are honored at runtime."""

    def test_return_type_consistency(self):
        """Ensure return types match declared signatures."""
```

#### **C. Data Flow Tests**
```python
# tests/guardian/data_flow/test_pipeline_integrity.py
class TestDataPipelineIntegrity:
    def test_pipeline_completeness(self):
        """Validate data pipelines have no breaks or missing stages."""

    def test_data_transformation_invariants(self):
        """Ensure data transformations preserve required invariants."""

    def test_schema_evolution_compatibility(self):
        """Test schema changes maintain backward compatibility."""
```

#### **D. Security Boundary Tests**
```python
# tests/guardian/security/test_security_boundary_enforcement.py
class TestSecurityBoundaryEnforcement:
    def test_privilege_escalation_prevention(self):
        """Verify no code paths allow privilege escalation."""

    def test_sensitive_data_access_control(self):
        """Ensure sensitive data access follows strict controls."""

    def test_network_isolation_compliance(self):
        """Validate network access follows allowed patterns only."""
```

#### **E. Performance Boundary Tests**
```python
# tests/guardian/performance/test_performance_boundary_compliance.py
class TestPerformanceBoundaryCompliance:
    def test_execution_time_limits(self):
        """Verify all operations stay within defined time limits."""

    def test_memory_usage_boundaries(self):
        """Ensure memory usage stays within allocated budgets."""

    def test_resource_cleanup_verification(self):
        """Validate proper cleanup of all allocated resources."""
```

### **F. Agent Lifecycle Tests**
```python
# tests/guardian/agents/test_agent_lifecycle_compliance.py
class TestAgentLifecycleCompliance:
    def test_agent_initialization_contracts(self):
        """Validate agents follow proper initialization protocols."""

    def test_state_machine_compliance(self):
        """Ensure agent state transitions follow defined state machines."""

    def test_cleanup_protocol_enforcement(self):
        """Verify agents properly clean up resources on termination."""
```

## Implementation Plan

### Phase 1: Guardian Registry Expansion
1. Add 8 new guardians to `agentic_core.L0_routing.types.guardian_registry`
2. Implement guardian entry points with proper contract interfaces
3. Update `test_guardian_meta_coverage.py` to include new guardians

### Phase 2: Core Guardian Implementation
1. Implement runtime contract validation logic
2. Create data flow integrity checking mechanisms
3. Build security boundary enforcement scanners
4. Develop agent lifecycle validation framework

### Phase 3: Comprehensive Test Suite
1. Create 15+ new test files covering all guardian categories
2. Implement AST-based validation for structural invariants
3. Add runtime contract testing infrastructure
4. Build performance boundary testing framework

### Phase 4: Integration & CI Enhancement
1. Update `.github/workflows/guardian-tests.yml` to include new guardians
2. Add performance budget testing to CI pipeline
3. Implement security scanning in guardian workflow
4. Create evidence generation for all new guardians

## Acceptance Criteria

### Functional Requirements
- [ ] All 8 new guardians registered and functional
- [ ] 15+ new test files with comprehensive coverage
- [ ] AST-based validation for structural invariants
- [ ] Runtime contract enforcement framework
- [ ] Performance boundary monitoring
- [ ] Security boundary validation
- [ ] Agent lifecycle compliance checking

### Quality Requirements
- [ ] All tests pass with `python -m pytest -q --color=no`
- [ ] Guardian aggregation includes all new guardians
- [ ] CI workflow runs all guardians successfully
- [ ] Evidence generation for all guardian results
- [ ] Meta-coverage test validates 100% guardian coverage

### Governance Requirements
- [ ] All guardians follow contract interface
- [ ] Deterministic execution with no side effects
- [ ] Proper error handling and reporting
- [ ] Integration with existing guardian aggregation
- [ ] Compliance with constitutional rules

## Risk Mitigation

### Technical Risks
- **Runtime overhead**: Implement performance budgeting to prevent guardian slowdown
- **False positives**: Use configurable thresholds and exception handling
- **Integration complexity**: Phase rollout with backward compatibility

### Operational Risks
- **CI pipeline impact**: Stagger guardian rollout to prevent pipeline failures
- **Development friction**: Provide clear documentation and debugging tools
- **Maintenance burden**: Automate guardian maintenance where possible

## Success Metrics

### Coverage Metrics
- Guardian count: 8 → 16 (100% increase)
- Test file count: 80+ → 95+ (20% increase)
- Structural invariant coverage: 70% → 95%
- Runtime contract coverage: 0% → 80%

### Quality Metrics
- Guardian execution time: <30s total aggregation
- Test suite execution: < full run
- False positive rate: <5% for all guardians
- CI pipeline stability: >95% success rate

This comprehensive enhancement plan ensures the agentic system has robust validation across all critical dimensions: structural integrity, runtime behavior, data flow, security boundaries, performance limits, and agent lifecycle management.

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

