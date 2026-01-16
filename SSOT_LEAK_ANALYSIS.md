# SSOT Leak Analysis: E2E Dashboard Process

**Date:** January 16, 2026  
**Scope:** Complete E2E dashboard pipeline (agent discovery → data generation → rendering → testing)  
**Status:** Comprehensive audit complete

---

## Executive Summary

**Total SSOT Leaks Identified:** 8 major categories  
**Impact:** High - Hardcoded values scattered across 15+ files  
**Priority:** Critical - Affects data integrity, maintainability, and test reliability

---

## SSOT Leak Inventory

| # | Category | Severity | Files Affected | Current State | Implementation Effort |
|---|----------|----------|----------------|---------------|---------------------|
| 1 | Territory Names | 🟢 FIXED | 2 files | SSOT enforced via `territory_ssot_definitions.py` | ✅ Complete |
| 2 | Column Names (JS) | 🔴 CRITICAL | 5 JS files | Hardcoded strings in rendering code | High |
| 3 | Field Names (Discovery) | 🟡 HIGH | 2 Python files | Hardcoded in agent discovery | Medium |
| 4 | Metric Thresholds | 🟡 HIGH | 10+ test files | Magic numbers (50, 80, 100) scattered | Medium |
| 5 | Health Score Weights | 🟡 HIGH | 3 files | Formula weights duplicated | Low |
| 6 | File Paths | 🟡 HIGH | 15+ files | Hardcoded paths to JSON/JS files | Medium |
| 7 | Observable % Placeholder | 🟢 LOW | 3 files | Documented placeholder (50.0) | Low |
| 8 | Metric Key Names | 🟡 HIGH | 3 JS files | Camel case keys hardcoded | Medium |

---

## Detailed Analysis

### **1. Territory Names** ✅ FIXED

**Status:** SSOT enforced  
**SSOT File:** `scripts/territory_ssot_definitions.py`

**Before:**
- Hardcoded in `full_agent_discovery.py` (100+ lines)
- Hardcoded in `regenerate_dashboard_data.py` (30+ lines)

**After:**
- Single source: `territory_ssot_definitions.py`
- Functions: `get_territory_from_path()`, `get_territory_sort_key()`
- Constants: `TERRITORY_SOVEREIGN_BASE`, `TERRITORY_L0_BASE`, etc.

**Implementation:** ✅ Complete (Jan 16, 2026)

---

### **2. Column Names in JavaScript** 🔴 CRITICAL

**Severity:** CRITICAL  
**Impact:** Rendering bugs, column mismatches  
**Files Affected:**
- `js/renderers/table-renderer.js` (20+ hardcoded column names)
- `js/renderers/content-renderer.js` (10+ hardcoded column names)
- `js/utils/math-utils.js` (metric key references)
- `autonomy_dashboard.html` (embedded JS with hardcoded columns)
- `autonomy_dashboard_backup.html` (legacy hardcoded columns)

**Examples:**
```javascript
// table-renderer.js (HARDCODED)
row['Health']
row['Code Quality Score']
row['Test %']
row['MCP Hardened %']
row['Heal Cap %']
row['Invocation %']
row['Complexity Health %']
row['Typed %']
row['Documented %']
row['Schema Strictness %']
row['Canonical Inheritance %']
```

**SSOT Exists:** `scripts/dashboard_ssot_definitions.py`
```python
COL_HEALTH = "Health"
COL_CODE_QUALITY = "Code Quality Score"
COL_TEST = "Test %"
COL_HARDENED = "MCP Hardened %"
# ... etc
```

**Problem:** JavaScript cannot import Python constants

**Implementation Plan:**

#### **Option A: Generate JS Constants File (RECOMMENDED)**
1. Create `scripts/generate_js_constants.py`
2. Read SSOT from `dashboard_ssot_definitions.py`
3. Generate `js/constants/dashboard-constants.js`:
   ```javascript
   // Auto-generated from dashboard_ssot_definitions.py
   // DO NOT EDIT MANUALLY
   export const COL_HEALTH = "Health";
   export const COL_CODE_QUALITY = "Code Quality Score";
   export const COL_TEST = "Test %";
   // ... etc
   ```
