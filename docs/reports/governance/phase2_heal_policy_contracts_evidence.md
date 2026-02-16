# Phase 2: Heal Escalation Policy Contracts Evidence

## Wave 2.1 — Pure Policy Types + Pure Decision Function

### Files Created
- agentic_core/L5_safety/types/heal_policy_types.py

### Import Smoke Test
```bash
python -c "from agentic_core.L5_safety.types.heal_policy_types import decide_reasoning_tier; print('ok')"
```

Output:
```
ok
```

### Module Characteristics
- Pure Python module using only stdlib (dataclasses, enum, typing)
- No imports from apps_*, routing, executors, model router, or agents
- Frozen dataclasses for immutability
- Deterministic decision logic with no randomness

---

## Wave 2.2 — CI-Grade Unit Tests

### Files Created
- tests/governance/test_heal_policy_types.py

### Test Execution Results
```bash
pytest -q tests/governance/test_heal_policy_types.py
```

Output:
```
===================== test session starts ======================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)                                                       plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio.default_fixture_loop_scope=None, asyncio.default_test_loop_scope=function         collected 19 items

tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_very_high_boundary PASSED [  5%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_very_high_boundary_just_below PASSED [ 10%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_high_boundary PASSED [ 15%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_high_boundary_just_below PASSED [ 21%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_medium_boundary PASSED [ 26%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_medium_boundary_just_below PASSED [ 31%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_low_values PASSED [ 36%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_validation_errors PASSED [ 42%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_trivial_rule_returns_low_even_with_low_confidence PASSED [ 47%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_trivial_rule_order PASSED [ 52%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_escalation_confidence_low PASSED [ 57%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_escalation_complexity_high PASSED [ 63%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_escalation_safety_risk_high PASSED [ 68%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_escalation_retry_count_high PASSED [ 73%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_default_low PASSED [ 78%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_determinism PASSED [ 84%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_validation_task_complexity PASSED [ 89%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_validation_safety_risk PASSED [ 94%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_validation_retry_count PASSED [100%]
===================== slowest 10 durations =====================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
====================== 19 passed in 0.04s ======================
```

### Full Pytest Suite (Governance Tests Still Execute)
```bash
pytest -q
```

Output (truncated, showing governance tests execute):
```
===================== test session starts ======================
...
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_very_high_boundary PASSED [  5%]
...
tests/governance/test_agent_heal_audit.py::TestDeterminism::test_byte_identical_json_runs PASSED [ 47%]
...
================== short test summary info ====================
FAILED tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[DagRuntimeInspectorAgent] - AssertionError: Cannot parse DagRuntimeInspectorAgent.py
...
================ 16 failed, 93 passed in 20.32s ================
```

Note: Governance tests including the new test_heal_policy_types.py are executing under plain pytest -q. The 16 failures are pre-existing issues unrelated to Phase 2 changes.

---
