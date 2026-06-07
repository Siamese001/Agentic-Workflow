# Artifacts Directory Reorganization Plan

**Date:** 2026-04-06  
**Purpose:** Recursive review and reorganization of `C:\Git\Agentic-Workflow\artifacts`  
**Goal:** Eliminate dead code, organize high/low signal files, ensure no root-level files

---

## EXECUTIVE SUMMARY

The artifacts directory contains 115 root-level files and 44 subdirectories. Major issues identified:

1. **Dead Code:** 4 duplicate/obsolete ADG directories consuming space
2. **Root File Clutter:** 115 files scattered at root (should be 0)
3. **Poor Signal Separation:** High and low signal files mixed together
4. **Missing Organization:** No dedicated directories for ADG analysis, wave reports, test artifacts

**Impact:** ~191.35 MB total size, significant cleanup potential

---

## CURRENT STRUCTURE ANALYSIS

### Root-Level Files (115 files) - PROBLEM

**Size Distribution:**
- >10 MB: 4 files (adg_test_surface_map.json, adg_semantic_graph.json, adg_test_classification.json, wave6a_validation_report.json)
- 1-10 MB: 18 files
- <1 MB: 93 files

**File Categories:**
1. **ADG Analysis (HIGH SIGNAL)** - 8 files, ~133 MB
   - adg_test_surface_map.json (67.37 MB)
   - adg_semantic_graph.json (41.78 MB)
   - adg_test_classification.json (16.96 MB)
   - test_surface_inventory.json (1019.92 KB)
   - ast_test_collection_results.json (1003.28 KB)
   - current_skip_analysis.json (1003.28 KB)
   - test_inventory.json (944.69 KB)
   - adg_scoped_test_files.txt (5.19 KB)

2. **Wave Reports (HIGH SIGNAL)** - 25 files, ~20 MB
   - wave1a_inventory_report.json (4.09 MB)
   - wave6a_validation_report.json (12.22 MB)
   - wave1b_classification_report.json (340 KB)
   - wave1d_categorization_report.json (839.85 KB)
   - wave2a_removal_report.json (12.90 KB)
   - wave2b_removal_report.json (904 B)
   - wave2c_removal_report.json (33.29 KB)
   - wave3a_restoration_report.json (2.48 KB)
   - wave3b_restoration_report.json (3.60 KB)
   - wave3c_restoration_report.json (3.99 KB)
   - wave4a_reduction_report.json (923 B)
   - wave4b_reduction_report.json (925 B)
   - wave4b_conversion_results.json (59.38 KB)
   - wave4ch_conversion_results.json (682.12 KB)
   - wave5a_hardening_report.json (15.77 KB)
   - wave5b_hardening_report.json (1.36 KB)
   - wave5bh_improvement_results.json (92.92 KB)
   - wave5c_hardening_report.json (204.61 KB)
   - wave6bh_finalization_results.json (1.19 KB)
   - wave7a_syntax_fix_results.json (9.76 KB)
   - wave7a_ci_hardening_report.json (2.89 KB)
   - wave7b_multi_environment_report.json (1.22 KB)
   - wave7c_collection_fix_results.json (1.47 MB)
   - wave7_final_completion_report.json (1.49 KB)

3. **Test Artifacts (MEDIUM SIGNAL)** - 30 files, ~15 MB
   - all_errors_raw.txt (2.92 MB)
   - test_collect_errors.txt (2.04 MB)
   - collection_safety_phase1.json (1.93 MB)
   - collection_safety.json (1.93 MB)
   - collection_verbose.txt (1.90 MB)
   - test_collect_clean.txt (1.90 MB)
   - wave7c_collection_fix_results.json (1.47 MB)
   - adg_failure_clusters.json (1.17 MB)
   - test_quality_analysis.json (1.03 MB)
   - collection_safety_phase1.json (1.93 MB)
   - test_suite_output.txt (201.67 KB)
   - test_full_output.txt (138.60 KB)
   - test_full_clean.txt (130.34 KB)
   - test_errors_clean.txt (129.96 KB)
   - test_output.txt (21.77 KB)
   - test_run_output.txt (11.65 KB)
   - collection_error_categories.json (6.21 KB)
   - collection_errors_raw.txt (830.97 KB)
   - collection_raw.txt (830.97 KB)
   - col_raw.txt (830.98 KB)
   - unit_errors_raw.txt (830.28 KB)
   - unit_errors_tbno.txt (819.82 KB)
   - unit67.txt (826.23 KB)
   - unit_collect.txt (635.65 KB)
   - unit_errors_full.txt (635.65 KB)
   - agentic_core_errors.txt (800.55 KB)
   - ac_errors.txt (800.55 KB)
   - collection_errors.txt (0 B)
   - test_errors_detail.txt (0 B)