4. Update all JS files to import constants:
   ```javascript
   import { COL_HEALTH, COL_CODE_QUALITY } from './constants/dashboard-constants.js';
   
   // Use constants instead of strings
   const healthColor = getWorstCaseColor(row[COL_HEALTH] || 0);
   ```
5. Add generation step to dashboard regeneration pipeline

**Effort:** 4-6 hours  
**Priority:** P0 - Prevents rendering bugs like Health/Code Quality issue

---

#### **Option B: JSON Configuration File**
1. Generate `data/dashboard-config.json` from SSOT
2. Load in JavaScript at runtime
3. Access via config object

**Effort:** 3-4 hours  
**Priority:** P1 - Alternative if ES6 modules not supported

---

### **3. Field Names in Agent Discovery** 🟡 HIGH

**Severity:** HIGH  
**Impact:** Data extraction errors, missing fields  
**Files Affected:**
- `scripts/full_agent_discovery.py` (field name strings)
- `scripts/regenerate_dashboard_data.py` (field access)

**Examples:**
```python
# full_agent_discovery.py (HARDCODED)
a.get('has_healing', False)
a.get('has_tests', False)
a.get('mcp_hardened', False)
a.get('typed_pct', 0)
a.get('documented_pct', 0)
a.get('territory', 'Unknown')

# regenerate_dashboard_data.py (HARDCODED)
sum(1 for a in agents if a.get('has_healing', False))
```

**Implementation Plan:**

1. Create `scripts/agent_field_ssot.py`:
   ```python
   # Agent discovery field names (SSOT)
   FIELD_HAS_HEALING = "has_healing"
   FIELD_HAS_TESTS = "has_tests"
   FIELD_MCP_HARDENED = "mcp_hardened"
   FIELD_TYPED_PCT = "typed_pct"
   FIELD_DOCUMENTED_PCT = "documented_pct"
   FIELD_TERRITORY = "territory"
   FIELD_CLASS_NAME = "class_name"
   FIELD_LAYER = "layer"
   FIELD_INVOCATION = "invocation"
   FIELD_CYCLOMATIC_COMPLEXITY = "cyclomatic_complexity"
   # ... etc
   ```

2. Update `full_agent_discovery.py`:
   ```python
   from agent_field_ssot import *
   
   # Use constants
   agent_data = {
       FIELD_CLASS_NAME: node.name,
       FIELD_LAYER: layer,
       FIELD_TERRITORY: territory,
       FIELD_HAS_HEALING: has_healing,
       FIELD_HAS_TESTS: has_tests,
       # ... etc
   }
   ```

3. Update `regenerate_dashboard_data.py`:
   ```python
   from agent_field_ssot import *
   
   # Use constants
   sum(1 for a in agents if a.get(FIELD_HAS_HEALING, False))
   ```

**Effort:** 2-3 hours  
**Priority:** P1 - Prevents field name typos

---

### **4. Metric Thresholds** 🟡 HIGH

**Severity:** HIGH  
**Impact:** Inconsistent test expectations, magic numbers  
**Files Affected:**
- `test_dashboard_data_integrity.py` (range expectations)
- `test_mcp_hardening_all_territories.py` (100.0 hardcoded)
- `test_strategic_recommendation_agent.py` (test data thresholds)
- `test_dashboard_visual.py` (50, 80, 100 thresholds)
- `js/renderers/table-renderer.js` (50, 60 thresholds for outliers)
- `js/utils/math-utils.js` (threshold logic)

**Examples:**
```python
# test_mcp_hardening_all_territories.py (HARDCODED)
if mcp_pct != 100.0:
    failures.append(f"{territory}: {mcp_pct}%")

# test_dashboard_data_integrity.py (HARDCODED)
EXPECTED_RANGES = {
    'Complexity Health %': (0, 60),
    'Test %': (0, 100),
    'MCP Hardened %': (80, 100),
    # ... etc
}
```

```javascript
// table-renderer.js (HARDCODED)
const metrics = ['healCap', 'invocation', 'hardened', 'test', 'complexityHealth', 'health'];
metrics.forEach(key => {
    const summary = getOutlierSummary(agentData[key] || [], 50);  // 50 hardcoded
});
```

**Implementation Plan:**

