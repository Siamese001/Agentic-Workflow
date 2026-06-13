# ADG-Backed Territory Simplification Analysis

**Date:** 2026-03-11
**Method:** AST consumer counting + ADG import/violation graph
**Scope:** All `.py` files across `agentic_core`, `apps_*`, `tests`, `ops_scripts`, `tools`, `system_learning`

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Summary: 7 Independent Simplifications Found

| # | Finding | Impact | Effort |
|---|---------|--------|--------|
| 1 | Three redundant exclusion sets with 13 overlapping entries; two incorrectly exclude real project directories | 315 consumers confused | Medium |
| 2 | Four-layer re-exporter chain creating 93 ADG L5 gravity violations | 136 files have wrong import path | High |
| 3 | `SOVEREIGN_TERRITORIES` still live with 29 direct app consumers + 6 runtime type bugs | Runtime crashes waiting | Low |
| 4 | 67 single-consumer symbols in a 163-symbol public API | Dead public API weight | Low |
| 5 | `structure_blueprint_data.py` — a 321-line L0-local satellite copy of L5 data | 5th SSOT location | Medium |
| 6 | `interfaces/structure_config.py` — 20 re-exports, 2 consumers | Unnecessary indirection | Low |
| 7 | `_get_sovereign_territories` private function exposed to application code | Encapsulation violation | Low |

---

## Finding 1: Three Redundant Exclusion Sets (315 Combined Consumers)

### The Three Sets

| Constant | Items | App Consumers | Problem |
|----------|-------|---------------|---------|
| `SOVEREIGN_EXCLUDED_FOLDERS` | 45 | **159** | Contains `data`, `docs`, `logs` — actual project territories |
| `GLOBAL_EXCLUDED_DIRS` | 22 | **95** | Contains `tests`, `reports` — actual project directories |
| `DISCOVERY_EXCLUDED_TERRITORIES` | 6 | **61** | Clean and correct |

### Overlap
```
SEF ∩ GED = 13 items  (.git, __pycache__, .venv, archives, build, dist, env, node_modules,
                        .mypy_cache, .pytest_cache, .sovereign_healing_backup, .healing_backups, venv)
SEF ∩ DET =  4 items  (archives, legacy_code, legacy_engines, stubs)
GED ∩ DET =  1 item   (archives)
Union of all three = 56 unique items
```

### The Critical Bug in `SOVEREIGN_EXCLUDED_FOLDERS`

`SOVEREIGN_EXCLUDED_FOLDERS` contains:
```
data   ← sovereign territory — scanners using this list SKIP all of data/
docs   ← sovereign territory — scanners using this list SKIP all of docs/
logs   ← volatile territory — acceptable to exclude
```

`GLOBAL_EXCLUDED_DIRS` contains:
```
tests    ← CODE_TERRITORY — scanners using this list SKIP all of tests/
reports  ← subdirectory of docs/ — wrong level of granularity
```

Any of the **159 files** importing `SOVEREIGN_EXCLUDED_FOLDERS` and passing it to `os.walk()` / `rglob()` exclusions are silently **skipping `data/` and `docs/`** in their scans.

### Solution: One Correct Exclusion Set

```python
# Replace all three with one correctly scoped set
SCAN_EXCLUDED_DIRS: Final[frozenset[str]] = frozenset({
    # VCS/IDE
    ".git", ".hg", ".svn", ".vscode", ".idea",
    # Python build artifacts
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox",
    "build", "dist", "dist-info", "node_modules", "site-packages",
    # Virtual environments
    ".venv", "venv", "venv_stable", "env",
    # Project-specific excluded
    ".healing_backups", ".sovereign_healing_backup", ".backup",
    "archives", "legacy_code", "legacy_engines",
    # Never scan
    ".DS_Store", "Thumbs.db",
})
# Keep DISCOVERY_EXCLUDED_TERRITORIES as-is (it's already correct)
```

**Migration:** Grep-replace `SOVEREIGN_EXCLUDED_FOLDERS` → `SCAN_EXCLUDED_DIRS` and `GLOBAL_EXCLUDED_DIRS` → `SCAN_EXCLUDED_DIRS` across 254 files. Removes the silent `data/`/`docs/`/`tests/` scan skip bug.

---

## Finding 2: Four-Layer Re-Exporter Chain (93 ADG Layer Violations)

### The Chain

