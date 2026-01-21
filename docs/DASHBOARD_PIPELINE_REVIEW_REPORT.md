# Dashboard Pipeline Review Report
## End-to-End Process Analysis: Agent Discovery to Visual Inspection

**Date:** January 20, 2026
**Scope:** Complete dashboard pipeline from agent discovery through testing and visual validation

---

## Executive Summary

The dashboard pipeline has evolved organically over time, resulting in significant complexity, redundancy, and maintenance burden. This report identifies **46+ dashboard-related Python scripts**, **7 separate test phases** with **487+ tests**, and multiple deprecated/duplicate scripts that should be consolidated or removed.

**Key Findings:**
- **Script Proliferation:** 46 dashboard-related Python scripts in `L0_maintenance/scripts` alone
- **Test Fragmentation:** 7 test phases scattered across 4 different directories
- **Deprecated Code:** At least 4 deprecated regeneration scripts still present
- **SSOT Duplication:** Dashboard SSOT definitions exist in 2 locations
- **Verification Redundancy:** 6+ verification scripts with overlapping functionality

---

## 1. Current Pipeline Architecture

### 1.1 Data Flow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CURRENT PIPELINE (Complex)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐      │
│  │ Agent Discovery  │───▶│ Dashboard SSOT   │───▶│ Dashboard Gen    │      │
│  │ full_agent_      │    │ dashboard_ssot   │    │ regenerate_      │      │
│  │ discovery.py     │    │ _definitions.py  │    │ dashboard_full.py│      │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘      │
│           │                      │                        │                 │
│           ▼                      ▼                        ▼                 │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐      │
│  │ agent_discovery_ │    │ dashboard_ssot   │    │ dashboard_data.js│      │
│  │ full.json        │    │ .yaml            │    │ agent_data.js    │      │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘      │
│                                                           │                 │
│                                                           ▼                 │
│                                                  ┌──────────────────┐      │
│                                                  │ autonomy_        │      │
│                                                  │ dashboard.html   │      │
│                                                  └──────────────────┘      │
│                                                           │                 │
│                                                           ▼                 │
│                                            ┌─────────────────────────┐     │
│                                            │   7 TEST PHASES         │     │
│                                            │   (487+ tests)          │     │
│                                            └─────────────────────────┘     │
│                                                           │                 │
│                                                           ▼                 │
│                                            ┌─────────────────────────┐     │
│                                            │   Playwright Visual     │     │
│                                            │   Inspection            │     │
│                                            └─────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Agent Discovery | `scripts/full_agent_discovery.py` | AST-based agent scanning (1838 lines) |
| Territory SSOT | `L0_maintenance/scripts/territory_ssot_definitions.py` | Territory name constants (561 lines) |
| Dashboard SSOT | `L5_safety/validators/dashboard_ssot_definitions.py` | Metric calculations (617 lines) |
| YAML Config | `L0_maintenance/scripts/config/dashboard_ssot.yaml` | Source of truth for constants |
| Dashboard Generator | `L0_maintenance/scripts/regenerate_dashboard_full.py` | Main regeneration script (465 lines) |
| Dashboard HTML | `L6_observability/dashboards/autonomy_dashboard.html` | 2.6MB HTML file |

---

## 2. Identified Issues

### 2.1 Script Proliferation (CRITICAL)

**46 dashboard-related Python scripts identified:**

