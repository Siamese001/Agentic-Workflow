# Bloat Elimination Report
## Findings and Recommendations for Approved Folders

**Generated:** 2026-01-20  
**Analysis Scope:** agentic_core, apps_rg, apps_lic, apps_shared, scripts, tests, docs, schemas

---

## Executive Summary

The codebase contains **significant bloat** in approved folders, primarily concentrated in:
- `agentic_core/L0_maintenance/scripts/` - **403 files** (1.59 MB) - largest single folder
- `agentic_core/L5_safety/validators/` - **154 files** (1.93 MB) - includes misplaced test files
- `scripts/` - **51 files** - many one-time migration/archive utilities

**Total Python files in agentic_core:** 1,317 files (7.30 MB)  
**Total agents discovered:** 201 agents

### Key Findings

| Category | Count | Impact |
|----------|-------|--------|
| Files with deprecation markers | 198 | HIGH - Should be archived |
| Empty/stub files (<5 code lines) | 65+ | MEDIUM - Dead code |
| Test files outside tests/ | 74 | MEDIUM - Misplaced |
| Duplicate filenames | 15+ | LOW - Confusion risk |
| One-time migration scripts | 30+ | MEDIUM - No longer needed |

---

## Detailed Findings

### 1. L0_maintenance/scripts Bloat (CRITICAL)

**Current State:** 403 Python files in a single folder  
**Expected:** <50 active maintenance scripts

#### Breakdown by Prefix:
| Prefix | Count | Recommendation |
|--------|-------|----------------|
| `utilities_*` | 41 | Archive - one-time utilities |
| `check_*` | 33 | Review - many are obsolete |
| `test_*` | 28 | Move to tests/ folder |
| `fix_*` | 19 | Archive - one-time fixes |
| `analyze_*` | 16 | Archive - analysis complete |
| `guard_*` | 5 | Keep - active guardrails |
| `batch_*` | 3 | Archive - migration complete |
| Other | 255 | Review individually |

#### Files to Archive (High Confidence):
```
agentic_core/L0_maintenance/scripts/analyze_consolidation.py
agentic_core/L0_maintenance/scripts/analyze_heal_invocation.py
agentic_core/L0_maintenance/scripts/analyze_mcp_hardening.py
agentic_core/L0_maintenance/scripts/analyze_remaining_mcp_gaps.py
agentic_core/L0_maintenance/scripts/analyze_test_coverage.py
agentic_core/L0_maintenance/scripts/analyze_typing_docs.py
agentic_core/L0_maintenance/scripts/batch_fix_9_agents.py
agentic_core/L0_maintenance/scripts/check_agent_data_staleness.py
agentic_core/L0_maintenance/scripts/check_all_rows_health_vs_quality.py
agentic_core/L0_maintenance/scripts/check_base_agents.py
agentic_core/L0_maintenance/scripts/check_base_classes.py
agentic_core/L0_maintenance/scripts/check_current_sort_order.py
```

### 2. Files with Deprecation Markers (198 files)

Files explicitly marked as DEPRECATED, LEGACY, or OBSOLETE:

#### High Priority Archives:
```
agentic_core/common/healing/healer_mixin.py - DEPRECATED
agentic_core/config/blueprint_sovereign/config_models.py - DEPRECATED
agentic_core/config/blueprint_sovereign/constants.py - LEGACY
agentic_core/config/blueprint_sovereign/core_contracts.py - LEGACY
agentic_core/L0_maintenance/scripts/analyze_discovery.py - DEPRECATED
agentic_core/L0_maintenance/scripts/analyze_duplicates_simple.py - DEPRECATED
agentic_core/L0_maintenance/scripts/archive_migration_analysis.py - OBSOLETE
agentic_core/L0_maintenance/scripts/bulk_hierarchy_heal.py - LEGACY
agentic_core/L0_maintenance/scripts/find_misnamed_agents.py - DEPRECATED
agentic_core/L0_maintenance/scripts/find_non_conforming_agents.py - DEPRECATED
agentic_core/L0_maintenance/scripts/guard_ddd_alignment.py - DEPRECATED
agentic_core/L0_maintenance/scripts/guard_no_hardcoded_config.py - DEPRECATED
agentic_core/L0_maintenance/scripts/healing_healing_engine.py - LEGACY
agentic_core/L0_maintenance/scripts/mark_deprecated_tests.py - DEPRECATED
agentic_core/L0_maintenance/scripts/reset_sovereign_state.py - LEGACY
agentic_core/L0_maintenance/scripts/run_cleanup.py - DEPRECATED
agentic_core/L0_maintenance/scripts/scan_hardcoded_paths.py - DEPRECATED
agentic_core/L0_maintenance/scripts/show_manual_review_files.py - DEPRECATED
```