4. **SSOT Scans (HIGH SIGNAL)** - 3 files, ~8 MB
   - ssot_violation_scan.json (6.57 MB)
   - hardcoded_path_scan.json (1.09 MB)
   - .schema_violations_tracking.yaml (5.58 KB)

5. **Guardian Analysis (HIGH SIGNAL)** - 3 files, ~9 MB
   - guardian_swallow_analysis.json (2.43 MB)
   - hollowed_tests_analysis.json (6.60 MB)
   - _guardian_adg_result.json (26.49 KB)
   - _guardian_adg_analysis.py (6.53 KB)

6. **ADG Profiles (HIGH SIGNAL)** - 10 files, ~50 KB
   - adg_e0_impact_profile.json (7.28 KB)
   - adg_zip_profile.json (7.02 KB)
   - adg_p8_v3_profile.json (6.51 KB)
   - adg_p8_v4_profile.json (4.47 KB)
   - adg_p8_v5_profile.json (3.30 KB)
   - adg_p8_v6_profile.json (3.28 KB)
   - adg_p8_v7_profile.json (618 B)
   - adg_p8_v8_e2e.json (1.43 KB)
   - adg_p8_v9_fresh_baselines.json (490 B)
   - adg_phase_profile.json (1.80 KB)
   - adg_p8_subphase_profile.json (3.16 KB)

7. **Execution/SSOT Artifacts (HIGH SIGNAL)** - 12 files, ~500 KB
   - execute_ssot_test_surface.json (447.50 KB)
   - execute_ssot_failure_chains.json (9.11 KB)
   - execute_ssot_root_clusters.json (6.18 KB)
   - execute_ssot_graph_intelligence.json (5.76 KB)
   - execute_ssot_final_report.json (4.40 KB)
   - execute_ssot_repair_log.json (4.20 KB)
   - execute_ssot_scoped_retests.json (2.66 KB)
   - execute_ssot_adg_validation.json (743 B)
   - validation_test_report.json (7.50 KB)
   - validation_enforcement_report.json (3.13 KB)
   - adg_validation_report.json (469 B)
   - sovereign_contract_guard_test_*.json (2x, 1.47 KB each)

8. **Low Signal/Temporary (LOW SIGNAL)** - 15 files, ~50 KB
   - _import_map.json (12.44 KB)
   - _import_map_v2.json (1.49 KB)
   - _scan_analyze_tmp.py (1.03 KB)
   - scan_summary_tmp.txt (1.05 KB)
   - plans_execution.txt (22.48 KB)
   - plans_rca.txt (5.15 KB)
   - plans_gap_analysis.txt (4.61 KB)
   - plans_investigation.txt (3.69 KB)
   - skip_burndown_plan.json (1.97 KB)
   - trace_emitter_inventory.json (4.45 KB)
   - agent_discovery.json (16.81 KB)
   - apps_refactor_verification.json (8.73 KB)
   - forensic_discovery_v54.json (149.27 KB)
   - path_replace_audit.json (27.80 KB)
   - eager_import_full_scan.json (91.44 KB)

9. **Other (MIXED SIGNAL)** - 9 files, ~5 MB
   - hollowed_tests_analysis.json (6.60 MB)
   - l4d_manifests.sqlite (80.00 KB)
   - dep_graph.sqlite (131 B)
   - skipped_tests_list.json (3 B)
   - cpu_benchmark_evidence.json (6.75 KB)
   - wave1_impact_analysis.json (5.13 KB)
   - ci_validation_after_fix.txt (253.12 KB)
   - ci_validation_grandfathered.txt (196.50 KB)
   - silent_swallower_report.json (via reports/)

### Subdirectory Analysis

**Well-Organized (KEEP AS-IS):**
- `reports/` - Properly structured with subdirectories (adg, assessments, audit, etc.)
- `discovery/` - Agent discovery artifacts (3 files)
- `audits/` - Architecture audit outputs (3 files)
- `analysis/` - Migration analysis (5 files)
- `architecture/` - Architecture artifacts (1 file)
- `freeze_reports/` - Freeze reports (3 files)
- `outputs/` - Output artifacts (15 files)
- `xml/` - XML files (13 files)
- `evidence/` - Evidence (minimal, just graphrag/)
- `ci/` - CI artifacts (1 file)

**Dead Code/Duplicates (REMOVE/ARCHIVE):**
1. `adg_clean/` - Old ADG files (03242026) - 6 files
2. `adg_runtime/` - Old runtime file (03242026) - 1 file
3. `adg_tools_backups/` - Old backup (04052026, older than adg/) - 18 files
4. `adg_truly_clean/` - Old backups (03242026-03312026) - 3 files

**Active (KEEP):**
- `adg/` - Current active ADG (04062026) - 16 files + subdirectories

