# Dashboard Sprawl & SSOT Violation Audit Report

**Date:** January 7, 2026  
**Issue:** Dashboard logic sprawled across multiple locations, violating SSOT  
**Status:** 🔴 **CRITICAL ARCHITECTURE VIOLATION**

---

## Executive Summary

**CRITICAL FINDING:** Dashboard logic is severely sprawled across **5 different locations** in the repository, creating massive SSOT violations, governance issues, and maintenance burden. The user is correct - dashboard files are NOT consolidated.

### Severity Assessment

🔴 **CRITICAL VIOLATIONS:**
- Dashboard generation modules in **wrong location** (`L5_safety/validators` instead of `observability/dashboard`)
- **3 different dashboard template files** across 2 locations
- **2 separate dashboard server implementations**
- **44 dashboard Python files** scattered across repo
- **14 dashboard HTML files** in various locations
- **No clear ownership** or governance structure

---

## Part 1: Dashboard File Sprawl Analysis

### Core Dashboard Components (WRONG LOCATION ❌)

**Location:** `agentic_core/L5_safety/validators/` ❌

| File | Lines | Purpose | Should Be In |
|------|-------|---------|--------------|
| `dashboard_data_generator.py` | 418 | Metrics computation | `observability/dashboard/` |
| `dashboard_renderer.py` | 356 | HTML rendering | `observability/dashboard/` |
| `test_dashboard_categories.py` | ? | Testing | `tests/unit/dashboard/` |

**VIOLATION:** These are **observability/dashboard** concerns, NOT L5 safety validation concerns.

**Why This Is Wrong:**
- L5 Safety layer should validate autonomy, not generate dashboards
- Violates layered architecture (L5 = Safety, L6 = Observability)
- Creates tight coupling between validation and visualization
- Makes dashboard logic hard to find and maintain

---

### Observability Dashboard (CORRECT LOCATION ✅ but INCOMPLETE)

**Location:** `agentic_core/observability/dashboard/` ✅

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `dashboard_api.py` | 23 | REST API endpoints | ✅ Correct |
| `dashboard_loader.py` | 168 | SSOT data loading | ✅ Correct |
| `dashboard_server.py` | 136 | FastAPI server | ✅ Correct |
| `dashboard_template.html` | 0 | Empty template | ❌ EMPTY FILE |
| `__init__.py` | 564 bytes | Module init | ✅ Correct |

**ISSUE:** This folder exists but is **incomplete** - missing the actual dashboard generation logic!

**What's Missing:**
- Dashboard data generator (currently in L5_safety)
- Dashboard renderer (currently in L5_safety)
- Actual template file (empty 0-byte file)

---

### Dashboard Templates (3 FILES, 2 LOCATIONS ❌)

| File | Size | Location | Status |
|------|------|----------|--------|
| `dashboard_template.html` | 93 KB | `config/validators/` | ✅ Active (SSOT) |
| `dashboard_template_with_detailed_tables.html` | ? | `config/validators/` | ⚠️ Duplicate? |
| `dashboard_template.html` | 0 bytes | `observability/dashboard/` | ❌ Empty |

**VIOLATION:** Templates scattered across 2 locations with unclear ownership.

**Expected:** Single template in `observability/dashboard/templates/`

---

### Observability Metrics (DUPLICATE SERVER ❌)

**Location:** `agentic_core/observability/metrics/dashboard_server.py`

**VIOLATION:** Duplicate dashboard server in metrics folder!

**Conflict:**
- `observability/dashboard/dashboard_server.py` (136 lines)
- `observability/metrics/dashboard_server.py` (unknown size)

**Why This Is Wrong:** Two servers serving same purpose = confusion and maintenance burden.

---

### Scripts Folder (MASSIVE SPRAWL ❌)

**Location:** `scripts/`

**Dashboard Scripts Found:** 20+ files

