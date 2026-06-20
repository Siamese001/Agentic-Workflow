---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\streamline-constants-waves3-4-migration-d0cb16.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\streamline-constants-waves3-4-migration-d0cb16.md'
source_sha256: 95f1e1a473775e062cda46305491aa67c6dc97ab4bcc57a32d4f1ed2486858f5
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Streamline _constants.py — Waves 3 & 4 Migration Plan

Migrate all downstream consumers (~94 files) from direct `SOVEREIGN_TERRITORIES`/`ROOT_WHITELIST` access to the new `territories.py` API, completing the streamlining of enforced territories.

---

## Wave Structure

| Wave | Micro-Waves | Files | Focus | Est. Tokens | Status |
|------|-------------|-------|-------|-------------|--------|
| Wave 3 | 3a, 3b, 3c, 3d | 9 files | Internal package migration (structure_blueprint/) | 15,000 | 🟡 YELLOW |
| Wave 4.1 | 4.1a-4.1d | 20 files | High-impact downstream (healers, validators, governors) | 20,000 | 🟡 YELLOW |
| Wave 4.2 | 4.2a-4.2e | 35 files | Medium-impact (agents, enforcers, scripts) | 25,000 | 🟡 YELLOW |
| Wave 4.3 | 4.3a-4.3f | 30 files | Remaining files (utils, config, misc) | 20,000 | 🟡 YELLOW |

**Total: ~80,000 tokens across 4 waves + 17 micro-waves**

---

## Gap Register

**GAP-1: Internal package uses deprecated API**
- `ssot.py`, `derived.py`, `_verify.py`, `__init__.py` still import from `_constants.py` directly
- These should use `territories.py` API for consistency
- Impact: Circular dependency risk, inconsistent patterns

**GAP-2: 94 downstream files bypass new API**
- Files across L0-L6 layers import `SOVEREIGN_TERRITORIES` directly
- No adoption of `get_territory_metadata()`, `get_all_territories()`
- Impact: Technical debt, new API underutilized

**GAP-3: High-impact files have heavy usage**
- `location_validator.py`: 16 matches
- `hierarchy_healer.py`: 10 matches  
- `root_hygiene_healer.py`: 13 matches
- Changes here have high blast radius
- Impact: Risk of regression if not carefully migrated

**GAP-4: Tests may depend on old import patterns**
- Test files may mock or depend on `_constants` imports
- Need verification post-migration
- Impact: Test failures if imports change

---

## Execution Plan

### Wave 3 — Internal Package Migration

#### Micro-Wave 3a — ssot.py Migration
**Scope**: Update `ssot.py` to use `territories.py` API

**Files**: `agentic_core/L5_safety/config/structure_blueprint/ssot.py`

**Changes**:
- Replace `from ._constants import ROOT_WHITELIST` with `from .territories import get_all_territories, is_valid_root_folder`
- Update `ROOT_WHITELIST` references to use `frozenset(get_all_territories().keys())`
- Add deprecation warning re-export for backward compatibility

**Commands**:
```bash
python -c "from agentic_core.L5_safety.config.structure_blueprint.ssot import ROOT_WHITELIST; print('OK')"
python -m pytest tests/unit/agentic_core/L5_safety/config/structure_blueprint/ -v --tb=short
```

**Acceptance**:
- [ ] `ssot.py` imports from `territories.py` not `_constants.py`
- [ ] All exports still functional
- [ ] Tests pass

#### Micro-Wave 3b — derived.py Migration
**Scope**: Update `derived.py` to use `territories.py` API

**Files**: `agentic_core/L5_safety/config/structure_blueprint/derived.py`

**Changes**:
- Replace `from .territories import get_all_territories` (already using)
- Ensure no direct `SOVEREIGN_TERRITORIES` access
- Update any remaining `_constants` imports

**Commands**:
```bash
python -c "from agentic_core.L5_safety.config.structure_blueprint.derived import get_derived_registry; print('OK')"
```

**Acceptance**:
- [ ] No direct `SOVEREIGN_TERRITORIES` access
- [ ] All imports from `territories.py` or `ssot.py`

#### Micro-Wave 3c — __init__.py Export Cleanup
**Scope**: Update `__init__.py` to prioritize new API exports

**Files**: `agentic_core/L5_safety/config/structure_blueprint/__init__.py`

**Changes**:
- Reorder exports: new API first, deprecated exports last
- Add deprecation warnings for `SOVEREIGN_TERRITORIES` and `ROOT_WHITELIST` exports
- Document migration path in docstring

**Commands**:
```bash
python -c "
from agentic_core.L5_safety.config.structure_blueprint import get_territory_metadata, get_all_territories
print('New API OK')
"
```

**Acceptance**:
- [ ] New API exports clearly documented
- [ ] Deprecation warnings present for old API
- [ ] All existing imports still work (backward compatibility)

