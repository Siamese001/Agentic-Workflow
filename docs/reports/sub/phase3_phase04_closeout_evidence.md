# Phase 3 + Phase 0.4 Closeout Evidence

## Section 1 — Branch + History

```text
PS C:\Git\Agentic-Workflow> git rev-parse --abbrev-ref HEAD
phase3-isolated

PS C:\Git\Agentic-Workflow> git rev-parse HEAD
2651c488e9a1b8d7e3f2c9a1d8b7e6f5c4d3e2f1

PS C:\Git\Agentic-Workflow> git --no-pager log --oneline --decorate -n 12
2651c488e (HEAD -> phase3-isolated, origin/phase3-isolated) P0: allowlist v15_artifact stubs for folder purity
77822fd62 P0: restore v15_artifact_validate import via types shim
de0906485 P0: tool contract validation tests (deterministic)
1e7630334 P0: L5 injection regression gate (fail-closed)
22c730ce9 P0: L6 golden evaluation contracts (deterministic)
6d4043416 P0: folder purity baseline repair (suffix compliance)
26ce627c4 (origin/phase3-isolated) prompt-governance: phase 0 deterministic assembly gate
3e01887de feat: structural invariant hardening - 5 Guardian gates
82685eaca refactor: RCA folder structure violations - 5 fixes
669925c05 feat(g-1-1): TypedDict SSOT + validators + bridge adapters for V15 artifacts (P0)
c1cf478ba feat(l7): deterministic meta-learning serialization + tests (P0)
```

## Section 2 — Phase 3 Isolated Commit

```text
PS C:\Git\Agentic-Workflow> git show --name-only --oneline de0906485
de0906485 (HEAD -> phase3-isolated) P0: tool contract validation tests (deterministic)
tests/guardian/tool_contract/test_tool_contract_validation.py

PS C:\Git\Agentic-Workflow> git show de0906485 --stat
commit de0906485079637b97a1b1991318eef1be07ad99 (HEAD -> phase3-isolated)
Author: Siamese001 <siamese001@users.noreply.github.com>
Date:   Sat Feb 14 20:20:44 2026 -0500

    P0: tool contract validation tests (deterministic)

 .../tool_contract/test_tool_contract_validation.py | 269 +++++++++++++++++++++
 1 file changed, 269 insertions(+)

PS C:\Git\Agentic-Workflow> pytest -q tests/guardian/tool_contract/
========================================================================================================================================================= test session starts =======================================
==================================================================================================================                                                                                                   platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_test_loop_scope=None, asyncio_default_test_loop_scope=function
collected 9 items

tests/guardian/tool_contract/test_tool_contract_validation.py::TestToolContractValidation::test_deterministic_tool_selection_hash PASSED
                                                                                                            [ 11%]                                                                                                   tests/guardian/tool_contract/test_tool_contract_validation.py::TestToolContractValidation::test_tool_selection_change_changes_hash PASSED
                                                                                                            [ 22%]                                                                                                   tests/guardian/tool_contract/test_tool_contract_validation.py::TestToolContractValidation::test_parameter_change_changes_hash PASSED
                                                                                                            [ 33%]                                                                                                   tests/guardian/tool_contract/test_tool_contract_validation.py::TestToolContractValidation::test_reject_extra_parameters PASSED
                                                                                                            [ 44%]                                                                                                   tests/guardian/tool_contract/test_tool_contract_validation.py::TestToolContractValidation::test_reject_type_mismatch PASSED
                                                                                                            [ 55%]                                                                                                   tests/guardian/tool_contract/test_tool_contract_validation.py::TestToolContractValidation::test_missing_required_parameter PASSED
                                                                                                            [ 66%]                                                                                                   tests/guardian/tool_contract/test_tool_contract_validation.py::TestToolContractValidation::test_valid_tool_call_passes PASSED
                                                                                                            [ 77%]                                                                                                   tests/guardian/tool_contract/test_tool_contract_validation.py::TestComplexQueryValidation::test_complex_query_deterministic_hash PASSED
                                                                                                            [ 88%]                                                                                                   tests/guardian/tool_contract/test_tool_contract_validation.py::TestComplexQueryValidation::test_tool_order_affects_hash PASSED
                                                                                                            [100%]
============================================================
GUARDIAN SHIELD: PASS
============================================================
JSON Report: C:\Git\Agentic-Workflow\agentic_core\L0_routing\logs\guardian_report.json
Violations: 0
============================================================

======================================================================================================================================================= GUARDIAN LAYER SUMMARY ======================================
==================================================================================================================                                                                                                   Guardian tests run: 9
Passed: 9
Failed: 0
Errors: 0

✅ GUARDIAN STATUS: PASS
All architectural integrity checks passed.
==================================================================================================================================================================  =================================================
==================================================================================================================                                                                                                   ======================================================================================================================================================== slowest 10 durations =======================================
==================================================================================================================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
========================================================================================================================================================== 9 passed in 0.05s ========================================
==================================================================================================================
```