**Other Subdirectories (KEEP AS-IS):**
- chroma*, gptcache*, l0_refactor, logs, manifests, memory, monitoring, observability, quarantine_artifacts, rollback, runtime_adg*, store, structure, windsurf, consolidation, dedup, fca_safety_gates, hitl, chatgpt_validation, generated, infrastructure, security, test_enforcement, tooling, verification, sub, environment, governance, guardian, MCP, misc, p0_waves, plans, prompt_rebaseline, assessments, convergence, graphrag, adh_integration, apps_lic, apps_rg

---

## DEAD CODE IDENTIFICATION

### Directories to Remove/Archive

| Directory | Reason | Size Estimate | Files |
|-----------|--------|---------------|-------|
| `adg_clean/` | Old ADG snapshot (03242026), superseded by adg/ | ~50 MB | 6 |
| `adg_runtime/` | Old runtime file (03242026) | ~5 MB | 1 |
| `adg_tools_backups/` | Backup from 04052026, older than current adg/ | ~100 MB | 18 |
| `adg_truly_clean/` | Old cleanup attempts (03242026-03312026) | ~15 MB | 3 |

**Total Dead Code:** ~170 MB, 28 files

### Root Files to Remove

| File | Reason | Size |
|------|--------|------|
| collection_errors.txt | 0 bytes, empty | 0 B |
| test_errors_detail.txt | 0 bytes, empty | 0 B |
| skipped_tests_list.json | 3 bytes, effectively empty | 3 B |

---

## REORGANIZATION PLAN

### New Directory Structure

```
artifacts/
├── adg/                           # KEEP - Current active ADG
├── adg_analysis/                  # NEW - ADG test surface, semantic graphs
├── wave_reports/                  # NEW - All wave-related reports
├── test_artifacts/                # NEW - Test collection outputs, error dumps
├── ssot_scans/                    # NEW - SSOT violation scans, hardcoded path scans
├── guardian_analysis/             # NEW - Guardian-related analysis
├── adg_profiles/                  # NEW - ADG performance profiles
├── execution_artifacts/           # NEW - Execute SSOT artifacts
├── low_signal/                    # NEW - Temporary scripts, old plans
├── reports/                       # KEEP - Well-structured reports
├── discovery/                     # KEEP
├── audits/                        # KEEP
├── analysis/                      # KEEP
├── architecture/                  # KEEP
├── freeze_reports/                # KEEP
├── outputs/                       # KEEP
├── xml/                           # KEEP
├── evidence/                      # KEEP
├── ci/                            # KEEP
├── [other existing dirs...]       # KEEP
└── _legacy_adg_archives/          # NEW - Archive of dead ADG directories
```

### File Moves

#### 1. Move to `adg_analysis/` (8 files, ~133 MB)
```
adg_test_surface_map.json
adg_semantic_graph.json
adg_test_classification.json
test_surface_inventory.json
ast_test_collection_results.json
current_skip_analysis.json
test_inventory.json
adg_scoped_test_files.txt
```

#### 2. Move to `wave_reports/` (25 files, ~20 MB)
```
wave1a_inventory_report.json
wave1b_classification_report.json
wave1d_categorization_report.json
wave2a_removal_report.json
wave2b_removal_report.json
wave2c_removal_report.json
wave3a_restoration_report.json
wave3b_restoration_report.json
wave3c_restoration_report.json
wave4a_reduction_report.json
wave4b_reduction_report.json
wave4b_conversion_results.json
wave4ch_conversion_results.json
wave5a_hardening_report.json
wave5b_hardening_report.json
wave5bh_improvement_results.json
wave5c_hardening_report.json
wave6a_validation_report.json
wave6bh_finalization_results.json
wave7a_syntax_fix_results.json
wave7a_ci_hardening_report.json
wave7b_multi_environment_report.json
wave7c_collection_fix_results.json
wave7_final_completion_report.json
wave1_impact_analysis.json
```

#### 3. Move to `test_artifacts/` (30 files, ~15 MB)
```
all_errors_raw.txt
test_collect_errors.txt
collection_safety_phase1.json
collection_safety.json
collection_verbose.txt
test_collect_clean.txt
adg_failure_clusters.json
test_quality_analysis.json
test_suite_output.txt
test_full_output.txt
test_full_clean.txt
test_errors_clean.txt
test_output.txt
test_run_output.txt
collection_error_categories.json
collection_errors_raw.txt
collection_raw.txt
col_raw.txt
unit_errors_raw.txt
unit_errors_tbno.txt
unit67.txt
unit_collect.txt
unit_errors_full.txt
agentic_core_errors.txt
ac_errors.txt
```

#### 4. Move to `ssot_scans/` (3 files, ~8 MB)
```
ssot_violation_scan.json
hardcoded_path_scan.json
.schema_violations_tracking.yaml
```