| Category | Count | Examples |
|----------|-------|----------|
| Regeneration Scripts | 6 | `regenerate_dashboard_full.py`, `regenerate_dashboard_data.py`, `regenerate_dashboard_from_discovery.py` (deprecated), `regenerate_dashboard_complete.py` (deprecated), `generate_modular_dashboard_data.py` (deprecated) |
| Verification Scripts | 8 | `verify_dashboard_simple.py`, `verify_dashboard_state.py`, `verify_dashboard_deployment.py`, `verify_dashboard_browser_state.py`, `verify_dashboard_columns.py`, `verify_dashboard_updates.py`, `verify_dashboard_e2e.py`, `verify_dashboard_e2e_playwright.py` |
| Test Scripts | 7 | `test_dashboard_end_to_end.py`, `test_dashboard_playwright_visual.py`, `test_dashboard_drilldown.py`, `test_dashboard_generation.py`, `test_dashboard_snapshot_regression.py`, `test_dashboard_visual.py` |
| Debug Scripts | 5 | `debug_dashboard_playwright.py`, `debug_dashboard_rendering.py`, `diagnose_dashboard_live.py`, `diagnose_user_dashboard_view.py`, `inspect_dashboard_browser.py` |
| Audit Scripts | 4 | `audit_dashboard_naming.py`, `audit_dashboard_ssot.py`, `audit_dashboard_ssot_flow.py`, `dashboard_qa_deep_audit.py` |
| Utility Scripts | 16+ | Various check, fix, trace, validate scripts |

### 2.2 Test Suite Fragmentation (HIGH)

**7 test phases across 4 directories:**

| Phase | Location | Tests | Purpose |
|-------|----------|-------|---------|
| Phase 1-2 | `agentic_core/observability/` | 88 | Telemetry tests |
| Phase 3-4 | `L0_maintenance/scripts/` | 69 | Frontend component tests |
| Phase 5 | `L0_maintenance/scripts/` | 66 | UI layout tests |
| Phase 6 | `L2_execution/ToolRegistry/` | 152 | Integration tests |
| Phase 7 | `L1_cognition/intent_analysis/` | 112 | Documentation tests |
| E2E | `L5_safety/validators/` | 34 | End-to-end tests |
| Playwright | `L0_maintenance/scripts/` | 6 | Visual validation |

**Issues:**
- Tests scattered across unrelated directories (L1, L2, L5, L6)
- No unified test runner
- Duplicate test coverage between phases
- Phase numbering implies sequence but tests can run independently

### 2.3 SSOT Definition Duplication (MEDIUM)

**Two SSOT definition files:**
1. `L5_safety/validators/dashboard_ssot_definitions.py` - Primary (617 lines)
2. `L0_maintenance/scripts/territory_ssot_definitions.py` - Territory names (561 lines)

**Plus YAML source:**
- `L0_maintenance/scripts/config/dashboard_ssot.yaml` - Generates Python constants

**Issues:**
- Territory names defined in both YAML and Python
- Import paths inconsistent across consumers
- Generator script (`generate_dashboard_ssot.py`) adds another layer

### 2.4 Deprecated Scripts Still Present (MEDIUM)

| Script | Status | Replacement |
|--------|--------|-------------|
| `regenerate_dashboard_from_discovery.py` | DEPRECATED | `regenerate_dashboard_full.py` |
| `regenerate_dashboard_complete.py` | DEPRECATED (empty) | `regenerate_dashboard_full.py` |
| `generate_modular_dashboard_data.py` | DEPRECATED | `regenerate_dashboard_full.py` |
| `generate_dashboard_ssot_WRAPPER.py` | DEPRECATED | Direct use of `generate_dashboard_ssot.py` |

### 2.5 Verification Script Redundancy (MEDIUM)

**6 verification scripts with overlapping functionality:**

| Script | Checks |
|--------|--------|
| `verify_dashboard_simple.py` | HTML sections, containers, JS includes |
| `verify_dashboard_state.py` | File existence, Plotly loading, data injection |
| `verify_dashboard_deployment.py` | Deployment readiness |
| `verify_dashboard_browser_state.py` | Browser-specific state |
| `verify_dashboard_columns.py` | Column structure |
| `verify_dashboard_updates.py` | Update verification |

### 2.6 Large HTML File (LOW)

- `autonomy_dashboard.html` is **2.6MB**
- Contains embedded data that could be externalized
- Difficult to diff/review changes

---

## 3. Recommendations

### 3.1 Consolidate Regeneration Scripts (HIGH PRIORITY)

**Current State:** 6 regeneration scripts (3 deprecated)

**Target State:** 1 canonical script

**Implementation Plan:**
1. Archive deprecated scripts to `archives/deprecated_dashboard/`
2. Consolidate `regenerate_dashboard_data.py` into `regenerate_dashboard_full.py`
3. Create single entry point: `python scripts/regenerate_dashboard.py`

