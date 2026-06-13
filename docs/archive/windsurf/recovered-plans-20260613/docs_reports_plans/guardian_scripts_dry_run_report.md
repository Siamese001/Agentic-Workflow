# Guardian Scripts Dry Run Report

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

Performed a comprehensive dry run of all guardian scripts in the `tests/guardian` directory. The guardian system consists of 7 registered guardians that perform structural and architectural validation of the codebase.

## Phase 1: Discovery and Inventory

### Guardian Test Files Found
- **Total test files**: 81 test files in `tests/guardian/`
- **Total tests collected**: 1,819 individual tests
- **Test categories**: Architecture compliance, import safety, SSOT validation, MRO integrity, V15 compliance, and more

### Registered Guardians (from guardian_registry.py)
1. **location_alignment** - Validates file placement and directory structure
2. **hygiene** - Checks for empty folders, temp artifacts, scan budgets
3. **manifest_integrity** - Validates manifest files (currently skipped)
4. **drift_detection** - Detects structural drift from baseline
5. **architecture_governance** - Enforces import compliance and layer gravity
6. **classification_compliance** - Validates naming and territory compliance
7. **hierarchy_compliance** - Validates folder structure and subfolder compliance

## Phase 2: Dry Run Execution Results

### Guardian Aggregator Status
- **Overall Status**: FAIL
- **Guardians Passed**: 1/7
- **Guardians Failed**: 6/7
- **Total Checks**: 13 checks across all guardians

### Individual Guardian Results

#### ✅ PASSED: manifest_integrity
- Status: SKIP (manifest.json absent)
- Reason: No manifest file found, check not applicable

#### ❌ FAILED: architecture_governance
- Status: FAIL (1/2 checks failed)
- Issues: 981 files scanned, import compliance violations found
- Details: Upward import violations detected

#### ❌ FAILED: classification_compliance
- Status: FAIL (2/2 checks failed)
- Issues: 1,402 files scanned
- Details: Naming and territory compliance violations

#### ❌ FAILED: drift_detection
- Status: FAIL (1/1 check failed)
- Issues: Structural drift detected from baseline

#### ❌ FAILED: hierarchy_compliance
- Status: FAIL (2/2 checks failed)
- Issues: Missing structure and subfolder compliance issues
- Details: 11 missing folders across various layers

#### ❌ FAILED: hygiene
- Status: FAIL (2/3 checks failed)
- Issues:
  - Scan budget exceeded (10,001 items > 10,000 limit)
  - 29 empty folders found
  - ✅ No __init__.py-only folders (passed)

#### ❌ FAILED: location_alignment
- Status: FAIL (2/2 checks failed)
- Issues:
  - 4 misplaced files found
  - 2 missing sovereign root directories

## Phase 3: Analysis and Findings

### Critical Issues Identified

1. **Import Violations**: Lower layers importing from higher layers (gravity violations)
2. **File Placement Issues**: Files in non-approved locations
3. **Empty Directories**: 29 empty folders throughout the codebase
4. **Missing Structure**: Required directories not present per SSOT blueprint
5. **Scan Budget**: Repository exceeds current scan limits
6. **Classification Issues**: Naming and territory compliance problems

### Specific Violations

#### Misplaced Files
- `.backup/test_illegal_root_file.py.bak`
- `.backup/test_shallow.py.bak`
- `agentic_core/prompt_governance/registry/backups/registry.v1.backup`
- `tests/conftest.py`

#### Missing Directories
- `.gravity_state`
- `dev_tools`

#### Empty Folders (29 total)
- Multiple empty directories in `agentic_core/L0_maintenance/`
- Empty cache directories in `apps_shared/types/cache/`
- Various empty test directories

### Test Execution Issues

- Individual test files require proper fixture setup
- Many tests use class-based organization with `pytest.mark.guardian`
- V15 enforcement requires `V15_TEST_SIGNING=1` environment variable
- Some tests may have dependency issues preventing execution

