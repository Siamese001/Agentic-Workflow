---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\ssot-consolidation-execution-plan.md'
original_relative_path: 'ssot-consolidation-execution-plan.md'
source_sha256: 25bc9261fe394c2c0cdd92baeff742459d313fbed28786131c17137104405b2d
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-04-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# SSOT Consolidation Execution Plan

Consolidate multiple sources of truth into canonical locations following the architectural boundary rules.

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|--------|
| Wave 1 | Duplicate type files | Remove apps_shared duplicate | A | 2,000 🟢 |
| Wave 2 | Config constants triplication | Consolidate into path_constants.py | B | 3,000 🟢 |
| Wave 3 | L0→L2 boundary violation | Move healing thresholds to L0 | C | 4,000 🟢 |
| Wave 4 | Dual lifecycle contracts | Remove runtime/ duplicate | D | 2,500 🟢 |
| Wave 5 | Import verification | Validate all imports work | E | 2,000 🟢 |

**Total: ~13,500 tokens across 5 waves, all GREEN**

---

## Gap Register

**GAP-1: Duplicate ssot_relocator_types.py**
- Same file exists in agentic_core/L5_safety/types/ and apps_shared/types/
- apps_shared version is a copy with identical implementation
- Violates DRY principle

**GAP-2: Config constants defined in 3 locations**
- MAX_RETRIES, DEFAULT_SLEEP, THRESHOLD, etc. defined in:
  - path_constants.py (L0 - canonical)
  - _constants.py (L5)
  - structure_blueprint_config.py (L5 shim)

**GAP-3: L0→L2 boundary violation**
- L0 module copies L2 constants to avoid cross-layer imports
- Proper fix: move thresholds to L0, have L2 import from L0

**GAP-4: Dual lifecycle_trace_contract.py**
- Identical files in L_CONTRACTS/ and runtime/
- Creates confusion about which is canonical

---

## Execution Plan

### Phase 1 — Wave 1: Remove Duplicate Type File
**Scope**: Delete apps_shared/types/ssot_relocator_types.py and verify no consumers

**Commands**:
```bash
# Check for consumers
grep -r "from apps_shared.types.ssot_relocator_types" --include="*.py"
# Delete file
rm apps_shared/types/ssot_relocator_types.py
# Verify imports
python -c "from agentic_core.L5_safety.types.ssot_relocator_types import SSOTRelocator"
```

**Acceptance**: No consumers broken, file deleted, imports work from canonical location

---

### Phase 2 — Wave 2: Consolidate Config Constants
**Scope**: Remove duplicate constants from _constants.py, import from path_constants.py

**Commands**:
```bash
# Edit _constants.py to import from path_constants.py instead of redefining
# Verify structure_blueprint/__init__.py still works
python -c "from agentic_core.L5_safety.config.structure_blueprint import MAX_RETRIES"
```

**Acceptance**: Constants imported not redefined, all exports work

---

### Phase 3 — Wave 3: Fix L0→L2 Boundary
**Scope**: Move healing thresholds to path_constants.py, update L2 to import from L0

**Commands**:
```bash
# Add thresholds to path_constants.py
# Update healing_tier_config.py to import from L0
# Update ssot_tier_constants.py (already a copy, can import)
python -c "from agentic_core.L0_routing.config.path_constants import HEALING_CONFIDENCE_X"
python -c "from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig"
```

**Acceptance**: No circular imports, L2 can import from L0 for thresholds

---

### Phase 4 — Wave 4: Consolidate Lifecycle Contracts
**Scope**: Remove runtime/lifecycle_trace_contract.py, keep L_CONTRACTS/ version

**Commands**:
```bash
# Check for consumers of runtime version
grep -r "from agentic_core.runtime.lifecycle_trace_contract" --include="*.py"
# Update consumers to use L_CONTRACTS version
# Delete runtime version
rm agentic_core/runtime/lifecycle_trace_contract.py
```

**Acceptance**: All consumers updated, runtime version deleted

---

### Phase 5 — Wave 5: Verification
**Scope**: Run import tests and pytest collection

**Commands**:
```bash
python -c "from agentic_core.L5_safety.config.structure_blueprint import *"
python -c "from agentic_core.L0_routing.config.path_constants import *"
python -m pytest tests/ --collect-only -q
```

**Acceptance**: No import errors, pytest collection passes

---

## Rules

1. **Layer Gravity**: L0 can be imported by any layer; L2 imports from L0 is allowed
2. **Backward Compatibility**: All existing import paths must continue to work
3. **Commit After Each Wave**: Git commit and push after each wave completion
4. **No Breaking Changes**: All __all__ exports preserved
5. **ADG Compliance**: No new layer boundary violations introduced

---

## Success Criteria

- [ ] Wave 1: apps_shared/types/ssot_relocator_types.py deleted
- [ ] Wave 2: No duplicate constant definitions
- [ ] Wave 3: L2 imports healing thresholds from L0
- [ ] Wave 4: runtime/lifecycle_trace_contract.py consolidated
- [ ] Wave 5: All imports work, pytest collection passes

---

## Rollback Strategy

If things go wrong:
1. Git revert the specific wave commit
2. Check for any new files created and remove them
3. Verify ADG status: `python tools/adg/adg_redis_ingest.py --check`
4. Run full test collection to verify baseline

---

## Acceptance Criteria

| Metric | Target | Verification |
|--------|--------|--------------|
| Duplicate files | 0 | `find . -name "ssot_relocator_types.py" | wc -l` = 1 |
| Constant redefinitions | 0 | grep for MAX_RETRIES in _constants.py returns import |
| L0→L2 boundary clean | Yes | healing_tier_config.py imports from L0 |
| Import errors | 0 | `python -m pytest tests/ --collect-only` passes |
