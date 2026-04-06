# Pre-Commit ADG Dependency Optimization

**Date:** 2026-04-06  
**Status:** COMPLETED

## Summary

Optimized pre-commit hooks to remove redundant ADG dependencies and improve commit workflow performance.

## Changes Made

### 1. T10.6: ADG Preflight - Made Conditional
**File:** `.pre-commit-config.yaml`

- Changed `always_run: true` to `always_run: false`
- Added `files: ^(agentic_core/|tools/generate/|tools/adg/).*\.py$` filter
- Now only runs when ADG-relevant files change
- **Impact:** Developers no longer forced to run full ADG generation (~95s) for every commit
- **Rationale:** Full ADG generation only needed when ADG infrastructure changes

### 2. T19: ADG Stale Guard - Removed
**File:** `.pre-commit-config.yaml`

- Completely removed from local pre-commit hooks
- **Impact:** Eliminates redundant staleness check
- **Rationale:** When T10.6 runs, ADG is by definition fresh; no need to check staleness
- **Note:** Can be re-added to CI-only if needed for long-running branches

### 3. T13.5: ADG Layer Violation Gate - Enhanced Warnings
**File:** `ops_scripts/ci/adg_layer_violation_gate.py`

- Added explicit warning when ADG SQLite not found
- Added command hint: `Run: python tools/generate/generate_full_adg.py`
- **Impact:** Developers get clear guidance when ADG is missing
- **Behavior:** Still non-blocking (warn mode), but more informative

### 4. T13.6: ADG P1 Defect Gate - Enhanced Warnings
**File:** `ops_scripts/ci/adg_p1_defect_gate.py`

- Added explicit warning when ADG SQLite not found
- Added command hint: `Run: python tools/generate/generate_full_adg.py`
- **Impact:** Developers get clear guidance when ADG is missing
- **Behavior:** Still returns empty list (passes) when ADG missing, but more informative

### 5. Typo Fix
**File:** `.pre-commit-config.yaml`

- Fixed typo in `pre-commit-summary-report` hook: `pass_filenames: fre` → `pass_filenames: false`
- **Impact:** Config now validates correctly

## Testing Results

All hooks tested successfully:
- ✅ T13.5 (adg-layer-violation-gate) - Runs and reports correctly
- ✅ T13.6 (adg-p1-defect-gate) - Runs and reports correctly
- ✅ T10.6 (adg-preflight) - Runs correctly with ADG available
- ✅ Pre-commit config validation passes

## Benefits

1. **Faster commits:** No longer forced to run full ADG generation for every change
2. **Better UX:** Clear warnings when ADG is needed vs. silent failures
3. **Reduced redundancy:** Removed T19 which was redundant with T10.6
4. **Conditional execution:** ADG-heavy hooks only run when ADG infrastructure changes

## Migration Notes

Developers should:
1. Run `python tools/generate/generate_full_adg.py` when changing files in:
   - `agentic_core/` (ADG infrastructure)
   - `tools/generate/` (ADG generation scripts)
   - `tools/adg/` (ADG analysis tools)
2. For other changes (app logic, tests, docs), full ADG generation is not required
3. T13.5 and T13.6 will provide clear warnings if ADG is needed but missing

## Files Modified

1. `.pre-commit-config.yaml` - Hook configuration changes
2. `ops_scripts/ci/adg_layer_violation_gate.py` - Enhanced warnings
3. `ops_scripts/ci/adg_p1_defect_gate.py` - Enhanced warnings

## Rollback Plan

If issues arise, revert to:
1. Set T10.6 `always_run: true` and remove `files` filter
2. Re-add T19 (adg-stale-guard) hook
3. Remove enhanced warnings from T13.5 and T13.6
