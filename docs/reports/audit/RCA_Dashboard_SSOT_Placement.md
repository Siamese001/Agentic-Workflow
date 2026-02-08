# RCA: dashboard_ssot.yaml Misplaced in L6/config/ Instead of L6/dashboards/

**Date:** 2026-02-07
**Severity:** Low (structural misplacement, no runtime impact)
**Scope:** 1 file, 5 path references

---

## Symptom

`dashboard_ssot.yaml` was in `L6_observability/config/` instead of `L6_observability/dashboards/`.

## Root Cause

### RC-1: YAML suffix matched the generic `config/` rule before the specific rule was added

The `NON_PYTHON_FOLDER_ROUTES` table in `structure_blueprint_config.py` has two entries relevant to this file:

```python
NON_PYTHON_FOLDER_ROUTES = {
    "dashboard_ssot.yaml": "dashboards",   # Specific rule (added later)
    ".yaml": "config",                      # Generic rule (original)
}
```

The **specific rule** (`"dashboard_ssot.yaml": "dashboards"`) was added to the config **after** the file was already placed in `config/` by the generic `.yaml → config/` rule. No healing pass ever moved the file to match the corrected routing.

### RC-2: Manual placement predated the routing rule

The file was originally placed manually in `L6_observability/config/` during initial dashboard SSOT implementation (Jan 2026). The `NON_PYTHON_FOLDER_ROUTES` specific override was added later as a correction, but no migration was performed.

---

## Fix Applied

1. **Moved** `L6_observability/config/dashboard_ssot.yaml` → `L6_observability/dashboards/dashboard_ssot.yaml`
2. **Updated** the functional `Path()` construction in `generate_dashboard_ssot_util.py` (line 36)
3. **Updated** 4 docstring/comment references across 2 files:
   - `generate_dashboard_ssot_util.py` (3 occurrences)
   - `dashboard_ssot_definitions_util.py` (1 occurrence)
4. **Removed** empty `L6_observability/config/` directory

### Files Modified
- `agentic_core/L0_maintenance/scripts/generate_dashboard_ssot_util.py` — path + docstrings
- `agentic_core/L0_maintenance/scripts/dashboard_ssot_definitions_util.py` — docstring

### Verification
- Zero remaining references to old path `L6_observability/config/dashboard_ssot.yaml`
- `NON_PYTHON_FOLDER_ROUTES` already had the correct rule — no config change needed