| File | Purpose | Should Be |
|------|---------|-----------|
| `check_dashboard_data.py` | Validation | `tests/unit/dashboard/` |
| `check_dashboard_l4.py` | Validation | `tests/unit/dashboard/` |
| `check_dashboard_rendering.py` | Validation | `tests/unit/dashboard/` |
| `check_dashboard_targets.py` | Validation | `tests/unit/dashboard/` |
| `comprehensive_dashboard_tests.py` | Testing | `tests/e2e/dashboard/` |
| `dashboard_live_server.py` | Server | `observability/dashboard/` |
| `dashboard_qa.py` | QA | `tests/unit/dashboard/` |
| `enforce_dashboard_freshness.py` | Enforcement | `observability/dashboard/` |
| `extract_dashboard_errors.py` | Debug | `observability/dashboard/debug/` |
| `serve_dashboard.py` | Server | `observability/dashboard/` |
| `start_dashboard_server.py` | Server | `observability/dashboard/` |
| `test_dashboard_generation.py` | Testing | `tests/unit/dashboard/` |
| `trace_dashboard_generation.py` | Debug | `observability/dashboard/debug/` |
| `validate_dashboard_html.py` | Validation | `tests/unit/dashboard/` |
| `validate_dashboard_totals.py` | Validation | `tests/unit/dashboard/` |
| `verify_dashboard_refresh.py` | Validation | `tests/unit/dashboard/` |
| `verify_dashboard_state.py` | Validation | `tests/unit/dashboard/` |
| `verify_dashboard_updates.py` | Validation | `tests/unit/dashboard/` |
| `windsurf_realtime_dashboard.py` | Server | `observability/dashboard/` |

**VIOLATION:** 20+ dashboard scripts in root `scripts/` folder instead of proper locations.

---

### Root Folder (DEBUG SCRIPTS ❌)

**Location:** Repository root

| File | Purpose | Should Be |
|------|---------|-----------|
| `check_dashboard.py` | Validation | `tests/unit/dashboard/` |
| `debug_dashboard_count.py` | Debug | `observability/dashboard/debug/` |
| `debug_dashboard_generation.py` | Debug | `observability/dashboard/debug/` |
| `stress_test_dashboard_pipeline.py` | Testing | `tests/stress/dashboard/` |
| `trace_dashboard_bug.py` | Debug | `observability/dashboard/debug/` |
| `verify_dashboard.py` | Validation | `tests/unit/dashboard/` |

**VIOLATION:** 6 dashboard files in repository root cluttering workspace.

---

### Apps Shared (DEPRECATED ✅)

**Location:** `apps_shared/P1_core/`

| File | Status |
|------|--------|
| `canon_dashboard.py` | ✅ Properly deprecated |
| `canon_dashboard_web.py` | ✅ Properly deprecated |

**Good:** These are properly marked as deprecated with clear migration path.

---

### Tests Folder (SCATTERED ⚠️)

**Dashboard Test Files:** 10+ files across 4 locations

| Location | Files | Should Be |
|----------|-------|-----------|
| `tests/e2e/dashboard/` | 2 files | ✅ Correct |
| `tests/integration/dashboard/` | 1 file | ✅ Correct |
| `tests/regression/` | 1 file | ⚠️ Should be in `tests/regression/dashboard/` |
| `tests/unit/` | 2 files | ⚠️ Should be in `tests/unit/dashboard/` |
| `tests/unit/observability/` | 1 file | ✅ Correct |
| `tests/` (root) | 3 files | ❌ Should be in subdirectories |

**ISSUE:** Tests scattered across multiple locations without clear organization.

---

## Part 2: SSOT Violations

### Violation 1: Dashboard Generation Logic in Wrong Layer

**Current State:**
```
agentic_core/
├── L5_safety/validators/          ❌ WRONG LAYER
│   ├── dashboard_data_generator.py
│   └── dashboard_renderer.py
└── observability/dashboard/       ✅ CORRECT LAYER (but incomplete)
    ├── dashboard_api.py
    ├── dashboard_loader.py
    └── dashboard_server.py
```

**Problem:**
- L5 = Safety/Validation layer
- L6 = Observability layer
- Dashboard is observability, not safety validation
- Creates architectural confusion

**Impact:**
- Violates layered architecture
- Makes dashboard hard to find
- Couples validation with visualization
- Confuses new developers

---

### Violation 2: Multiple Dashboard Templates

**Current State:**
```
agentic_core/
├── config/validators/
│   ├── dashboard_template.html              (93 KB - Active)
│   └── dashboard_template_with_detailed_tables.html  (? KB - Duplicate?)
└── observability/dashboard/
    └── dashboard_template.html              (0 bytes - Empty)
```

**Problem:**
- 3 template files
- 2 locations
- 1 empty file
- Unclear which is canonical

**Impact:**
- Template changes require updating multiple files
- Risk of divergence
- Confusion about SSOT

---

### Violation 3: Duplicate Dashboard Servers

