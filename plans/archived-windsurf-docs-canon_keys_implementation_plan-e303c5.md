---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\canon_keys_implementation_plan-e303c5.md'
original_relative_path: 'canon_keys_implementation_plan-e303c5.md'
source_sha256: 6a12f1e69e9186740dde6fdee1467d8f935e93edefaf0b6f881ffd8abbac4d58
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Canon Keys Deprecation Implementation Plan

This detailed implementation plan outlines the systematic removal of all canon keys (0-51) references from the repository, organized into phases and sub-phases to maximize success probability while maintaining system integrity.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Phase 1: Foundation Cleanup (Week 1)

### Sub-Phase 1.1: Core Registry Removal (Days 1-2)
**Objective**: Remove all deprecated registry definitions and references

**Actions**:
1. **Remove Empty Registry Definition**
   - File: `agentic_core/L5_safety/validators/structure_blueprint.py`
   - Delete lines 4056-4059: `SAFETY_VALIDATION_REGISTRY` empty dict
   - Remove lines 4049-4054: Deprecation comment block
   - Verify no import statements reference the removed registry

2. **Clean Structural Blueprint Comments**
   - Remove line 489: "# agentic_core/utils/core_extensions EVICTED per CANON_VALIDATION_REGISTRY"
   - Remove line 2436: "# "core_extensions": "utils",  # EVICTED per CANON_VALIDATION_REGISTRY"
   - Update any remaining registry references in comments

3. **Update Constants Lists**
   - Remove "CANON_VALIDATION_REGISTRY" from required_constants in test files
   - Update any structural blueprint constant references

**Verification**:
- Run `python -c "from agentic_core.L5_safety.validators.structure_blueprint import *"` successfully
- Verify no import errors for removed constants

### Sub-Phase 1.2: Import Statement Cleanup (Days 3-4)
**Objective**: Remove all import statements referencing deprecated canon key components

**Actions**:
1. **Test File Import Cleanup**
   - `tests/unit/agentic_core/L0_maintenance/scripts/test_canon_key_removal.py`: Remove line 37
   - `tests/unit/agentic_core/L5_safety/validators/test_structure_reconciliation.py`: Remove line 103
   - `tests/unit/agentic_core/L0_maintenance/scripts/test_consolidated_migration.py`: Remove line 118
   - `tests/unit/agentic_core/L0_maintenance/scripts/test_final_integrity_audit.py`: Remove line 159
   - `tests/unit/agentic_core/L0_maintenance/scripts/test_final_integrity_simple.py`: Remove line 112

2. **Conditional Import Updates**
   - Update try/except blocks that handle missing registry imports
   - Remove fallback logic for deprecated components

**Verification**:
- Run `pytest --collect-only` on affected test files
- Ensure no ImportError exceptions during collection

### Sub-Phase 1.3: Phase 1 Validation (Day 5)
**Objective**: Complete validation of foundation cleanup

**Actions**:
1. **Comprehensive Testing**
   - Run full test suite on modified files
   - Verify structural blueprint integrity
   - Check for runtime import errors

2. **Documentation Update**
   - Update any documentation referencing the removed registry
   - Update implementation summaries

**Success Criteria**:
- All import statements succeed
- No registry-related errors in logs
- Test collection completes without import failures

## Phase 2: Test Framework Migration (Week 2)

### Sub-Phase 2.1: Active Test File Conversion (Days 1-3)
**Objective**: Convert active canon key tests to Guardian framework

**Actions**:
1. **Primary Test File Updates**
   - `tests/unit/agentic_core/L0_maintenance/scripts/test_canon_key_removal.py`:
     - Remove all `check_key_*` method calls (lines 126, 132, 137, 142)
     - Remove registry validation logic (lines 40-50)
     - Replace with Guardian equivalent validation tests
     - Fix test class constructor to avoid collection warnings

   - `tests/e2e/ops_scripts/maintenance/test_canon_key_removal.py`:
     - Remove method calls (lines 73, 79, 84)
     - Update to use Guardian reporting framework
     - Remove class constructor issues

2. **Test Logic Modernization**
   - Replace specific key validation with Guardian violation detection
   - Update assertions to match Guardian reporting format
   - Convert test methods to use Guardian remediation guidance

