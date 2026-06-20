# Scanner Exclusion Gaps — Manual Fix Record (Wave 1.1)

**Date:** 2026-04-05  
**SVP Wave:** W1.1 (Immediate Gap Closure)  
**Status:** COMPLETED — Last manual constants patch before YAML infrastructure (W2.x)

---

## Gaps Identified

| Gap | .gitignore Status | Scanner Status | Risk |
|-----|-------------------|----------------|------|
| `coverage_html/` | ✅ Excluded | ❌ Missing | Scanner processes pytest-cov output |
| `.test_artifacts/` | ✅ Excluded | ❌ Missing | Hidden test artifacts scanned unnecessarily |

---

## Fix Applied

**File:** `agentic_core/L5_safety/config/structure_blueprint/ssot.py`  
**Lines:** Added entries to `SOVEREIGN_EXCLUDED_FOLDERS` frozenset (lines 995, 999)

```python
SOVEREIGN_EXCLUDED_FOLDERS: frozenset[str] = frozenset(
    {
        # ... existing entries ...
        ".test_artifacts",  # Test artifacts with leading dot (W1.1 gap closure)
        # ... existing entries ...
        "coverage_html",  # pytest-cov output directory (W1.1 gap closure)
        # ...
    },
)
```

---

## Verification

```bash
# Confirm entries present
python -c "from ssot import SOVEREIGN_EXCLUDED_FOLDERS; 
           assert 'coverage_html' in SOVEREIGN_EXCLUDED_FOLDERS; 
           assert '.test_artifacts' in SOVEREIGN_EXCLUDED_FOLDERS; 
           print('W1.1 gaps closed')"

# Regression test
python -m pytest tests/unit/agentic_core/adg/extraction/test_static_scanner.py -v
# Result: 3 passed
```

---

## Why This is the Last Manual Fix

Per SVP Engineering Principle (archival over deletion), this document records the final manual constants patch.  
**Wave 2 (W2.1-W2.3)** will replace hardcoded lists with YAML-driven infrastructure:
- `config/excluded_paths.yaml` — canonical SSOT
- `exclusion_loader.py` — YAML → frozenset converter
- `ops_scripts/ci/exclusion_sync_gate.py` — CI enforcement
- `tools/generate_gitignore.py` — .gitignore generation from YAML

---

## Artifacts

- Modified: `agentic_core/L5_safety/config/structure_blueprint/ssot.py`
- Test evidence: `tests/unit/agentic_core/adg/extraction/test_static_scanner.py` (3/3 pass)
- Plan: `.codex/plans/scanner-exclusion-sync-two-wave-6d6151.md`

---

## Rollback

```bash
git revert <commit_hash>  # Single commit revert if issues found
# Re-apply after fixing root cause before next ADG generation
```
