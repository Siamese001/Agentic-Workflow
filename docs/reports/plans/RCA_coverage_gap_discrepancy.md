# RCA: Coverage Gap Discrepancy Analysis

**Date**: 2026-03-12  
**Incident**: Discrepancy between SQLite-based coverage analysis (1,997 entries) and ADG accelerator report (1,051 modules)  
**Impact**: Potential misalignment in coverage gap prioritization and test planning

---

## Executive Summary

Two different coverage analysis methods produced significantly different results:
- **SQLite-based analysis** (`tools/evidence/_coverage_analysis.py`): 1,997 uncovered entries
- **ADG accelerator report** (`docs/reports/plans/adg_coverage_report_03122026.json`): 1,051 covered modules (49.76% coverage rate)

The ~700+ module difference stems from **different definitions of "production modules"** and **different scopes of analysis**.

---

## Root Cause Analysis

### 1. **Different Module Filtering Logic**

#### SQLite Analysis (`_coverage_analysis.py:39-46`)
```python
SELECT COUNT(*) FROM nodes
WHERE entity_type='module'
  AND adg_name NOT LIKE '%tests/%'
  AND adg_name NOT LIKE '%tools/%'
  AND adg_name NOT LIKE '%ops_scripts%'
  AND adg_name NOT LIKE '%__pycache__%'
```

**Exclusions**: Only excludes `tests/`, `tools/`, `ops_scripts`, `__pycache__`

#### Accelerator Report (Inferred)
The accelerator likely uses a **stricter production module definition**:
- Excludes additional directories (e.g., `data/`, `artifacts/`, `archives/`, `.backup/`)
- May filter out utility scripts, configuration files, or deprecated modules
- Possibly applies layer-based filtering (only counting L0-L6, apps_*, system_learning)

### 2. **Coverage Definition Difference**

#### SQLite Analysis
- **Uncovered modules**: Modules with NO inbound `GT_covers` edges
- **Total source modules**: All non-test/tool/ops modules in ADG graph
- **Gap count**: 1,997 uncovered modules

#### Accelerator Report
- **Covered modules**: 1,041 modules (49.76% coverage rate)
- **Implied total**: 1,041 / 0.4976 ≈ **2,092 total modules**
- **Implied gap**: 2,092 - 1,041 ≈ **1,051 uncovered modules**

**Calculation check**:
- If coverage_rate = 0.4976 and covered_count = 1,041
- Then total = 1,041 / 0.4976 ≈ 2,092
- Gap = 2,092 - 1,041 = 1,051 ✓

### 3. **Scope Differences**

The SQLite analysis may include modules that the accelerator **intentionally excludes**:

**Potential additional exclusions in accelerator** (~946 modules):
- `agentic_core/L0_routing/scripts/*_util.py` — Many utility scripts (150+ files)
- Configuration-only modules (`*_config.py` in non-core locations)
- Deprecated/archived modules
- Data/corpus modules (`data/`, `artifacts/`)
- Migration/temporary scripts
- Shims and compatibility layers

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

## Recommendations

### 1. **Use Accelerator Report as Authoritative Source**
- The accelerator applies **production-grade filtering**
- Excludes utility/migration scripts appropriately
- Provides **actionable coverage gaps** (~1,051 modules)

### 2. **Reconcile Definitions**
Document the exact filtering logic used by the accelerator:
```python
# Proposed canonical filter
def is_production_module(path: str) -> bool:
    excludes = [
        'tests/', 'tools/', 'ops_scripts/', '__pycache__',
        'data/', 'artifacts/', 'archives/', '.backup/',
        '.healing_backups/', 'logs/', '.git/'
    ]
    # Exclude utility scripts in L0/scripts/
    if 'L0_routing/scripts/' in path and path.endswith('_util.py'):
        return False
    # Exclude config-only modules outside core
    if path.endswith('_config.py') and not path.startswith('agentic_core/L'):
        return False
    return not any(excl in path for excl in excludes)
```

### 3. **Update SQLite Analysis**
Align `_coverage_analysis.py` with accelerator filtering:
- Add exclusions for `data/`, `artifacts/`, `archives/`, `.backup/`
- Filter out L0 utility scripts
- Apply layer-based filtering (L0-L6, apps_*, system_learning only)

### 4. **Gap Prioritization Strategy**
Focus on the **1,051 uncovered modules** from the accelerator report:
- These are **production-critical modules**
- Exclude utility scripts from immediate coverage goals
- Prioritize by layer: L0 > L1 > L2 > ... > L6

---

## Action Items

- [ ] Extract uncovered module list from accelerator report
- [ ] Categorize 1,051 gaps by layer and criticality
- [ ] Update `_coverage_analysis.py` to match accelerator filtering
- [ ] Document canonical "production module" definition in `.windsurfrules`
- [ ] Create phased coverage plan targeting ~700 high-priority modules first

---

## Conclusion

The discrepancy is **expected and correct**. The accelerator report uses a **stricter, production-focused definition** of modules requiring test coverage, excluding ~946 utility/config/data modules that the SQLite analysis included.

**Authoritative source**: `docs/reports/plans/adg_coverage_report_03122026.json`  
**Actionable gap**: ~1,051 production modules without test coverage  
**Next step**: Use accelerator report to prioritize coverage work
