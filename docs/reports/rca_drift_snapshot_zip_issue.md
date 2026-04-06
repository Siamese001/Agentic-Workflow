# RCA: Drift Detection Snapshot (.json.gz) Incorrectly Compressed and Added to Zip

**Date:** 2026-04-06  
**Status:** RESOLVED  
**Severity:** MEDIUM (inefficiency, archiving issues)

## Problem

The drift detection snapshot file `adg_graphsnap_*.json.gz` was being:
1. **Compressed** when it should be uncompressed (.json)
2. **Added to the zip archive**, causing double compression (already .gz, then .zip)
3. **Causing archiving issues** with historical file zip not being archived
4. **Load function was falling back** to Tier 1 snapshot files (`adg_snapshot_*.json`) which have incompatible format

## Root Cause

**Issue 1: Compression mismatch**
In `tools/generate/generate_full_adg.py` line 469, `save_snapshot` was called with default `compress=True`, which automatically adds `.gz` to the filename even when the path was set to `.json`.

```python
snap_path = adg_artifacts_dir / f"adg_graphsnap_{ts}.json"
save_snapshot(snapshot, snap_path)  # compress=True by default → saves as .json.gz
```

**Issue 2: Incorrect zip inclusion**
Line 595 in generate_full_adg.py added the drift detection snapshot to the artifact_files list for the zip archive.

**Issue 3: Load function fallback**
In `agentic_core/adg/analysis/CanonicalSnapshot.py`, `load_latest_snapshot` had a legacy fallback to `adg_snapshot_*.json` (Tier 1 snapshots) which have a different schema than drift detection snapshots, causing KeyError when loading.

## Solution

**File:** `tools/generate/generate_full_adg.py`

**Change 1:** Pass `compress=False` to save_snapshot (line 469)
```python
snap_path = adg_artifacts_dir / f"adg_graphsnap_{ts}.json"
save_snapshot(snapshot, snap_path, compress=False)
```

**Change 2:** Removed drift detection snapshot from artifact_files list (lines 593-598)
```python
# NOTE: adg_graphsnap_*.json is an internal drift detection state file, not archived
# Zip contains: 2 ADG artifacts (snapshot.json, sqlite) + reports
artifact_files = [
    paths.snapshot,
    paths.sqlite,
]
```

**Change 3:** Updated header comment (line 12)
```python
adg_graphsnap_<ts>.json       E7 drift detection — previous-run snapshot for diff (uncompressed)
```

**File:** `agentic_core/adg/analysis/CanonicalSnapshot.py`

**Change 4:** Removed legacy fallback from load_latest_snapshot (lines 141-155)
```python
def load_latest_snapshot(artifacts_dir: Path) -> CanonicalSnapshot | None:
    """Load the most recent canonical snapshot from artifacts_dir, or None.

    Looks for files matching 'adg_graphsnap_*.json.gz' (compressed)
    or 'adg_graphsnap_*.json' (uncompressed), sorted by name
    (timestamp suffix).
    """
    # Try compressed files first (preferred)
    candidates = sorted(artifacts_dir.glob("adg_graphsnap_*.json.gz"))
    if not candidates:
        # Fall back to uncompressed
        candidates = sorted(artifacts_dir.glob("adg_graphsnap_*.json"))
    if not candidates:
        return None
    return load_snapshot(candidates[-1])
```

## Verification

**Test 1:** File saved as uncompressed .json
```bash
dir artifacts\adg\adg_graphsnap*.*
```
**Result:** ✅ PASSED - File saved as `adg_graphsnap_04062026_0651.json` (63 MB, uncompressed)

**Test 2:** Zip does not include graphsnap file
```bash
python -c "import zipfile; z = zipfile.ZipFile('artifacts/adg/adg_run_04062026_0651.zip'); print('\n'.join(z.namelist))"
```
**Result:** ✅ PASSED - Zip contains only 2 ADG artifacts + 8 reports, no graphsnap

**Test 3:** ADG generation completes successfully
**Result:** ✅ PASSED - Full ADG generation completed without errors

**Zip Contents:**
```
adg/adg_snapshot_04062026_0651.json
adg/adg_indexed_04062026_0651.sqlite
adg/layer_coverage_report_04062026_0651.json
adg/edge_density_report_04062026_0651.json
adg/provenance_report_04062026_0651.json
adg/replay_determinism_report_04062026_0651.json
adg/boundary_report_04062026_0651.json
adg/mutation_integrity_report_04062026_0651.json
adg/test_surface_coverage_04062026_0651.json
adg/closure_validation_report_04062026_0651.json
```

## Impact

**Before Fix:**
- Drift detection saved as .json.gz (compressed)
- Added to zip archive (double compression)
- Load function fell back to incompatible Tier 1 snapshots
- Archiving issues with historical files

**After Fix:**
- Drift detection saved as .json (uncompressed, 63 MB)
- Not included in zip archive
- Load function only looks for drift detection snapshots
- Proper archiving of historical files

## Files Modified

1. `tools/generate/generate_full_adg.py` - Pass compress=False, removed from zip, updated comments
2. `agentic_core/adg/analysis/CanonicalSnapshot.py` - Removed legacy fallback
3. `docs/reports/rca_drift_snapshot_zip_issue.md` - RCA document

## Corrective Actions Taken

1. ✅ Pass compress=False to save_snapshot
2. ✅ Removed drift detection snapshot from artifact_files list
3. ✅ Updated comments to clarify snapshot is uncompressed
4. ✅ Removed legacy fallback from load_latest_snapshot
5. ✅ Verified file saved as uncompressed .json
6. ✅ Verified zip does not include graphsnap file
7. ✅ Verified ADG generation completes successfully

## Status

**RESOLVED** - Drift detection snapshot is now saved as uncompressed .json, not included in zip archive, and load function correctly handles only drift detection snapshots.
