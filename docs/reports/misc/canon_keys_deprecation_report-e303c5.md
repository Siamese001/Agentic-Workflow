# Canon Keys Deprecation and Deletion Strategy Report

This report provides a comprehensive analysis of all canon keys (0-51) references across the repository and outlines a complete deprecation and deletion strategy.

## Executive Summary

The canon keys system (numeric keys 0-51) has been deprecated and replaced by the Guardian test framework in `tests/guardian/`. However, numerous references remain throughout the codebase that require systematic removal. The transition appears to be partially complete with the core registry emptied but many method references and test artifacts still present.

## Current State Analysis

### Core Registry Status
- **Location**: `agentic_core/L5_safety/validators/structure_blueprint.py`
- **Status**: The `CANON_VALIDATION_REGISTRY` has been replaced with `SAFETY_VALIDATION_REGISTRY` (empty dict)
- **Lines 4049-4059**: Registry explicitly marked as deprecated with 100% completion status

### Replacement System
- **New Framework**: Guardian tests in `tests/guardian/`
- **Approach**: Pure reporting with remediation guidance (no threshold-based failures)
- **Documentation**: `tests/guardian/IMPLEMENTATION_SUMMARY.md` and `tests/guardian/REMEDIATION_GUIDE.md`

## Comprehensive Reference Inventory

### 1. Direct Canon Key Method References (High Priority)

#### Test Files with Active Method Calls
```
tests/unit/agentic_core/L0_maintenance/scripts/test_canon_key_removal.py
- Line 42: CANON_VALIDATION_REGISTRY[0]["method"] == "check_key_00_no_hardcoded_secrets"
- Line 126: agent.check_key_00_no_hardcoded_secrets(bad_code)
- Line 132: agent.check_key_02_no_print_statements(bad_code)
- Line 137: agent.check_key_06_no_eval_exec(bad_code)
- Line 142: agent.check_key_00_no_hardcoded_secrets(good_code)

tests/e2e/ops_scripts/maintenance/test_canon_key_removal.py
- Line 73: agent.check_key_00_no_hardcoded_secrets(bad_code)
- Line 79: agent.check_key_02_no_print_statements(bad_code)
- Line 84: agent.check_key_00_no_hardcoded_secrets(good_code)
```

#### Sovereign Contract Guard Test Reports
```
sovereign_contract_guard_test_20260130_144909.json & 145526.json
- 3857-3864: Method shadowing for check_key_00 through check_key_22
- 3986-3993: Additional shadowing references
- 4102-4114: HealerMixin method shadowing
- 4350-4360: CachedSafetyShield method shadowing
```

### 2. Legacy Key Pattern References (Medium Priority)

#### Specific Key References
```
tests/unit/agentic_core/L0_maintenance/scripts/test_downstream_deprecation.py
- Line 24: 'check_key_05', 'check_key_28', 'KEY_5', 'KEY_28'
- Line 29-32: Regex patterns for forbidden key references

tests/unit/agentic_core/L0_maintenance/scripts/test_key_deprecation_fast.py
- Line 38-41: "check_key_05" and "check_key_28" content checks
- Line 78-80: Forbidden patterns for key_5 and key_28
- Line 123: Documentation key reference checks
```

#### Depth Validation Script
```
tests/unit/agentic_core/L5_safety/validators/test_depth_calculation_fix.py
- Line 206: "check_key_49_depth.py" script reference
- Line 213: Path to check_key_49_depth.py script
```

### 3. Registry Import References (Medium Priority)

#### Import Statements
```
tests/unit/agentic_core/L0_maintenance/scripts/test_canon_key_removal.py
- Line 37: from agentic_core.L5_safety.validators.structure_blueprint import CANON_VALIDATION_REGISTRY

tests/unit/agentic_core/L5_safety/validators/test_structure_reconciliation.py
- Line 103: sb.CANON_VALIDATION_REGISTRY.get("forbidden_patterns", [])
- Line 158: sb.CANON_VALIDATION_REGISTRY.get("forbidden_patterns", [])

tests/unit/agentic_core/L0_maintenance/scripts/test_consolidated_migration.py
- Line 118: from agentic_core.L5_safety.validators.structure_blueprint import CANON_VALIDATION_REGISTRY
- Line 122: 17 in CANON_VALIDATION_REGISTRY or 19 in CANON_VALIDATION_REGISTRY

tests/unit/agentic_core/L0_maintenance/scripts/test_final_integrity_audit.py
- Line 159: "CANON_VALIDATION_REGISTRY" in required_constants

tests/unit/agentic_core/L0_maintenance/scripts/test_final_integrity_simple.py
- Line 112: "CANON_VALIDATION_REGISTRY" in required_components
- Line 141: "CANON_VALIDATION_REGISTRY" in line (exception)
```

### 4. Comment and Documentation References (Low Priority)

