# Phase 8 Performance Envelope & Scaling Hardening Evidence

## CODE_COMMIT
35e0fbc1fc76296621e3a5698600a3a0991319f1

## PYTHON_VERSION
Python 3.12.10

## TEST_RUN_1

### pytest -q tests/unit_min_deps/ -k "performance_envelope or truncation or store_limit"
EXIT CODE: 0
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 457 items / 416 deselected / 41 selected

tests/unit_min_deps/test_performance_envelope.py::test_truncation_deterministic_and_hash_changes [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/test_performance_envelope.py::test_replay_metrics_determinism [32mPASSED[0m[32m [ 33%][0m
tests/unit_min_deps/test_performance_envelope.py::test_store_list_limit_deterministic [32mPASSED[0m[33m [ 50%][0m
tests/unit_min_deps/test_performance_envelope.py::test_scaling_200_small_artifacts [32mPASSED[0m[33m [ 66%][0m
tests/unit_min_deps/test_performance_envelope.py::test_scaling_25_replay_commands [32mPASSED[0m[33m [ 83%][0m
tests/unit_min_deps/test_performance_envelope.py::test_scaling_deterministic_across_runs [32mPASSED[0m[33m [100%][0m

[33m============================== warnings summary ===============================[0m
tests/unit_min_deps/test_performance_envelope.py::test_replay_metrics_determinism
tests/unit_min_deps/test_performance_envelope.py::test_replay_metrics_determinism
tests/unit_min_deps/test_performance_envelope.py::test_scaling_25_replay_commands
tests/unit_min_deps/test_performance_envelope.py::test_scaling_deterministic_across_runs
tests/unit_min_deps/test_performance_envelope.py::test_scaling_deterministic_across_runs
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\replay\deterministic_replay.py:62: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

tests/unit_min_deps/test_performance_envelope.py: 212 warnings
  C:\Git\Agentic-Workflow\agentic_core\L4_state\storage\persistent_store.py:127: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_utc = datetime.utcnow().isoformat() + "Z"

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 6
Failed: 0
Errors: 0

\u2705 GUARDIAN STATUS: PASS
All architectural integrity checks passed.
======================================  =======================================
============================ slowest 10 durations =============================
0.59s call     tests/unit_min_deps/test_performance_envelope.py::test_scaling_25_replay_commands
0.14s call     tests/unit_min_deps/test_performance_envelope.py::test_scaling_200_small_artifacts
0.05s call     tests/unit_min_deps/test_performance_envelope.py::test_scaling_deterministic_across_runs
0.05s call     tests/unit_min_deps/test_performance_envelope.py::test_replay_metrics_determinism
0.01s call     tests/unit_min_deps/test_performance_envelope.py::test_store_list_limit_deterministic

(5 durations < 0.005s hidden.  Use -vv to show these durations.)
[33m=============== [32m6 passed[0m, [33m[1m416 deselected[0m, [33m[1m217 warnings[0m[33m in 1.21s[0m[33m ===============[0m


## TEST_RUN_2

### pytest -q tests/unit_min_deps/ -k "performance_envelope or truncation or store_limit"
EXIT CODE: 0
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 457 items / 416 deselected / 41 selected

tests/unit_min_deps/test_performance_envelope.py::test_truncation_deterministic_and_hash_changes [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/test_performance_envelope.py::test_replay_metrics_determinism [32mPASSED[0m[32m [ 33%][0m
tests/unit_min_deps/test_performance_envelope.py::test_store_list_limit_deterministic [32mPASSED[0m[33m [ 50%][0m
tests/unit_min_deps/test_performance_envelope.py::test_scaling_200_small_artifacts [32mPASSED[0m[33m [ 66%][0m
tests/unit_min_deps/test_performance_envelope.py::test_scaling_25_replay_commands [32mPASSED[0m[33m [ 83%][0m
tests/unit_min_deps/test_performance_envelope.py::test_scaling_deterministic_across_runs [32mPASSED[0m[33m [100%][0m

[33m============================== warnings summary ===============================[0m
tests/unit_min_deps/test_performance_envelope.py::test_replay_metrics_determinism
tests/unit_min_deps/test_performance_envelope.py::test_replay_metrics_determinism
tests/unit_min_deps/test_performance_envelope.py::test_scaling_25_replay_commands
tests/unit_min_deps/test_performance_envelope.py::test_scaling_deterministic_across_runs
tests/unit_min_deps/test_performance_envelope.py::test_scaling_deterministic_across_runs
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\replay\deterministic_replay.py:62: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

tests/unit_min_deps/test_performance_envelope.py: 212 warnings
  C:\Git\Agentic-Workflow\agentic_core\L4_state\storage\persistent_store.py:127: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_utc = datetime.utcnow().isoformat() + "Z"

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 6
Failed: 0
Errors: 0

\u2705 GUARDIAN STATUS: PASS
All architectural integrity checks passed.
======================================  =======================================
============================ slowest 10 durations =============================
0.61s call     tests/unit_min_deps/test_performance_envelope.py::test_scaling_25_replay_commands
0.15s call     tests/unit_min_deps/test_performance_envelope.py::test_scaling_200_small_artifacts
0.05s call     tests/unit_min_deps/test_performance_envelope.py::test_replay_metrics_determinism
0.05s call     tests/unit_min_deps/test_performance_envelope.py::test_scaling_deterministic_across_runs
0.01s call     tests/unit_min_deps/test_performance_envelope.py::test_store_list_limit_deterministic

(5 durations < 0.005s hidden.  Use -vv to show these durations.)
[33m=============== [32m6 passed[0m, [33m[1m416 deselected[0m, [33m[1m217 warnings[0m[33m in 1.04s[0m[33m ===============[0m


## SCOPE_VERIFICATION

### git diff --name-only
EXIT CODE: 0
STDOUT:
(empty)

### git status --porcelain
EXIT CODE: 0
STDOUT:
(empty)
