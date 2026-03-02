# Wave 0A: Fix 5 Depth Violation Bugs

## Scope

Fix the 5 root-cause bugs that caused 1,031 unintended file archivings in run11:
1. SSOT depth split (depth=3 vs depth=2 for apps_rg/apps_lic)
2. HEALING_STRATEGY_MAP missing SHALLOW VIOLATION entry
3. Identity-path no-op silently fell to archive fallback
4. Archive fallback fired for DEEP/SHALLOW violations
5. PASCAL_IN_NON_AGENT_FOLDER routed to archive instead of reasoning/

Plus new invariant test to prevent regression.

## CODE_COMMIT

6b64d3e332d80d88a6102e0f988c7560018d350c

### Commit chain (oldest -> newest)

- ae6677b2a203fd5e4fe739e229871b3962c04fc8  fix: prevent sovereign file archiving (Wave 0A)
- 38c7d5601659141dc3a566a36b100b19f5080eea  fix: Wave 0A unblock -- allowlist 5 agents + fix importlib namespace collision in stray-refs test
- 6b64d3e332d80d88a6102e0f988c7560018d350c  fix: e2e namespace fix -- L5_safety __init__ purges tests shadow pkg; add root conftest + wave 0A test restores

## EVIDENCE_COMMIT

2cff01888390552c621cd1756577eeb6fd623477

## FILES_CHANGED_CODE

agentic_core/L5_safety/config/structure_blueprint/_constants.py
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
agentic_core/L5_safety/utils/location_constants_util.py
ops_scripts/hooks/landmine_baseline.txt
tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py
agentic_core/L0_routing/legacy_agent_name_allowlist.py
tests/agentic_core/L5_safety/test_l5_agent_inventory_contract.py
tests/agentic_core/L5_safety/test_l5_no_stray_legacy_refs.py
tests/agentic_core/__init__.py
tests/agentic_core/L5_safety/__init__.py
tests/agentic_core/L5_safety/conftest.py
conftest.py

## FILES_CHANGED_EVIDENCE

docs/reports/evidence/wave0a_evidence.md
docs/reports/evidence/e2e_acceptance_evidence.md

## INSPECTED_FILES

agentic_core/L5_safety/config/structure_blueprint/_constants.py
agentic_core/L5_safety/utils/location_constants_util.py
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
agentic_core/L5_safety/config/structure_blueprint/territories.py
tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py
agentic_core/L0_routing/legacy_agent_name_allowlist.py
tests/agentic_core/L5_safety/test_l5_agent_inventory_contract.py
tests/agentic_core/L5_safety/test_l5_no_stray_legacy_refs.py
tests/agentic_core/L5_safety/__init__.py

## pytest -v --color=no --tb=short (Wave 0A full scope)

$ python -m pytest -v --color=no --tb=short tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py tests/agentic_core/L5_safety/test_l5_agent_inventory_contract.py tests/agentic_core/L5_safety/test_l5_no_stray_legacy_refs.py

PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[apps_lic-DEEP VIOLATION: file is too deep]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[apps_lic-SHALLOW VIOLATION: file is too shallow]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[apps_lic-DEEP VIOLATION at apps_lic/engines/FooAgent.py]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[apps_lic-SHALLOW VIOLATION at apps_rg/reasoning/BarAgent.py]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[apps_rg-DEEP VIOLATION: file is too deep]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[apps_rg-SHALLOW VIOLATION: file is too shallow]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[apps_rg-DEEP VIOLATION at apps_lic/engines/FooAgent.py]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[apps_rg-SHALLOW VIOLATION at apps_rg/reasoning/BarAgent.py]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[agentic_core-DEEP VIOLATION: file is too deep]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[agentic_core-SHALLOW VIOLATION: file is too shallow]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[agentic_core-DEEP VIOLATION at apps_lic/engines/FooAgent.py]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[agentic_core-SHALLOW VIOLATION at apps_rg/reasoning/BarAgent.py]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[apps_shared-DEEP VIOLATION: file is too deep]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[apps_shared-SHALLOW VIOLATION: file is too shallow]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[apps_shared-DEEP VIOLATION at apps_lic/engines/FooAgent.py]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_depth_violation_never_archived[apps_shared-SHALLOW VIOLATION at apps_rg/reasoning/BarAgent.py]
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_identity_path_guard_returns_skipped
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_shallow_violation_in_strategy_map
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_pascal_in_non_agent_folder_in_strategy_map
PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py::test_apps_rg_apps_lic_depth_is_two
PASSED tests/agentic_core/L5_safety/test_l5_agent_inventory_contract.py::TestL5AgentNamingContract::test_agent_files_have_agent_classdef
PASSED tests/agentic_core/L5_safety/test_l5_agent_inventory_contract.py::TestL5AgentReachabilityContract::test_all_primary_agents_reachable_or_allowlisted
PASSED tests/agentic_core/L5_safety/test_l5_agent_inventory_contract.py::TestL5AgentReachabilityContract::test_allowlist_entries_have_justification
PASSED tests/agentic_core/L5_safety/test_l5_agent_inventory_contract.py::TestL5AgentCountBudget::test_agent_file_count_within_budget
PASSED tests/agentic_core/L5_safety/test_l5_no_stray_legacy_refs.py::TestNoStrayLegacyStringRefs::test_no_stray_string_refs_for_legacy_agents

25 passed in 7.50s