**Effort:** 2-4 hours

### 3.2 Unify Test Suite (HIGH PRIORITY)

**Current State:** 7 phases, 487+ tests, 4 directories

**Target State:** Single test directory with unified runner

**Implementation Plan:**
1. Create `tests/dashboard/` directory structure:
   ```
   tests/dashboard/
   ├── __init__.py
   ├── conftest.py
   ├── test_telemetry.py      # Phase 1-2
   ├── test_frontend.py       # Phase 3-4
   ├── test_ui_layout.py      # Phase 5
   ├── test_integration.py    # Phase 6
   ├── test_documentation.py  # Phase 7
   ├── test_e2e.py            # E2E
   └── test_visual.py         # Playwright
   ```
2. Create unified test runner: `python -m pytest tests/dashboard/`
3. Eliminate duplicate test coverage
4. Move test files from scattered locations

**Effort:** 4-8 hours

### 3.3 Consolidate SSOT Definitions (MEDIUM PRIORITY)

**Current State:** 2 Python files + 1 YAML file

**Target State:** Single YAML source with auto-generated Python

**Implementation Plan:**
1. Merge `territory_ssot_definitions.py` content into `dashboard_ssot.yaml`
2. Extend `generate_dashboard_ssot.py` to generate territory constants
3. Single import path: `from agentic_core.config.dashboard_ssot import *`

**Effort:** 2-4 hours

### 3.4 Archive Deprecated Scripts (MEDIUM PRIORITY)

**Scripts to Archive:**
- `regenerate_dashboard_from_discovery.py`
- `regenerate_dashboard_complete.py`
- `generate_modular_dashboard_data.py`
- `generate_dashboard_ssot_WRAPPER.py`

**Implementation Plan:**
1. Move to `archives/deprecated_dashboard/`
2. Update any references
3. Add README explaining deprecation

**Effort:** 1 hour

### 3.5 Consolidate Verification Scripts (MEDIUM PRIORITY)

**Current State:** 6 verification scripts

**Target State:** 1 comprehensive verification script

**Implementation Plan:**
1. Create `scripts/verify_dashboard.py` with subcommands:
   - `--quick` - Fast checks (file existence, basic structure)
   - `--full` - All checks including browser state
   - `--deployment` - Pre-deployment validation
2. Archive individual verification scripts

**Effort:** 2-4 hours

### 3.6 Externalize Dashboard Data (LOW PRIORITY)

**Current State:** 2.6MB HTML with embedded data

**Target State:** Modular data files (already partially done)

**Implementation Plan:**
1. Ensure all data in `dashboards/data/` directory
2. HTML loads data via script tags
3. Reduces HTML to ~100KB

**Effort:** 2-4 hours (partially complete)

---

## 4. Detailed Implementation Plan

### Phase 1: Cleanup (Week 1)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Archive 4 deprecated regeneration scripts | High | 1h | - |
| Delete `__pycache__` for deprecated scripts | High | 0.5h | - |
| Update imports in consuming scripts | High | 1h | - |
| Document canonical scripts in README | Medium | 1h | - |

### Phase 2: Consolidation (Week 2)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Merge regeneration scripts | High | 3h | - |
| Consolidate verification scripts | Medium | 3h | - |
| Merge SSOT definitions | Medium | 3h | - |
| Update all import paths | Medium | 2h | - |

### Phase 3: Test Unification (Week 3)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Create `tests/dashboard/` structure | High | 1h | - |
| Migrate Phase 1-2 tests | High | 1h | - |
| Migrate Phase 3-4 tests | High | 1h | - |
| Migrate Phase 5-7 tests | High | 2h | - |
| Create unified test runner | High | 1h | - |
| Eliminate duplicate tests | Medium | 2h | - |

### Phase 4: Documentation (Week 4)

| Task | Priority | Effort | Owner |
|------|----------|--------|-------|
| Update DASHBOARD_META_LEARNING_GUIDE.md | Medium | 2h | - |
| Create DASHBOARD_DEVELOPER_GUIDE.md | Medium | 3h | - |
| Update memory with new structure | Low | 0.5h | - |

