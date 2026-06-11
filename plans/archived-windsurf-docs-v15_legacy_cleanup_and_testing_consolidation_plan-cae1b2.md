---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\v15_legacy_cleanup_and_testing_consolidation_plan-cae1b2.md'
original_relative_path: 'v15_legacy_cleanup_and_testing_consolidation_plan-cae1b2.md'
source_sha256: d1303f842f0ccfb53889d32a412a4e285137e5b36496ca9bf570b6581f3fb14d
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# V15 Legacy Cleanup and Testing Structure Consolidation Plan

This plan addresses the critical issue of V15 legacy references in guardian tests and provides a comprehensive consolidation strategy for the testing structure.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Critical Finding: V15 Legacy References

**Problem**: Guardian tests contain extensive V15 references that appear to be from an old/obsolete version, creating confusion and technical debt.

**Evidence**:
- 40+ V15-specific test files in `tests/guardian/`
- V15 type files still present in `agentic_core/L0_routing/types/`
- V15_ENFORCEMENT environment variable references throughout test suite
- Current codebase shows V16+ references in apps, indicating V15 is indeed legacy

**Impact**: Outdated version references create maintenance burden and potential confusion about current compliance requirements.

## Updated Testing Structure Analysis

### Guardian Test Suite Issues

**Current State**: 113 test files with significant V15 legacy contamination

**Critical Issues**:
1. **V15 Legacy Files**: 40+ files testing V15-specific functionality that may no longer be relevant
2. **Version Confusion**: Mixed V15 and V16+ references create unclear compliance standards
3. **Maintenance Overhead**: Supporting old version tests wastes development resources
4. **Test Relevance**: V15 tests may be testing obsolete requirements

### Updated Consolidation Strategy

## Phase 0: V15 Legacy Cleanup (CRITICAL - Highest Priority)

**Target**: Remove all V15 legacy references and obsolete test files

**Actions Required**:
1. **Identify V15-Only Files**: Determine which V15 test files are completely obsolete
2. **Preserve Relevant Tests**: Extract any still-relevant test logic from V15 files
3. **Remove V15 Type Dependencies**: Eliminate dependencies on V15-specific types
4. **Clean Environment Variables**: Remove V15_ENFORCEMENT references where obsolete
5. **Update Test Names**: Rename non-V15 tests that incorrectly reference V15

**Files for Immediate Review/Removal**:
```
tests/guardian/test_v15_*.py (40+ files)
tests/guardian/test_execute_ssot_v15_contract.py
agentic_core/L0_routing/types/v15_*.py (12+ files)
```

**Expected Reduction**: 40+ files removed immediately

## Phase 1: Core Guardian Test Consolidation

**Target**: Consolidate essential guardian tests (post-V15 cleanup)

**Revised Structure**:
```
tests/guardian/
├── core/
│   ├── test_ssot_compliance.py         # Core SSOT validation
│   ├── test_import_safety.py           # Import validation (consolidated)
│   ├── test_architecture_governance.py  # Architecture compliance
│   └── test_contract_compatibility.py  # Contract validation
├── validation/
│   ├── test_mro_integrity.py          # Method Resolution Order
│   ├── test_subatomic_compliance.py   # Subatomic validation
│   └── test_folder_purity.py          # Folder structure validation
├── integration/
│   ├── test_guardian_integration.py    # Integration tests
│   └── test_healing_integration.py     # Healing system tests
└── performance/
    ├── test_performance_caps.py        # Performance validation
    └── test_scan_budget.py            # Budget compliance
```

**Expected Reduction**: 113 → ~25 files (78% reduction after V15 cleanup)

## Phase 2: Unit Test Optimization

**Target**: Remove redundant unit tests while maintaining coverage

**Focus Areas**:
1. **Remove Obsolete Agent Tests**: Clean up tests for deprecated agents
2. **Consolidate Engine Tests**: Merge similar engine test files
3. **Standardize Test Structure**: Ensure consistent 7-pattern framework
4. **Remove V15 Dependencies**: Clean unit tests that reference V15 types

**Expected Reduction**: 821 → ~750 files (9% reduction)

## Implementation Strategy

### Step 1: V15 Legacy Assessment (Week 1)
1. **Inventory V15 Files**: Catalog all V15-specific test and type files
2. **Relevance Analysis**: Determine which V15 functionality is still current
3. **Dependency Mapping**: Identify current code that depends on V15 types
4. **Migration Planning**: Plan migration of any relevant V15 test logic

### Step 2: V15 Cleanup Execution (Week 1-2)
1. **Remove Obsolete Files**: Delete clearly outdated V15 test files
2. **Preserve Relevant Logic**: Extract still-useful test patterns
3. **Update Dependencies**: Modify code that references obsolete V15 types
4. **Clean Environment**: Remove V15_ENFORCEMENT and related env vars

### Step 3: Guardian Test Restructuring (Week 2-3)
1. **Create New Structure**: Implement revised guardian test organization
2. **Consolidate Overlapping Tests**: Merge tests with similar functionality
3. **Update Test References**: Fix all import and reference changes
4. **Validate Coverage**: Ensure no test coverage is lost

### Step 4: Unit Test Cleanup (Week 3-4)
1. **Remove Redundant Tests**: Eliminate duplicate and obsolete unit tests
2. **Standardize Patterns**: Ensure consistent testing framework usage
3. **Update Dependencies**: Remove V15 references from unit tests
4. **Validate Functionality**: Ensure all unit tests still pass

## Risk Mitigation

### High-Risk Areas
1. **V15 Dependencies**: Current code may still depend on V15 types
2. **Coverage Loss**: Removing V15 tests might eliminate important validation
3. **CI Pipeline**: Test file changes may break existing workflows

### Mitigation Strategies
1. **Dependency Analysis**: Thoroughly map all V15 dependencies before removal
2. **Incremental Removal**: Remove V15 files in phases with validation
3. **Backup and Rollback**: Keep backups of removed files for recovery
4. **Comprehensive Testing**: Validate system functionality after each cleanup phase

## Updated Success Metrics

### Primary Metrics
- **V15 File Removal**: Target 100% removal of obsolete V15 test files
- **Test File Reduction**: 934 → ~775 files (17% overall reduction)
- **Code Reduction**: ~60,000 → ~35,000 lines (42% reduction)
- **Coverage Maintenance**: Maintain 100% coverage of current functionality

### Critical Success Factors
- **Zero V15 References**: Complete elimination of V15 legacy references
- **Current Compliance**: Tests validate current (not legacy) requirements
- **Clear Versioning**: No version confusion in test suite
- **Maintained Functionality**: All current features remain tested

## Immediate Actions Required

1. **Confirm V15 Obsolescence**: Verify with team that V15 is indeed legacy
2. **Identify Critical V15 Tests**: Determine if any V15 tests must be preserved
3. **Plan Dependency Updates**: Identify code changes needed for V15 removal
4. **Schedule Cleanup Window**: Plan the V15 cleanup during low-risk period

## Expected Benefits

### Immediate Benefits (V15 Cleanup)
- **Clarity**: Remove confusion about version requirements
- **Maintenance**: Reduce burden of supporting legacy tests
- **Focus**: Concentrate on current compliance requirements
- **Performance**: Faster test execution with fewer files

### Long-term Benefits (Full Consolidation)
- **Maintainability**: Significantly reduced test maintenance overhead
- **Developer Experience**: Clearer, more focused test structure
- **Resource Efficiency**: Reduced computational and storage requirements
- **Agility**: Faster test suite execution and easier modifications

This revised plan prioritizes the critical V15 legacy cleanup while maintaining the overall goal of test consolidation and improved maintainability.

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