### 3. Test Files Outside tests/ (74 files)

Test files should be in `tests/` folder, not scattered in production code:

#### In L0_maintenance/scripts (28 files):
```
test_agent_discovery_volatility.py
test_base_class_enforcer.py
test_capability_enforcement.py
test_code_dedup_comprehensive.py
test_code_dedup_fuzzy.py
test_cognitive_recovery_mixin.py
test_corrected_meta_learning.py
test_dashboard_drilldown.py
test_dashboard_generation.py
test_dashboard_playwright_visual.py
test_dashboard_snapshot_regression.py
test_dashboard_visual.py
test_healing_execution.py
test_mcp_hardening_playwright.py
test_meta_learning_recording.py
test_mro_propagation.py
test_orchestration.py
test_orchestrator_cognitive_recovery.py
test_orchestrator_execution_with_cognitive.py
test_phase3_phase4_frontend.py
... and 8 more
```

#### In L5_safety/validators (12 files):
```
test_backup_folder_ssot_compliance.py (14.5 KB)
test_base_agent_naming.py (7.6 KB)
test_dashboard_categories.py (13.0 KB)
test_dashboard_data_integrity.py (21.0 KB)
test_dashboard_end_to_end.py (154.0 KB) ← LARGEST
test_discovery_roster_builder.py (18.4 KB)
test_healer_mixin_heal_repository.py (8.7 KB)
test_health_score_validation.py (7.5 KB)
test_hierarchy_agent_root_healing.py (21.1 KB)
test_l4_structure_validation.py (19.2 KB)
test_table_column_rendering.py (6.9 KB)
test_toxic_hub_mission.py (7.6 KB)
```

### 4. scripts/ Folder Archive Candidates (30 files)

One-time migration and archive utilities no longer needed:

#### Archive Utilities (10 files):
```
scripts/archive_consolidated_agents.py
scripts/archive_consolidation_report_agents.py
scripts/archive_legacy_orchestrators.py
scripts/archive_legacy_validators.py
scripts/archive_phase3_legacy_agents.py
scripts/archive_phase4_legacy_agents.py
scripts/restore_all_archived_agents.py
scripts/restore_app_agents.py
scripts/restore_void_agents.py
scripts/scan_archives_for_restoration.py
```

#### Batch Migration Scripts (6 files):
```
scripts/phase4_batch1_ast_decorator.py
scripts/phase4_batch1_decorator_sweep.py
scripts/phase4_batch1_decorator_sweep_v2.py
scripts/phase4_batch1_hardened_ast.py
scripts/phase4_batch4_base_class_cleanup.py
scripts/phase4_batch4_mro_cleanup.py
```

#### Import Migration Scripts (3 files):
```
scripts/update_orchestrator_imports.py
scripts/update_phase3_imports.py
scripts/update_validator_imports.py
```

### 5. Empty/Stub Files (65+ files)

Files with <1KB or <5 lines of actual code:

```
agentic_core/L0_maintenance/scripts/diag_tool_1766880209.py
agentic_core/L0_maintenance/scripts/tooling_fix_final.py
agentic_core/L1_cognition/thought_engine/agent_capabilities.py
agentic_core/L1_cognition/thought_engine/test_action_registry.py
agentic_core/L2_execution/ToolRegistry/P4_agents___init__.py
agentic_core/L2_execution/ToolRegistry/definitions.py
agentic_core/L2_execution/ToolRegistry/sandbox___init__.py
agentic_core/L3_orchestration/workflow_engines/S3_vitality___init__.py
agentic_core/L4_state/ValidationContext/cache___init__.py
```

### 6. Duplicate Agent Names

```
NamingAgent:
  - apps_rg/engines/NamingAgent.py
  - agentic_core/L5_safety/validators/NamingAgent.py
```

### 7. Large Files (>100KB)

Files that may need splitting or review:

| Size | Lines | File |
|------|-------|------|
| 154.0 KB | ~4000 | L5_safety/validators/test_dashboard_end_to_end.py |
| 89.7 KB | ~2500 | L5_safety/validators/structure_blueprint.py |
| 80.1 KB | ~2000 | L5_safety/validators/LocationAgent.py |
| 49.9 KB | ~1300 | L5_safety/validators/HierarchyAgent.py |

