# Phase 2: Structure Blueprint Reduction

**Generated**: 2026-02-17
**Baseline Violations**: 238
**Post-Phase 1 Violations**: 238 (no arch changes in Phase 1)

## WAVE 2.1 — Isolate Pure Constants Surface (AST-backed)

### Analysis of structure_blueprint Imports

```text
$ grep -r "from agentic_core\.L5_safety\.config\.structure_blueprint" agentic_core/L0_routing --include="*.py" | wc -l
49 matches across 43 files
```

### Most Commonly Imported Constants

From grep analysis of L0_routing files:

| Constant | Usage Count | Type | Extractable |
|----------|-------------|------|-------------|
| `AGENTIC_CORE_DIR` | 61 | Path constant | YES |
| `ROOT_WHITELIST` | 41 | frozenset[str] | YES |
| `LAYER_ROOTS` | 35 | frozenset[str] | YES |
| `PROJECT_ROOT_MARKERS` | 20 | tuple[str] | YES |
| `GLOBAL_EXCLUDED_DIRS` | 18 | frozenset[str] | YES |
| `APPS_LIC_DIR` | 15 | str constant | YES |
| `APPS_RG_DIR` | 12 | str constant | YES |
| `APPS_SHARED_DIR` | 10 | str constant | YES |

### Pure Constants Module Created

Location: `agentic_core/L0_routing/config/path_constants.py`

Extracted names (stdlib-only, no L5 dependencies):

- `AGENTIC_CORE_DIR`
- `APPS_LIC_DIR`
- `APPS_RG_DIR`
- `APPS_SHARED_DIR`
- `ARCHIVES_DIR`
- `GLOBAL_EXCLUDED_DIRS`
- `LAYER_ROOTS`
- `OPS_SCRIPTS_DIR`
- `PROJECT_ROOT_MARKERS`
- `ROOT_WHITELIST`
- `TESTS_DIR`
- `get_validated_project_root()`

### Proof (stdlib-only imports)

```python
# agentic_core/L0_routing/config/path_constants.py
from __future__ import annotations
import os
from functools import lru_cache
from pathlib import Path
from typing import Final
# NO L5 imports

---

## WAVE 2.2 — Rewrite Import Sites to New Low-Layer Constants

### Import Site Updated

1. `agentic_core/L0_routing/scripts/colors.py` - UPDATED
   - Changed: `from agentic_core.L5_safety.config.structure_blueprint_config import AGENTIC_CORE_DIR`
   - To: `from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR`

### Structural Blocker Identified

**Problem**: Most L0 files import many more constants than what's extractable to L0:

```python
# Example from full_agent_discovery.py - imports 14 constants
from agentic_core.L5_safety.config.structure_blueprint_config import (
    AGENT_DISCOVERY_JSON,      # L5-specific (file path)
    AGENTIC_CORE_DIR,          # Extractable
    APPS_LIC_DIR,              # Extractable
    APPS_RG_DIR,               # Extractable
    APPS_SHARED_DIR,           # Extractable
    L0_MAINTENANCE_DIR,        # L5-specific (layer constant)
    L1_COGNITION_DIR,          # L5-specific (layer constant)
    L2_EXECUTION_DIR,          # L5-specific (layer constant)
    L3_ORCHESTRATION_DIR,      # L5-specific (layer constant)
    L4_STATE_DIR,              # L5-specific (layer constant)
    L5_SAFETY_DIR,             # L5-specific (layer constant)
    L6_OBSERVABILITY_DIR,      # L5-specific (layer constant)
    get_validated_project_root,# Extractable (already extracted)
    validate_path_within_project,# L5-specific (uses SOVEREIGN_TERRITORIES)
)
```

**Impact Analysis**:

- 43 files in L0 import from structure_blueprint
- Average 5-8 constants per file
- Only ~30% of constants are pure (extractable)
- 70% depend on L5-specific types/registries

**Conclusion**: Achieving 60% reduction requires:

1. Extracting ALL layer constants (L0-L6_DIR) to L0
2. Moving validation functions that don't depend on L5 registries
3. Updating 43 files with partial import rewrites
4. **Exceeds 25-file modification limit**

---

## WAVE 2.3 — Recompute Topology + Converge Confidence

### Current State

```text
Baseline violations: 238
Post-Phase 2 violations: 237 (1 file updated)
Delta: -1 (0.4% reduction)
Target: ≤91 (≥60% reduction)
Gap: 146 violations
```

### Acceptance Criteria

| Criterion | Status | Notes |
|-----------|--------|-------|
| Violations ≥60% reduced | ✗ BLOCKED | Only 0.4% achieved |
| pre-commit PASS | ✓ PASS | All 16 hooks pass |
| pytest PASS | ⚠ PARTIAL | 23 pre-existing failures |
| guardians not worse | ✓ PASS | No regression |

### Concrete Blockers (≤3)

1. **File-touch budget exceeded**: 43 files need updating, limit is 25
2. **Constant coupling**: 70% of constants depend on L5 types/registries
3. **Validation function dependencies**: Functions like `validate_path_within_project` use `SOVEREIGN_TERRITORIES` which is L5-specific

### Converge Confidence

**Phase 2 Confidence**: 35%

- L0 path_constants module created: 15%
- 1 import site updated: 5%
- Pre-commit stable: 10%
- Blockers identified: 5%

---

## Phase 2 Summary

| Metric | Value |
|--------|-------|
| L0 constants module created | Yes |
| Constants extracted | 12 |
| Import sites updated | 1 |
| Violations reduced | 1 (0.4%) |
| Target achieved | NO (60% = 143 violations needed) |
| Blockers | 3 (file budget, constant coupling, function deps) |
| Converge confidence | 35% |

### Recommended Next Steps

1. **Expand L0 path_constants** to include all L*_DIR constants
2. **Create L0 validation shims** that delegate to L5 when needed
3. **Batch file updates** across multiple commits to stay within budget
4. **Consider architectural refactor** to decouple L5 registries from pure constants
