# ADG Critical Gaps Remediation Plan

## Executive Summary
Address the 5 most critical gaps identified in the assessment to achieve "materially more reliable, attributable, and auditable" ADG system.

## Phase 1: Critical Reporting Gaps (Priority 1) ✅ COMPLETED

### 1.1 Generate Missing Reports ✅
- **Target**: Create `boundary_report.json` and `mutation_integrity_report.json`
- **Status**: ✅ COMPLETED
- **Result**: All 6 required reports now generated successfully
- **Files**:
  - `tools/generate_full_adg.py` - Added boundary and mutation report generation
  - Updated `_generate_standardized_reports()` to include all 6 reports
- **Success Criteria**: ✅ All 6 required reports exist and are valid JSON

### 1.2 Fix Report-DB Reconciliation ✅
- **Target**: Align report data with SQLite ground truth
- **Status**: ✅ COMPLETED
- **Issues Fixed**:
  - ✅ `schema_version` now uses SQLite value (4.0.0)
  - ✅ Total nodes/edges now match SQLite counts
  - ✅ Critical edge counts now use SQLite as authoritative source
  - ✅ Added reconciliation section to provenance report
- **Files**: `tools/generate_full_adg.py` - Updated report generation to use SQLite as source of truth

### Phase 1 Results
- ✅ All 6 reports generated (4 original + 2 new)
- ✅ Report-DB reconciliation implemented
- ✅ Schema version consistency (4.0.0)
- ✅ Accurate edge counts from SQLite
- ✅ Zip archive includes all 6 reports

## Phase 2: Boundary Normalization (Priority 2)

### 2.1 Implement Real Boundary Tagging
- **Target**: Add boundary edge types to ADG scanner
- **Edge Types to Add**:
  - `internal_to_internal`
  - `internal_to_external`
  - `external_to_internal`
  - `unresolved_boundary`
- **Files**: `agentic_core/adg/extraction/static_scanner.py` - Enhance `_ImportVisitor`
- **Success Criteria**: Boundary report shows non-zero counts for all edge types

### 2.2 Enforce Unresolved Import Reporting
- **Target**: Zero unresolved imports in L0/L2/L5 critical paths
- **Current State**: 471 unresolved imports (120 L0, 155 L2, 287 L5)
- **Strategy**:
  - Fix actual import issues where possible
  - Add explicit boundary annotations for intentional external dependencies
  - Create allowlist for acceptable unresolved imports

## Phase 3: Layer Attribution Reconciliation (Priority 3)

### 3.1 Fix Report-DB Layer Mismatch
- **Target**: Reconcile 99.99% report coverage with 46,094 `L_UNKNOWN` nodes
- **Root Cause**: Report is module-scoped while DB is node-scoped
- **Solution**: Update layer inference to be consistent across both reporting and DB population
- **Files**:
  - `tools/generate_full_adg.py` - Fix `_infer_layer()` consistency
  - `agentic_core/adg/extraction/static_scanner.py` - Ensure consistent layer assignment

### 3.2 Complete L4 Persistence Normalization
- **Target**: Fix remaining unknowns in `agentic_core/L4_persistence/...`
- **Strategy**: Add specific layer overrides for persistence patterns
- **Files**: `tools/adg_layer_overrides.yaml` - Add L4 persistence patterns

## Phase 4: Critical Edge Densification Enhancement (Priority 4)

### 4.1 Improve Edge Reporting Accuracy
- **Target**: Fix critical edge count reporting discrepancies
- **Issues**: Reports show 0 for edges that exist in SQLite
- **Solution**: Use SQLite as authoritative source for edge counts
- **Files**: `tools/generate_full_adg.py` - Update edge density report generation

### 4.2 Targeted Edge Densification
- **Target**: Increase coverage in core modules for critical families
- **Focus Areas**:
  - `determinism_seed` (currently 1 core module)
  - `policy_verification` (currently 2 core modules)
  - `blast_radius_check` (currently 2 core modules)
  - `execution_plan_dispatch` (currently 0 core modules)
- **Strategy**: Add explicit calls/annotations in core modules where missing

## Phase 5: Validation and Testing (Priority 5)

### 5.1 End-to-End Validation
- **Target**: Verify all fixes work together
- **Test Cases**:
  - Generate ADG and verify all 6 reports exist
  - Cross-validate report data with SQLite ground truth
  - Verify boundary tags are correctly applied
  - Confirm layer attribution consistency

### 5.2 Audit Trail Verification
- **Target**: Ensure complete audit trail from provenance to edge coverage
- **Validation Points**:
  - Provenance chain完整性
  - Boundary enforcement correctness
  - Layer attribution accuracy
  - Critical edge coverage completeness

## Implementation Timeline

| Phase | Duration | Dependencies | Success Metrics |
|-------|----------|--------------|----------------|
| 1 - Critical Reports | 2 hours | None | All 6 reports exist and reconcile |
| 2 - Boundary Normalization | 4 hours | Phase 1 | Zero unresolved core imports |
| 3 - Layer Attribution | 3 hours | Phase 1 | Report-DB layer consistency |
| 4 - Edge Enhancement | 3 hours | Phase 1 | Accurate edge reporting |
| 5 - Validation | 2 hours | All phases | End-to-end validation passes |

**Total Estimated Time**: 14 hours

## Risk Mitigation

1. **Data Loss Risk**: Backup current ADG artifacts before changes
2. **Performance Risk**: Monitor ADG generation time with new reports
3. **Compatibility Risk**: Ensure changes don't break existing consumers
4. **Accuracy Risk**: Cross-validate all new reports against SQLite

## Success Criteria

1. ✅ All 6 required reports exist and are valid
2. ✅ Report data reconciles with SQLite ground truth
3. ✅ Zero unresolved imports in L0/L2/L5 core paths
4. ✅ Layer attribution consistent between reports and DB
5. ✅ Critical edge counts accurately reported
6. ✅ End-to-end audit trail complete and verifiable

## Next Steps

1. Execute Phase 1 immediately (critical reporting gaps)
2. Review and adjust plan based on Phase 1 results
3. Proceed with remaining phases sequentially
4. Conduct final validation and sign-off