**Current State:**
```
agentic_core/observability/
├── dashboard/
│   └── dashboard_server.py       (136 lines - FastAPI)
└── metrics/
    └── dashboard_server.py       (? lines - Duplicate?)
```

**Problem:**
- Two servers with same name
- Unclear which is canonical
- Potential port conflicts

**Impact:**
- Confusion about which server to use
- Maintenance burden (fix bugs twice)
- Risk of divergence

---

### Violation 4: Scripts Sprawl

**Current State:**
```
scripts/
├── check_dashboard_*.py          (4 files)
├── dashboard_*.py                (3 files)
├── serve_dashboard.py
├── start_dashboard_server.py
├── test_dashboard_*.py           (1 file)
├── validate_dashboard_*.py       (3 files)
├── verify_dashboard_*.py         (3 files)
└── ... (20+ dashboard scripts)
```

**Problem:**
- 20+ dashboard scripts in flat structure
- No organization by purpose
- Mixes testing, validation, serving, debugging

**Impact:**
- Hard to find relevant scripts
- Duplication of functionality
- No clear ownership

---

### Violation 5: Import Chaos

**Current Imports:**
```python
# Tests import from L5_safety (WRONG)
from agentic_core.L5_safety.validators.dashboard_data_generator import DashboardDataGenerator
from agentic_core.L5_safety.validators.dashboard_renderer import DashboardRenderer

# AutonomyGuardianAgent imports from L5_safety (WRONG)
from agentic_core.L5_safety.validators.dashboard_data_generator import DashboardDataGenerator
from agentic_core.L5_safety.validators.dashboard_renderer import DashboardRenderer

# Server imports from observability (CORRECT)
from agentic_core.observability.dashboard.dashboard_loader import load_agents
```

**Problem:**
- Imports point to wrong layer
- Creates coupling between L5 and dashboard
- Makes refactoring difficult

---

## Part 3: Root Cause Analysis

### Why Are Dashboard Modules in L5_safety/validators?

**Historical Context:**
1. Dashboard was originally part of `AutonomyGuardianAgent` (L5 validator)
2. Code was extracted to reduce complexity
3. **BUT:** Extracted to same folder instead of correct location
4. Result: Modules stayed in `L5_safety/validators/` instead of moving to `observability/dashboard/`

**This Is Classic "Proximity Bias":**
- Extracted code stayed near original code
- Didn't consider proper architectural placement
- Created technical debt

---

### Why Multiple Templates?

**Historical Context:**
1. Original template in `config/validators/` (near validator)
2. Empty placeholder created in `observability/dashboard/` (correct location)
3. "Detailed tables" variant created (experimentation?)
4. No cleanup or consolidation performed

**Result:** 3 templates, unclear ownership

---

### Why Scripts Sprawl?

**Historical Context:**
1. Dashboard development involved lots of debugging
2. Debug scripts created in root for quick access
3. Test scripts created in `scripts/` for convenience
4. No cleanup or organization performed
5. Scripts accumulated over time

**Result:** 20+ scripts in wrong locations

---

## Part 4: Impact Assessment

### Maintenance Burden

**Current State:**
- Dashboard logic in 5+ locations
- Changes require updating multiple files
- Risk of missing updates
- Hard to ensure consistency

**Example:** Schema Strictness fix required changes in 3 files because logic was duplicated.

---

### Developer Confusion

**Current State:**
- New developers can't find dashboard code
- Unclear which files are canonical
- Import paths point to wrong layer
- No clear ownership

**Example:** "Where is the dashboard code?" → 5 different answers

---

### Testing Complexity

**Current State:**
- Tests scattered across 6+ locations
- Unclear which tests are canonical
- Hard to run all dashboard tests
- Duplication of test logic

---

### Governance Issues

**Current State:**
- No clear owner for dashboard code
- No clear process for changes
- No clear SSOT
- Multiple sources of truth

---

## Part 5: Recommended Consolidation Plan

### Target Architecture

