# Phase 10 Multi-Agent Arbitration Evidence

## CODE_COMMIT
89ebf88cb6c71351c4ad51d19f760ce497597c46

## PYTHON_VERSION
Python 3.12.10

## TEST_RUN_1

### pytest -q tests/unit_min_deps/ -k "arbitration"
EXIT CODE: 1
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 487 items / 437 deselected / 50 selected

tests/unit_min_deps/test_arbitration.py::test_advisor_proposal_validation [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/test_arbitration.py::test_arbitration_input_validation [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/test_arbitration.py::test_deterministic_scoring [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_arbitration.py::test_deterministic_selection_under_ties [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_arbitration.py::test_tie_break_by_confidence [32mPASSED[0m[32m [ 33%][0m
tests/unit_min_deps/test_arbitration.py::test_serialization_stable [31mFAILED[0m[31m [ 40%][0m
tests/unit_min_deps/test_arbitration.py::test_arbitration_decision_serialization [31mFAILED[0m[31m [ 46%][0m
tests/unit_min_deps/test_arbitration.py::test_arbitrator_with_no_proposals [32mPASSED[0m[31m [ 53%][0m
tests/unit_min_deps/test_arbitration.py::test_arbitration_deterministic_across_runs [32mPASSED[0m[31m [ 60%][0m
tests/unit_min_deps/test_arbitration.py::test_advisor_deterministic_outputs [32mPASSED[0m[31m [ 66%][0m
tests/unit_min_deps/test_arbitration.py::test_run_advisors_validation [32mPASSED[0m[31m [ 73%][0m
tests/unit_min_deps/test_arbitration.py::test_run_all_advisors [32mPASSED[0m[31m    [ 80%][0m
tests/unit_min_deps/test_arbitration.py::test_advisor_task_kind_behavior [32mPASSED[0m[31m [ 86%][0m
tests/unit_min_deps/test_arbitration.py::test_execute_ssot_plan_arbitration_integration [32mPASSED[0m[31m [ 93%][0m
tests/unit_min_deps/test_arbitration.py::test_arbitration_output_stable [32mPASSED[0m[31m [100%][0m

================================== FAILURES ===================================
[31m[1m__________________________ test_serialization_stable __________________________[0m
[1m[31mtests\unit_min_deps\test_arbitration.py[0m:214: in test_serialization_stable
    [0m[94massert[39;49;00m restored == proposal[90m[39;49;00m
[1m[31mE   AssertionError: assert AdvisorPropos...e2', 'file3']) == AdvisorPropos...e1', 'file2'])[0m
[1m[31mE     [0m
[1m[31mE     Omitting 4 identical items, use -vv to show[0m
[1m[31mE     Differing attributes:[0m
[1m[31mE     [0m[[33m'[39;49;00m[33mrationale[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33martifacts[39;49;00m[33m'[39;49;00m][90m[39;49;00m[0m
[1m[31mE     [0m
[1m[31mE     Drill down into differing attribute rationale:[0m
[1m[31mE       rationale: [0m[[33m'[39;49;00m[33malpha[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33mbeta[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33mzebra[39;49;00m[33m'[39;49;00m][90m[39;49;00m != [0m[[33m'[39;49;00m[33mzebra[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33malpha[39;49;00m[33m'[39;49;00m...[0m
[1m[31mE     [0m
[1m[31mE     ...Full output truncated (22 lines hidden), use '-vv' to show[0m
[31m[1m___________________ test_arbitration_decision_serialization ___________________[0m
[1m[31mtests\unit_min_deps\test_arbitration.py[0m:243: in test_arbitration_decision_serialization
    [0m[94massert[39;49;00m restored == decision[90m[39;49;00m
[1m[31mE   AssertionError: assert ArbitrationDe...k1', 'risk2']) == ArbitrationDe...k2', 'risk1'])[0m
[1m[31mE     [0m
[1m[31mE     Omitting 3 identical items, use -vv to show[0m
[1m[31mE     Differing attributes:[0m
[1m[31mE     [0m[[33m'[39;49;00m[33mmerged_rationale[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33mmerged_risks[39;49;00m[33m'[39;49;00m][90m[39;49;00m[0m
[1m[31mE     [0m
[1m[31mE     Drill down into differing attribute merged_rationale:[0m
[1m[31mE       merged_rationale: [0m[[33m'[39;49;00m[33mreason1[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33mreason2[39;49;00m[33m'[39;49;00m][90m[39;49;00m != [0m[[33m'[39;49;00m[33mreason2[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33mreason1[39;49;00m[33m'[39;49;00m][90m[39;49;00m...[0m
[1m[31mE     [0m
[1m[31mE     ...Full output truncated (19 lines hidden), use '-vv' to show[0m
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 13
Failed: 2
Errors: 0

\u274c GUARDIAN STATUS: FAIL
Architectural violations detected. Review failed tests.
======================================  =======================================
============================ slowest 10 durations =============================
0.20s call     tests/unit_min_deps/test_arbitration.py::test_execute_ssot_plan_arbitration_integration
0.17s call     tests/unit_min_deps/test_arbitration.py::test_arbitration_output_stable
0.01s call     tests/unit_min_deps/test_arbitration.py::test_serialization_stable

(7 durations < 0.005s hidden.  Use -vv to show these durations.)
[36m[1m=========================== short test summary info ===========================[0m
[31mFAILED[0m tests/unit_min_deps/test_arbitration.py::[1mtest_serialization_stable[0m - AssertionError: assert AdvisorPropos...e2', 'file3']) == AdvisorPropos...e1...
[31mFAILED[0m tests/unit_min_deps/test_arbitration.py::[1mtest_arbitration_decision_serialization[0m - AssertionError: assert ArbitrationDe...k1', 'risk2']) == ArbitrationDe...k2...
[31m================ [31m[1m2 failed[0m, [32m13 passed[0m, [33m437 deselected[0m[31m in 0.83s[0m[31m =================[0m


## TEST_RUN_2

### pytest -q tests/unit_min_deps/ -k "arbitration"
EXIT CODE: 1
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 487 items / 437 deselected / 50 selected

tests/unit_min_deps/test_arbitration.py::test_advisor_proposal_validation [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/test_arbitration.py::test_arbitration_input_validation [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/test_arbitration.py::test_deterministic_scoring [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_arbitration.py::test_deterministic_selection_under_ties [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_arbitration.py::test_tie_break_by_confidence [32mPASSED[0m[32m [ 33%][0m
tests/unit_min_deps/test_arbitration.py::test_serialization_stable [31mFAILED[0m[31m [ 40%][0m
tests/unit_min_deps/test_arbitration.py::test_arbitration_decision_serialization [31mFAILED[0m[31m [ 46%][0m
tests/unit_min_deps/test_arbitration.py::test_arbitrator_with_no_proposals [32mPASSED[0m[31m [ 53%][0m
tests/unit_min_deps/test_arbitration.py::test_arbitration_deterministic_across_runs [32mPASSED[0m[31m [ 60%][0m
tests/unit_min_deps/test_arbitration.py::test_advisor_deterministic_outputs [32mPASSED[0m[31m [ 66%][0m
tests/unit_min_deps/test_arbitration.py::test_run_advisors_validation [32mPASSED[0m[31m [ 73%][0m
tests/unit_min_deps/test_arbitration.py::test_run_all_advisors [32mPASSED[0m[31m    [ 80%][0m
tests/unit_min_deps/test_arbitration.py::test_advisor_task_kind_behavior [32mPASSED[0m[31m [ 86%][0m
tests/unit_min_deps/test_arbitration.py::test_execute_ssot_plan_arbitration_integration [32mPASSED[0m[31m [ 93%][0m
tests/unit_min_deps/test_arbitration.py::test_arbitration_output_stable [32mPASSED[0m[31m [100%][0m

================================== FAILURES ===================================
[31m[1m__________________________ test_serialization_stable __________________________[0m
[1m[31mtests\unit_min_deps\test_arbitration.py[0m:214: in test_serialization_stable
    [0m[94massert[39;49;00m restored == proposal[90m[39;49;00m
[1m[31mE   AssertionError: assert AdvisorPropos...e2', 'file3']) == AdvisorPropos...e1', 'file2'])[0m
[1m[31mE     [0m
[1m[31mE     Omitting 4 identical items, use -vv to show[0m
[1m[31mE     Differing attributes:[0m
[1m[31mE     [0m[[33m'[39;49;00m[33mrationale[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33martifacts[39;49;00m[33m'[39;49;00m][90m[39;49;00m[0m
[1m[31mE     [0m
[1m[31mE     Drill down into differing attribute rationale:[0m
[1m[31mE       rationale: [0m[[33m'[39;49;00m[33malpha[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33mbeta[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33mzebra[39;49;00m[33m'[39;49;00m][90m[39;49;00m != [0m[[33m'[39;49;00m[33mzebra[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33malpha[39;49;00m[33m'[39;49;00m...[0m
[1m[31mE     [0m
[1m[31mE     ...Full output truncated (22 lines hidden), use '-vv' to show[0m
[31m[1m___________________ test_arbitration_decision_serialization ___________________[0m
[1m[31mtests\unit_min_deps\test_arbitration.py[0m:243: in test_arbitration_decision_serialization
    [0m[94massert[39;49;00m restored == decision[90m[39;49;00m
[1m[31mE   AssertionError: assert ArbitrationDe...k1', 'risk2']) == ArbitrationDe...k2', 'risk1'])[0m
[1m[31mE     [0m
[1m[31mE     Omitting 3 identical items, use -vv to show[0m
[1m[31mE     Differing attributes:[0m
[1m[31mE     [0m[[33m'[39;49;00m[33mmerged_rationale[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33mmerged_risks[39;49;00m[33m'[39;49;00m][90m[39;49;00m[0m
[1m[31mE     [0m
[1m[31mE     Drill down into differing attribute merged_rationale:[0m
[1m[31mE       merged_rationale: [0m[[33m'[39;49;00m[33mreason1[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33mreason2[39;49;00m[33m'[39;49;00m][90m[39;49;00m != [0m[[33m'[39;49;00m[33mreason2[39;49;00m[33m'[39;49;00m, [33m'[39;49;00m[33mreason1[39;49;00m[33m'[39;49;00m][90m[39;49;00m...[0m
[1m[31mE     [0m
[1m[31mE     ...Full output truncated (19 lines hidden), use '-vv' to show[0m
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 13
Failed: 2
Errors: 0

\u274c GUARDIAN STATUS: FAIL
Architectural violations detected. Review failed tests.
======================================  =======================================
============================ slowest 10 durations =============================
0.18s call     tests/unit_min_deps/test_arbitration.py::test_execute_ssot_plan_arbitration_integration
0.17s call     tests/unit_min_deps/test_arbitration.py::test_arbitration_output_stable
0.01s call     tests/unit_min_deps/test_arbitration.py::test_serialization_stable

(7 durations < 0.005s hidden.  Use -vv to show these durations.)
[36m[1m=========================== short test summary info ===========================[0m
[31mFAILED[0m tests/unit_min_deps/test_arbitration.py::[1mtest_serialization_stable[0m - AssertionError: assert AdvisorPropos...e2', 'file3']) == AdvisorPropos...e1...
[31mFAILED[0m tests/unit_min_deps/test_arbitration.py::[1mtest_arbitration_decision_serialization[0m - AssertionError: assert ArbitrationDe...k1', 'risk2']) == ArbitrationDe...k2...
[31m================ [31m[1m2 failed[0m, [32m13 passed[0m, [33m437 deselected[0m[31m in 0.59s[0m[31m =================[0m


## EXECUTE_SSOT_ARBITRATION_PLAN

### python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --plan --arbitrate-plan
EXIT CODE: 0
STDOUT:
PHASE 1: Discovery
  - reconciler.detect_root_drift
    # filesystem SSOT drift detection
  - location.run
    # location validation (confidence gated heal)
  - file_classification.run (validate_only=True, dry_run=True)
    # file classification early detection

PHASE 2: Reconciliation
  - reconciler.heal
    # drift reconciliation (confidence gated)

PHASE 2.5: Structural Alignment & Sovereignty
  - hierarchy.heal_hierarchy
    # hierarchy alignment (confidence gated)
  - file_classification.heal_repository
    # sovereignty purge (confidence gated, not dry_run, not validate)

PHASE 3: Architectural Validation
  - arch_governor.comprehensive_territory_audit
    # territory audit
  - system_architect.validate_core_architecture
    # architecture validation

PHASE 4: Healing
  - arch_governor.generate_healing_plan
    # healing plan generation
  - arch_governor.execute_healing_plan
    # healing plan execution

PHASE 4.5: Additional Agents
  - conversational_repair.scan_violations
    # conversational repair scan
  - root_hygiene.scan_root_violations
    # root hygiene scan (if registered)

PHASE 5: Certification
  - *.aggregate
    # final aggregation and certification

=== MULTI-AGENT ARBITRATION ===
Selected Advisor: risk_averse
Selected Decision: create_detailed_plan
Score Breakdown: {'risk_averse': 87, 'throughput': 76}
Merged Rationale: ['Detailed planning reduces uncertainty', 'Documentation enables review', 'Iterative refinement possible', 'Just-in-time detail collection', 'Minimal planning enables faster start', 'Step-by-step approach minimizes errors']
Merged Risks: ['May miss important details', 'Over-planning can delay execution', 'Planning may take longer', 'Requires more adaptation during execution']



### python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --plan
EXIT CODE: 0
STDOUT:
PHASE 1: Discovery
  - reconciler.detect_root_drift
    # filesystem SSOT drift detection
  - location.run
    # location validation (confidence gated heal)
  - file_classification.run (validate_only=True, dry_run=True)
    # file classification early detection

PHASE 2: Reconciliation
  - reconciler.heal
    # drift reconciliation (confidence gated)

PHASE 2.5: Structural Alignment & Sovereignty
  - hierarchy.heal_hierarchy
    # hierarchy alignment (confidence gated)
  - file_classification.heal_repository
    # sovereignty purge (confidence gated, not dry_run, not validate)

PHASE 3: Architectural Validation
  - arch_governor.comprehensive_territory_audit
    # territory audit
  - system_architect.validate_core_architecture
    # architecture validation

PHASE 4: Healing
  - arch_governor.generate_healing_plan
    # healing plan generation
  - arch_governor.execute_healing_plan
    # healing plan execution

PHASE 4.5: Additional Agents
  - conversational_repair.scan_violations
    # conversational repair scan
  - root_hygiene.scan_root_violations
    # root hygiene scan (if registered)

PHASE 5: Certification
  - *.aggregate
    # final aggregation and certification



## SCOPE_VERIFICATION

### git diff --name-only
EXIT CODE: 0
STDOUT:
(empty)

### git status --porcelain
EXIT CODE: 0
STDOUT:
(empty)
