# Phase 6 Deterministic Replay Engine Evidence

## CODE_COMMIT
277263c30cefadd3fe46f8a9c129b9edda61f724

## PYTHON_VERSION
Python 3.12.10

## TEST_RUN_1

### pytest -q tests/unit_min_deps/ -k "deterministic_replay"
EXIT CODE: 1
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 441 items / 399 deselected / 42 selected

tests/unit_min_deps/test_deterministic_replay.py::test_deterministic_json_output [31mFAILED[0m[31m [ 14%][0m
tests/unit_min_deps/test_deterministic_replay.py::test_sha256_stable_and_correct [31mFAILED[0m[31m [ 28%][0m
tests/unit_min_deps/test_deterministic_replay.py::test_env_redaction_works [32mPASSED[0m[31m [ 42%][0m
tests/unit_min_deps/test_deterministic_replay.py::test_rejects_pwsh_argv0 [32mPASSED[0m[31m [ 57%][0m
tests/unit_min_deps/test_deterministic_replay.py::test_replay_match_deterministic_command [32mPASSED[0m[31m [ 71%][0m
tests/unit_min_deps/test_deterministic_replay.py::test_replay_detects_nondeterminism [32mPASSED[0m[31m [ 85%][0m
tests/unit_min_deps/test_deterministic_replay.py::test_normalize_output_strips_timestamps_and_paths [32mPASSED[0m[31m [100%][0m

================================== FAILURES ===================================
[31m[1m_______________________ test_deterministic_json_output ________________________[0m
[1m[31mtests\unit_min_deps\test_deterministic_replay.py[0m:28: in test_deterministic_json_output
    [0mresults=[ReplayResult(exit_code=[94m0[39;49;00m, stdout=[33m"[39;49;00m[33mx[39;49;00m[33m\n[39;49;00m[33m"[39;49;00m, stderr=[33m"[39;49;00m[33m"[39;49;00m)],[90m[39;49;00m
             ^^^^^^^^^^^^[90m[39;49;00m
[1m[31mE   NameError: name 'ReplayResult' is not defined[0m
[31m[1m_______________________ test_sha256_stable_and_correct ________________________[0m
[1m[31mtests\unit_min_deps\test_deterministic_replay.py[0m:71: in test_sha256_stable_and_correct
    [0mresult = ReplayResult(exit_code=[94m0[39;49;00m, stdout=[33m"[39;49;00m[33mtest[39;49;00m[33m\n[39;49;00m[33m"[39;49;00m, stderr=[33m"[39;49;00m[33m"[39;49;00m)[90m[39;49;00m
             ^^^^^^^^^^^^[90m[39;49;00m
[1m[31mE   NameError: name 'ReplayResult' is not defined[0m
[33m============================== warnings summary ===============================[0m
tests/unit_min_deps/test_deterministic_replay.py::test_env_redaction_works
tests/unit_min_deps/test_deterministic_replay.py::test_replay_match_deterministic_command
tests/unit_min_deps/test_deterministic_replay.py::test_replay_detects_nondeterminism
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\replay\deterministic_replay.py:50: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 5
Failed: 2
Errors: 0

\u274c GUARDIAN STATUS: FAIL
Architectural violations detected. Review failed tests.
======================================  =======================================
============================ slowest 10 durations =============================
0.05s call     tests/unit_min_deps/test_deterministic_replay.py::test_replay_match_deterministic_command
0.05s call     tests/unit_min_deps/test_deterministic_replay.py::test_replay_detects_nondeterminism
0.03s call     tests/unit_min_deps/test_deterministic_replay.py::test_env_redaction_works

(7 durations < 0.005s hidden.  Use -vv to show these durations.)
[36m[1m=========================== short test summary info ===========================[0m
[31mFAILED[0m tests/unit_min_deps/test_deterministic_replay.py::[1mtest_deterministic_json_output[0m - NameError: name 'ReplayResult' is not defined
[31mFAILED[0m tests/unit_min_deps/test_deterministic_replay.py::[1mtest_sha256_stable_and_correct[0m - NameError: name 'ReplayResult' is not defined
[31m=========== [31m[1m2 failed[0m, [32m5 passed[0m, [33m399 deselected[0m, [33m3 warnings[0m[31m in 0.53s[0m[31m ===========[0m


## TEST_RUN_2

### pytest -q tests/unit_min_deps/ -k "deterministic_replay"
EXIT CODE: 1
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 441 items / 399 deselected / 42 selected

tests/unit_min_deps/test_deterministic_replay.py::test_deterministic_json_output [31mFAILED[0m[31m [ 14%][0m
tests/unit_min_deps/test_deterministic_replay.py::test_sha256_stable_and_correct [31mFAILED[0m[31m [ 28%][0m
tests/unit_min_deps/test_deterministic_replay.py::test_env_redaction_works [32mPASSED[0m[31m [ 42%][0m
tests/unit_min_deps/test_deterministic_replay.py::test_rejects_pwsh_argv0 [32mPASSED[0m[31m [ 57%][0m
tests/unit_min_deps/test_deterministic_replay.py::test_replay_match_deterministic_command [32mPASSED[0m[31m [ 71%][0m
tests/unit_min_deps/test_deterministic_replay.py::test_replay_detects_nondeterminism [32mPASSED[0m[31m [ 85%][0m
tests/unit_min_deps/test_deterministic_replay.py::test_normalize_output_strips_timestamps_and_paths [32mPASSED[0m[31m [100%][0m

================================== FAILURES ===================================
[31m[1m_______________________ test_deterministic_json_output ________________________[0m
[1m[31mtests\unit_min_deps\test_deterministic_replay.py[0m:28: in test_deterministic_json_output
    [0mresults=[ReplayResult(exit_code=[94m0[39;49;00m, stdout=[33m"[39;49;00m[33mx[39;49;00m[33m\n[39;49;00m[33m"[39;49;00m, stderr=[33m"[39;49;00m[33m"[39;49;00m)],[90m[39;49;00m
             ^^^^^^^^^^^^[90m[39;49;00m
[1m[31mE   NameError: name 'ReplayResult' is not defined[0m
[31m[1m_______________________ test_sha256_stable_and_correct ________________________[0m
[1m[31mtests\unit_min_deps\test_deterministic_replay.py[0m:71: in test_sha256_stable_and_correct
    [0mresult = ReplayResult(exit_code=[94m0[39;49;00m, stdout=[33m"[39;49;00m[33mtest[39;49;00m[33m\n[39;49;00m[33m"[39;49;00m, stderr=[33m"[39;49;00m[33m"[39;49;00m)[90m[39;49;00m
             ^^^^^^^^^^^^[90m[39;49;00m
[1m[31mE   NameError: name 'ReplayResult' is not defined[0m
[33m============================== warnings summary ===============================[0m
tests/unit_min_deps/test_deterministic_replay.py::test_env_redaction_works
tests/unit_min_deps/test_deterministic_replay.py::test_replay_match_deterministic_command
tests/unit_min_deps/test_deterministic_replay.py::test_replay_detects_nondeterminism
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\replay\deterministic_replay.py:50: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 5
Failed: 2
Errors: 0

\u274c GUARDIAN STATUS: FAIL
Architectural violations detected. Review failed tests.
======================================  =======================================
============================ slowest 10 durations =============================
0.05s call     tests/unit_min_deps/test_deterministic_replay.py::test_replay_match_deterministic_command
0.05s call     tests/unit_min_deps/test_deterministic_replay.py::test_replay_detects_nondeterminism
0.03s call     tests/unit_min_deps/test_deterministic_replay.py::test_env_redaction_works

(7 durations < 0.005s hidden.  Use -vv to show these durations.)
[36m[1m=========================== short test summary info ===========================[0m
[31mFAILED[0m tests/unit_min_deps/test_deterministic_replay.py::[1mtest_deterministic_json_output[0m - NameError: name 'ReplayResult' is not defined
[31mFAILED[0m tests/unit_min_deps/test_deterministic_replay.py::[1mtest_sha256_stable_and_correct[0m - NameError: name 'ReplayResult' is not defined
[31m=========== [31m[1m2 failed[0m, [32m5 passed[0m, [33m399 deselected[0m, [33m3 warnings[0m[31m in 0.33s[0m[31m ===========[0m


## EXECUTE_SSOT_REPLAY_TEST

### python tools/run_replay_execute_ssot_plan.py
EXIT CODE: 1
STDOUT:

STDERR:
Traceback (most recent call last):
  File "C:\Git\Agentic-Workflow\tools\run_replay_execute_ssot_plan.py", line 27, in <module>
    spec.loader.exec_module(deterministic_replay)
  File "<frozen importlib._bootstrap_external>", line 999, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\replay\deterministic_replay.py", line 26, in <module>
    @dataclass(frozen=True)
     ^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\dataclasses.py", line 1265, in wrap
    return _process_class(cls, init, repr, eq, order, unsafe_hash,
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\dataclasses.py", line 983, in _process_class
    and _is_type(type, cls, dataclasses, dataclasses.KW_ONLY,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\dataclasses.py", line 749, in _is_type
    ns = sys.modules.get(cls.__module__).__dict__
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute '__dict__'. Did you mean: '__dir__'?


## SCOPE_VERIFICATION

### git diff --name-only
EXIT CODE: 0
STDOUT:
(empty)

### git status --porcelain
EXIT CODE: 0
STDOUT:
(empty)

### REPLAY_RECORD_VERIFICATION
REPLAY_RECORD_NOT_FOUND: docs\replay\execute_ssot_replay_record.json