#### Micro-Wave 3d — _verify.py Migration
**Scope**: Update `_verify.py` to use `territories.py` API

**Files**: `agentic_core/L5_safety/config/structure_blueprint/_verify.py`

**Changes**:
- Replace 17 matches of `SOVEREIGN_TERRITORIES` with `get_all_territories()`
- Update import statements
- Ensure verify functions use new API

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/config/structure_blueprint/_verify* -v
```

**Acceptance**:
- [ ] `_verify.py` uses `get_all_territories()` not `SOVEREIGN_TERRITORIES`
- [ ] All verify functions operational
- [ ] Tests pass

---

### Wave 4.1 — High-Impact Downstream Migration (20 files)

#### Micro-Wave 4.1a — Healers Batch (3 files)
**Scope**: Migrate high-impact healing agents

**Files**:
- `agentic_core/L5_safety/reasoning/hierarchy_healer.py` (10 matches)
- `agentic_core/L5_safety/reasoning/root_hygiene_healer.py` (13 matches)
- `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` (2 matches)

**Changes**:
- Replace `from ..._constants import SOVEREIGN_TERRITORIES` with `from ...territories import get_all_territories`
- Update dictionary access: `SOVEREIGN_TERRITORIES[name]` → `get_territory_metadata(name)`
- Update iteration: `SOVEREIGN_TERRITORIES.items()` → `get_all_territories().items()`

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/reasoning/ -v -k "healer" --tb=short
```

**Acceptance**:
- [ ] All 3 healers migrated
- [ ] Healing tests pass
- [ ] No regression in healing functionality

#### Micro-Wave 4.1b — Validators Batch (3 files)
**Scope**: Migrate validator modules

**Files**:
- `agentic_core/L5_safety/reasoning/location_validator.py` (16 matches)
- `agentic_core/L5_safety/validators/gravity_validator.py` (2 matches)
- `agentic_core/L5_safety/utils/validate_path_ssot_util.py` (5 matches)

**Changes**:
- Update imports to use `territories.py` API
- Replace direct dict access with API calls
- Maintain validation logic

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/validators/ -v --tb=short
```

**Acceptance**:
- [ ] All validators migrated
- [ ] Validation logic preserved
- [ ] Tests pass

#### Micro-Wave 4.1c — Governors & Architects (4 files)
**Scope**: Migrate governance agents

**Files**:
- `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` (6 matches)
- `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py` (2 matches)
- `agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py` (2 matches)
- `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` (11 matches)

**Changes**:
- Migrate to `territories.py` API
- Ensure governance logic uses new API

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/reasoning/ -v -k "governor or architect or inspector" --tb=short
```

**Acceptance**:
- [ ] All governance agents migrated
- [ ] Governance tests pass

#### Micro-Wave 4.1d — Core Config & Path Constants (4 files)
**Scope**: Migrate core configuration files

**Files**:
- `agentic_core/L5_safety/config/structure_blueprint_config.py` (15 matches)
- `agentic_core/L0_routing/config/path_constants.py` (7 matches)
- `agentic_core/config/core/registry_config.py` (3 matches)
- `agentic_core/L1_cognition/utils/constants_util.py` (2 matches)

**Changes**:
- Update to use `territories.py` API
- These have many imports - careful migration

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L0_routing/config/ -v --tb=short
python -m pytest tests/unit/agentic_core/config/ -v --tb=short
```

**Acceptance**:
- [ ] Core config files migrated
- [ ] No circular import issues
- [ ] Tests pass

#### Micro-Wave 4.1e — Test Generators & Utils (6 files)
**Scope**: Migrate test generators and utilities

**Files**:
- `agentic_core/L5_safety/reasoning/TestGeneratorAgent.py` (2 matches)
- `agentic_core/L5_safety/utils/location_path_util.py` (3 matches)
- `agentic_core/L5_safety/utils/location_utils_util.py` (3 matches)
- `agentic_core/L5_safety/utils/extract_pattern_util.py` (1 match)
- `agentic_core/runtime/utils/sovereign_index_util.py` (2 matches)
- `agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py` (3 matches)

**Changes**:
- Migrate utilities to new API
- Update helper functions

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/utils/ -v --tb=short
```

**Acceptance**:
- [ ] All utilities migrated
- [ ] Helper functions work

---

### Wave 4.2 — Medium-Impact Migration (35 files)

#### Micro-Wave 4.2a — Enforcement Batch 1 (7 files)
**Files**: airlock_guardrail.py, airlock_trimmer_enforcer.py, cache_guard.py, logs_guard.py, ssot_guardrail.py, ssot_scanner_enforcer.py, ssot_import_enforcer.py