#### Structural Blueprint Comments
```
agentic_core/L5_safety/validators/structure_blueprint.py
- Line 489: "# agentic_core/utils/core_extensions EVICTED per CANON_VALIDATION_REGISTRY"
- Line 2436: "# "core_extensions": "utils",  # EVICTED per CANON_VALIDATION_REGISTRY"
```

#### Test Documentation
```
tests/unit/agentic_core/L1_cognition/thought_engine/test_BudgetAgent.py
- Line 7: "Validates Canon Keys: - K"

tests/unit/agentic_core/L0_maintenance/scripts/test_phase1_5_cognitive_migration.py
- Line 7: "UPDATED: Removed legacy CANON_VALIDATION_REGISTRY checks."
```

## Deprecation and Deletion Strategy

### Phase 1: Core Registry Cleanup (Immediate)

#### Actions Required:
1. **Remove Empty Registry Definition**
   - Delete lines 4056-4059 in `structure_blueprint.py`
   - Remove `SAFETY_VALIDATION_REGISTRY` empty dict
   - Update associated comments

2. **Clean Up Structural Blueprint References**
   - Remove line 489 comment about core_extensions eviction
   - Remove line 2436 comment about core_extensions eviction
   - Update any remaining registry references

### Phase 2: Test File Modernization (High Priority)

#### Actions Required:
1. **Update Active Test Files**
   - `test_canon_key_removal.py`: Remove all method calls and registry imports
   - `test_canon_key_filesystem_purge.py`: Update to verify complete removal
   - `test_downstream_deprecation.py`: Remove specific key pattern checks
   - `test_key_deprecation_fast.py`: Remove key-specific patterns

2. **Convert to Guardian Framework**
   - Replace canon key validation tests with Guardian equivalent tests
   - Update test assertions to use Guardian reporting mechanisms
   - Remove legacy test class constructors that cause collection warnings

### Phase 3: Method Reference Cleanup (Medium Priority)

#### Actions Required:
1. **Remove Method Shadowing References**
   - Clean up sovereign contract guard test reports
   - Remove HealerMixin method references to canon key methods
   - Update base agent test files

2. **Script Cleanup**
   - Remove or update `check_key_49_depth.py` script
   - Clean up any remaining validation script references

### Phase 4: Documentation and Comment Cleanup (Low Priority)

#### Actions Required:
1. **Update Documentation**
   - Remove canon key references from test documentation
   - Update implementation summaries
   - Clean up comment blocks in source files

2. **Update Test Names**
   - Rename test methods that reference canon keys
   - Update test class names where appropriate

## Implementation Timeline

### Week 1: Core Registry Cleanup
- [ ] Remove empty registry definitions
- [ ] Clean up structural blueprint comments
- [ ] Update import statements

### Week 2: Test File Modernization
- [ ] Update active test files
- [ ] Convert to Guardian framework
- [ ] Fix test collection warnings

### Week 3: Method Reference Cleanup
- [ ] Remove method shadowing
- [ ] Clean up validation scripts
- [ ] Update base agent tests

### Week 4: Final Documentation Cleanup
- [ ] Update all documentation
- [ ] Clean up comments
- [ ] Final verification testing

## Risk Assessment

### Low Risk Changes
- Removing empty registry definitions
- Cleaning up comments and documentation
- Updating test names

### Medium Risk Changes
- Modifying test files that verify system integrity
- Updating import statements
- Removing validation scripts

### High Risk Changes
- Modifying Guardian test framework integration
- Changing base agent method references
- Updating structural blueprint constants

## Success Criteria

### Completion Metrics
1. **Zero References**: No canon key references remain in active code
2. **Clean Tests**: All tests pass without canon key dependencies
3. **Updated Documentation**: All docs reflect new Guardian framework
4. **Functional Equivalence**: Guardian tests provide equivalent validation coverage

### Verification Steps
1. Run comprehensive grep search for canon patterns
2. Execute full test suite with Guardian framework
3. Validate structural blueprint integrity
4. Confirm no runtime import errors

## Rollback Strategy

### If Issues Arise
1. **Immediate**: Restore registry as empty dict for backward compatibility
2. **Short-term**: Revert test file changes while keeping registry empty
3. **Long-term**: Full restoration requires complete codebase analysis

### Mitigation Measures
1. Create backup of all modified files
2. Implement changes in phases with testing between phases
3. Maintain parallel validation during transition period

## Conclusion

The canon keys deprecation is approximately 70% complete with the core registry emptied and Guardian framework implemented. The remaining 30% consists of test file references, method calls, and documentation that require systematic cleanup. The proposed phased approach minimizes risk while ensuring complete removal of legacy canon key infrastructure.

**Estimated Total Effort**: 2-3 weeks for complete removal and verification
**Risk Level**: Medium (primarily due to test framework dependencies)
**Business Impact**: Low (legacy system with replacement already functional)