---

## Implementation Plan

### Phase 1: Quick Wins (Day 1) - ~200 files

**Goal:** Archive clearly deprecated/obsolete files

1. **Archive deprecated L0 scripts** (estimated 50 files)
   ```bash
   # Create archive folder
   mkdir -p archives/deprecated_l0_scripts_2026_01
   
   # Move files with DEPRECATED/OBSOLETE markers
   # See list above
   ```

2. **Archive one-time migration scripts** (19 files)
   ```bash
   mkdir -p archives/migration_scripts_2026_01
   mv scripts/phase4_batch*.py archives/migration_scripts_2026_01/
   mv scripts/update_*_imports.py archives/migration_scripts_2026_01/
   mv scripts/archive_*.py archives/migration_scripts_2026_01/
   mv scripts/restore_*.py archives/migration_scripts_2026_01/
   ```

3. **Archive empty/stub files** (10 files)
   ```bash
   mkdir -p archives/empty_stubs_2026_01
   # Move files with 0 code lines
   ```

### Phase 2: Test File Relocation (Day 2) - ~74 files

**Goal:** Move test files to proper tests/ folder

1. **Create test subdirectories**
   ```bash
   mkdir -p tests/l0_maintenance
   mkdir -p tests/l5_validators
   mkdir -p tests/dashboard
   ```

2. **Move L0 test files** (28 files)
   ```bash
   mv agentic_core/L0_maintenance/scripts/test_*.py tests/l0_maintenance/
   ```

3. **Move L5 test files** (12 files)
   ```bash
   mv agentic_core/L5_safety/validators/test_*.py tests/l5_validators/
   ```

4. **Update imports** in moved test files

### Phase 3: L0_maintenance Cleanup (Day 3-4) - ~150 files

**Goal:** Reduce L0_maintenance/scripts from 403 to <100 files

1. **Archive `utilities_*` files** (41 files)
   - Review each for active usage
   - Archive those not imported elsewhere

2. **Archive `check_*` files** (33 files)
   - Keep only actively used checks
   - Archive one-time validation scripts

3. **Archive `analyze_*` files** (16 files)
   - These are typically one-time analysis scripts

4. **Archive `fix_*` files** (19 files)
   - One-time fixes should be archived

### Phase 4: Consolidation Review (Day 5)

**Goal:** Identify remaining consolidation opportunities

1. **Review duplicate NamingAgent**
   - Determine which is canonical
   - Archive or merge the other

2. **Review large files for splitting**
   - `test_dashboard_end_to_end.py` (154 KB)
   - `structure_blueprint.py` (89 KB)
   - `LocationAgent.py` (80 KB)

3. **Clean up unused imports**
   - 30 files have 7+ unused imports
   - Run automated cleanup

---

## Expected Results

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| L0_maintenance/scripts | 403 files | ~100 files | 75% |
| Test files outside tests/ | 74 files | 0 files | 100% |
| Files with deprecation markers | 198 files | ~50 files | 75% |
| scripts/ folder | 51 files | ~20 files | 60% |
| **Total agentic_core** | **1,317 files** | **~900 files** | **~30%** |

---

## Verification Steps

After each phase:

1. **Run agent discovery**
   ```bash
   python scripts/full_agent_discovery.py --force
   ```
   - Verify agent count remains stable (201 agents)

2. **Run test suite**
   ```bash
   pytest tests/ -v
   ```
   - Ensure no tests break

3. **Check imports**
   ```bash
   python -c "import agentic_core"
   ```
   - Verify no import errors

---

## Risk Mitigation

1. **All archives are reversible** - Files moved to `archives/` with dated folders
2. **Git history preserved** - Use `git mv` for moves
3. **Incremental approach** - One phase at a time with verification
4. **Backup before each phase** - Create git tag before major changes

---

## Files to KEEP (Do Not Archive)

Critical infrastructure that should NOT be archived:

```
# Core discovery
scripts/full_agent_discovery.py

# Active test runners
scripts/test_dashboard_e2e.py

# Active audits
scripts/audit_residual_rglob.py
scripts/bloat_analysis.py

# L0 Base Agents
agentic_core/L0_maintenance/scripts/L0MaintenanceBaseAgent.py

# Structure Blueprint (SSOT)
agentic_core/L5_safety/validators/structure_blueprint.py
```

---

## Appendix: Full File Lists

See `audit_residual_rglob_results.json` for complete file listings.

Run `python scripts/bloat_analysis.py` for updated statistics.