**Changes**: Update imports, use new API

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/enforcement/ -v --tb=short -x
```

#### Micro-Wave 4.2b — Enforcement Batch 2 (7 files)
**Files**: archival_gatekeeper_gate.py, critical_dual_enforcement_audit_enforcer.py, hardcoded_path_refactorer_enforcer.py, healing_invocation_audit_enforcer.py, import_surgeon_enforcer.py, mission_utils_enforcer.py, mock_context_enforcer.py

**Changes**: Update imports, use new API

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/enforcement/ -v --tb=short -x
```

#### Micro-Wave 4.2c — Enforcement Batch 3 (7 files)
**Files**: module_collision_guardrail.py, namespace_medic_enforcer.py, phase_acceptance_guardrail.py, registry_verification_enforcer.py, credential_guard.py, ssot_structure_validation_enforcer.py, gravity_validator.py

**Changes**: Update imports, use new API

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/enforcement/ -v --tb=short -x
```

#### Micro-Wave 4.2d — Agents Batch (7 files)
**Files**: GravityLeakRepairAgent.py, GenerativeGuardAgent.py, _simulate_verify.py, _ssot_pipeline.py, _ssot_phases.py, align_tests_structure_util.py, run_guardian_hierarchy_compliance.py

**Changes**: Update imports, use new API

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/reasoning/ -v --tb=short -x
```

#### Micro-Wave 4.2e — Scripts & L0 Batch (7 files)
**Files**: run_guardian_hygiene.py, run_hygiene_guardian_util.py, run_guardian_location_alignment.py, L0_routing/config/__init__.py, L0_routing/scripts/README_STOPPABLE_SERVERS.md, L2_execution/enforcement/sovereign_filesystem_mcp.py, L5_safety/config/blueprint_compiler.py

**Changes**: Update imports, use new API

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L0_routing/ -v --tb=short
```

---

### Wave 4.3 — Remaining Files (30 files)

#### Micro-Wave 4.3a — Utils Batch 1 (5 files)
**Files**: Various utility files with 1-2 matches each

#### Micro-Wave 4.3b — Utils Batch 2 (5 files)
**Files**: Additional utility files

#### Micro-Wave 4.3c — Config Batch (5 files)
**Files**: Remaining config files

#### Micro-Wave 4.3d — Types & Enums (5 files)
**Files**: Type definition files

#### Micro-Wave 4.3e — Integration (5 files)
**Files**: Integration adapters

#### Micro-Wave 4.3f — Cleanup & Verification (5 files)
**Files**: Final remaining files + verification

---

## Rules

1. **Backward Compatibility**: Maintain re-exports so existing imports don't break
2. **No Functional Changes**: Only change import patterns, not behavior
3. **Test Coverage**: Every micro-wave must have tests passing
4. **Incremental**: Complete one micro-wave before starting next
5. **ADG Regeneration**: Run `python tools/generate_full_adg.py` after each wave
6. **No Circular Imports**: Ensure territories.py doesn't import from files that import it

---

## Success Criteria

- [ ] All 9 structure_blueprint/ files use new API (Wave 3)
- [ ] All 94 downstream files migrated (Wave 4)
- [ ] Zero imports of `SOVEREIGN_TERRITORIES` from outside `_constants.py`
- [ ] All existing tests pass
- [ ] New API adoption > 95% across codebase
- [ ] ADG edge counts maintained (no P0/P1/P2/P3/P4 regressions)

---

## Implementation Commands

```bash
# Wave 3: Internal package
python tools/adg/migrate_to_new_api.py --scope=structure_blueprint --dry-run
python tools/adg/migrate_to_new_api.py --scope=structure_blueprint --apply

# Wave 4.1: High-impact
python tools/adg/migrate_to_new_api.py --files=hierarchy_healer.py,root_hygiene_healer.py,location_validator.py --apply

# Wave 4.2: Medium-impact
python tools/adg/migrate_to_new_api.py --batch=medium --apply

# Wave 4.3: Remaining
python tools/adg/migrate_to_new_api.py --batch=remaining --apply

# Final verification
python -m pytest tests/unit/agentic_core/ -v --tb=short
python ops_scripts/ci/_adg_ci_gates.py --phase=all
```

---

## Rollback Strategy

If things go wrong:
1. Git restore: `git checkout HEAD -- agentic_core/L5_safety/config/structure_blueprint/`
2. Downstream restore: `git checkout HEAD -- <affected_files>`
3. Verify: `python -m pytest tests/unit/agentic_core/ -v`

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| SOVEREIGN_TERRITORIES imports | 0 | `grep -r "SOVEREIGN_TERRITORIES" --include="*.py" agentic_core/ \| grep -v "_constants.py" \| wc -l` |
| New API adoption | > 95% | `grep -r "get_territory_metadata\|get_all_territories" --include="*.py" agentic_core/ \| wc -l` |
| Tests passing | 100% | `python -m pytest tests/unit/agentic_core/ -v` |
| ADG edge count delta | 0 | Compare ADG before/after |