1. Create `scripts/metric_thresholds_ssot.py`:
   ```python
   # Metric thresholds (SSOT)
   THRESHOLD_MCP_HARDENED_TARGET = 100.0
   THRESHOLD_TEST_COVERAGE_MIN = 50.0
   THRESHOLD_TEST_COVERAGE_TARGET = 80.0
   THRESHOLD_COMPLEXITY_HEALTH_MAX = 60.0
   THRESHOLD_HEALTH_SCORE_MIN = 60.0
   THRESHOLD_OUTLIER_DEFAULT = 50.0
   
   # Expected ranges for validation
   EXPECTED_RANGES = {
       COL_COMPLEXITY_HEALTH: (0, THRESHOLD_COMPLEXITY_HEALTH_MAX),
       COL_TEST: (0, 100),
       COL_HARDENED: (THRESHOLD_TEST_COVERAGE_TARGET, 100),
       COL_HEALTH: (THRESHOLD_HEALTH_SCORE_MIN, 100),
       # ... etc
   }
   ```

2. Update test files to import thresholds
3. Generate JS constants file with thresholds
4. Update JS files to use threshold constants

**Effort:** 3-4 hours  
**Priority:** P1 - Ensures consistent expectations

---

### **5. Health Score Formula Weights** 🟡 HIGH

**Severity:** HIGH  
**Impact:** Formula drift, calculation errors  
**Files Affected:**
- `scripts/dashboard_ssot_definitions.py` (canonical formula)
- `test_dashboard_end_to_end.py` (test validation)
- `test_health_score_validation.py` (test validation)

**Current State:**
```python
# dashboard_ssot_definitions.py (CANONICAL)
def calc_health_score(...):
    return round(
        heal_cap_pct * 0.30 +
        invocation_pct * 0.10 +
        test_pct * 0.25 +
        observable_pct * 0.20 +
        complexity_health * 0.15,
        1
    )
```

**Problem:** Weights (0.30, 0.10, 0.25, 0.20, 0.15) are magic numbers

**Implementation Plan:**

1. Add constants to `dashboard_ssot_definitions.py`:
   ```python
   # Health score formula weights (SSOT)
   WEIGHT_HEAL_CAP = 0.30
   WEIGHT_INVOCATION = 0.10
   WEIGHT_TEST = 0.25
   WEIGHT_OBSERVABLE = 0.20
   WEIGHT_COMPLEXITY = 0.15
   
   # Validate weights sum to 1.0
   assert abs(sum([WEIGHT_HEAL_CAP, WEIGHT_INVOCATION, WEIGHT_TEST, 
                    WEIGHT_OBSERVABLE, WEIGHT_COMPLEXITY]) - 1.0) < 0.001
   
   def calc_health_score(...):
       return round(
           heal_cap_pct * WEIGHT_HEAL_CAP +
           invocation_pct * WEIGHT_INVOCATION +
           test_pct * WEIGHT_TEST +
           observable_pct * WEIGHT_OBSERVABLE +
           complexity_health * WEIGHT_COMPLEXITY,
           1
       )
   ```

2. Document formula in docstring with weight constants

**Effort:** 1 hour  
**Priority:** P2 - Low risk but improves clarity

---

### **6. File Paths** 🟡 HIGH

**Severity:** HIGH  
**Impact:** Brittle code, breaks if files move  
**Files Affected:**
- 15+ test files
- `regenerate_dashboard_data.py`
- Various verification scripts

**Examples:**
```python
# test_dashboard_data_integrity.py (HARDCODED)
data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"

# test_dashboard_playwright_visual.py (HARDCODED)
dashboard_dir = project_root / "agentic_core" / "L6_observability" / "dashboards"

# Multiple files (HARDCODED)
source_file = project_root / "agent_discovery_full.json"
```

**SSOT Exists:** `agentic_core/config/blueprint_sovereign/structure_blueprint.py`
```python
AGENT_DISCOVERY_JSON = "agent_discovery_full.json"
DASHBOARD_DIR = "agentic_core/L6_observability/dashboards"
L6_OBSERVABILITY_DIR = "agentic_core/L6_observability"
```

**Problem:** Not all files import from blueprint

**Implementation Plan:**

1. Add missing constants to `structure_blueprint.py`:
   ```python
   DASHBOARD_DATA_JS = "agentic_core/L6_observability/dashboards/data/dashboard_data.js"
   DASHBOARD_HTML = "agentic_core/L6_observability/dashboards/autonomy_dashboard.html"
   ```

