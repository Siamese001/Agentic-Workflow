# E2E Acceptance Evidence — Healing Plan Waves 0A-6

## Scope

End-to-end acceptance run covering all healing plan waves (0A through 6).
Verifies: Wave 0A invariant tests, Wave 1-6 invariant tests, L5_safety contracts,
L0_routing contracts, L4_state contracts, namespace fix for --import-mode=importlib.

## CODE_COMMIT

6b64d3e332d80d88a6102e0f988c7560018d350c

## EVIDENCE_COMMIT

f59b9dee7c7ff07ebd00cb9e965950e99c4211b3

## FILES_CHANGED_CODE

conftest.py
tests/agentic_core/__init__.py
tests/agentic_core/L5_safety/__init__.py
tests/agentic_core/L5_safety/conftest.py
tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py

## FILES_CHANGED_EVIDENCE

docs/reports/evidence/e2e_acceptance_evidence.md

## INSPECTED_FILES

tests/agentic_core/L5_safety/__init__.py
tests/agentic_core/__init__.py
tests/agentic_core/L5_safety/conftest.py
conftest.py
tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py
tests/agentic_core/L5_safety/test_l5_agent_inventory_contract.py
tests/agentic_core/L5_safety/test_l5_no_stray_legacy_refs.py

## Wave Suite pytest

$ python -m pytest -q --color=no --tb=no tests/agentic_core/L5_safety/ tests/agentic_core/L0_routing/ tests/agentic_core/L4_state/ tests/agentic_core/test_wave4_v15_agent_id.py tests/agentic_core/test_wave5_longpaths_guard.py tests/agentic_core/test_wave6_hitl_gates.py
85 passed, 24 skipped in 8.71s

## Key Tests Verified

Wave 0A:
  PASSED tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py (20 tests)
  PASSED tests/agentic_core/L5_safety/test_l5_agent_inventory_contract.py::TestL5AgentReachabilityContract::test_all_primary_agents_reachable_or_allowlisted
  PASSED tests/agentic_core/L5_safety/test_l5_no_stray_legacy_refs.py::TestNoStrayLegacyStringRefs::test_no_stray_string_refs_for_legacy_agents

Wave 1:
  PASSED tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py (4 tests)

Wave 2:
  PASSED tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py (4 tests)

Wave 3:
  PASSED tests/agentic_core/L5_safety/test_wave3_reconciler_force.py (4 tests)

Wave 4:
  PASSED tests/agentic_core/test_wave4_v15_agent_id.py (4 tests)

Wave 5:
  PASSED tests/agentic_core/test_wave5_longpaths_guard.py (2 tests)

Wave 6:
  PASSED tests/agentic_core/test_wave6_hitl_gates.py (8 tests)

## Pre-existing Failures (not regressions from wave work)

26 pre-existing failures in tests/system_learning/ports/, tests/system_learning/engines/,
and tests/unit_min_deps/utils/test_ast_fuzzy.py confirmed to exist at commit 38c7d5601
(before this session) via git stash verification. These are NOT caused by any wave change.

  - tests/unit_min_deps/utils/test_ast_fuzzy.py: agentic_core.utils.ast_fuzzy missing (3 failures)
  - tests/system_learning/ports/: HealingInput missing violation_metadata_refs arg + protocol checks (23 failures)