```
_constants.py           [L5, leaf node — defines SOVEREIGN_TERRITORIES]
    ↓
structure_blueprint/__init__.py    [L5, package API — 163 symbols]
    ↓
structure_blueprint_config.py      [L5, backward-compat shim]
    ↓  ← LAYER VIOLATION (L0 importing from L5)
L0_routing/config/__init__.py      [L0, second re-exporter — 136 consumers]
    +
interfaces/structure_config.py    [L? — third re-exporter — 2 consumers]
```

### The Damage

- **136 files** import from `agentic_core.L0_routing.config` to get structure config
- **40 files** import from **both** `L0_routing.config` AND `structure_blueprint` directly — confused about canonical source
- **93 ADG layer violations** all trace back to `L0_routing/config/__init__.py` importing from `L5_safety`
- `L0_routing/config/__init__.py` imports 20 symbols from `structure_blueprint_data.py` (L0-local) AND directly from `_constants.py` (L5) — mixing two wrong patterns

### Why It Happened

`L0_routing/config/__init__.py` was the original single config module before the structure_blueprint package existed. It was never properly retired after the package was created, so it kept accumulating re-exports and became a second SSOT satellite.

### Solution

```python
# L0_routing/config/__init__.py — STOP re-exporting structure config
# Remove all imports from structure_blueprint and structure_blueprint_data
# Only keep path_constants.py exports (project root, directory names)

# Migrate 136 consumers to import directly:
from agentic_core.L5_safety.config.structure_blueprint import X
# or use the shim:
from agentic_core.L5_safety.config.structure_blueprint_config import X
```

This eliminates all 93 L5 layer violations in a single refactor.

---

## Finding 3: Six Runtime Type Bugs + 29 Remaining SOVEREIGN_TERRITORIES Consumers

Already documented in `plan_eliminate_sovereign_territories.md`.

**Critical:** These are runtime `AttributeError` crashes waiting to happen:
```python
# frozenset has no .get() — crashes at runtime
max_depth = ENFORCED_TERRITORIES.get(root_folder, {}).get("depth", 3)
```

**6 files affected:**
1. `L5_safety/utils/location_path_util.py`
2. `L5_safety/utils/location_utils_util.py`
3. `L5_safety/reasoning/location_validator.py`
4. `L5_safety/reasoning/hierarchy_healer.py`
5. `L5_safety/reasoning/ArchitectureGovernorAgent.py`
6. `L5_safety/validators/gravity_validator.py`

**Fix:** Add `DEPTH_RULES: dict[str, int]` to `ssot.py`, replace `.get("depth")` calls.

---

## Finding 4: 67 Single-Consumer Symbols in a 163-Symbol Public API

The structure_blueprint package exposes 163 public symbols. ADG shows **67 of these have exactly one non-re-exporter consumer** — meaning they're private implementation details masquerading as public API.

### Worst Offenders (symbols only used by _verify.py internals)

These are `_verify.py` internal symbols that leaked into the public API:
```
ImportGraph, blueprint_hash, c_rw, c_st, cross_layer, emit_report_json,
leaf_node, make_report, mixin_ast, s_rw, s_st, t_st, territory_diff, volatile_rules
```
All consumed only by `structure_blueprint/_verify.py` — they should be private imports within that module, not part of the 163-symbol public API.

### FileClassificationAgent Owns 11 Single-Consumer Symbols

```
APP_RG_STRING_TERMS, APP_SPECIFIC_PREFIXES, COMPOUND_SUFFIX_CONFLICTS,
FOLDER_ALIASES, FOLDER_PURITY_RULES, FORBIDDEN_FILENAME_PATTERNS,
INFRASTRUCTURE_PROFILES, KNOWN_ARCHITECTURAL_SUFFIXES, NON_PYTHON_FOLDER_ROUTES,
SERVICE_CLASS_INDICATORS, STUTTERING_PREFIX_MAP
```

These should be defined in `FileClassificationAgent.py` directly or in a `classification_agent_config.py` co-located with the agent.

### Single-Consumer Path Constants

These belong in `path_constants.py` (L0), not in structure_blueprint:
```
SYSTEM_LEARNING_DIR   ← only L0_routing/scripts/run_guardian_c0_sovereignty.py
TESTS_L2_SUBFOLDER_MAP ← only L0_routing/scripts/align_tests_structure_util.py
TESTS_AUTOGEN_DIR     ← only TestGeneratorAgent.py
RUNTIME_STATE_JSON    ← only ops_scripts/general/mission_telemetry_dashboard.py
```