2. Update all files to import from blueprint:
   ```python
   from agentic_core.config.blueprint_sovereign.structure_blueprint import (
       AGENT_DISCOVERY_JSON,
       DASHBOARD_DATA_JS,
       DASHBOARD_HTML,
       get_validated_project_root
   )
   
   project_root = get_validated_project_root()
   data_file = project_root / DASHBOARD_DATA_JS
   ```

3. Add to SSOT enforcement test

**Effort:** 2-3 hours  
**Priority:** P1 - Prevents path errors

---

### **7. Observable % Placeholder** 🟢 LOW

**Severity:** LOW  
**Impact:** Documented placeholder, not a leak  
**Files Affected:**
- `regenerate_dashboard_data.py` (50.0 placeholder)
- `test_health_score_validation.py` (50.0 placeholder)
- `dashboard_ssot_definitions.py` (documented in formula)

**Current State:**
```python
# regenerate_dashboard_data.py
total_health = calc_health_score(
    total_heal_cap, total_invocation, total_test, 
    50.0,  # Observable % placeholder
    total_complexity_health,
    is_l0=False
)
```

**Status:** This is a **documented placeholder**, not a leak. Observable % is not yet implemented.

**Implementation Plan:**

1. Add constant to `dashboard_ssot_definitions.py`:
   ```python
   # Observable % placeholder (awaiting implementation)
   OBSERVABLE_PCT_PLACEHOLDER = 50.0
   ```

2. Update calls to use constant:
   ```python
   total_health = calc_health_score(
       total_heal_cap, total_invocation, total_test, 
       OBSERVABLE_PCT_PLACEHOLDER,
       total_complexity_health,
       is_l0=False
   )
   ```

**Effort:** 30 minutes  
**Priority:** P3 - Nice to have

---

### **8. Metric Key Names (JavaScript)** 🟡 HIGH

**Severity:** HIGH  
**Impact:** Key mismatches between Python and JS  
**Files Affected:**
- `js/renderers/table-renderer.js` (camelCase keys)
- `js/utils/math-utils.js` (camelCase keys)
- `autonomy_dashboard_backup.html` (camelCase keys)

**Examples:**
```javascript
// table-renderer.js (HARDCODED camelCase)
const allMetrics = ['healCap', 'invocation', 'hardened', 'test', 
                    'complexityHealth', 'health', 'typed', 'documented', 
                    'schemaStrictness', 'properBase', 'codeQuality'];

// Python uses different keys in agent_discovery_full.json
{
  "has_healing": true,
  "has_tests": true,
  "mcp_hardened": true,
  "typed_pct": 100.0,
  "documented_pct": 100.0
}
```

**Problem:** Mismatch between Python field names and JS metric keys

**Implementation Plan:**

1. Document key mapping in SSOT:
   ```python
   # scripts/dashboard_ssot_definitions.py
   
   # Python field names (from agent_discovery_full.json)
   FIELD_HAS_HEALING = "has_healing"
   FIELD_HAS_TESTS = "has_tests"
   FIELD_MCP_HARDENED = "mcp_hardened"
   
   # JavaScript metric keys (camelCase for agentData)
   JS_KEY_HEAL_CAP = "healCap"
   JS_KEY_INVOCATION = "invocation"
   JS_KEY_HARDENED = "hardened"
   JS_KEY_TEST = "test"
   
   # Mapping dictionary
   PYTHON_TO_JS_KEY_MAP = {
       FIELD_HAS_HEALING: JS_KEY_HEAL_CAP,
       FIELD_HAS_TESTS: JS_KEY_TEST,
       FIELD_MCP_HARDENED: JS_KEY_HARDENED,
       # ... etc
   }
   ```

2. Generate JS constants with key names
3. Update JS to use constants

**Effort:** 2-3 hours  
**Priority:** P1 - Prevents key mismatch errors

---

## Implementation Priority Matrix

