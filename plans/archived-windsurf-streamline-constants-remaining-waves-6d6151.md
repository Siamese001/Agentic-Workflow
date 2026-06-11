---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\streamline-constants-remaining-waves-6d6151.md'
original_relative_path: 'streamline-constants-remaining-waves-6d6151.md'
source_sha256: c98bfac85609e74e7864fa9bb009ae123902d2744b0f1a1b88b452fcf56f7a6c
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Streamline _constants.py Territory Definitions — Remaining Waves Plan

Complete the streamlining of _constants.py by migrating all downstream files from deprecated `SOVEREIGN_TERRITORIES` access to the new `territories.py` API.

---

## Current State (Post Waves 1-2)

| Metric | Value |
|--------|-------|
| `_constants.py` lines | 728 (was 1,752) |
| Territory data | Loaded from JSON (21 territories) |
| Operational config | Consolidated in `governance.py` |
| Downstream files importing `_constants` | ~165 files |
| Direct `SOVEREIGN_TERRITORIES` references | 53 matches in 6 files (structure_blueprint) |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| Wave 3 | P3a-P3d | structure_blueprint package migration | 8,000 | 🟡 | 0 direct SOVEREIGN_TERRITORIES in package |
| Wave 4 | P4a-P4c | L5_safety/config module migration | 5,000 | 🟡 | Config modules use territories.py API |
| Wave 5 | P5a-P5f | High-impact downstream (top 30 files) | 12,000 | 🟡 | Top consumers migrated |
| Wave 6 | P6a-P6c | Bulk migration (remaining ~135 files) | 15,000 | 🔴 | All files use new API |
| Wave 7 | P7a-P7b | Cleanup & final verification | 5,000 | 🟢 | Tests pass, metrics met |

**Total: ~45,000 tokens across 5 waves**

---

## Gap Register

**GAP-1: Direct SOVEREIGN_TERRITORIES access in structure_blueprint**
- 53 references across _verify.py (17), __init__.py (10), ssot.py (6), derived.py (2), territories.py (8)
- These are the canonical territory consumers and must use the new API
- Impact: Blocks adoption of JSON-based territory data

**GAP-2: High-import-count downstream files**
- L0_routing/scripts/_ssot_routing.py (6 imports)
- L0_routing/config/ssot_tier_constants.py (3 imports)
- L2_execution/healers/healing_tier_config.py (3 imports)
- These files have heavy coupling to _constants.py internals
- Impact: High risk of circular dependencies, test failures

**GAP-3: apps_* test mirror definitions use per-app entries**
- Current tests/unit mirrors list apps_lic, apps_rg, apps_shared separately
- User preference: use wildcard `apps_*` entry instead
- Impact: Violates user preference for streamlined definitions

**GAP-4: ~165 files import from _constants.py directly**
- Pattern: `from agentic_core.L5_safety.config.structure_blueprint._constants import ...`
- Need to migrate to: `from agentic_core.L5_safety.config.structure_blueprint import get_territory_metadata`
- Impact: Technical debt, API inconsistency

---

## Execution Plan

### Wave 3 — structure_blueprint Package Migration

#### Micro-Wave 3a: _verify.py Migration
**Scope**: Update `_verify.py` to use `territories.py` API

**Changes**:
- Replace `SOVEREIGN_TERRITORIES.get(name)` → `get_territory_metadata(name)`
- Replace `name in SOVEREIGN_TERRITORIES` → `is_valid_root_folder(name)`
- Replace iteration over `SOVEREIGN_TERRITORIES.items()` → `get_all_territories().items()`

**Verification**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/config/structure_blueprint/test_verify.py -v
```

#### Micro-Wave 3b: ssot.py Migration
**Scope**: Update `ssot.py` to use `territories.py` API

**Changes**:
- Replace `ROOT_WHITELIST` usage with `is_valid_root_folder()`
- Replace `SOVEREIGN_TERRITORIES` access with `get_territory_metadata()`

**Verification**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/config/structure_blueprint/test_ssot.py -v
```

#### Micro-Wave 3c: derived.py Migration
**Scope**: Update `derived.py` to use `territories.py` API

**Changes**:
- Replace direct dict access with `get_all_territories()`

