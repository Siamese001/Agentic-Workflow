# RCA: SSOT Reports Path Violation

**Date:** 2026-02-06
**Severity:** Medium
**Status:** RESOLVED

## Summary

The `run_file_classification_heal_agentic_core.py` script was saving reports to `data/reports/` instead of the SSOT-approved location `docs/reports/`. This violated the repository's Single Source of Truth (SSOT) principle for report storage.

## Root Cause Analysis

### 1. Incorrect Path Hardcoded in Script
- **File:** `ops_scripts/general/run_file_classification_heal_agentic_core.py`
- **Line 107:** `output_path = project_root / "data" / "reports" / "file_classification_healing_agentic_core.json"`
- **Issue:** Hardcoded path used `data/reports/` instead of `docs/reports/`

### 2. SSOT Violation
- **SSOT Rule:** All reports must be saved to `docs/reports/`
- **Violation:** Script created and used `data/reports/` directory
- **Impact:** Reports stored in non-standard location, breaking SSOT compliance

### 3. Discovery Method
- User identified the violation after reviewing report location
- Manual inspection revealed incorrect path in script

## Evidence

### Before Fix
```python
# Line 107 (INCORRECT)
output_path = project_root / "data" / "reports" / "file_classification_healing_agentic_core.json"
```

### After Fix
```python
# Line 107 (CORRECT)
output_path = project_root / "docs" / "reports" / "file_classification_healing_agentic_core.json"
```

## Impact Assessment

### Files Affected
1. `ops_scripts/general/run_file_classification_heal_agentic_core.py` - Fixed
2. `data/reports/file_classification_healing_agentic_core.json` - Moved to correct location
3. `data/reports/` directory - Removed (empty)

### Scope
- **Low Impact:** Only one script affected
- **No Data Loss:** Report successfully moved to correct location
- **No Breaking Changes:** Script continues to function correctly

## Resolution

### Actions Taken

1. **Fixed Script Path**
   - Updated line 107 in `run_file_classification_heal_agentic_core.py`
   - Changed `data/reports/` to `docs/reports/`
   - Added comment clarifying SSOT compliance

2. **Moved Existing Report**
   - Moved `data/reports/file_classification_healing_agentic_core.json` to `docs/reports/`
   - Preserved all report data and metadata

3. **Removed Non-SSOT Directory**
   - Deleted empty `data/reports/` directory
   - Prevents future confusion about report locations

### Verification
- ✅ Script updated to use correct SSOT path
- ✅ Existing report moved to `docs/reports/`
- ✅ Non-SSOT directory removed
- ✅ No other scripts found using `data/reports/`

## Prevention Measures

### Recommendations

1. **SSOT Documentation**
   - Document all SSOT paths in central configuration
   - Create reference guide for common SSOT locations

2. **Code Review Checklist**
   - Add SSOT path verification to code review checklist
   - Flag hardcoded paths during review

3. **Automated Validation**
   - Consider adding pre-commit hook to detect non-SSOT paths
   - Validate report paths against approved SSOT locations

4. **Path Constants**
   - Create centralized constants for SSOT paths
   - Import from single source to prevent hardcoding

## SSOT Path Reference

### Approved Report Locations
- ✅ `docs/reports/` - Primary SSOT for all reports
- ✅ `docs/architecture/` - Architecture documentation
- ✅ `docs/metrics/` - Metrics and performance reports
- ✅ `docs/plans/` - Planning documents
- ✅ `docs/project/` - Project documentation

### Deprecated/Non-SSOT Locations
- ❌ `data/reports/` - REMOVED (use `docs/reports/`)
- ⚠️ `data/freeze_reports/` - Legacy, evaluate for migration
- ⚠️ `agentic_core/L6_observability/reports/` - Layer-specific, evaluate purpose
- ⚠️ `apps_lic/reports/` - App-specific, evaluate purpose

## Related Files

- `ops_scripts/general/run_file_classification_heal_agentic_core.py` - Fixed
- `docs/reports/file_classification_healing_agentic_core.json` - Moved to SSOT location
- This RCA: `docs/reports/RCA_SSOT_REPORTS_PATH_VIOLATION.md`

## Conclusion

The SSOT violation was successfully resolved with minimal impact. The script now correctly saves reports to `docs/reports/`, and the non-SSOT directory has been removed. Future violations can be prevented through documentation, code review, and automated validation.
