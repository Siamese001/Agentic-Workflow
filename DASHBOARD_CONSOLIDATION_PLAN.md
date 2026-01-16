# Dashboard File Consolidation Plan

**Objective:** Consolidate all dashboard-related files under `agentic_core/L6_observability/dashboards` to enforce SSOT architecture.

---

## **AUDIT RESULTS**

### **Files Currently in scripts/ (63 dashboard-related files)**

#### **Category 1: SSOT Core Files (MUST MOVE)**
These are the canonical SSOT implementation files:

1. **`dashboard_ssot_definitions.py`** (21KB) - ⚠️ **CRITICAL**
   - Contains all canonical calculation functions
   - Imported by 4+ files
   - **Target:** `agentic_core/L6_observability/dashboards/core/ssot_definitions.py`

2. **`generate_dashboard_ssot.py`** (15KB) - ⚠️ **CRITICAL**
   - Generates Python and JS constants from YAML
   - **Target:** `agentic_core/L6_observability/dashboards/scripts/generate_ssot.py`

3. **`config/dashboard_ssot.yaml`** - ⚠️ **CRITICAL**
   - Single source of truth configuration
   - **Target:** `agentic_core/L6_observability/dashboards/config/ssot.yaml`

4. **`regenerate_dashboard_data.py`** (6.7KB) - ⚠️ **CRITICAL**
   - Main data generation script
   - **Target:** `agentic_core/L6_observability/dashboards/scripts/regenerate_data.py`

#### **Category 2: Active Test Files (SHOULD MOVE)**

5. **`test_ssot_enforcement.py`** (17KB)
   - **Target:** `agentic_core/L6_observability/dashboards/tests/test_ssot_enforcement.py`

6. **`test_dashboard_end_to_end.py`** (127KB)
   - **Target:** `agentic_core/L6_observability/dashboards/tests/test_end_to_end.py`

7. **`test_dashboard_data_integrity.py`** (21KB)
   - **Target:** `agentic_core/L6_observability/dashboards/tests/test_data_integrity.py`

8. **`test_dashboard_generation.py`** (7.8KB)
   - **Target:** `agentic_core/L6_observability/dashboards/tests/test_generation.py`

9. **`test_dashboard_playwright_visual.py`** (16KB)
   - **Target:** `agentic_core/L6_observability/dashboards/tests/test_playwright_visual.py`

#### **Category 3: Utility Scripts (SHOULD MOVE)**

10. **`dashboard_live_server.py`** (3.6KB)
    - **Target:** `agentic_core/L6_observability/dashboards/scripts/live_server.py`

11. **`start_dashboard_server.py`** (1.8KB)
    - **Target:** `agentic_core/L6_observability/dashboards/scripts/start_server.py`

#### **Category 4: Legacy/Duplicate Files (DEPRECATE)**

**Duplicate Data Generation Scripts:**
- `regenerate_dashboard_complete.py` (0 bytes) - EMPTY
- `regenerate_dashboard_properly.py` (0 bytes) - EMPTY
- `regenerate_dashboard_full.py` (19KB) - OLD VERSION
- `regenerate_dashboard_from_discovery.py` (3.9KB) - OLD VERSION
- `generate_modular_dashboard_data.py` (19KB) - OLD VERSION

**Audit/Debug Scripts (Archive):**
- `audit_dashboard_heal_cap.py` (0 bytes)
- `audit_dashboard_naming.py` (10KB)
- `audit_dashboard_ssot.py` (2.8KB)
- `audit_dashboard_ssot_flow.py` (11KB)
- `analyze_dashboard_color_bug.py` (7.6KB)
- `check_dashboard_l4.py` (1.4KB)
- `check_dashboard_rendering.py` (3KB)
- `check_dashboard_targets.py` (1.9KB)
- `clean_dashboard_html.py` (1.2KB)
- `compare_dashboard_data.py` (5.8KB)
- `debug_dashboard_playwright.py` (7.3KB)
- `debug_dashboard_rendering.py` (5.4KB)
- `diagnose_dashboard_live.py` (2.9KB)
- `diagnose_user_dashboard_view.py` (3.8KB)
- `extract_dashboard_errors.py` (3.8KB)
- `fix_dashboard_hardcoding.py` (4KB)
- `inspect_dashboard_browser.py` (6.2KB)
- `rca_dashboard_row_collapse.py` (7.6KB)
- `trace_dashboard_generation.py` (3.5KB)

**Validation Scripts (Archive):**
- `validate_dashboard_changes.py` (2.5KB)
- `validate_dashboard_data_sourcing.py` (9.7KB)
- `validate_dashboard_ssot.py` (4.4KB)
- `validate_dashboard_totals.py` (5KB)
- `verify_dashboard_browser_state.py` (6KB)
- `verify_dashboard_columns.py` (1.6KB)
- `verify_dashboard_deployment.py` (8.6KB)
- `verify_dashboard_simple.py` (4.7KB)
- `verify_dashboard_state.py` (5KB)
- `verify_dashboard_updates.py` (1.7KB)

**Test HTML Files (Archive):**
- `simple_dashboard_test.html` (5KB)
- `test_dashboard_browser.html` (2KB)
- `test_dashboard_browser_console.html` (7KB)