**Verification**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/config/structure_blueprint/test_derived.py -v
```

#### Micro-Wave 3d: __init__.py Cleanup
**Scope**: Update `__init__.py` exports to prefer new API

**Changes**:
- Add explicit exports: `get_territory_metadata`, `get_all_territories`, `is_valid_root_folder`
- Keep backward-compatible exports with deprecation comments
- Reorder exports: new API first, legacy second

---

### Wave 4 — L5_safety/config Module Migration

#### Micro-Wave 4a: structure_blueprint_config.py
**Scope**: Migrate `structure_blueprint_config.py` (2 references)

**Changes**:
- Update imports to use `territories.py` API
- Remove direct `_constants` imports where possible

#### Micro-Wave 4b: Config module audit
**Scope**: Audit all L5_safety/config modules for _constants usage

**Command**:
```bash
grep -r "from.*_constants import\|import.*_constants" agentic_core/L5_safety/config/ --include="*.py"
```

#### Micro-Wave 4c: Migrate identified modules
**Scope**: Update any remaining config modules

---

### Wave 5 — High-Impact Downstream Migration

#### Micro-Wave 5a: L0_routing/scripts/_ssot_routing.py
**Scope**: Migrate high-import file (6 references)

**Pattern**: Likely uses territory metadata for routing decisions
**Approach**: Replace with `get_territory_metadata()` calls

#### Micro-Wave 5b: L0_routing/config/ssot_tier_constants.py
**Scope**: Migrate config file (3 references)

**Pattern**: Likely imports territory constants
**Approach**: Use `get_all_territories()` for initialization

#### Micro-Wave 5c: L2_execution/healers/healing_tier_config.py
**Scope**: Migrate healer config (3 references)

**Pattern**: Likely uses territory definitions for healing
**Approach**: Use new API with lazy initialization

#### Micro-Wave 5d: Top 10 import-count files
**Scope**: Migrate highest-impact consumers

**Command to identify**:
```bash
grep -r "from.*_constants import" agentic_core/ --include="*.py" | cut -d: -f1 | sort | uniq -c | sort -rn | head -20
```

#### Micro-Wave 5e: L0_routing/scripts bulk (batch 1)
**Scope**: Migrate 10-15 script files

**Files**: Various scripts in `agentic_core/L0_routing/scripts/`

#### Micro-Wave 5f: Remaining high-impact (batch 2)
**Scope**: Migrate next 10-15 files

---

### Wave 6 — Bulk Migration

#### Micro-Wave 6a: Automated migration script
**Scope**: Create pattern-based migration tool

**Approach**:
```python
# Pseudo-code for migration patterns
PATTERNS = [
    ("SOVEREIGN_TERRITORIES.get(name)", "get_territory_metadata(name)"),
    ("name in SOVEREIGN_TERRITORIES", "is_valid_root_folder(name)"),
    ("SOVEREIGN_TERRITORIES.keys()", "get_all_territories().keys()"),
    ("SOVEREIGN_TERRITORIES.items()", "get_all_territories().items()"),
    ("ROOT_WHITELIST", "frozenset(get_all_territories().keys())"),
]
```

#### Micro-Wave 6b: Batch migration (remaining files)
**Scope**: Apply automated migration to ~135 remaining files

**Command**:
```bash
python tools/adg/migrate_territory_imports.py --apply --scope=remaining
```

#### Micro-Wave 6c: Manual fixup pass
**Scope**: Fix any edge cases from automated migration

---

### Wave 7 — Cleanup & Verification

#### Micro-Wave 7a: Remove deprecated exports (optional)
**Scope**: After all consumers migrated, remove deprecated exports from _constants.py

**Note**: Only if 100% confident all downstream files migrated

#### Micro-Wave 7b: Final verification
**Scope**: Full test suite verification

**Commands**:
```bash
# Test collection
python -m pytest tests/unit/agentic_core/L5_safety/ -v --collect-only

# Run tests
python -m pytest tests/unit/agentic_core/L5_safety/ -v --tb=short

# Verify no SOVEREIGN_TERRITORIES usage outside _constants.py
grep -r "SOVEREIGN_TERRITORIES" --include="*.py" agentic_core/ | grep -v "_constants.py\|territories.py"
```

---

## Rules

1. **Backward compatibility**: Maintain exports from _constants.py until Wave 7
2. **Test-first**: Run tests before and after each micro-wave
3. **No functional changes**: Only API migration, no behavior changes
4. **Pattern consistency**: Use `get_territory_metadata()` for lookup, `get_all_territories()` for iteration
5. **Author-Gate for high-impact**: Present options if >10 files affected in one micro-wave

---

## Success Criteria

- [ ] Wave 3: 0 direct `SOVEREIGN_TERRITORIES` references in structure_blueprint/
- [ ] Wave 4: L5_safety/config modules use new API
- [ ] Wave 5: Top 30 files migrated
- [ ] Wave 6: All remaining ~135 files migrated
- [ ] All tests pass after each wave
- [ ] No regressions in ADG edge counts
- [ ] `territories.py` API adoption > 90%

---

## Rollback Strategy

If issues arise:
1. Revert specific micro-wave files: `git checkout HEAD -- <affected_files>`
2. Verify with targeted tests
3. Re-apply with fixes

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Downstream SOVEREIGN_TERRITORIES imports | 0 | `grep -r "SOVEREIGN_TERRITORIES" --include="*.py" agentic_core/ \| grep -v "_constants.py\|territories.py" \| wc -l` |
| Tests passing | 100% | `python -m pytest tests/unit/agentic_core/L5_safety/ -v` |
| API adoption | > 90% | `grep -r "get_territory_metadata\|get_all_territories" --include="*.py" agentic_core/ \| wc -l` |
| _constants.py line count | < 500 | `wc -l agentic_core/L5_safety/config/structure_blueprint/_constants.py` |