**Verification**:
- Run converted tests with Guardian framework
- Verify equivalent validation coverage
- Check test collection warnings are resolved

### Sub-Phase 2.2: Reference Pattern Cleanup (Days 4-5)
**Objective**: Remove specific key pattern references and forbidden patterns

**Actions**:
1. **Pattern Reference Removal**
   - `tests/unit/agentic_core/L0_maintenance/scripts/test_downstream_deprecation.py`:
     - Remove lines 24-32: specific key patterns (check_key_05, check_key_28, KEY_5, KEY_28)
     - Update global search patterns to focus on Guardian violations
     - Remove forbidden_patterns regex compilation

   - `tests/unit/agentic_core/L0_maintenance/scripts/test_key_deprecation_fast.py`:
     - Remove lines 38-41: key_05 and key_28 content checks
     - Remove lines 78-80: forbidden patterns
     - Remove line 123: documentation key reference checks

2. **Depth Script Reference Update**
   - `tests/unit/agentic_core/L5_safety/validators/test_depth_calculation_fix.py`:
     - Update line 206: Remove "check_key_49_depth.py" reference
     - Update line 213: Remove script path reference
     - Replace with Guardian depth validation equivalent

**Verification**:
- Run updated pattern validation tests
- Verify no legacy key patterns remain
- Check depth validation still functions

### Sub-Phase 2.3: Phase 2 Validation (Days 6-7)
**Objective**: Complete test framework migration validation

**Actions**:
1. **Guardian Framework Integration**
   - Verify all converted tests use Guardian reporting
   - Check remediation guidance is properly linked
   - Validate test coverage equivalence

2. **Collection Warning Resolution**
   - Fix any remaining pytest collection warnings
   - Update test class constructors where needed
   - Verify test discovery works correctly

**Success Criteria**:
- All tests pass with Guardian framework
- No collection warnings
- Equivalent validation coverage maintained

## Phase 3: Method Reference Cleanup (Week 3)

### Sub-Phase 3.1: Base Agent Method Cleanup (Days 1-2)
**Objective**: Remove canon key method references from base agents and mixins

**Actions**:
1. **HealerMixin Method References**
   - Remove all `check_key_*` method references from HealerMixin
   - Update method shadowing reports in sovereign contract tests
   - Clean up base agent test files

2. **SovereignBaseAgent Cleanup**
   - Remove canon key method implementations
   - Update inheritance hierarchies
   - Clean up method shadowing in CachedSafetyShield

3. **Base Agent Test Updates**
   - `tests/unit/agentic_core/base_agents/test_hardened_core_synthesis.py`:
     - Remove line 175: "check_key_00_no_hardcoded_secrets" reference
     - Update validation logic for Guardian framework

**Verification**:
- Run base agent test suite
- Verify no method shadowing errors
- Check inheritance hierarchies remain intact

### Sub-Phase 3.2: Validation Script Cleanup (Days 3-4)
**Objective**: Remove or update remaining validation scripts

**Actions**:
1. **Script File Management**
   - Locate and remove `check_key_49_depth.py` if exists
   - Clean up any remaining validation script references
   - Update script calls to use Guardian equivalents

2. **Contract Guard Report Cleanup**
   - Clean up sovereign contract guard test reports:
     - `sovereign_contract_guard_test_20260130_144909.json`
     - `sovereign_contract_guard_test_20260130_145526.json`
   - Remove method shadowing references (lines 3857-3864, 3986-3993, 4102-4114, 4350-4360)

**Verification**:
- Run validation script tests
- Verify contract guard reports are clean
- Check no script reference errors

### Sub-Phase 3.3: Phase 3 Validation (Days 5-7)
**Objective**: Complete method reference cleanup validation

**Actions**:
1. **Comprehensive Method Testing**
   - Run full agent test suite
   - Verify no canon key method calls remain
   - Check method resolution order (MRO) integrity

2. **Integration Testing**
   - Test Guardian framework integration with cleaned agents
   - Verify validation workflows function correctly
   - Check end-to-end validation coverage

**Success Criteria**:
- No canon key method references remain
- All agent tests pass
- Guardian validation workflows function correctly

## Phase 4: Documentation and Final Cleanup (Week 4)

### Sub-Phase 4.1: Documentation Updates (Days 1-2)
**Objective**: Update all documentation to reflect Guardian framework