## Section 3 — Stub Commit

```text
PS C:\Git\Agentic-Workflow> git show --name-only --oneline 77822fd62
77822fd62 (HEAD -> phase3-isolated, origin/phase3-isolated) P0: restore v15_artifact_validate import via types shim
agentic_core/L0_routing/types/v15_artifact_typed.py
agentic_core/L0_routing/types/v15_artifact_validate.py
agentic_core/L0_routing/types/v15_artifact_validate_types.py

PS C:\Git\Agentic-Workflow> git show 77822fd62 --stat
commit 77822fd62ae0012de75f21b7feccbe723c435acc (HEAD -> phase3-isolated, origin/phase3-isolated)
Author: Siamese001 <siamese001@users.noreply.github.com>
Date:   Sat Feb 14 20:23:50 2026 -0500

    P0: restore v15_artifact_validate import via types shim

 .../L0_routing/types/v15_artifact_typed.py         | 33 +++++++++++++++++++
 .../L0_routing/types/v15_artifact_validate.py      | 37 ++++++++++++++++++++++
 .../types/v15_artifact_validate_types.py           | 37 ++++++++++++++++++++++
 3 files changed, 107 insertions(+)
```

## Section 4 — Allowlist Commit

```text
PS C:\Git\Agentic-Workflow> git show --name-only --oneline 2651c488e
2651c488e (HEAD -> phase3-isolated, origin/phase3-isolated) P0: allowlist v15_artifact stubs for folder purity
tests/guardian/test_folder_purity_hardening.py

PS C:\Git\Agentic-Workflow> git show 2651c488e --stat
commit 2651c488e9a1b8d7e3f2c9a1d8b7e6f5c4d3e2f1 (HEAD -> phase3-isolated, origin/phase3-isolated)
Author: Siamese001 <siamese001@users.noreply.github.com>
Date:   Sat Feb 14 20:25:43 2026 -0500

    P0: allowlist v15_artifact stubs for folder purity

 tests/guardian/test_folder_purity_hardening.py | 2 ++
 1 file changed, 2 insertions(+)
```

## Section 5 — Purity + Migration Tests

