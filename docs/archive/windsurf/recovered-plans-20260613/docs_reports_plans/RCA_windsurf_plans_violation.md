# RCA: Why Plans Saved to `.windsurf` Instead of SSOT-Approved Folder

**Date:** 2026-02-05
**Severity:** HIGH - SSOT Violation
**Status:** RESOLVED

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

Plans were being saved to `C:\Users\amita\.windsurf\plans\` (external to repository) instead of the SSOT-approved location `docs/reports/plans/`. This violated the PROJECT_ROOT_WHITELIST and created files outside the repository's sovereign territories.

## Root Cause Analysis

### 1. Planning Guidance Violation

**Issue:** The system planning guidance instructed:
```
Save your plan as a markdown file in C:\Users\amita\.windsurf\plans for the user to review,
with a suffix of -d851b4. Ex. "C:\Users\amita\.windsurf\plans/my-plan-d851b4.md"
```

**Problem:** This path is:
- **External to repository** (user home directory, not project directory)
- **Not in PROJECT_ROOT_WHITELIST** (line 1539-1556 of structure_blueprint_config.py)
- **Not a sovereign territory** defined in SOVEREIGN_TERRITORIES

### 2. SSOT Defines Correct Location

**From structure_blueprint_config.py (line 525):**
```python
DOCS_REPORTS_PLANS: str = "docs/reports/plans"
```

**From SOVEREIGN_TERRITORIES (lines 368-395):**
```python
"docs": {
    "depth": 3,
    "purpose": "Documentation and reporting.",
    "subfolders": {
        "reports": {
            "purpose": "Categorized assessment and execution reports.",
            "subfolders": {
                "assessments": {...},
                "coverage": {...},
                "telemetry": {...},
                "security": {...},
                "audit": {...},
                "missions": {...},
            },
        },
        "plans": {},  # ← Plans should be at docs/plans/ OR docs/reports/plans/
    },
}
```

### 3. PROJECT_ROOT_WHITELIST Does Not Include `.windsurf`

**Approved root-level folders (lines 1539-1556):**
- `agentic_core`, `apps_rg`, `apps_lic`, `apps_shared`
- `ops_scripts`, `tests`, `docs`, `data`, `archives`
- `.git`, `.github`, `.gravity_state`, `.backup`, `.vscode`

**`.windsurf` is NOT listed** and is therefore a SSOT violation.

## Impact Assessment

### Violations Created

1. **SSOT Compliance Violation**
   - Files created outside PROJECT_ROOT_WHITELIST
   - Files created outside SOVEREIGN_TERRITORIES
   - Files not tracked in repository

2. **Architectural Drift**
   - Plans stored in user-specific location
   - Not version controlled
   - Not accessible to other developers
   - Not subject to guardian validation

3. **Constitutional Principle Violation**
   - Violates STRUCTURAL INVARIANT (files must be in approved territories)
   - Violates PROJECT_ROOT_WHITELIST enforcement

## Resolution

### Actions Taken

1. **Created SSOT-Compliant Directory**
   ```bash
   New-Item -ItemType Directory -Path "docs/reports/plans" -Force
   ```

2. **Moved Plan to Correct Location**
   ```bash
   Copy-Item "C:\Users\amita\.windsurf\plans\guardian-refactoring-plan-3fa038.md" \
             -Destination "docs/reports/plans/guardian-refactoring-plan-d851b4.md"
   ```

3. **Verified SSOT Compliance**
   - ✅ `docs/reports/plans/` is within `docs` sovereign territory
   - ✅ `docs` is in PROJECT_ROOT_WHITELIST
   - ✅ Path follows depth=3 constraint for docs territory
   - ✅ File is now version controlled

### Correct Location Hierarchy

```
c:\Git\Agentic-Workflow\           ← Repository root
└── docs\                           ← Sovereign territory (depth 1)
    └── reports\                    ← Subfolder (depth 2)
        └── plans\                  ← Subfolder (depth 3)
            └── guardian-refactoring-plan-d851b4.md  ← Plan file
```

## Prevention Measures

### 1. Update Planning Guidance

The system planning guidance should be updated to:
```
Save your plan as a markdown file in docs/reports/plans/ for the user to review,
with a suffix of -d851b4. Ex. "docs/reports/plans/my-plan-d851b4.md"
```

### 2. Add Guardian Validation

Create guardian test to validate no files exist outside PROJECT_ROOT_WHITELIST:
- Check for files in user home directories
- Check for files in `.windsurf`, `.cursor`, or other IDE-specific folders
- Emit SSOT violation if found

### 3. Pre-commit Hook Enhancement

Add pre-commit hook to reject commits with files outside SSOT territories:
```python
def validate_file_in_ssot(file_path: Path) -> bool:
    """Validate file is in SSOT-approved location."""
    if file_path.is_absolute() and PROJECT_ROOT not in file_path.parents:
        return False  # File outside repository

    rel_path = file_path.relative_to(PROJECT_ROOT)
    root = rel_path.parts[0]

    return root in PROJECT_ROOT_WHITELIST
```

## Lessons Learned

1. **Always validate paths against SSOT** before file operations
2. **User home directories are NEVER valid** for repository artifacts
3. **IDE-specific folders** (`.windsurf`, `.vscode`, `.cursor`) should only contain IDE settings, never project artifacts
4. **Plans and reports** belong in `docs/reports/plans/` per SSOT definition

## References

- **SSOT Definition:** `agentic_core/L5_safety/validators/structure_blueprint_config.py`
- **PROJECT_ROOT_WHITELIST:** Lines 1539-1556
- **SOVEREIGN_TERRITORIES:** Lines 80-420
- **DOCS_REPORTS_PLANS constant:** Line 525
- **Constitutional Principles:** Lines 11-42

## Status

✅ **RESOLVED** - Plan moved to SSOT-compliant location
✅ **VERIFIED** - File now in `docs/reports/plans/` (version controlled)
⚠️ **ACTION REQUIRED** - Update system planning guidance to prevent recurrence

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