---

## 5. Expected Outcomes

### Before Consolidation

| Metric | Current |
|--------|---------|
| Dashboard Python scripts | 46 |
| Test phases | 7 |
| Test directories | 4 |
| SSOT definition files | 3 |
| Verification scripts | 6 |
| Deprecated scripts | 4 |

### After Consolidation

| Metric | Target | Reduction |
|--------|--------|-----------|
| Dashboard Python scripts | ~15 | 67% |
| Test phases | 1 (unified) | 86% |
| Test directories | 1 | 75% |
| SSOT definition files | 1 | 67% |
| Verification scripts | 1 | 83% |
| Deprecated scripts | 0 | 100% |

### Benefits

1. **Reduced Cognitive Load:** Single entry points for regeneration, testing, verification
2. **Faster Onboarding:** Clear documentation and structure
3. **Easier Maintenance:** Fewer files to update when making changes
4. **Better Test Coverage:** Unified test suite with clear coverage metrics
5. **Reduced CI/CD Time:** Single test run instead of 7 phases

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing workflows | Medium | High | Gradual migration with aliases |
| Missing test coverage during migration | Low | Medium | Run both old and new tests in parallel |
| Import path changes breaking consumers | Medium | Medium | Provide compatibility shims |
| Loss of specialized functionality | Low | Low | Review each script before archiving |

---

## 7. Appendix: Complete Script Inventory

### A. Regeneration Scripts (6)

| Script | Status | Lines | Purpose |
|--------|--------|-------|---------|
| `regenerate_dashboard_full.py` | **CANONICAL** | 465 | Main regeneration |
| `regenerate_dashboard_data.py` | Active | 176 | Data-only regeneration |
| `regenerate_dashboard_from_discovery.py` | DEPRECATED | 121 | Legacy |
| `regenerate_dashboard_complete.py` | DEPRECATED | 12 | Empty stub |
| `generate_modular_dashboard_data.py` | DEPRECATED | 422 | Legacy modular |
| `generate_dashboard_ssot.py` | Active | 428 | YAML to Python generator |

### B. Test Scripts (7)

| Script | Location | Tests |
|--------|----------|-------|
| `test_phase1_phase2_telemetry.py` | `agentic_core/observability/` | 88 |
| `test_phase3_phase4_frontend.py` | `L0_maintenance/scripts/` | 69 |
| `test_phase5_ui_layout.py` | `L0_maintenance/scripts/` | 66 |
| `test_phase6_integration.py` | `L2_execution/ToolRegistry/` | 152 |
| `test_phase7_documentation.py` | `L1_cognition/intent_analysis/` | 112 |
| `test_dashboard_end_to_end.py` | `L5_safety/validators/` | 34 |
| `test_dashboard_playwright_visual.py` | `L0_maintenance/scripts/` | 6 |

### C. Verification Scripts (6)

| Script | Lines | Purpose |
|--------|-------|---------|
| `verify_dashboard_simple.py` | 137 | Basic HTML checks |
| `verify_dashboard_state.py` | 132 | File state verification |
| `verify_dashboard_deployment.py` | ~200 | Deployment readiness |
| `verify_dashboard_browser_state.py` | ~150 | Browser state |
| `verify_dashboard_columns.py` | ~100 | Column structure |
| `verify_dashboard_updates.py` | ~100 | Update verification |

---

## 8. Conclusion

The dashboard pipeline has grown organically to address various needs but now suffers from significant complexity and redundancy. The recommended consolidation will reduce the number of scripts by ~67%, unify testing into a single suite, and establish clear entry points for all dashboard operations.

**Recommended Priority Order:**
1. Archive deprecated scripts (immediate, low risk)
2. Consolidate regeneration scripts (high impact)
3. Unify test suite (high impact, moderate effort)
4. Consolidate verification scripts (medium impact)
5. Merge SSOT definitions (medium impact)

**Total Estimated Effort:** 20-30 hours over 4 weeks

---

*Report generated by Cascade - January 20, 2026*
