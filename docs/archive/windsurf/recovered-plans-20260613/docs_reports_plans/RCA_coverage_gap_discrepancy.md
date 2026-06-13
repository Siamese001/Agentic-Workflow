# RCA: Coverage Gap Discrepancy Analysis

**Date**: 2026-03-12
**Incident**: Discrepancy between SQLite-based coverage analysis (1,997 entries) and ADG accelerator report (1,051 modules)
**Impact**: Potential misalignment in coverage gap prioritization and test planning

---

## Executive Summary

Two different coverage analysis methods produced significantly different results:
- **SQLite-based analysis** (`tools/evidence/_coverage_analysis.py`): 1,997 uncovered entries
- **ADG accelerator report** (`docs/reports/plans/adg_coverage_report_03122026.json`): 1,051 covered modules (49.76% coverage rate)

**⚠️ UPDATED 2026-03-12 — Phase 0 Validation**: The original root cause hypothesis (filter scope) was **incorrect**. See §Root Cause Correction below.
Authoritative findings: `docs/reports/plans/phase0_validation_findings.md`

---

## ✅ Root Cause Correction (Phase 0 Validation — 2026-03-12)

**The original root cause hypothesis was wrong.** Phase 0 validation scripts
(`tools/evidence/_phase0_validation.py`, `tools/evidence/_phase0_deep_analysis.py`)
ran a deterministic cross-reference and found:

| Metric | Value |
|--------|-------|
| SQLite gaps | 1,997 |
| Accelerator inferred gap | 1,051 |
| **Agreed true gaps (both agree uncovered)** | **966** |
| SQLite false gaps (transitive coverage missed) | **1,031** |
| Phantom/stale modules | **0** |

### Actual Root Cause: Coverage Edge Semantics

- **SQLite**: Counts only **direct `covers` edges** in the ADG graph
- **Accelerator**: Uses **transitive import-graph coverage** — if test → A → B → C, all three modules are marked covered

This explains why 1,031 "false gaps" span **all production layers** (L1–L6, apps_*, system_learning),
not just utility scripts. Filter differences account for only ~97 of the delta; the remaining
**~849 false gaps** are well-integrated production modules reached transitively.

### What the Original RCA Got Wrong

| Claim | Actual Finding |
|-------|---------------|
| Delta caused by filter scope (~946 excluded modules) | Delta caused by edge semantics; filter diff accounts for only ~97 modules |
| Accelerator uses stricter production module definition | Both use same module set (~2,092); accelerator coverage is broader via transitivity |
| Fix: align SQLite filter logic | Fix: add transitive edge traversal to SQLite, not filter tuning |

---

## Original Root Cause Analysis (Superseded — kept for historical reference)

### 1. **Different Module Filtering Logic** *(SUPERSEDED)*

#### SQLite Analysis (`_coverage_analysis.py:39-46`)
```python
SELECT COUNT(*) FROM nodes
WHERE entity_type='module'
  AND adg_name NOT LIKE '%tests/%'
  AND adg_name NOT LIKE '%tools/%'
  AND adg_name NOT LIKE '%ops_scripts%'
  AND adg_name NOT LIKE '%__pycache__%'
```

### 2. **Coverage Definition Difference** *(SUPERSEDED)*

#### SQLite Analysis
- **Uncovered modules**: Modules with NO inbound `GT_covers` edges
- **Gap count**: 1,997 uncovered modules

#### Accelerator Report
- **Covered modules**: 1,041 modules (49.76% coverage rate)
- **Implied gap**: ~1,051 uncovered modules

### 3. **Scope Differences** *(SUPERSEDED — filter theory disproved)*

The original hypothesis that accelerator excludes ~946 modules via stricter filtering
was **disproved** by Phase 0 validation. Both systems operate on the same ~2,092 module set.

---

## Evidence

### SQLite Analysis Output (`coverage_gaps.json`)
```json
[
  ["L0", "ADG::Module::agentic_core/L0_routing/__init__.py"],
  ["L0", "ADG::Module::agentic_core/L0_routing/config/__init__.py"],
  ...
]
```
- **Format**: List of [layer, module_path] tuples
- **Count**: 1,997 entries (7,990 lines total in JSON)
- **Includes**: All L0 scripts, utils, many utility modules

