---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\plan_eliminate_sovereign_territories.md'
original_relative_path: 'plan_eliminate_sovereign_territories.md'
source_sha256: e52136cccfd8dabc29bae516db3a674692ccd0a6859407c238082044fa9138c8
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Eliminate SOVEREIGN_TERRITORIES

**Date:** 2026-03-11
**Status:** ACTIVE
**Priority:** High — 6 runtime type bugs exist today

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


## Problem Statement

`SOVEREIGN_TERRITORIES` in `_constants.py` is a 1500-line God Object `Mapping[str, Any]` that:

1. Mixes three fundamentally different categories of directories (code, data/docs, system)
2. Defines validation metadata for system directories that should **never** be validated (`.backup`, `artifacts`, `.gravity_state`, `logs`)
3. Is 95% unused — the only metadata actually consumed at runtime is `depth` (one integer per territory)
4. Generated 6 runtime type bugs when the previous session replaced `SOVEREIGN_TERRITORIES` (a Mapping) with `ENFORCED_TERRITORIES`/`CODE_TERRITORIES` (both `frozenset[str]`) — callers that use `.get()` on those frozensets will `AttributeError` at runtime

**The simpler model already partially exists in `ssot.py`:**
- `CODE_TERRITORIES: frozenset[str]` — 8 code dir names ✅
- `ENFORCED_TERRITORIES: frozenset[str]` — 10 territory names ✅
- `VOLATILE_TERRITORIES: frozenset[str]` — 2 excluded dir names ✅

What is **missing** is a single `DEPTH_RULES: dict[str, int]` — the only piece of per-territory metadata that is genuinely used.

---

## Directory Taxonomy

### Code Territories (8) — need depth + structure validation
| Directory | Max Depth | Notes |
|-----------|-----------|-------|
| `agentic_core` | 4 | L0–L6 / LCD / file.py |
| `apps_rg` | 3 | apps_rg / domain / file.py |
| `apps_lic` | 3 | |
| `apps_shared` | 3 | |
| `tests` | 3 | |
| `ops_scripts` | 2 | |
| `system_learning` | 2 | |
| `tools` | 2 | |

### Data/Docs Territories (2) — routing rules only, no depth enforcement
- `data`, `docs`

### System Directories (6) — **never validate, never scan**
- `.backup`, `.github`, `.gravity_state`, `artifacts`, `logs`, `archives`
- All are gitignored or auto-generated; depth/subfolder rules are meaningless

---

## Root Cause of Type Bugs

Previous session replaced `SOVEREIGN_TERRITORIES` (Mapping) with `ENFORCED_TERRITORIES` (frozenset) in 19 files but left behind dict-style `.get()` calls that frozensets don't support:

```python
# CRASHES at runtime — frozenset has no .get()
max_depth = ENFORCED_TERRITORIES.get(root_folder, {}).get("depth", 3)
```

**6 files affected:**
1. `agentic_core/L5_safety/utils/location_path_util.py`
2. `agentic_core/L5_safety/utils/location_utils_util.py`
3. `agentic_core/L5_safety/reasoning/location_validator.py`
4. `agentic_core/L5_safety/reasoning/hierarchy_healer.py`
5. `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py`
6. `agentic_core/L5_safety/validators/gravity_validator.py`

---

## Phases

### Phase 0 — Fix Runtime Type Bugs (IMMEDIATE)

Add `DEPTH_RULES: dict[str, int]` to `ssot.py` and fix all 6 files.

**Add to `ssot.py`:**
```python
DEPTH_RULES: Final[dict[str, int]] = {
    "agentic_core":   4,
    "apps_rg":        3,
    "apps_lic":       3,
    "apps_shared":    3,
    "tests":          3,
    "ops_scripts":    2,
    "system_learning": 2,
    "tools":          2,
    "data":           3,
    "docs":           3,
}
```

**Fix pattern in all 6 files:**
```python
# BEFORE (crashes)
max_depth = ENFORCED_TERRITORIES.get(root_folder, {}).get("depth", 3)

# AFTER
from agentic_core.L5_safety.config.structure_blueprint import DEPTH_RULES
max_depth = DEPTH_RULES.get(root_folder, 3)
```

### Phase 1 — Eliminate SOVEREIGN_TERRITORIES from application code

Complete migration of 4 remaining files that still import `SOVEREIGN_TERRITORIES` directly (outside the `structure_blueprint` package):

| File | Replacement |
|------|-------------|
| `L0_routing/scripts/run_guardian_hierarchy_compliance.py` | `CODE_TERRITORIES` + `DEPTH_RULES` |
| `L0_routing/scripts/execute_ssot.py` | `ENFORCED_TERRITORIES` + `DEPTH_RULES` |
| `L0_routing/scripts/populate_ssot_folders_util.py` | `ENFORCED_TERRITORIES` |
| `config/core/registry_config.py` | `CODE_TERRITORIES` |