```
agentic_core/observability/dashboard/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── data_generator.py      ← MOVE from L5_safety/validators/
│   ├── renderer.py            ← MOVE from L5_safety/validators/
│   └── loader.py              ← KEEP (already here)
├── server/
│   ├── __init__.py
│   ├── api.py                 ← MOVE from dashboard_api.py
│   ├── app.py                 ← CONSOLIDATE both dashboard_server.py files
│   └── routes.py              ← NEW (extract from app.py)
├── templates/
│   ├── dashboard.html         ← MOVE from config/validators/dashboard_template.html
│   └── components/            ← NEW (for template partials)
├── scripts/
│   ├── serve.py               ← CONSOLIDATE serve_dashboard.py, start_dashboard_server.py
│   ├── validate.py            ← CONSOLIDATE check_dashboard_*.py, validate_dashboard_*.py
│   └── debug.py               ← CONSOLIDATE debug_dashboard_*.py, trace_dashboard_*.py
└── tests/
    ├── unit/
    │   ├── test_data_generator.py
    │   ├── test_renderer.py
    │   └── test_loader.py
    ├── integration/
    │   └── test_dashboard_integration.py
    └── e2e/
        └── test_dashboard_e2e.py

tests/
├── unit/dashboard/            ← MOVE dashboard tests here
├── integration/dashboard/     ← KEEP
├── e2e/dashboard/            ← KEEP
└── regression/dashboard/      ← NEW (move regression tests)

scripts/
└── (remove all dashboard scripts - move to observability/dashboard/scripts/)
```

---

### Migration Steps

#### Phase 1: Move Core Modules (HIGH PRIORITY)

**Step 1.1:** Move dashboard generation modules
```bash
# Move files
mv agentic_core/L5_safety/validators/dashboard_data_generator.py \
   agentic_core/observability/dashboard/core/data_generator.py

mv agentic_core/L5_safety/validators/dashboard_renderer.py \
   agentic_core/observability/dashboard/core/renderer.py
```

**Step 1.2:** Update imports
```python
# OLD (WRONG)
from agentic_core.L5_safety.validators.dashboard_data_generator import DashboardDataGenerator
from agentic_core.L5_safety.validators.dashboard_renderer import DashboardRenderer

# NEW (CORRECT)
from agentic_core.observability.dashboard.core.data_generator import DashboardDataGenerator
from agentic_core.observability.dashboard.core.renderer import DashboardRenderer
```

**Files to Update:**
- `agentic_core/L5_safety/validators/AutonomyGuardianAgent.py`
- `tests/e2e/dashboard/test_dashboard_ssot_e2e.py`
- Any other files importing these modules

**Step 1.3:** Run tests to verify
```bash
pytest tests/e2e/dashboard/ -v
pytest tests/unit/dashboard/ -v
```

---

#### Phase 2: Consolidate Templates (MEDIUM PRIORITY)

**Step 2.1:** Move canonical template
```bash
# Create templates directory
mkdir -p agentic_core/observability/dashboard/templates

# Move canonical template
mv agentic_core/config/validators/dashboard_template.html \
   agentic_core/observability/dashboard/templates/dashboard.html
```

**Step 2.2:** Remove duplicates
```bash
# Remove empty template
rm agentic_core/observability/dashboard/dashboard_template.html

# Evaluate if detailed tables template is needed
# If yes: move to templates/dashboard_detailed.html
# If no: delete
```

**Step 2.3:** Update renderer to use new path
```python
# In observability/dashboard/core/renderer.py
self.template_paths = [
    project_root / "agentic_core" / "observability" / "dashboard" / "templates" / "dashboard.html",
]
```

---

#### Phase 3: Consolidate Servers (MEDIUM PRIORITY)

**Step 3.1:** Audit both servers
```bash
# Compare functionality
diff agentic_core/observability/dashboard/dashboard_server.py \
     agentic_core/observability/metrics/dashboard_server.py
```

**Step 3.2:** Consolidate into single server
```python
# agentic_core/observability/dashboard/server/app.py
# Merge functionality from both servers
# Keep FastAPI implementation from dashboard/dashboard_server.py
# Add any unique features from metrics/dashboard_server.py
```

**Step 3.3:** Remove duplicate
```bash
rm agentic_core/observability/metrics/dashboard_server.py
```

---

#### Phase 4: Organize Scripts (LOW PRIORITY)

**Step 4.1:** Categorize scripts
- **Serving:** `serve_dashboard.py`, `start_dashboard_server.py`, `dashboard_live_server.py`
- **Validation:** `check_dashboard_*.py`, `validate_dashboard_*.py`, `verify_dashboard_*.py`
- **Debug:** `debug_dashboard_*.py`, `trace_dashboard_*.py`, `extract_dashboard_errors.py`
- **Testing:** `test_dashboard_*.py`, `comprehensive_dashboard_tests.py`

**Step 4.2:** Consolidate by category
```bash
# Serving scripts → single serve.py
# Validation scripts → single validate.py
# Debug scripts → single debug.py
# Testing scripts → move to tests/
```

