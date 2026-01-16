# Dashboard Testing Protocol Improvements

**Date:** January 16, 2026  
**Status:** Production Ready  
**Impact:** Critical - Prevents rendering bugs, ensures data integrity

---

## Overview

This document describes comprehensive improvements made to the dashboard testing suite to prevent bugs like the Health/Code Quality Score rendering issue and ensure robust validation across all test phases.

---

## CRITICAL: Automated Server Restart (NEW)

### **Feature:** Automated Dashboard Server Management

**Status:** ✅ IMPLEMENTED (January 16, 2026)

**Problem Solved:**
- Manual server restart was error-prone and often forgotten
- Stale server instances caused test failures
- Port conflicts from multiple server instances

**Solution:**
The E2E test suite now **automatically stops and restarts** the dashboard server before running tests.

### Implementation Details

**Function:** `restart_dashboard_server()`

**Process:**
1. Scans for existing Python HTTP servers on port 8765
2. Kills all existing server processes
3. Waits 2 seconds for port release
4. Starts new server in background (detached process)
5. Verifies server started successfully

**Usage:**
```bash
# Default: Automated server restart enabled
python scripts/test_dashboard_end_to_end.py

# Skip server restart (manual mode)
python scripts/test_dashboard_end_to_end.py --no-server-restart
```

**Output:**
```
======================================================================
🔄 AUTOMATED DASHBOARD SERVER RESTART
======================================================================
   🛑 Stopping existing server (PID 12345)...
   ✅ Stopped 1 existing server(s)
   
   🚀 Starting new server...
      Directory: C:\Git\Agentic-Workflow\agentic_core\L6_observability\dashboards
      Port: 8765
   ✅ Server started successfully (PID 67890)
   🌐 Dashboard URL: http://localhost:8765/autonomy_dashboard.html
```

**Dependencies:**
- `psutil` library (for process management)
- Python `subprocess` module

**Benefits:**
- ✅ Eliminates manual server restart step
- ✅ Prevents port conflicts
- ✅ Ensures fresh server state for tests
- ✅ Reduces test setup time
- ✅ Improves test reliability

**Remaining Manual Step:**
- ⚠️ Browser cache clearing still required (cannot be automated)
- User must confirm cache clearing before tests run

---

## New Test: Column Rendering Validation

### **File:** `scripts/test_table_column_rendering.py`

**Purpose:** Validates JavaScript rendering code displays correct data fields in each column

**Critical:** This test would have caught the Health/Code Quality bug immediately

### Tests Performed

1. **Table 1 Health Column Field**
   - Verifies Health column uses `row['Health']`
   - Ensures it doesn't use `row['Code Quality Score']`

2. **Table 2 Code Quality Column Field**
   - Verifies Code Quality column uses `row['Code Quality Score']`

3. **Health Color Variable Field**
   - Verifies `healthColor` uses `row['Health']` for color coding

4. **Column-to-Field Mapping**
   - Validates all expected fields are present in Table 1 rendering code

### Integration

**Status:** Standalone test (ready for E2E integration)

**Run Command:**
```bash
python scripts/test_table_column_rendering.py
```

**Expected Output:** 4/4 tests passed

**Note:** This test is now part of the automated E2E workflow with server restart

---

## Enhanced Tests

### **1. test_ssot_enforcement.py**

**Improvements:**
- AST-based import detection (more accurate than string matching)
- Centralized project root discovery via blueprint
- Robust regex patterns with `re.escape()` for special characters
- Enhanced whitespace matching in calculation patterns

**Impact:** Better detection of SSOT violations, handles edge cases

---

### **2. test_dashboard_generation.py**

**Improvements:**
- JSON validation of `dashboardData` (parses and validates structure)
- `gaugeData` key validation (ensures `overallHealth` exists)
- `strategicObservationsData` placeholder check (Phase 5 requirement)
- `REPORTS_DIR` import from centralized blueprint

**Impact:** Catches malformed JSON, validates required data structures, prevents UI errors

---

### **3. test_dashboard_end_to_end.py**

**Improvements:**
- **Inheritance cross-verification:** Validates `proper_base_class` flag against actual inheritance list
- **Raw object inheritance detection:** Catches agents inheriting only from `object`
- **MCP summary validation:** Ensures L5 agents have meaningful summaries (>10 chars)
- **Rendering order validation:** Verifies JS functions execute in correct sequence

**Impact:** Stronger architecture validation, prevents orphaned agents, ensures proper execution flow

---

### **4. test_dashboard_data_integrity.py**

**Improvements:**
- **Regex-based JSON extraction:** Safer parsing with `re.search()`
- **Exhaustive validation:** Tests ALL territories instead of random sampling (100% coverage)
- **Canonical inheritance check:** Added to calculation validation
- **Enhanced snapshot reporting:** Shows 32-char SHA-256 hash, clearer messaging

**Impact:** 100% territory coverage, catches all calculation errors, more robust parsing

---

## Test Coverage Gaps Addressed

### Before Improvements

| Gap | Description |
|-----|-------------|
| ❌ Data vs Rendering | Tests validated data files, not rendered output |
| ❌ Sampling | Random sampling missed edge cases |
| ❌ Column Mapping | No validation that column N displays field X |
| ❌ Execution Order | No rendering sequence checks |
| ❌ Import Detection | Simple string matching for imports |

### After Improvements

