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

ae6677b2a203fd5e4fe739e229871b3962c04fc8

## EVIDENCE_COMMIT

PENDING

## FILES_CHANGED_CODE

agentic_core/L5_safety/config/structure_blueprint/_constants.py
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
agentic_core/L5_safety/utils/location_constants_util.py
ops_scripts/hooks/landmine_baseline.txt
tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py

## FILES_CHANGED_EVIDENCE

PENDING

## INSPECTED_FILES

agentic_core/L5_safety/config/structure_blueprint/_constants.py
agentic_core/L5_safety/utils/location_constants_util.py
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
agentic_core/L5_safety/config/structure_blueprint/territories.py
tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py

## pytest -q --color=no (L5_safety suite, excl. new invariant test)

```
FAILED tests/agentic_core/L5_safety/test_l5_agent_inventory_contract.py::TestL5AgentReachabilityContract::test_all_primary_agents_reachable_or_allowlisted
FAILED tests/agentic_core/L5_safety/test_l5_no_stray_legacy_refs.py::TestNoStrayLegacyStringRefs::test_no_stray_string_refs_for_legacy_agents - ModuleNotFoundError: No module named 'agentic_core.L0_routing.legacy_agent_name_allowlist'
2 failed, 3 passed, 54 skipped in 0.59s
```

NOTE: Both failures are pre-existing (run11 archived modules). Wave 0A changes introduced zero new failures.