## Recommendations

### Immediate Actions
1. **Remove misplaced files**: Move or delete the 4 misplaced files identified
2. **Create missing directories**: Add `.gravity_state` and `dev_tools` directories
3. **Clean empty folders**: Remove or populate the 29 empty directories
4. **Fix import violations**: Resolve upward import dependencies

### Structural Improvements
1. **Increase scan budget**: Consider raising `MAX_FILES_PER_SCAN` if justified
2. **Review classification**: Address naming and territory compliance issues
3. **Update baseline**: Refresh drift detection baseline if changes are intentional
4. **Manifest creation**: Consider adding manifest.json for integrity tracking

### Process Enhancements
1. **CI Integration**: Ensure V15_TEST_SIGNING is set in CI environments
2. **Regular guardian runs**: Schedule periodic guardian validation
3. **Documentation**: Update documentation for expected directory structure
4. **Monitoring**: Track guardian results over time for trend analysis

## Conclusion

The guardian system is functioning correctly and identifying real structural issues in the codebase. While 6 out of 7 guardians currently fail, these failures highlight legitimate architectural concerns that should be addressed. The guardian scripts provide valuable automated validation of the codebase's structural integrity and should be integrated into the regular development workflow.

## Technical Notes

- Environment variable `V15_TEST_SIGNING=1` required for V15 enforcement
- Guardian aggregator outputs both human-readable text and machine-readable JSON
- Individual tests may require specific fixtures and environment setup
- Total execution time for full guardian run: approximately 30-60 seconds

---

## Appendix: Raw Execution Output

**Execution Date**: 2026-02-16
**Command**: `$env:V15_TEST_SIGNING="1"; python -m agentic_core.L0_routing.scripts.run_all_guardians --format json`
**Exit Code**: 0

### Summary
- **Status**: FAIL
- **Guardians**: 6 failed / 1 passed (7 total)
- **Total Checks**: 13
- **V15 Signature**: `44aa42a88bb6c0917073ba65dfe29c9f3f8956c8eb25e1b4d196311999ab6e44`

### Empty Folders Detected (30)
```
agentic_core/L0_maintenance/enforcement
agentic_core/L0_maintenance/engines
agentic_core/L0_maintenance/reasoning
agentic_core/L0_maintenance/scripts
agentic_core/L0_maintenance/types
agentic_core/L0_maintenance/utils
apps_shared/types/cache/chroma_memory
apps_shared/types/cache/rag_cache
apps_shared/types/cache/rag_telemetry
archives/gatekeeper
data/golden
data/injections
data/logs
data/output
data/raw/2025-12-09_initial_ingestion
docs/reports/missions
docs/reports/plans/guardian_dry_run
docs/reports/plans/v15_incident_bundle_example/inputs
tests/agentic_core/L0_maintenance/config
tests/agentic_core/L0_maintenance/core
tests/agentic_core/L0_maintenance/enforcement
tests/agentic_core/L0_maintenance/engines
tests/agentic_core/L0_maintenance/reasoning
tests/agentic_core/L0_maintenance/scripts
tests/agentic_core/L0_maintenance/sensors
tests/agentic_core/L0_maintenance/types
tests/agentic_core/L0_maintenance/utils
tests/agentic_core/L7_meta_learning/enforcement
tests/unit/agentic_core/fixtures
tests/unit/utils
```

### Remediation Hints (from guardian output)
1. Add meaningful content to __init__.py-only folders or remove them
2. Create missing L2/L3 directories per SOVEREIGN_TERRITORIES blueprint
3. Create missing sovereign root directories
4. Fix upward import violations: lower layers must not import from higher layers
5. Move agents to their assigned layer per the SSOT scanner classification
6. Move archived/backup/old files to archives/
7. Move misplaced files to correct LCD folders per classification
8. Remove or populate empty folders
9. Remove or relocate backup/temp files (.bak, .backup, .old, .tmp)

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