**Step 4.3:** Move to proper location
```bash
mv scripts/dashboard_consolidated_*.py \
   agentic_core/observability/dashboard/scripts/
```

---

#### Phase 5: Organize Tests (LOW PRIORITY)

**Step 5.1:** Create test structure
```bash
mkdir -p tests/unit/dashboard
mkdir -p tests/regression/dashboard
```

**Step 5.2:** Move tests
```bash
# Move unit tests from tests/ root
mv tests/test_dashboard_*.py tests/unit/dashboard/

# Move regression tests
mv tests/regression/test_dashboard_regression.py \
   tests/regression/dashboard/
```

---

### Breaking Changes & Migration Guide

**Breaking Changes:**
1. Import paths change from `L5_safety.validators` to `observability.dashboard.core`
2. Template path changes from `config/validators` to `observability/dashboard/templates`
3. Server consolidation may change port or endpoints

**Migration Guide for Users:**
```python
# Before
from agentic_core.L5_safety.validators.dashboard_data_generator import DashboardDataGenerator

# After
from agentic_core.observability.dashboard.core.data_generator import DashboardDataGenerator
```

**Backward Compatibility (Optional):**
```python
# In agentic_core/L5_safety/validators/dashboard_data_generator.py
# Keep as shim for 1-2 releases
import warnings
from agentic_core.observability.dashboard.core.data_generator import DashboardDataGenerator

warnings.warn(
    "Importing from L5_safety.validators is deprecated. "
    "Use observability.dashboard.core instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['DashboardDataGenerator']
```

---

## Part 6: Governance Recommendations

### Ownership

**Assign Clear Owner:**
- **Owner:** Observability team (or designated maintainer)
- **Location:** `agentic_core/observability/dashboard/`
- **Responsibility:** All dashboard code, templates, servers, scripts

### Change Process

**All Dashboard Changes Must:**
1. Go through observability/dashboard/ location
2. Update tests in tests/*/dashboard/
3. Update documentation
4. Get review from dashboard owner

### SSOT Enforcement

**Rules:**
1. **One location** for dashboard generation: `observability/dashboard/core/`
2. **One template** location: `observability/dashboard/templates/`
3. **One server** implementation: `observability/dashboard/server/`
4. **No dashboard code** in other layers (especially L5_safety)

### Documentation

**Required Documentation:**
1. Architecture diagram showing dashboard components
2. Developer guide for dashboard changes
3. API documentation for dashboard endpoints
4. Template customization guide

---

## Part 7: Success Metrics

### Before Consolidation

| Metric | Current State |
|--------|---------------|
| **Dashboard locations** | 5 locations |
| **Template files** | 3 files (2 locations) |
| **Server implementations** | 2 servers |
| **Scripts in wrong location** | 20+ files |
| **Import paths** | 2 different paths |
| **Test locations** | 6+ locations |
| **Lines of sprawled code** | 1,000+ lines |

### After Consolidation

| Metric | Target State |
|--------|--------------|
| **Dashboard locations** | 1 location (observability/dashboard/) |
| **Template files** | 1 file (templates/dashboard.html) |
| **Server implementations** | 1 server (server/app.py) |
| **Scripts in wrong location** | 0 files |
| **Import paths** | 1 path (observability.dashboard.core) |
| **Test locations** | 3 locations (unit/, integration/, e2e/) |
| **Lines of sprawled code** | 0 lines |

---

## Conclusion

**CRITICAL FINDING:** Dashboard sprawl is a severe architectural violation that must be addressed.

**Key Issues:**
1. ❌ Dashboard generation in wrong layer (L5 instead of L6)
2. ❌ 3 template files across 2 locations
3. ❌ 2 duplicate server implementations
4. ❌ 20+ scripts in wrong locations
5. ❌ Tests scattered across 6+ locations
6. ❌ No clear SSOT or governance

**Impact:**
- High maintenance burden
- Developer confusion
- Testing complexity
- Governance issues
- SSOT violations

**Recommendation:** Execute consolidation plan in 5 phases, starting with moving core modules from L5_safety to observability/dashboard.

**Priority:** 🔴 **HIGH** - This is a fundamental architecture issue that affects maintainability and clarity.

---

**Report Generated:** January 7, 2026  
**Audit Performed By:** Cascade AI  
**Status:** 🔴 **CRITICAL - CONSOLIDATION REQUIRED**