### Solution

1. Prefix `_verify.py`-internal symbols with `_` and remove from `__all__`
2. Move single-consumer agent config to co-located config files
3. Reduce public API from 163 symbols to ~80 genuinely shared constants

---

## Finding 5: `structure_blueprint_data.py` — The Hidden 5th SSOT

**Location:** `agentic_core/L0_routing/config/structure_blueprint_data.py` (321 lines)

**Purpose per docstring:** "L0 Structure Blueprint Data — Literal-only constants extracted from L5. No functions, classes, or imports from L5+ layers."

**The intent was correct** (avoid L0→L5 import violations) but the execution created a **5th SSOT location**:

```
SSOT Location 1: structure_blueprint/_constants.py        ← canonical
SSOT Location 2: structure_blueprint/ssot.py              ← derived subsets
SSOT Location 3: structure_blueprint_config.py            ← backward-compat shim
SSOT Location 4: L0_routing/config/__init__.py            ← re-exporter (wrong layer)
SSOT Location 5: L0_routing/config/structure_blueprint_data.py ← literal copy (drift risk)
```

`structure_blueprint_data.py` contains literal copies of 20 symbols that also exist in L5. These will drift independently over time.

### Solution

The correct approach for L0 modules that need structure config is to either:
- Accept the L0→L5 import (most are L0 scripts, not hot-path modules)
- Use `path_constants.py` (L0) for directory name strings only

Delete `structure_blueprint_data.py` and update `L0_routing/config/__init__.py` to import from the canonical L5 source.

---

## Finding 6: `interfaces/structure_config.py` — 20 Imports, 2 Consumers

**Location:** `agentic_core/interfaces/structure_config.py` (103 lines)

**Consumers:**
- `apps_lic/tools/fix_duplicate_realagentdata.py`
- `apps_rg/config/void_compliance_config.py`

Two app files created a dependency on an `interfaces/` shim that re-exports 20 structure_blueprint symbols. Both should import from `structure_blueprint` directly.

**Delete `interfaces/structure_config.py`** and update the 2 consumers.

---

## Finding 7: `_get_sovereign_territories` Exposed to Application Code

`_get_sovereign_territories` (note the leading `_`) is a private internal function. ADG shows it's being imported by `ArchitectureGovernorAgent.py`:

```python
from agentic_core.L5_safety.config.structure_blueprint import (
    get_sovereign_territories as _get_sovereign_territories,
)
```

This private function returns the full `SOVEREIGN_TERRITORIES` dict — exactly what the SSOT enforcement is trying to prevent. Fix: replace with `CODE_TERRITORIES` lookup.

---

## Priority Order for Implementation

```
P0 (crashes today)
  └─ Fix 6 frozenset type bugs
  └─ Add DEPTH_RULES to ssot.py

P1 (data correctness — scanners silently skipping data/, docs/, tests/)
  └─ Fix SOVEREIGN_EXCLUDED_FOLDERS (remove data, docs)
  └─ Fix GLOBAL_EXCLUDED_DIRS (remove tests, reports)
  └─ Consolidate to SCAN_EXCLUDED_DIRS

P2 (93 layer violations — architecture hygiene)
  └─ Remove structure config re-exports from L0_routing/config/__init__.py
  └─ Migrate 136 consumers to import from structure_blueprint directly
  └─ Delete structure_blueprint_data.py

P3 (API surface reduction)
  └─ Remove 67 single-consumer symbols from __all__
  └─ Delete interfaces/structure_config.py (2 consumers)
  └─ Fix _get_sovereign_territories exposure

P4 (final elimination)
  └─ Delete SOVEREIGN_TERRITORIES + build_sovereign_territories() (~1400 lines)
```

---

## ADG Metrics Before / After

| Metric | Before | After |
|--------|--------|-------|
| ADG layer violations | 247 | ~154 (93 fixed by P2) |
| SSOT locations for structure config | 5 | 2 (ssot.py + path_constants.py) |
| Structure blueprint public API size | 163 symbols | ~80 symbols |
| Files confused about import path | 40 | 0 |
| Incorrect scan exclusions | data/, docs/ silently skipped | Fixed |
| Runtime type bugs | 6 | 0 |
| Lines in _constants.py | 1539 | ~100 |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

