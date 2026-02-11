# Architectural Anomalies Report — apps_* Folders

**Generated:** 2026-02-07
**Scope:** `apps_rg/` and `apps_lic/` directories
**Analyzer:** Deep Static Analysis with import/inheritance/content heuristics

---

## 1. Executive Summary

### File Inventory

| Territory | .py Files | Role |
|-----------|-----------|------|
| **apps_rg** | 167 | Resume Generation Application |
| **apps_lic** | 141 | LinkedIn Canonical Application |
| **Total** | 308 | |

### Distribution by Subfolder (apps_rg)

| Subfolder | Files | % |
|-----------|-------|---|
| engines/ | 78 | 46.7% |
| shared/ | 43 | 25.7% |
| scripts/ | 10 | 6.0% |
| types/ | 7 | 4.2% |
| logic_nodes/ | 6 | 3.6% |
| domain/ | 5 | 3.0% |
| validation/ | 5 | 3.0% |
| reasoning/ | 4 | 2.4% |
| config/ | 3 | 1.8% |
| utils/ | 2 | 1.2% |
| asset_library/ | 1 | 0.6% |
| system_flow/ | 1 | 0.6% |
| core/ | 1 | 0.6% |

### Distribution by Subfolder (apps_lic)

| Subfolder | Files | % |
|-----------|-------|---|
| shared/ | 58 | 41.1% |
| engines/ | 47 | 33.3% |
| domain/ | 15 | 10.6% |
| scripts/ | 5 | 3.5% |
| types/ | 5 | 3.5% |
| validation/ | 3 | 2.1% |
| logic_nodes/ | 2 | 1.4% |
| config/ | 1 | 0.7% |
| reasoning/ | 1 | 0.7% |
| utils/ | 1 | 0.7% |
| asset_library/ | 1 | 0.7% |
| system_flow/ | 1 | 0.7% |
| tools/ | 1 | 0.7% |

### LCD Compliance

| Territory | config/ | types/ | reasoning/ | utils/ | LCD Score |
|-----------|:-------:|:------:|:----------:|:------:|:---------:|
| apps_rg | ✅ (3) | ✅ (7) | ✅ (4) | ✅ (2) | 4/4 |
| apps_lic | ✅ (1) | ✅ (5) | ✅ (1) | ✅ (1) | 4/4 |

### Health Score

