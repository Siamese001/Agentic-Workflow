# Phase 7 Persistent Storage Layer Evidence

## CODE_COMMIT
f99d7e1434f769bad8e2ce3ce6a7e2310409cc4a

## PYTHON_VERSION
Python 3.12.10

## TEST_RUN_1

### pytest -q tests/unit_min_deps/ -k "persistent_store or filesystem_store or replay_storage"
EXIT CODE: 1
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 451 items / 406 deselected / 45 selected

tests/unit_min_deps/test_persistent_store.py::test_sanitize_id [31mFAILED[0m[31m    [ 10%][0m
tests/unit_min_deps/test_persistent_store.py::test_canonicalize_payload [32mPASSED[0m[31m [ 20%][0m
tests/unit_min_deps/test_persistent_store.py::test_compute_sha256 [32mPASSED[0m[31m [ 30%][0m
tests/unit_min_deps/test_persistent_store.py::test_create_artifact [32mPASSED[0m[31m [ 40%][0m
tests/unit_min_deps/test_persistent_store.py::test_filesystem_store_put_creates_v0001_then_v0002 [32mPASSED[0m[31m [ 50%][0m
tests/unit_min_deps/test_persistent_store.py::test_filesystem_store_get_round_trip [32mPASSED[0m[31m [ 60%][0m
tests/unit_min_deps/test_persistent_store.py::test_filesystem_store_list_ordering [32mPASSED[0m[31m [ 70%][0m
tests/unit_min_deps/test_persistent_store.py::test_filesystem_store_rejects_path_traversal [32mPASSED[0m[31m [ 80%][0m
tests/unit_min_deps/test_persistent_store.py::test_filesystem_store_size_cap_enforced [32mPASSED[0m[31m [ 90%][0m
tests/unit_min_deps/test_persistent_store.py::test_filesystem_store_list_filter_by_kind [32mPASSED[0m[31m [100%][0m

================================== FAILURES ===================================
[31m[1m______________________________ test_sanitize_id _______________________________[0m
[1m[31mtests\unit_min_deps\test_persistent_store.py[0m:24: in test_sanitize_id
    [0m[94massert[39;49;00m _sanitize_id([33m"[39;49;00m[33m../etc/passwd[39;49;00m[33m"[39;49;00m) == [33m"[39;49;00m[33m.._etc_passwd[39;49;00m[33m"[39;49;00m[90m[39;49;00m
[1m[31mE   AssertionError: assert 'id_.._etc_passwd' == '.._etc_passwd'[0m
[1m[31mE     [0m
[1m[31mE     [0m[91m- .._etc_passwd[39;49;00m[90m[39;49;00m[0m
[1m[31mE     [92m+ id_.._etc_passwd[39;49;00m[90m[39;49;00m[0m
[1m[31mE     ? +++[90m[39;49;00m[0m
[33m============================== warnings summary ===============================[0m
tests/unit_min_deps/test_persistent_store.py: 13 warnings
  C:\Git\Agentic-Workflow\agentic_core\L4_state\storage\persistent_store.py:116: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_utc = datetime.utcnow().isoformat() + "Z"

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 9
Failed: 1
Errors: 0

\u274c GUARDIAN STATUS: FAIL
Architectural violations detected. Review failed tests.
======================================  =======================================
============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[36m[1m=========================== short test summary info ===========================[0m
[31mFAILED[0m tests/unit_min_deps/test_persistent_store.py::[1mtest_sanitize_id[0m - AssertionError: assert 'id_.._etc_passwd' == '.._etc_passwd'
[31m========== [31m[1m1 failed[0m, [32m9 passed[0m, [33m406 deselected[0m, [33m13 warnings[0m[31m in 0.41s[0m[31m ===========[0m


## TEST_RUN_2

### pytest -q tests/unit_min_deps/ -k "persistent_store or filesystem_store or replay_storage"
EXIT CODE: 1
STDOUT:
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 451 items / 406 deselected / 45 selected

tests/unit_min_deps/test_persistent_store.py::test_sanitize_id [31mFAILED[0m[31m    [ 10%][0m
tests/unit_min_deps/test_persistent_store.py::test_canonicalize_payload [32mPASSED[0m[31m [ 20%][0m
tests/unit_min_deps/test_persistent_store.py::test_compute_sha256 [32mPASSED[0m[31m [ 30%][0m
tests/unit_min_deps/test_persistent_store.py::test_create_artifact [32mPASSED[0m[31m [ 40%][0m
tests/unit_min_deps/test_persistent_store.py::test_filesystem_store_put_creates_v0001_then_v0002 [32mPASSED[0m[31m [ 50%][0m
tests/unit_min_deps/test_persistent_store.py::test_filesystem_store_get_round_trip [32mPASSED[0m[31m [ 60%][0m
tests/unit_min_deps/test_persistent_store.py::test_filesystem_store_list_ordering [32mPASSED[0m[31m [ 70%][0m
tests/unit_min_deps/test_persistent_store.py::test_filesystem_store_rejects_path_traversal [32mPASSED[0m[31m [ 80%][0m
tests/unit_min_deps/test_persistent_store.py::test_filesystem_store_size_cap_enforced [32mPASSED[0m[31m [ 90%][0m
tests/unit_min_deps/test_persistent_store.py::test_filesystem_store_list_filter_by_kind [32mPASSED[0m[31m [100%][0m

================================== FAILURES ===================================
[31m[1m______________________________ test_sanitize_id _______________________________[0m
[1m[31mtests\unit_min_deps\test_persistent_store.py[0m:24: in test_sanitize_id
    [0m[94massert[39;49;00m _sanitize_id([33m"[39;49;00m[33m../etc/passwd[39;49;00m[33m"[39;49;00m) == [33m"[39;49;00m[33m.._etc_passwd[39;49;00m[33m"[39;49;00m[90m[39;49;00m
[1m[31mE   AssertionError: assert 'id_.._etc_passwd' == '.._etc_passwd'[0m
[1m[31mE     [0m
[1m[31mE     [0m[91m- .._etc_passwd[39;49;00m[90m[39;49;00m[0m
[1m[31mE     [92m+ id_.._etc_passwd[39;49;00m[90m[39;49;00m[0m
[1m[31mE     ? +++[90m[39;49;00m[0m
[33m============================== warnings summary ===============================[0m
tests/unit_min_deps/test_persistent_store.py: 13 warnings
  C:\Git\Agentic-Workflow\agentic_core\L4_state\storage\persistent_store.py:116: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_utc = datetime.utcnow().isoformat() + "Z"

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 9
Failed: 1
Errors: 0

\u274c GUARDIAN STATUS: FAIL
Architectural violations detected. Review failed tests.
======================================  =======================================
============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[36m[1m=========================== short test summary info ===========================[0m
[31mFAILED[0m tests/unit_min_deps/test_persistent_store.py::[1mtest_sanitize_id[0m - AssertionError: assert 'id_.._etc_passwd' == '.._etc_passwd'
[31m========== [31m[1m1 failed[0m, [32m9 passed[0m, [33m406 deselected[0m, [33m13 warnings[0m[31m in 0.23s[0m[31m ===========[0m


## REPLAY_STORAGE_TEST

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


### STORED_ARTIFACTS_VERIFICATION
STORE_ROOT_NOT_FOUND: docs/store

## SCOPE_VERIFICATION

### git diff --name-only
EXIT CODE: 0
STDOUT:
(empty)

### git status --porcelain
EXIT CODE: 0
STDOUT:
(empty)