| Priority | Category | Effort | Impact | Timeline |
|----------|----------|--------|--------|----------|
| **P0** | Column Names (JS) | High | Critical | Week 1 |
| **P1** | Field Names (Discovery) | Medium | High | Week 1 |
| **P1** | File Paths | Medium | High | Week 1 |
| **P1** | Metric Thresholds | Medium | High | Week 2 |
| **P1** | Metric Key Names (JS) | Medium | High | Week 2 |
| **P2** | Health Score Weights | Low | Medium | Week 3 |
| **P3** | Observable % Placeholder | Low | Low | Week 3 |

---

## Recommended Implementation Order

### **Phase 1: Critical Fixes (Week 1)**

1. **Generate JS Constants** (P0)
   - Create `scripts/generate_js_constants.py`
   - Generate `js/constants/dashboard-constants.js`
   - Update all JS files to import constants
   - Add to regeneration pipeline

2. **Field Name SSOT** (P1)
   - Create `scripts/agent_field_ssot.py`
   - Update `full_agent_discovery.py`
   - Update `regenerate_dashboard_data.py`

3. **File Path SSOT** (P1)
   - Add constants to `structure_blueprint.py`
   - Update all test files
   - Update verification scripts

### **Phase 2: High Priority (Week 2)**

4. **Metric Thresholds** (P1)
   - Create `scripts/metric_thresholds_ssot.py`
   - Update test files
   - Generate JS threshold constants

5. **Metric Key Names** (P1)
   - Document Python-to-JS key mapping
   - Generate JS key constants
   - Update JS files

### **Phase 3: Polish (Week 3)**

6. **Health Score Weights** (P2)
   - Add weight constants
   - Update formula
   - Add validation

7. **Observable % Placeholder** (P3)
   - Add placeholder constant
   - Update all references

---

## Testing Strategy

After each phase:

1. **Run SSOT enforcement test:**
   ```bash
   python scripts/test_ssot_enforcement.py
   ```

2. **Run data integrity test:**
   ```bash
   python scripts/test_dashboard_data_integrity.py
   ```

3. **Run E2E test:**
   ```bash
   python scripts/test_dashboard_end_to_end.py
   ```

4. **Run column rendering test:**
   ```bash
   python scripts/test_table_column_rendering.py
   ```

5. **Regenerate and verify:**
   ```bash
   python scripts/full_agent_discovery.py
   python scripts/regenerate_dashboard_data.py
   # Hard refresh browser
   ```

---

## Success Metrics

- ✅ Zero hardcoded column names in JS
- ✅ Zero hardcoded field names in Python
- ✅ Zero hardcoded file paths
- ✅ Zero magic number thresholds
- ✅ All constants imported from SSOT files
- ✅ All tests pass with SSOT enforcement

---

## Files to Create

1. `scripts/generate_js_constants.py` - Generate JS constants from Python SSOT
2. `scripts/agent_field_ssot.py` - Agent discovery field names
3. `scripts/metric_thresholds_ssot.py` - Metric threshold constants
4. `js/constants/dashboard-constants.js` - Auto-generated JS constants

---

## Files to Modify

1. `scripts/full_agent_discovery.py` - Use field name constants
2. `scripts/regenerate_dashboard_data.py` - Use field name constants
3. `scripts/dashboard_ssot_definitions.py` - Add weight constants
4. `agentic_core/config/blueprint_sovereign/structure_blueprint.py` - Add file path constants
5. `js/renderers/table-renderer.js` - Import and use constants
6. `js/renderers/content-renderer.js` - Import and use constants
7. `js/utils/math-utils.js` - Import and use constants
8. All test files - Import file paths from blueprint

---

## Estimated Total Effort

- **Phase 1 (Critical):** 12-15 hours
- **Phase 2 (High Priority):** 8-10 hours
- **Phase 3 (Polish):** 3-4 hours
- **Total:** 23-29 hours (3-4 days)

---

## Risk Assessment

**High Risk:**
- JS constant generation - Requires build step integration
- Column name changes - Could break existing dashboards

**Medium Risk:**
- Field name changes - Requires careful migration
- Threshold changes - Could affect test expectations

**Low Risk:**
- File path consolidation - Straightforward refactor
- Weight constants - No behavior change

---

## Conclusion

**Current State:** 7 active SSOT leaks (1 already fixed)  
**Recommended Action:** Implement in 3 phases over 3-4 days  
**Expected Outcome:** 100% SSOT enforcement across E2E dashboard pipeline  
**Maintenance Benefit:** Single point of change for all dashboard constants
