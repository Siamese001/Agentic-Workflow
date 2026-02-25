# Phase 5 Write Gateway Hardening Evidence

## CODE_COMMIT
b9fc2bff4a99021a17fb1c3b80cedd5955c00d20

## PYTHON_VERSION
Python 3.12.10

## TEST_RUN_1

### pytest -q tests/unit_min_deps/test_write_gateway_guards.py
EXIT CODE: 0
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/unit_min_deps/test_write_gateway_guards.py::test_write_size_cap_exceeded [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_write_amplification_detected [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_write_amplification_boundary_cases [32mPASSED[0m[32m [ 42%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_mutation_entropy_cap [32mPASSED[0m[32m [ 57%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_mutation_entropy_default_expected_max [32mPASSED[0m[32m [ 71%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_mutation_entropy_pass [32mPASSED[0m[32m [ 85%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_prohibition_loop_signal
[1m-------------------------------- live log call --------------------------------[0m
2026-02-23 04:15:13 [[33m WARNING[0m] L2.WriteGateway: MUTATION_PROHIBITION_LOOP: layer=L0 op=json.dump path=/path/to/file.json count=2
[32mPASSED[0m[32m                                                                   [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m7 passed[0m[32m in 0.05s[0m[32m ==============================[0m


### pytest -q tests/unit_min_deps/ -k "write_gateway_guards or prohibition_loop_signal or mutation_entropy"
EXIT CODE: 0
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 434 items / 392 deselected / 42 selected

tests/unit_min_deps/test_write_gateway_guards.py::test_write_size_cap_exceeded [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_write_amplification_detected [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_write_amplification_boundary_cases [32mPASSED[0m[32m [ 42%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_mutation_entropy_cap [32mPASSED[0m[32m [ 57%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_mutation_entropy_default_expected_max [32mPASSED[0m[32m [ 71%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_mutation_entropy_pass [32mPASSED[0m[32m [ 85%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_prohibition_loop_signal
[1m-------------------------------- live log call --------------------------------[0m
2026-02-23 04:15:13 [[33m WARNING[0m] L2.WriteGateway: MUTATION_PROHIBITION_LOOP: layer=L0 op=json.dump path=/path/to/file.json count=2
[32mPASSED[0m[32m                                                                   [100%][0m

=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 7
Failed: 0
Errors: 0

\u2705 GUARDIAN STATUS: PASS
All architectural integrity checks passed.
======================================  =======================================
============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m====================== [32m[1m7 passed[0m, [33m392 deselected[0m[32m in 0.39s[0m[32m ======================[0m


## TEST_RUN_2

### pytest -q tests/unit_min_deps/test_write_gateway_guards.py
EXIT CODE: 0
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/unit_min_deps/test_write_gateway_guards.py::test_write_size_cap_exceeded [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_write_amplification_detected [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_write_amplification_boundary_cases [32mPASSED[0m[32m [ 42%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_mutation_entropy_cap [32mPASSED[0m[32m [ 57%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_mutation_entropy_default_expected_max [32mPASSED[0m[32m [ 71%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_mutation_entropy_pass [32mPASSED[0m[32m [ 85%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_prohibition_loop_signal
[1m-------------------------------- live log call --------------------------------[0m
2026-02-23 04:15:14 [[33m WARNING[0m] L2.WriteGateway: MUTATION_PROHIBITION_LOOP: layer=L0 op=json.dump path=/path/to/file.json count=2
[32mPASSED[0m[32m                                                                   [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m7 passed[0m[32m in 0.05s[0m[32m ==============================[0m


### pytest -q tests/unit_min_deps/ -k "write_gateway_guards or prohibition_loop_signal or mutation_entropy"
EXIT CODE: 0
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 434 items / 392 deselected / 42 selected

tests/unit_min_deps/test_write_gateway_guards.py::test_write_size_cap_exceeded [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_write_amplification_detected [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_write_amplification_boundary_cases [32mPASSED[0m[32m [ 42%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_mutation_entropy_cap [32mPASSED[0m[32m [ 57%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_mutation_entropy_default_expected_max [32mPASSED[0m[32m [ 71%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_mutation_entropy_pass [32mPASSED[0m[32m [ 85%][0m
tests/unit_min_deps/test_write_gateway_guards.py::test_prohibition_loop_signal
[1m-------------------------------- live log call --------------------------------[0m
2026-02-23 04:15:14 [[33m WARNING[0m] L2.WriteGateway: MUTATION_PROHIBITION_LOOP: layer=L0 op=json.dump path=/path/to/file.json count=2
[32mPASSED[0m[32m                                                                   [100%][0m

=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 7
Failed: 0
Errors: 0

\u2705 GUARDIAN STATUS: PASS
All architectural integrity checks passed.
======================================  =======================================
============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m====================== [32m[1m7 passed[0m, [33m392 deselected[0m[32m in 0.18s[0m[32m ======================[0m


## SCOPE_VERIFICATION

### git diff --name-only
EXIT CODE: 0
STDOUT:
(empty)

### git status --porcelain
EXIT CODE: 0
STDOUT:
?? tools/run_phase5_write_gateway_evidence.py


### RCA_ARTIFACT_VERIFICATION
EXIT CODE: 0
RCA_ARTIFACT_TRACKED: docs/reports/rca_gravity_leak_corruption_phase4.md
