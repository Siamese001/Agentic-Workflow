---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\streamline-constants-territories-d0cb16.md'
original_relative_path: '_archive\\2026-05\\streamline-constants-territories-d0cb16.md'
source_sha256: 77e880d9112e50debd34bc2f3e73e7648816f31678181d0e79d608dd68276382
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Streamline _constants.py Territory Definitions

Refactor the 1,752-line `_constants.py` to separate territory data from builder logic, migrate downstream files from deprecated `SOVEREIGN_TERRITORIES` to the new `territories.py` API, and consolidate operational governance config into dedicated modules.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | P1a, P1b | Separate data from logic in _constants.py | 12,000 | No API changes yet | 🟢 GREEN | Builder functions moved, data extracted to JSON |
| Wave 2 | P2a, P2b | Consolidate operational config into governance.py | 8,000 | Configs moved, imports updated | 🟢 GREEN | HEALING_CONFIG, GRAVITY_CONFIG, etc. consolidated |
| Wave 3 | P3a, P3b | Migrate structure_blueprint/ to new API | 10,000 | Internal package first | 🟢 GREEN | No direct SOVEREIGN_TERRITORIES imports in package |
| Wave 4 | P4a, P4b | Migrate all downstream files (~185 files) | 25,000 | Pattern-based migration | 🟡 YELLOW | All files use territories.py API |

**Total: ~55,000 tokens across 4 waves, mostly GREEN/YELLOW**

---

## Gap Register

**GAP-1: Mixed concerns in _constants.py**
- Territory data, builder logic, operational config, and trace emitters all in one file
- 1,752 lines makes the file hard to navigate and maintain
- Impact: High maintenance burden, risk of drift between data and logic

**GAP-2: Deprecated API still primary access pattern**
- `SOVEREIGN_TERRITORIES` and `ROOT_WHITELIST` are marked deprecated but heavily used
- New `territories.py` API (`get_territory_metadata`, `get_all_territories`) is underutilized
- Impact: Technical debt, inconsistency in codebase

**GAP-3: Operational config scattered**
- `HEALING_CONFIG`, `AGENT_RESILIENCE_CONFIG`, `MISSION_CONFIG`, `GRAVITY_CONFIG`, `MCP_CAPABILITIES` in _constants.py
- Should live in `governance.py` or dedicated config modules
- Impact: Poor separation of concerns, config drift risk

**GAP-4: Downstream files bypass new API**
- 185 files import directly from `_constants.py` instead of using `territories.py`
- Pattern includes: `_verify.py`, `hierarchy_healer.py`, `location_validator.py`, `ssot.py`, `derived.py`, etc.
- Impact: New API adoption blocked, circular dependency risk

---

## Execution Plan

### Phase 1a — Extract Territory Data to JSON
**Scope**: Move the territory definitions (the actual data) from Python dicts to a JSON file

**Commands**:
```bash
# Create data directory for SSOT
mkdir -p agentic_core/L5_safety/config/structure_blueprint/data

# Verify JSON structure
python -c "import json; json.load(open('agentic_core/L5_safety/config/structure_blueprint/data/territories.json'))"
```

**Acceptance**:
- [ ] `territories.json` exists with validated schema
- [ ] `_constants.py` still works (backward compatibility shim)
- [ ] All existing tests pass

### Phase 1b — Refactor Builder Functions
**Scope**: Move `_build_lcd_subfolders_template`, `_build_layer_definition`, `_deep_freeze` to `_builders.py`

**Commands**:
```bash
# Create builders module
touch agentic_core/L5_safety/config/structure_blueprint/_builders.py

# Verify imports work
python -c "from agentic_core.L5_safety.config.structure_blueprint._builders import build_sovereign_territories"
```

**Acceptance**:
- [ ] `_builders.py` contains all builder functions
- [ ] `_constants.py` imports from `_builders.py`
- [ ] No functional changes to output

### Phase 2a — Consolidate Operational Config
**Scope**: Move `HEALING_CONFIG`, `AGENT_RESILIENCE_CONFIG`, `MISSION_CONFIG`, `GRAVITY_CONFIG`, `MCP_CAPABILITIES` to `governance.py`

**Commands**:
```bash
# Update governance.py exports
python -c "from agentic_core.L5_safety.config.structure_blueprint.governance import HEALING_CONFIG, GRAVITY_CONFIG"

# Run guardian tests
python -m pytest tests/unit/agentic_core/L5_safety/config/ -v --tb=short
```

**Acceptance**:
- [ ] All config constants accessible from `governance.py`
- [ ] `_constants.py` re-exports from `governance.py` for backward compatibility
- [ ] Tests pass

### Phase 2b — Clean Up Trace Emitters
**Scope**: Remove duplicate lifecycle trace emitter calls from `_constants.py` and `territories.py` (keep only in `territories.py`)

**Commands**:
```bash
# Verify no duplicate emitters
python -c "
from agentic_core.L5_safety.config.structure_blueprint import territories
# Should not import _constants emitters
"
```

**Acceptance**:
- [ ] Only one set of trace emitters (in territories.py)
- [ ] ADG edge counts maintained