| Category | Count | % |
|----------|-------|---|
| **Correctly placed** | ~278 | ~90.3% |
| **Agent classes outside reasoning/** | 12 | 3.9% |
| **Agent classes in _types.py files** | 4 | 1.3% |
| **PascalCase/test files in scripts/** | 14 | 4.5% |
| **Overall Health Score** | | **~90%** |

---

## 2. Functional Mismatches (High Priority)

### 2.1 Subprocess Imports

**No subprocess imports found in apps_rg or apps_lic.** ✅

This is correct — apps_* folders are application logic, not execution infrastructure.

### 2.2 Agent Classes Outside reasoning/ (apps_rg)

| File Path | Current Subfolder | Should Be |
|-----------|------------------|-----------|
| `apps_rg/engines/utils/ATSCompatibilityAgent.py` | engines/utils/ | reasoning/ |
| `apps_rg/engines/utils/BrandComplianceAgent.py` | engines/utils/ | reasoning/ |
| `apps_rg/engines/utils/CampaignPlannerAgent.py` | engines/utils/ | reasoning/ |
| `apps_rg/engines/utils/ContentQualityAgent.py` | engines/utils/ | reasoning/ |
| `apps_rg/engines/utils/ContentStrategyAgent.py` | engines/utils/ | reasoning/ |
| `apps_rg/engines/utils/FactCheckAgent.py` | engines/utils/ | reasoning/ |
| `apps_rg/engines/utils/ProactiveAgent.py` | engines/utils/ | reasoning/ |
| `apps_rg/engines/utils/RgReflectionAgent.py` | engines/utils/ | reasoning/ |
| `apps_rg/engines/utils/RgStrategicPlannerAgent.py` | engines/utils/ | reasoning/ |
| `apps_rg/engines/utils/RgTemplateOptimizerAgent.py` | engines/utils/ | reasoning/ |
| `apps_rg/engines/utils/SectionBalanceAgent.py` | engines/utils/ | reasoning/ |

**Verdict:** 11 Agent classes in `apps_rg/engines/utils/` should be moved to `apps_rg/reasoning/`.

### 2.3 Agent Classes Embedded in _types.py Files

| File Path | Agent Class | Action |
|-----------|-------------|--------|
| `apps_rg/types/gap_closure_architect_agent_types.py` | `GapClosureArchitectAgent` | Split: extract Agent to reasoning/ |
| `apps_lic/engines/competitor_recon_agent_types.py` | Agent class | Split: extract Agent to reasoning/ |
| `apps_lic/engines/stack_modernization_agent_types.py` | Agent class | Split: extract Agent to reasoning/ |
| `apps_lic/types/app_content_validator_agent_types.py` | Agent class | Split: extract Agent to reasoning/ |

**Verdict:** 4 files with compound suffix `_agent_types.py` contain both types AND Agent classes. These should be split.

### 2.4 PascalCase Files in scripts/ (Not Actually PascalCase)

Upon inspection, these files are snake_case but were flagged due to regex matching. Actual violations:

| File Path | Issue | Action |
|-----------|-------|--------|
| `apps_rg/scripts/test_engine.py` | test_* in scripts/ | Move to tests/ |
| `apps_rg/scripts/test_input.py` | test_* in scripts/ | Move to tests/ |
| `apps_rg/scripts/test_run_grand_unification_tests.py` | test_* in scripts/ | Move to tests/ |

**Verdict:** 3 test files in `apps_rg/scripts/` should be moved to `tests/`.

---

## 3. Recommendations (Prioritized)

### P0 — Critical

1. **Move 11 Agent classes from `apps_rg/engines/utils/` to `apps_rg/reasoning/`**
   - ATSCompatibilityAgent.py
   - BrandComplianceAgent.py
   - CampaignPlannerAgent.py
   - ContentQualityAgent.py
   - ContentStrategyAgent.py
   - FactCheckAgent.py
   - ProactiveAgent.py
   - RgReflectionAgent.py
   - RgStrategicPlannerAgent.py
   - RgTemplateOptimizerAgent.py
   - SectionBalanceAgent.py

### P1 — High

2. **Split 4 compound `_agent_types.py` files**
   - Extract Agent classes to reasoning/
   - Keep type definitions in types/
   - Rename files to remove `_agent` prefix

3. **Move 3 test files from `apps_rg/scripts/` to `tests/`**
   - test_engine.py
   - test_input.py
   - test_run_grand_unification_tests.py

### P2 — Medium

4. **Consolidate apps_rg/core/** — Only 1 file remains (`__init__.py`). Consider removing empty folder.

5. **Balance apps_lic/reasoning/** — Only 1 file. Consider moving more Agent classes here.

---

## 4. Structural Comparison (apps_rg vs apps_lic)

| Metric | apps_rg | apps_lic | Parity |
|--------|---------|----------|--------|
| Total files | 167 | 141 | ✅ Similar |
| engines/ | 78 (47%) | 47 (33%) | ⚠️ apps_rg heavier |
| shared/ | 43 (26%) | 58 (41%) | ⚠️ apps_lic heavier |
| reasoning/ | 4 (2%) | 1 (1%) | ⚠️ Both low |
| types/ | 7 (4%) | 5 (4%) | ✅ Balanced |
| config/ | 3 (2%) | 1 (1%) | ✅ Similar |
| validation/ | 5 (3%) | 3 (2%) | ✅ Similar |

**Key Insight:** Both apps have very few files in `reasoning/` (4 and 1 respectively), while having many Agent classes scattered in `engines/utils/`. This suggests the LCD refactoring is incomplete — Agent classes should be consolidated in `reasoning/`.

---

## 5. Action Items Summary

| Priority | Action | Files Affected |
|----------|--------|----------------|
| P0 | Move Agent classes to reasoning/ | 11 |
| P1 | Split _agent_types.py files | 4 |
| P1 | Move test_* from scripts/ to tests/ | 3 |
| P2 | Clean up empty apps_rg/core/ | 1 |
| **Total** | | **19 files** |

---

*Report generated by architectural analysis on apps_* folders.*