### Phase 2 — Remove SOVEREIGN_TERRITORIES from `_constants.py`

Once no application code imports `SOVEREIGN_TERRITORIES`, remove it from the internal SSOT package:

1. Delete `build_sovereign_territories()` function (~1400 lines)
2. Delete `SOVEREIGN_TERRITORIES = _deep_freeze(build_sovereign_territories())`
3. Keep `TerritoryDefinition`, `SubfolderDefinition` TypedDicts only if still used by `DEPTH_RULES`-style consumers
4. Update `__init__.py` to remove the re-export
5. Update `structure_blueprint_config.py` shim accordingly

### Phase 3 — Clean up derived.py

`derived.py` currently builds `CORE_SUBFOLDER_MAP`, `APPS_*_SUBFOLDER_MAP` by parsing `SOVEREIGN_TERRITORIES`. Once the registry is gone, these must either:

- **Option A (preferred):** Discover from the filesystem at import time using `os.listdir()`
- **Option B (fallback):** Inline the ~10 relevant subfolder names as simple frozensets

`CORE_SUBFOLDER_MAP` is used by gravity_validator and hierarchy_healer to validate L1 layer folder names. The L1 names are just `L0_routing`, `L1_cognition`, … — they're already captured in `LAYER_ROOTS` in `ssot.py`. Use that instead.

---

## End State

### Before (current)
```
structure_blueprint/
  _constants.py          — 1539 lines, SOVEREIGN_TERRITORIES is a 16-key Mapping[str, Any]
  derived.py             — 340 lines, derives maps from SOVEREIGN_TERRITORIES
  ssot.py                — 1091 lines, partially correct frozensets but missing DEPTH_RULES
```

### After (target)
```
structure_blueprint/
  _constants.py          — ~100 lines, TypedDicts + governance constants only
  derived.py             — DELETED or 50 lines of filesystem discovery
  ssot.py                — add DEPTH_RULES (10 lines), everything else unchanged
```

### Canonical Constants After Migration
| Constant | Type | Size | Purpose |
|----------|------|------|---------|
| `CODE_TERRITORIES` | `frozenset[str]` | 8 names | Membership check: has Python code |
| `ENFORCED_TERRITORIES` | `frozenset[str]` | 10 names | Membership check: has structure rules |
| `VOLATILE_TERRITORIES` | `frozenset[str]` | 2 names | Exclusion from scans |
| `DEPTH_RULES` | `dict[str, int]` | 10 entries | Depth limit per territory |
| `PROJECT_ROOT_WHITELIST` | `frozenset[str]` | 17 names | Approved directories at root |
| `LAYER_ROOTS` | `frozenset[str]` | 7 names | `L0_routing` … `L6_observability` |

---

## Verification

After each phase, run:

```python
python -c "
import re
from pathlib import Path
root = Path('c:/Git/Agentic-Workflow')
# Test 1: No .get() on frozensets
pattern = re.compile(r'(ENFORCED_TERRITORIES|CODE_TERRITORIES)\.get\(')
bugs = []
for f in root.rglob('*.py'):
    if any(x in str(f) for x in ['.git', 'archives', '.healing_backups']):
        continue
    src = f.read_text(encoding='utf-8', errors='ignore')
    if pattern.search(src):
        bugs.append(str(f.relative_to(root)))
print('Type bugs remaining:', len(bugs))
for b in bugs:
    print(' ', b)
"
```

```python
python -c "
from pathlib import Path
root = Path('c:/Git/Agentic-Workflow')
violations = []
for f in root.rglob('*.py'):
    if 'structure_blueprint' in str(f) or 'archives' in str(f) or '.healing_backups' in str(f):
        continue
    src = f.read_text(encoding='utf-8', errors='ignore')
    if 'SOVEREIGN_TERRITORIES' in src:
        violations.append(str(f.relative_to(root)))
print('Application SOVEREIGN_TERRITORIES imports:', len(violations))
for v in sorted(violations):
    print(' ', v)
"
```

---

## What We Do NOT Need

This plan deliberately does NOT include:

- `purpose` strings per territory → belongs in `docs/`, not code
- `subfolders` nested dicts per territory → discover from `os.listdir()` or use `LAYER_ROOTS`
- `forbidden_patterns` per territory → global rules in existing `FORBIDDEN_PATTERNS`
- `allowed_extensions` per territory → global rules
- `no_cross_layer_imports` flag → ADG handles this
- `volatile` flag → replaced by `VOLATILE_TERRITORIES` frozenset
- `enforcement_level: relaxed` → replaced by explicit exclusion sets

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