### Phase 3a — Migrate structure_blueprint Package
**Scope**: Update all files in `structure_blueprint/` to use `territories.py` API

**Files**:
- `ssot.py` - Replace SOVEREIGN_TERRITORIES.get() with get_territory_metadata()
- `derived.py` - Use get_all_territories() instead of direct dict access
- `_verify.py` - Use territory lookup functions

**Commands**:
```bash
# Run package tests
python -m pytest tests/unit/agentic_core/L5_safety/config/structure_blueprint/ -v
```

**Acceptance**:
- [ ] No direct `SOVEREIGN_TERRITORIES` access in package
- [ ] All tests pass

### Phase 3b — Update __init__.py Exports
**Scope**: Ensure `__init__.py` exports new API clearly, deprecates old patterns

**Commands**:
```bash
# Verify clean imports
python -c "
from agentic_core.L5_safety.config.structure_blueprint import get_territory_metadata, get_all_territories
print('OK')
"
```

**Acceptance**:
- [ ] New API easily accessible
- [ ] Deprecation warnings for old patterns

### Phase 4a — Migrate High-Impact Downstream Files
**Scope**: Top 20 files by import count

**Priority list**:
1. `hierarchy_healer.py` (10 imports)
2. `location_validator.py` (10 imports)
3. `_verify.py` (17 imports)
4. `root_hygiene_healer.py` (13 imports)
5. `ssot.py` (already handled in Wave 3)
6. `classification.py`
7. `semantics.py`
8. `artifacts.py`

**Commands**:
```bash
# Run affected tests
python -m pytest tests/unit/agentic_core/L5_safety/reasoning/ -v --tb=short
```

**Acceptance**:
- [ ] All high-impact files migrated
- [ ] Tests pass

### Phase 4b — Bulk Migrate Remaining Files
**Scope**: Remaining ~165 files using automated pattern replacement

**Commands**:
```bash
# Generate migration report
python tools/adg/migrate_territory_imports.py --dry-run --output=territory_migration_report.json

# Apply migrations
python tools/adg/migrate_territory_imports.py --apply
```

**Acceptance**:
- [ ] Zero direct `SOVEREIGN_TERRITORIES` imports outside structure_blueprint/
- [ ] All tests pass
- [ ] Migration report generated

---

## Rules

1. **Backward compatibility**: Maintain re-exports from `_constants.py` until Wave 4 completes
2. **No functional changes**: Only refactoring, no behavior changes
3. **Test coverage**: Every wave must pass existing tests
4. **Pattern consistency**: Use `get_territory_metadata()` for single lookup, `get_all_territories()` for iteration
5. **SSOT preservation**: Territory data must remain single-source in JSON after Wave 1

---

## Success Criteria

- [ ] `_constants.py` under 500 lines (target: ~400 lines)
- [ ] Territory data in JSON format, loaded at runtime
- [ ] Builder functions in separate `_builders.py` module
- [ ] Operational config consolidated in `governance.py`
- [ ] New `territories.py` API adopted by all downstream files
- [ ] Zero imports of `SOVEREIGN_TERRITORIES` from outside structure_blueprint/
- [ ] All existing tests pass
- [ ] ADG edge counts maintained (no P0/P1/P2/P3/P4 regressions)

---

## Implementation Commands

```bash
# Wave 1: Data extraction
python tools/adg/extract_territory_data.py --output=agentic_core/L5_safety/config/structure_blueprint/data/territories.json

# Wave 2: Config consolidation
python tools/adg/consolidate_governance_config.py --source=_constants.py --target=governance.py

# Wave 3: Package migration
python tools/adg/migrate_package_to_new_api.py --package=structure_blueprint

# Wave 4: Downstream migration
python tools/adg/migrate_territory_imports.py --apply --scope=all

# Final verification
python -m pytest tests/unit/agentic_core/L5_safety/ -v
python ops_scripts/ci/_adg_ci_gates.py --phase=all
```

---

## Rollback Strategy

If things go wrong:
1. Restore `territories.json` from git: `git checkout HEAD -- agentic_core/L5_safety/config/structure_blueprint/data/territories.json`
2. Revert `_constants.py` to original: `git checkout HEAD -- agentic_core/L5_safety/config/structure_blueprint/_constants.py`
3. Revert downstream changes: `git checkout HEAD -- <affected_files>`
4. Verify with: `python -m pytest tests/unit/agentic_core/L5_safety/ -v`

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| _constants.py line count | < 500 lines | `wc -l agentic_core/L5_safety/config/structure_blueprint/_constants.py` |
| Territory data format | JSON | `file agentic_core/L5_safety/config/structure_blueprint/data/territories.json` |
| Downstream SOVEREIGN_TERRITORIES imports | 0 | `grep -r "SOVEREIGN_TERRITORIES" --include="*.py" agentic_core/ \| grep -v "structure_blueprint/\|_constants.py" \| wc -l` |
| Tests passing | 100% | `python -m pytest tests/unit/agentic_core/L5_safety/ -v` |
| API adoption | > 90% | `grep -r "get_territory_metadata\|get_all_territories" --include="*.py" agentic_core/ \| wc -l` vs baseline |