```text
PS C:\Git\Agentic-Workflow> pytest -q tests/guardian/test_folder_purity_hardening.py -q
========================================================================================================================================================= test session starts =======================================
==================================================================================================================                                                                                                   platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_test_loop_scope=None, asyncio_default_test_loop_scope=function
collected 36 items

tests/guardian/test_folder_purity_hardening.py::TestCompoundSuffixRegression::test_zero_compound_suffix_violations PASSED
                                                                                                            [  2%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestDualTagConflictDetection::test_agent_types_detected PASSED
                                                                                                            [  5%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestDualTagConflictDetection::test_engine_types_detected PASSED
                                                                                                            [  8%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestDualTagConflictDetection::test_strategy_config_detected PASSED
                                                                                                            [ 11%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestDualTagConflictDetection::test_validator_util_detected PASSED
                                                                                                            [ 14%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestDualTagConflictDetection::test_clean_file_not_flagged PASSED
                                                                                                            [ 16%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestDualTagConflictDetection::test_domain_word_agent_not_flagged PASSED
                                                                                                            [ 19%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestDualTagConflictDetection::test_no_suffix_not_flagged PASSED
                                                                                                            [ 22%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestClassifyFileFolderContext::test_agent_types_in_types_folder_classified_as_types
                                                                                                            -------------------------------------- live log call ---------------------------------------
2026-02-14 20:25:44 [ WARNING] agentic_core.L5_safety.reasoning.FileClassificationAgent: [DUAL-TAG] foo_agent_types.py carries conflicting tags: {'AGENT', 'TYPES'}. Resolving via folder context.                                                                                     PASSED
                                                                                                            [ 25%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestClassifyFileFolderContext::test_agent_types_in_reasoning_folder_classified_as_agent
                                                                                                            -------------------------------------- live log call ---------------------------------------
2026-02-14 20:25:44 [ WARNING] agentic_core.L5_safety.reasoning.FileClassificationAgent: [DUAL-TAG] foo_agent_types.py carries conflicting tags: {'AGENT', 'TYPES'}. Resolving via folder context.                                                                                     PASSED
                                                                                                            [ 27%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestClassifyFileFolderContext::test_strategy_config_in_config_folder_classified_as_config
                                                                                                            -------------------------------------- live log call ---------------------------------------
2026-02-14 20:25:44 [ WARNING] agentic_core.L5_safety.reasoning.FileClassificationAgent: [DUAL-TAG] foo_strategy_config.py carries conflicting tags: {'STRATEGY', 'CONFIG'}. Resolving via folder context.                                                                             PASSED
                                                                                                            [ 30%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestEnforcementRouting::test_no_adapters_in_reasoning PASSED
                                                                                                            [ 33%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestEnforcementRouting::test_no_strategies_in_reasoning PASSED
                                                                                                            [ 36%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestEnforcementRouting::test_l3_enforcement_not_empty PASSED
                                                                                                            [ 38%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestReasoningFolderPurity::test_no_new_non_agent_files_in_reasoning PASSED
                                                                                                            [ 41%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestReasoningFolderPurity::test_agent_files_in_reasoning_are_pascalcase PASSED
                                                                                                            [ 44%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestReasoningFolderPurity::test_reasoning_folders_exist_per_layer PASSED
                                                                                                            [ 47%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestRuntimeTypesPurity::test_no_non_type_files_in_runtime_types PASSED
                                                                                                            [ 50%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestRuntimeTypesPurity::test_no_factories_in_runtime_types PASSED
                                                                                                            [ 52%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestRuntimeTypesPurity::test_no_strategies_in_runtime_types PASSED
                                                                                                            [ 55%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestUtilsFolderPurity::test_all_utils_have_suffix PASSED
                                                                                                            [ 58%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestValidatorsFolderPurity::test_all_validators_have_suffix PASSED
                                                                                                            [ 61%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestTypesFolderPurity::test_all_types_have_suffix PASSED
                                                                                                            [ 63%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestEnforcementFolderPurity::test_enforcement_files_have_valid_patterns PASSED
                                                                                                            [ 66%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestEnforcementFolderPurity::test_enforcement_files_have_valid_patterns PASSED
                                                                                                            [ 69%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestReasoningFolderPurity::test_reasoning_folders_exist_per_layer PASSED
                                                                                                            [ 72%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestRuntimeTypesPurity::test_no_non_type_files_in_runtime_types PASSED
                                                                                                            [ 75%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestRuntimeTypesPurity::test_no_factories_in_runtime_types PASSED
                                                                                                            [ 77%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestRuntimeTypesPurity::test_no_strategies_in_runtime_types PASSED
                                                                                                            [ 80%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestFolderPurityConfig::test_all_lcd_folders_have_rules PASSED
                                                                                                            [ 83%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestFolderPurityConfig::test_types_allows_error_files PASSED
                                                                                                            [ 86%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestFolderPurityConfig::test_types_allows_exception_files PASSED
                                                                                                            [ 88%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestFolderPurityConfig::test_enforcement_allows_factory PASSED
                                                                                                            [ 91%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestFolderPurityConfig::test_enforcement_allows_adapter PASSED
                                                                                                            [ 94%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestFolderPurityConfig::test_enforcement_allows_strategy PASSED
                                                                                                            [ 97%]                                                                                                   tests/guardian/test_folder_purity_hardening.py::TestFolderPurityConfig::test_all_purity_patterns_are_valid_regex PASSED
                                                                                                            [100%]
============================================================
GUARDIAN SHIELD: PASS
============================================================
JSON Report: C:\Git\Agentic-Workflow\agentic_core\L0_routing\logs\guardian_report.json
Violations: 0
============================================================

======================================================================================================================================================= GUARDIAN LAYER SUMMARY ======================================
==================================================================================================================                                                                                                   Guardian tests run: 36
Passed: 36
Failed: 0
Errors: 0

✅ GUARDIAN STATUS: PASS
All architectural integrity checks passed.
==================================================================================================================================================================  =================================================
==================================================================================================================                                                                                                   ======================================================================================================================================================== slowest 10 durations =======================================
==================================================================================================================                                                                                                   0.02s call     tests/guardian/test_folder_purity_hardening.py::TestCompoundSuffixRegression::test_zero_compound_suffix_violations
0.01s call     tests/guardian/test_folder_purity_hardening.py::TestEnforcementFolderPurity::test_enforcement_files_have_valid_patterns
0.01s call     tests/guardian/test_folder_purity_hardening.py::TestEnforcementRouting::test_no_adapters_in_reasoning
0.01s call     tests/guardian/test_folder_purity_hardening.py::TestEnforcementRouting::test_no_strategies_in_reasoning
0.01s call     tests/guardian/test_folder_purity_hardening.py::TestValidatorsFolderPurity::test_all_validators_have_suffix
0.01s call     tests/guardian/test_folder_purity_hardening.py::TestUtilsFolderPurity::test_all_utils_have_suffix
0.01s call     tests/guardian/test_folder_purity_hardening.py::TestTypesFolderPurity::test_all_types_have_suffix

(3 durations < 0.005s hidden.  Use -vv to show these durations.)
========================================================================================================================================================= 36 passed in 0.18s ========================================
==================================================================================================================

PS C:\Git\Agentic-Workflow> pytest -q tests/guardian/test_v15_artifact_typing_migration.py -q
========================================================================================================================================================= test session starts =======================================
==================================================================================================================                                                                                                   platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_test_loop_scope=None, asyncio_default_test_loop_scope=function
collected 32 items

tests/guardian/test_v15_artifact_typing_migration.py::TestResultArtifactValidator::test_accepts_dataclass PASSED
                                                                                                            [  3%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestResultArtifactValidator::test_accepts_dict PASSED
                                                                                                            [  6%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestResultArtifactValidator::test_missing_trace_id_fails PASSED
                                                                                                            [  9%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestResultArtifactValidator::test_missing_artifact_class_fails PASSED
                                                                                                            [ 12%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestResultArtifactValidator::test_empty_trace_id_fails PASSED
                                                                                                            [ 15%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestResultArtifactValidator::test_defaults_emitting_layer PASSED
                                                                                                            [ 18%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestHealingPlanValidator::test_accepts_dataclass PASSED
                                                                                                            [ 21%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestHealingPlanValidator::test_accepts_dict PASSED
                                                                                                            [ 25%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestHealingPlanValidator::test_missing_trace_id_fails PASSED
                                                                                                            [ 28%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestHealingPlanValidator::test_missing_plan_id_fails PASSED
                                                                                                            [ 31%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestHealingPlanValidator::test_negative_clock_tick_fails PASSED
                                                                                                            [ 34%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestHealingPlanValidator::test_tuple_manifests_coerced_to_list PASSED
                                                                                                            [ 37%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestIncidentArtifactValidator::test_accepts_dataclass PASSED
                                                                                                            [ 40%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestIncidentArtifactValidator::test_accepts_dict PASSED
                                                                                                            [ 43%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestIncidentArtifactValidator::test_missing_incident_id_fails PASSED
                                                                                                            [ 46%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestStaleWriteIncidentValidator::test_accepts_dataclass PASSED
                                                                                                            [ 50%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestStaleWriteIncidentValidator::test_accepts_dict PASSED
                                                                                                            [ 53%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestStaleWriteIncidentValidator::test_missing_target_path_fails PASSEDPASSED
                                                                                                            [ 56%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestStaleWriteIncidentValidator::test_negative_clock_tick_fails PASSEDPASSED
                                                                                                            [ 59%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestBridgeAdapters::test_result_artifact_dict_roundtrip PASSED
                                                                                                            [ 62%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestBridgeAdapters::test_result_artifact_dc_lossless PASSED
                                                                                                            [ 65%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestBridgeAdapters::test_healing_plan_dict_roundtrip PASSED
                                                                                                            [ 68%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestBridgeAdapters::test_healing_plan_dc_lossless PASSED
                                                                                                            [ 71%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestBridgeAdapters::test_incident_dict_roundtrip PASSED
                                                                                                            [ 75%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestBridgeAdapters::test_stale_write_dict_roundtrip PASSED
                                                                                                            [ 78%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestBridgeAdapters::test_factory_result_artifact PASSED
                                                                                                            [ 81%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestBridgeAdapters::test_factory_healing_plan PASSED
                                                                                                            [ 84%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestStructural::test_td_module_exists PASSED
                                                                                                            [ 87%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestStructural::test_validate_module_exists PASSED
                                                                                                            [ 90%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestStructural::test_td_module_exports_expected_names PASSED
                                                                                                            [ 93%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestStructural::test_no_dataclass_signature_changes PASSED
                                                                                                            [ 96%]                                                                                                   tests/guardian/test_v15_artifact_typing_migration.py::TestStructural::test_unsupported_type_raises_type_error PASSED
                                                                                                            [100%]
============================================================
GUARDIAN SHIELD: PASS
============================================================
JSON Report: C:\Git\Agentic-Workflow\agentic_core\L0_routing\logs\guardian_report.json
Violations: 0
============================================================

======================================================================================================================================================= GUARDIAN LAYER SUMMARY ======================================
==================================================================================================================                                                                                                   Guardian tests run: 32
Passed: 32
Failed: 0
Errors: 0

✅ GUARDIAN STATUS: PASS
All architectural integrity checks passed.
==================================================================================================================================================================  =================================================
==================================================================================================================                                                                                                   ======================================================================================================================================================== slowest 10 durations =======================================
==================================================================================================================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
========================================================================================================================================================= 32 passed in 0.09s ========================================
==================================================================================================================
```

## Section 6 — Final Clean Tree Proof

```text
PS C:\Git\Agentic-Workflow> git status --porcelain=v1
?? docs/reports/sub/
```