| Fix | Description |
|-----|-------------|
| ✅ Rendering Validation | New test validates rendered output (`test_table_column_rendering.py`) |
| ✅ Exhaustive Testing | All territories validated (no sampling) |
| ✅ Column Mapping | Explicit column-to-field validation |
| ✅ Order Enforcement | Rendering sequence validated |
| ✅ AST Parsing | Proper import detection via AST |

---

## Testing Workflow

### Mandatory Test Sequence

1. **SSOT Enforcement**
   ```bash
   python scripts/test_ssot_enforcement.py
   ```
   Validates all tests use canonical definitions

2. **Column Rendering**
   ```bash
   python scripts/test_table_column_rendering.py
   ```
   Validates JS rendering code uses correct fields

3. **Data Integrity**
   ```bash
   python scripts/test_dashboard_data_integrity.py
   ```
   Validates dashboard data matches SSOT calculations

4. **E2E Tests**
   ```bash
   python scripts/test_dashboard_end_to_end.py
   ```
   Comprehensive end-to-end validation

5. **Playwright Visual**
   ```bash
   python scripts/test_dashboard_playwright_visual.py
   ```
   Visual validation of rendered dashboard

---

## CI/CD Integration

### Deployment Blockers

The following tests MUST pass before deployment:

1. ✅ `test_ssot_enforcement.py` - SSOT compliance
2. ✅ `test_table_column_rendering.py` - Column rendering accuracy
3. ✅ `test_dashboard_data_integrity.py` - Data integrity (Phase 1 tests)
4. ✅ `test_dashboard_end_to_end.py` - E2E validation
5. ✅ Playwright visual inspection - Visual validation

### Recommended CI/CD Pipeline

```yaml
# .github/workflows/dashboard-tests.yml (example)
name: Dashboard Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run SSOT Enforcement
        run: python scripts/test_ssot_enforcement.py
      
      - name: Run Column Rendering Tests
        run: python scripts/test_table_column_rendering.py
      
      - name: Run Data Integrity Tests
        run: python scripts/test_dashboard_data_integrity.py
      
      - name: Run E2E Tests
        run: python scripts/test_dashboard_end_to_end.py --auto
      
      - name: Run Playwright Visual Tests
        run: python scripts/test_dashboard_playwright_visual.py
```

---

## Bug Prevention

### Health/Code Quality Score Bug

**Root Cause:** JavaScript rendering code used wrong field

**File:** `js/renderers/table-renderer.js`
- Line 247: `healthColor` used `row['Code Quality Score']` instead of `row['Health']`
- Line 292: Health column displayed `row['Code Quality Score']` instead of `row['Health']`

**Why Tests Didn't Catch It:**
- Tests validated data files, not rendered output
- No JavaScript execution in Python tests
- No column-to-field mapping validation

**Prevention:** `test_table_column_rendering.py` now validates:
```python
# Verify Table 1 doesn't use Code Quality Score
if "row['Code Quality Score']" in table1_code:
    print("❌ FAILED: Table 1 uses 'Code Quality Score' field")
    return False
```

---

## Test Metrics

### Coverage Statistics

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_ssot_enforcement.py` | 3 files × 3 checks | SSOT compliance |
| `test_table_column_rendering.py` | 4 tests | Column mapping |
| `test_dashboard_data_integrity.py` | 8 tests | 100% territories |
| `test_dashboard_end_to_end.py` | 34 tests | Full E2E |
| `test_dashboard_playwright_visual.py` | 6 visual tests | Browser rendering |

**Total:** 55+ tests across 5 test files

---

## Best Practices

### When Adding New Dashboard Features

1. **Add SSOT definitions** in `dashboard_ssot_definitions.py`
2. **Update column mappings** in `test_ssot_enforcement.py`
3. **Add rendering validation** in `test_table_column_rendering.py`
4. **Add E2E test** in `test_dashboard_end_to_end.py`
5. **Update Playwright tests** if visual changes

### When Modifying Existing Features

1. **Run full test suite** before committing
2. **Clear browser cache** before manual testing
3. **Restart dashboard server** to see changes
4. **Update baseline hashes** if data intentionally changed

---

## Troubleshooting

### Test Failures

**SSOT Enforcement Fails:**
- Check imports in test files
- Verify using `COL_*` constants, not hardcoded strings

**Column Rendering Fails:**
- Check `js/renderers/table-renderer.js`
- Verify column uses correct `row['FieldName']`

**Data Integrity Fails:**
- Regenerate dashboard data
- Check SSOT calculation functions
- Verify source data (`agent_discovery_full.json`)

**E2E Tests Fail:**
- Clear browser cache
- Restart dashboard server
- Check for stale data

---

## Maintenance

### Regular Tasks

- **Weekly:** Run full test suite
- **Before deployment:** Run all tests + Playwright
- **After data changes:** Update baseline hashes
- **After JS changes:** Clear cache, test rendering

### Test Updates

When dashboard structure changes:
1. Update SSOT definitions
2. Update test expectations
3. Regenerate baseline data
4. Update documentation

---

## Summary

These improvements create a robust, multi-layered testing strategy that:

1. ✅ Validates data integrity (SSOT compliance)
2. ✅ Validates rendering accuracy (column mapping)
3. ✅ Validates execution flow (rendering order)
4. ✅ Validates visual output (Playwright)
5. ✅ Provides 100% coverage (exhaustive validation)

**Result:** Prevents bugs like the Health/Code Quality issue from reaching production.