#### 5. Move to `guardian_analysis/` (4 files, ~9 MB)
```
guardian_swallow_analysis.json
hollowed_tests_analysis.json
_guardian_adg_result.json
_guardian_adg_analysis.py
```

#### 6. Move to `adg_profiles/` (11 files, ~50 KB)
```
adg_e0_impact_profile.json
adg_zip_profile.json
adg_p8_v3_profile.json
adg_p8_v4_profile.json
adg_p8_v5_profile.json
adg_p8_v6_profile.json
adg_p8_v7_profile.json
adg_p8_v8_e2e.json
adg_p8_v9_fresh_baselines.json
adg_phase_profile.json
adg_p8_subphase_profile.json
```

#### 7. Move to `execution_artifacts/` (12 files, ~500 KB)
```
execute_ssot_test_surface.json
execute_ssot_failure_chains.json
execute_ssot_root_clusters.json
execute_ssot_graph_intelligence.json
execute_ssot_final_report.json
execute_ssot_repair_log.json
execute_ssot_scoped_retests.json
execute_ssot_adg_validation.json
validation_test_report.json
validation_enforcement_report.json
adg_validation_report.json
sovereign_contract_guard_test_20260208_124009.json
sovereign_contract_guard_test_20260208_130635.json
```

#### 8. Move to `low_signal/` (15 files, ~50 KB)
```
_import_map.json
_import_map_v2.json
_scan_analyze_tmp.py
scan_summary_tmp.txt
plans_execution.txt
plans_rca.txt
plans_gap_analysis.txt
plans_investigation.txt
skip_burndown_plan.json
trace_emitter_inventory.json
agent_discovery.json
apps_refactor_verification.json
forensic_discovery_v54.json
path_replace_audit.json
eager_import_full_scan.json
```

#### 9. Move to appropriate existing directories (9 files)
```
l4d_manifests.sqlite → manifests/
dep_graph.sqlite → adg/ (if ADG-related) or low_signal/
cpu_benchmark_evidence.json → analysis/
ci_validation_after_fix.txt → ci/
ci_validation_grandfathered.txt → ci/
silent_swallower_report.json → reports/
```

#### 10. Remove empty files (3 files)
```
collection_errors.txt (0 B)
test_errors_detail.txt (0 B)
skipped_tests_list.json (3 B)
```

### Dead Code Archival

Move dead ADG directories to `_legacy_adg_archives/`:
```
adg_clean/ → _legacy_adg_archives/adg_clean_03242026/
adg_runtime/ → _legacy_adg_archives/adg_runtime_03242026/
adg_tools_backups/ → _legacy_adg_archives/adg_tools_backups_04052026/
adg_truly_clean/ → _legacy_adg_archives/adg_truly_clean/
```

---

## EXPECTED OUTCOMES

### Before Reorganization
- Root files: 115
- Root directories: 44
- Total size: ~191.35 MB
- Dead code: ~170 MB

### After Reorganization
- Root files: 0 (all moved to subdirectories)
- Root directories: 52 (44 + 8 new)
- Active size: ~21 MB (191 - 170 dead code)
- Archived size: ~170 MB (in _legacy_adg_archives/)

### Benefits
1. **Zero root files** - Clean directory structure
2. **High signal separation** - Easy access to important artifacts
3. **Dead code removed** - 170 MB savings
4. **Logical organization** - Files grouped by purpose
5. **Maintainability** - Clear structure for future additions

---

## EXECUTION STEPS

### Phase 1: Create New Directories
```bash
mkdir artifacts/adg_analysis
mkdir artifacts/wave_reports
mkdir artifacts/test_artifacts
mkdir artifacts/ssot_scans
mkdir artifacts/guardian_analysis
mkdir artifacts/adg_profiles
mkdir artifacts/execution_artifacts
mkdir artifacts/low_signal
mkdir artifacts/_legacy_adg_archives
```

### Phase 2: Move Files (8 batches)
Execute file moves according to the file moves section above.

### Phase 3: Archive Dead Code
Move 4 dead ADG directories to `_legacy_adg_archives/`.

### Phase 4: Remove Empty Files
Delete 3 empty/near-empty files.

### Phase 5: Validation
- Verify root has 0 files
- Verify all files moved successfully
- Verify no broken references
- Create summary report

---

## RISK MITIGATION

1. **Backup before moves** - Create full artifacts backup
2. **Test references** - Check for hardcoded paths to artifacts
3. **Gradual moves** - Execute in phases with validation
4. **Rollback plan** - Keep backup until validation complete

---

## SUCCESS CRITERIA

- [ ] Root directory has 0 files
- [ ] All 115 root files moved to appropriate subdirectories
- [ ] Dead code directories archived to _legacy_adg_archives/
- [ ] No broken file references in codebase
- [ ] Validation report created
- [ ] Size reduction of ~170 MB achieved