**Old Test Files (Archive):**
- `comprehensive_dashboard_tests.py` (35KB)
- `test_dashboard_drilldown.py` (7.3KB)
- `test_dashboard_snapshot_regression.py` (8.8KB)
- `test_dashboard_visual.py` (7KB)

**Pipeline Scripts (Archive):**
- `dashboard_e2e_pipeline.py` (14KB)
- `dashboard_e2e_pipeline_fast.py` (17KB)
- `dashboard_qa.py` (17KB)
- `dashboard_qa_deep_audit.py` (13KB)

**Misc (Archive):**
- `enforce_dashboard_freshness.py` (5.6KB)
- `sync_dashboard_agent_count.py` (1.5KB)
- `update_dashboard_data.py` (0 bytes)
- `update_dashboard_test_coverage.py` (1.5KB)

---

## **PROPOSED NEW STRUCTURE**

```
agentic_core/L6_observability/dashboards/
├── config/
│   └── ssot.yaml                          # MOVED from scripts/config/dashboard_ssot.yaml
├── core/
│   └── ssot_definitions.py                # MOVED from scripts/dashboard_ssot_definitions.py
├── scripts/
│   ├── generate_ssot.py                   # MOVED from scripts/generate_dashboard_ssot.py
│   ├── regenerate_data.py                 # MOVED from scripts/regenerate_dashboard_data.py
│   ├── live_server.py                     # MOVED from scripts/dashboard_live_server.py
│   └── start_server.py                    # MOVED from scripts/start_dashboard_server.py
├── tests/
│   ├── test_ssot_enforcement.py           # MOVED from scripts/
│   ├── test_end_to_end.py                 # MOVED from scripts/test_dashboard_end_to_end.py
│   ├── test_data_integrity.py             # MOVED from scripts/
│   ├── test_generation.py                 # MOVED from scripts/
│   └── test_playwright_visual.py          # MOVED from scripts/
├── data/
│   └── dashboard_data.js                  # EXISTING
├── js/
│   └── constants/
│       └── dashboard-constants.js         # EXISTING
└── autonomy_dashboard.html                # EXISTING
```

---

## **IMPORT UPDATES REQUIRED**

### **Files Importing dashboard_ssot_definitions:**
1. `scripts/check_mcp_hardening.py`
2. `scripts/regenerate_dashboard_data.py` (will be moved)
3. `scripts/regenerate_dashboard_full.py`
4. `scripts/test_dashboard_end_to_end.py` (will be moved)
5. `scripts/test_dashboard_generation.py` (will be moved)

**New Import Pattern:**
```python
# OLD:
from scripts.dashboard_ssot_definitions import calc_health_score

# NEW:
from agentic_core.L6_observability.dashboards.core.ssot_definitions import calc_health_score
```

---

## **MIGRATION STEPS**

### **Phase 1: Create New Structure**
1. Create directories under `agentic_core/L6_observability/dashboards/`:
   - `config/`
   - `core/`
   - `scripts/`
   - `tests/`

### **Phase 2: Move SSOT Core Files (CRITICAL)**
1. Move `dashboard_ssot.yaml` → `config/ssot.yaml`
2. Move `dashboard_ssot_definitions.py` → `core/ssot_definitions.py`
3. Move `generate_dashboard_ssot.py` → `scripts/generate_ssot.py`
4. Move `regenerate_dashboard_data.py` → `scripts/regenerate_data.py`

### **Phase 3: Update All Imports**
1. Update `generate_ssot.py` to reference new YAML path
2. Update all files importing `dashboard_ssot_definitions`
3. Update test files to import from new location

### **Phase 4: Move Test Files**
1. Move test files to `tests/` directory
2. Update pytest configuration
3. Update test imports

### **Phase 5: Move Utility Scripts**
1. Move server scripts to `scripts/` directory
2. Update any references

### **Phase 6: Archive Legacy Files**
1. Create `scripts/archive/dashboard_legacy/`
2. Move all deprecated files there
3. Add README explaining deprecation

### **Phase 7: Comprehensive Testing**
1. Run SSOT enforcement tests
2. Run E2E tests
3. Regenerate dashboard data
4. Verify dashboard loads correctly
5. Test all imports work

---

## **RISK ASSESSMENT**

### **High Risk (Breaking Changes)**
- Moving `dashboard_ssot_definitions.py` - imported by 5+ files
- Moving `generate_dashboard_ssot.py` - referenced in documentation
- Changing YAML path - hardcoded in generator

### **Medium Risk**
- Moving test files - pytest discovery may break
- Moving data generation script - CI/CD references

### **Low Risk**
- Moving utility scripts - rarely used
- Archiving legacy files - already unused

---

## **ROLLBACK PLAN**

If issues occur:
1. Keep original files in place initially (copy, don't move)
2. Test new structure thoroughly
3. Only delete originals after 100% verification
4. Git commit after each phase for easy rollback

---

## **SUCCESS CRITERIA**

✅ All SSOT files under `L6_observability/dashboards/`
✅ All imports updated and working
✅ All tests passing
✅ Dashboard generates and loads correctly
✅ Zero files in `scripts/` with "dashboard" in name (except archives)
✅ Documentation updated with new paths