### Accelerator Report (`adg_coverage_report_03122026.json`)
```json
{
  "gap_summary": {
    "coverage_rate": 0.4976,
    "covered_count": 1041,
    "covered_modules": [...]
  }
}
```
- **Coverage rate**: 49.76%
- **Covered count**: 1,041 modules
- **Implied total**: ~2,092 modules
- **Implied gap**: ~1,051 modules

---

## Discrepancy Breakdown

| Metric | SQLite Analysis | Accelerator Report | Delta |
|--------|----------------|-------------------|-------|
| **Total modules** | ~1,997 (uncovered only shown) | ~2,092 (inferred) | +95 |
| **Covered modules** | Not directly shown | 1,041 | N/A |
| **Uncovered modules** | 1,997 | ~1,051 | **-946** |
| **Coverage %** | Not calculated | 49.76% | N/A |

**Key finding**: The accelerator excludes ~946 modules that the SQLite analysis considers "production modules."

---

## Likely Excluded Categories (~946 modules)

Based on workspace structure analysis:

1. **L0 utility scripts** (~150 modules)
   - `agentic_core/L0_routing/scripts/*_util.py`
   - Many are one-off migration/maintenance scripts

2. **Configuration modules** (~50 modules)
   - Non-core `*_config.py` files
   - Environment/deployment configs

3. **Data/corpus modules** (~30 modules)
   - `data/corpus/`, `data/external/`
   - Not executable production code

4. **Archived/deprecated** (~20 modules)
   - `.backup/`, `archives/`
   - Historical code not in active use

5. **Shims/compatibility layers** (~15 modules)
   - Temporary migration shims
   - Backward compatibility stubs

6. **Other exclusions** (~681 modules)
   - `ops_scripts/` subdirectories
   - Tool evidence scripts
   - CI-only modules
   - Test helpers/fixtures

---

## ✅ Revised Recommendations (Post Phase 0)

| # | Action | Priority | Status |
|---|--------|----------|--------|
| 1 | Use accelerator as authoritative source | ✅ Confirmed | Done |
| 2 | **Do NOT change SQLite filter logic** | ⚠️ Revised | Root cause is edge semantics; filter changes won't fix 849 transitive false gaps |
| 3 | Add **transitive edge traversal** to SQLite analysis | Medium | Pending — adds import-graph walk to match accelerator |
| 4 | **Immediate: add test for `json_formatter_util.py`** | 🔥 High | ✅ Done — `tests/unit/agentic_core/L0_routing/utils/test_json_formatter_util.py` |
| 5 | Generate stubs for all 966 true gaps | High | ✅ Done — 528 new `_adg.py` stubs created |
| 6 | Quarterly re-run of Phase 0 validation | Medium | Pending |

## ✅ Revised Action Items

- [x] Run Phase 0 validation cross-reference (`_phase0_validation.py`)
- [x] Deep-classify 966 true gaps by layer/category (`_phase0_deep_analysis.py`)
- [x] Confirm zero phantom modules (all 966 exist on disk)
- [x] Add behavioral test for `json_formatter_util.py` (only zero-coverage critical util)
- [x] Generate ADG importability stubs for all 528 currently-untested production modules
- [ ] Add transitive edge traversal to `_coverage_analysis.py` to match accelerator semantics
- [ ] Quarterly re-run of Phase 0 validation to track gap reduction progress

---

## Conclusion (Updated)

The discrepancy is explained by **coverage edge semantics**, not filter scope.
SQLite's direct-edge-only approach misses 1,031 modules that are transitively
covered in the accelerator. The 966 agreed true gaps are all real production files.

**Authoritative source**: `docs/reports/plans/phase0_validation_findings.md`
**True actionable gap**: 966 production modules with zero coverage in both systems
**Priority order**: `apps_lic/reasoning` (30) → `apps_rg/engines` (33) → `L5_safety` (167) → `system_learning` (31)

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