**Actions**:
1. **Test Documentation Updates**
   - `tests/unit/agentic_core/L1_cognition/thought_engine/test_BudgetAgent.py`:
     - Remove line 7: "Validates Canon Keys: - K"
     - Update to reference Guardian validation

   - `tests/unit/agentic_core/L0_maintenance/scripts/test_phase1_5_cognitive_migration.py`:
     - Update line 7: Remove canon key reference
     - Document Guardian framework migration

2. **Implementation Summary Updates**
   - Update `tests/guardian/IMPLEMENTATION_SUMMARY.md` with canon key deprecation status
   - Update `tests/guardian/REMEDIATION_GUIDE.md` with new validation paths
   - Update any architectural documentation

**Verification**:
- Review all updated documentation
- Verify accuracy of Guardian framework references
- Check documentation consistency

### Sub-Phase 4.2: Final Reference Cleanup (Days 3-4)
**Objective**: Remove any remaining canon key references

**Actions**:
1. **Comprehensive Search and Destroy**
   - Run global search for remaining patterns:
     - "canon_key", "CANON_KEY", "check_key_"
     - "KEY_[0-9]", numeric key references
     - Any remaining registry references

2. **Test Name Updates**
   - Rename test methods that reference canon keys
   - Update test class names where appropriate
   - Ensure naming consistency with Guardian framework

**Verification**:
- Run comprehensive grep search validation
- Verify zero canon key references remain
- Check test naming consistency

### Sub-Phase 4.3: Phase 4 Validation (Days 5-7)
**Objective**: Final validation and system integrity verification

**Actions**:
1. **System-Wide Testing**
   - Run complete test suite
   - Verify Guardian framework functionality
   - Check system performance and stability

2. **Final Documentation Review**
   - Review all updated documentation
   - Verify implementation completeness
   - Create final decompletion report

**Success Criteria**:
- Zero canon key references remain in codebase
- Guardian framework fully functional
- All documentation updated and accurate
- System stability maintained

## Risk Mitigation Strategies

### High-Risk Operations
1. **Test Framework Migration**
   - **Risk**: Breaking validation coverage
   - **Mitigation**: Parallel testing during transition
   - **Rollback**: Keep legacy tests as backup during migration

2. **Base Agent Method Removal**
   - **Risk**: Breaking inheritance hierarchies
   - **Mitigation**: Step-by-step method removal with testing
   - **Rollback**: Maintain method stubs during transition

### Medium-Risk Operations
1. **Import Statement Cleanup**
   - **Risk**: Import errors and broken dependencies
   - **Mitigation**: Incremental cleanup with testing
   - **Rollback**: Maintain conditional imports during transition

2. **Registry Removal**
   - **Risk**: Breaking structural blueprint integrity
   - **Mitigation**: Verify all references before removal
   - **Rollback**: Keep empty registry as fallback

### Low-Risk Operations
1. **Documentation Updates**
   - **Risk**: Documentation inconsistency
   - **Mitigation**: Review and validation process
   - **Rollback**: Version control revert if needed

## Success Metrics and Validation

### Quantitative Metrics
- **Zero References**: 0 canon key references in codebase
- **Test Coverage**: 100% Guardian framework coverage
- **Test Success Rate**: 100% test pass rate
- **Documentation Accuracy**: 100% updated documentation

### Qualitative Metrics
- **System Stability**: No performance degradation
- **Maintainability**: Cleaner, more maintainable codebase
- **Developer Experience**: Clearer validation framework
- **Architecture Consistency**: Aligned with Guardian framework design

### Validation Checkpoints
- **End of Each Phase**: Comprehensive testing and validation
- **End of Each Sub-Phase**: Specific component testing
- **Daily Progress**: Incremental validation and rollback capability

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Foundation Cleanup | Week 1 | Clean registry, updated imports |
| Phase 2: Test Migration | Week 2 | Guardian framework integration |
| Phase 3: Method Cleanup | Week 3 | Clean agent hierarchies |
| Phase 4: Final Cleanup | Week 4 | Complete deprecation |

**Total Estimated Duration**: 
**Critical Path**: Test framework migration (Phase 2)
**Success Probability**: 95% with phased approach and rollback strategies

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

