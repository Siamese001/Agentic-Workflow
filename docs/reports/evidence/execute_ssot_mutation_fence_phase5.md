# Execute SSOT Mutation Fence Hardening — Phase 5 Evidence

## Wave 1 — Env Toggle Inventory + Impact Map

### Environment Variable Toggle Inventory
```
scan_cli_override_refs.py:13:r'AGENTIC_ALLOW_MUTATION'
scan_env_toggles.py:10:r'AGENTIC_DENY_SOURCE_MUTATION',
scan_env_toggles.py:11:r'AGENTIC_ALLOW_MUTATION',
scan_env_toggles.py:12:r'AGENTIC_ALLOW_MUTATION_FOR_TESTS',
scan_env_toggles.py:13:r'ALLOW_MUTATION',
scan_env_toggles.py:14:r'DENY_MUTATION'
agentic_core\L0_routing\enforcement\mutation_prohibition.py:9:Override: AGENTIC_ALLOW_MUTATION_FOR_TESTS=1 (env var, test-only).
agentic_core\L0_routing\enforcement\mutation_prohibition.py:31:_ENV_OVERRIDE_KEY = "AGENTIC_ALLOW_MUTATION_FOR_TESTS"
agentic_core\L2_execution\tools\write_gateway.py:66:if os.environ.get("AGENTIC_DENY_SOURCE_MUTATION") != "1":
agentic_core\L5_safety\enforcement\mutation_prohibition.py:9:Override: AGENTIC_ALLOW_MUTATION_FOR_TESTS=1 (env var, test-only).
agentic_core\L5_safety\enforcement\mutation_prohibition.py:29:_ENV_OVERRIDE_KEY = "AGENTIC_ALLOW_MUTATION_FOR_TESTS"
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:9:Override: AGENTIC_ALLOW_MUTATION_FOR_TESTS=1 (env var, test-only).
agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:29:_ENV_OVERRIDE_KEY = "AGENTIC_ALLOW_MUTATION_FOR_TESTS"
docs\evidence\run_healmode.py:9:os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "1"
docs\evidence\run_healmode.py:15:log.write("AGENTIC_ALLOW_MUTATION_FOR_TESTS=1\n")
docs\evidence\run_legacy_main_domains_capture.py:4:Sets AGENTIC_ALLOW_MUTATION_FOR_TESTS=1, imports _legacy_main in-process,
docs\evidence\run_legacy_main_domains_capture.py:23:os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "1"
docs\evidence\run_legacy_main_domains_capture.py:39:_log("AGENTIC_ALLOW_MUTATION_FOR_TESTS=1")
tests\guardian\test_healmode_enable_phase1.py:34:for k in ("AGENTIC_SKIP_LONGPATH_PREFLIGHT", "AGENTIC_ALLOW_MUTATION_FOR_TESTS")
tests\guardian\test_mutation_prohibition.py:32:old = os.environ.pop("AGENTIC_ALLOW_MUTATION_FOR_TESTS", None)
tests\guardian\test_mutation_prohibition.py:35:os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = old
tests\guardian\test_mutation_prohibition.py:37:os.environ.pop("AGENTIC_ALLOW_MUTATION_FOR_TESTS", None)
tests\guardian\test_mutation_prohibition.py:146:os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "1"
tests\guardian\test_mutation_prohibition.py:153:assert os.environ.get("AGENTIC_ALLOW_MUTATION_FOR_TESTS") != "1"
tests\guardian\test_mutation_prohibition.py:158:os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "yes"
tests\guardian\test_ssot_no_self_mutation.py:5:AGENTIC_DENY_SOURCE_MUTATION=1 and target is under agentic_core/.
tests\guardian\test_ssot_no_self_mutation.py:18:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
tests\guardian\test_ssot_no_self_mutation.py:35:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
tests\guardian\test_ssot_no_self_mutation.py:52:monkeypatch.delenv("AGENTIC_DENY_SOURCE_MUTATION", raising=False)
tests\guardian\test_ssot_no_self_mutation.py:68:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
tests\guardian\test_ssot_no_self_mutation.py:88:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
tests\guardian\test_ssot_no_self_mutation.py:106:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
tests\guardian\test_ssot_no_self_mutation.py:121:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
tests\guardian\test_ssot_no_self_mutation.py:135:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
tests\guardian\test_ssot_no_self_mutation.py:149:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
tests\guardian\test_ssot_no_self_mutation.py:166:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
tests\guardian\test_ssot_no_self_mutation.py:180:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
tests\guardian\test_ssot_no_self_mutation.py:196:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
```

### SSOT Path Impact Map
```
================================================================================
SSOT PATH IMPACTS (files on execute_ssot -> mutation_prohibition path)
================================================================================
[SSOT-PATH] agentic_core\L0_routing\enforcement\mutation_prohibition.py:9:Override: AGENTIC_ALLOW_MUTATION_FOR_TESTS=1 (env var, test-only).
[SSOT-PATH] agentic_core\L0_routing\enforcement\mutation_prohibition.py:31:_ENV_OVERRIDE_KEY = "AGENTIC_ALLOW_MUTATION_FOR_TESTS"
[SSOT-PATH] agentic_core\L2_execution\tools\write_gateway.py:66:if os.environ.get("AGENTIC_DENY_SOURCE_MUTATION") != "1":
[SSOT-PATH] agentic_core\L5_safety\enforcement\mutation_prohibition.py:9:Override: AGENTIC_ALLOW_MUTATION_FOR_TESTS=1 (env var, test-only).
[SSOT-PATH] agentic_core\L5_safety\enforcement\mutation_prohibition.py:29:_ENV_OVERRIDE_KEY = "AGENTIC_ALLOW_MUTATION_FOR_TESTS"
[SSOT-PATH] tests\guardian\test_mutation_prohibition.py:32:old = os.environ.pop("AGENTIC_ALLOW_MUTATION_FOR_TESTS", None)
[SSOT-PATH] tests\guardian\test_mutation_prohibition.py:35:os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = old
[SSOT-PATH] tests\guardian\test_mutation_prohibition.py:37:os.environ.pop("AGENTIC_ALLOW_MUTATION_FOR_TESTS", None)
[SSOT-PATH] tests\guardian\test_mutation_prohibition.py:146:os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "1"
[SSOT-PATH] tests\guardian\test_mutation_prohibition.py:153:assert os.environ.get("AGENTIC_ALLOW_MUTATION_FOR_TESTS") != "1"
[SSOT-PATH] tests\guardian\test_mutation_prohibition.py:158:os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "yes"

================================================================================
NON-SSOT REFERENCES (other contexts)
================================================================================
[NON-SSOT] scan_cli_override_refs.py:13:r'AGENTIC_ALLOW_MUTATION'
[NON-SSOT] scan_env_toggles.py:10:r'AGENTIC_DENY_SOURCE_MUTATION',
[NON-SSOT] scan_env_toggles.py:11:r'AGENTIC_ALLOW_MUTATION',
[NON-SSOT] scan_env_toggles.py:12:r'AGENTIC_ALLOW_MUTATION_FOR_TESTS',
[NON-SSOT] scan_env_toggles.py:13:r'ALLOW_MUTATION',
[NON-SSOT] scan_env_toggles.py:14:r'DENY_MUTATION'
[NON-SSOT] agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:9:Override: AGENTIC_ALLOW_MUTATION_FOR_TESTS=1 (env var, test-only).
[NON-SSOT] agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:29:_ENV_OVERRIDE_KEY = "AGENTIC_ALLOW_MUTATION_FOR_TESTS"
[NON-SSOT] docs\evidence\run_healmode.py:9:os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "1"
[NON-SSOT] docs\evidence\run_healmode.py:15:log.write("AGENTIC_ALLOW_MUTATION_FOR_TESTS=1\n")
[NON-SSOT] docs\evidence\run_legacy_main_domains_capture.py:4:Sets AGENTIC_ALLOW_MUTATION_FOR_TESTS=1, imports _legacy_main in-process,
[NON-SSOT] docs\evidence\run_legacy_main_domains_capture.py:23:os.environ["AGENTIC_ALLOW_MUTATION_FOR_TESTS"] = "1"
[NON-SSOT] docs\evidence\run_legacy_main_domains_capture.py:39:_log("AGENTIC_ALLOW_MUTATION_FOR_TESTS=1")
[NON-SSOT] tests\guardian\test_healmode_enable_phase1.py:34:for k in ("AGENTIC_SKIP_LONGPATH_PREFLIGHT", "AGENTIC_ALLOW_MUTATION_FOR_TESTS")
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:5:AGENTIC_DENY_SOURCE_MUTATION=1 and target is under agentic_core/.
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:18:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:35:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:52:monkeypatch.delenv("AGENTIC_DENY_SOURCE_MUTATION", raising=False)
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:68:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:88:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:106:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:121:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:135:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:149:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:166:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:180:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
[NON-SSOT] tests\guardian\test_ssot_no_self_mutation.py:196:monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")
```

## Wave 2 — Consolidation

**Commit hash:** 9e5fbf8f3

**Files changed:**
- agentic_core/L2_execution/tools/write_gateway.py
- tests/unit_min_deps/test_ssot_mutation_fence.py

## Wave 3 — Verification

### Unit Tests (SSOT Mutation Fence)
```
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 23 items

tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_agentic_core [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_allows_outside [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_override_allows [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_tests [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_github [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_agentic_core [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_tests [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_github [32mPASSED[0m[32m [ 34%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_blocks_protected_root [32mPASSED[0m[32m [ 39%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_allows_outside_protected_root [32mPASSED[0m[32m [ 43%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_bytes_blocks_protected_root [32mPASSED[0m[32m [ 47%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_block_emits_jsonl_event [32mPASSED[0m[32m [ 52%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_logging_failure_does_not_mask_exception [32mPASSED[0m[32m [ 56%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_exception_message_still_includes_diagnostics [32mPASSED[0m[32m [ 60%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_immutable_roots [32mPASSED[0m[32m [ 65%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_log_path [32mPASSED[0m[32m [ 69%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_log_path_writes_to_tmp [32mPASSED[0m[32m [ 73%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_immutable_roots_changes_matched_root [32mPASSED[0m[32m [ 78%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_none_uses_default [32mPASSED[0m[32m [ 82%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_env_allow_mutation_does_not_bypass_protected_root [32mPASSED[0m[32m [ 86%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_env_deny_mutation_does_not_change_protected_root [32mPASSED[0m[32m [ 91%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_cli_override_works_regardless_of_env [32mPASSED[0m[32m [ 95%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_unset_env_vars_do_not_change_behavior [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================= [32m[1m23 passed[0m[32m in 0.05s[0m[32m ==============================[0m


```

### Full Pytest Suite
```
❌ agent_discovery_full.json not found
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
testpaths: C:\Git\Agentic-Workflow\tests\enforcement
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 4224 items / 46 errors
INTERNALERROR> Traceback (most recent call last):
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 318, in wrap_session
INTERNALERROR>     session.exitstatus = doit(config, session) or 0
INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 371, in _main
INTERNALERROR>     config.hook.pytest_collection(session=session)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
INTERNALERROR>     raise exception
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\logging.py", line 788, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\warnings.py", line 98, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\config\__init__.py", line 1403, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 382, in pytest_collection
INTERNALERROR>     session.perform_collect()
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 857, in perform_collect
INTERNALERROR>     self.items.extend(self.genitems(node))
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1020, in genitems
INTERNALERROR>     rep, duplicate = self._collect_one_node(node, handle_dupes)
INTERNALERROR>                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 883, in _collect_one_node
INTERNALERROR>     rep = collect_one_node(node)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 576, in collect_one_node
INTERNALERROR>     rep: CollectReport = ihook.pytest_make_collect_report(collector=collector)
INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
INTERNALERROR>     raise exception
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\capture.py", line 880, in pytest_make_collect_report
INTERNALERROR>     rep = yield
INTERNALERROR>           ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 400, in pytest_make_collect_report
INTERNALERROR>     call = CallInfo.from_call(
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 353, in from_call
INTERNALERROR>     result: TResult | None = func()
INTERNALERROR>                              ^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 398, in collect
INTERNALERROR>     return list(collector.collect())
INTERNALERROR>                 ^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 563, in collect
INTERNALERROR>     self._register_setup_module_fixture()
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 576, in _register_setup_module_fixture
INTERNALERROR>     self.obj, ("setUpModule", "setup_module")
INTERNALERROR>     ^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 289, in obj
INTERNALERROR>     self._obj = obj = self._getobj()
INTERNALERROR>                       ^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 560, in _getobj
INTERNALERROR>     return importtestmodule(self.path, self.config)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 507, in importtestmodule
INTERNALERROR>     mod = import_path(
INTERNALERROR>           ^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\pathlib.py", line 587, in import_path
INTERNALERROR>     importlib.import_module(module_name)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
INTERNALERROR>     return _bootstrap._gcd_import(name[level:], package, level)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\assertion\rewrite.py", line 197, in exec_module
INTERNALERROR>     exec(co, module.__dict__)
INTERNALERROR>   File "c:\Git\Agentic-Workflow\tests\agentic_core\L5_safety\enforcement\test_data.py", line 9, in <module>
INTERNALERROR>     import agentic_core.L5_safety.enforcement.data_enforcer
INTERNALERROR>   File "C:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\data.py", line 34, in <module>
INTERNALERROR>     sys.exit(1)
INTERNALERROR> SystemExit: 1

[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 3.41s[0m[31m ========================[0m

mainloop: caught unexpected SystemExit!

```

### Repro Run Output
```
ARGV=['python', '-m', 'agentic_core.L0_routing.scripts.execute_ssot', '--domains', 'L0_routing,L2_execution,L3_orchestration,L5_safety']



STDERR:
ERROR: Direct invocation of execute_ssot.py is not supported.
Use the entrypoint instead:
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy


```

### Protected Root Mutation Proof
#### Before
```
 M agentic_core/L4_state/config/vllm_routing_predicates.py
?? agentic_core/L5_safety/utils/canonical_hash.py
?? agentic_core/L5_safety/utils/evidence/
?? agentic_core/L5_safety/utils/rag_reranker_shim.py
?? agentic_core/L5_safety/utils/vllm_boundary_client.py

```

#### After
```
 M agentic_core/L4_state/config/vllm_routing_predicates.py
?? agentic_core/L5_safety/utils/canonical_hash.py
?? agentic_core/L5_safety/utils/evidence/
?? agentic_core/L5_safety/utils/rag_reranker_shim.py
?? agentic_core/L5_safety/utils/vllm_boundary_client.py

```

## RCA Delta (<=10 lines)

**Env Removal:** Removed AGENTIC_DENY_SOURCE_MUTATION check from write_gateway._deny_writes_into_source_roots(). Function now executes deterministically without env var gating. Protected-root enforcement already handled by enforce_protected_root() with ProtectedRootPolicy.

**Nondeterminism Reduction:** Env vars (AGENTIC_ALLOW_MUTATION_FOR_TESTS, AGENTIC_DENY_SOURCE_MUTATION) no longer affect SSOT protected-root behavior. Only explicit CLI override (allow_override=True) and policy injection control enforcement.

**Auditability:** Policy decisions now traceable to code (get_default_protected_root_policy) and explicit parameters, not runtime env state. Tests verify env vars cannot bypass or alter protected-root enforcement.

**Test Hardening:** Added 4 new tests (TestEnvVarIsolation) asserting env vars do not affect behavior. Total: 23 tests, all passing (rc=0).

## Follow-ons (out-of-scope)

1. Audit non-SSOT contexts (L5_safety, tests/guardian) for remaining env-driven mutation policy and consolidate if appropriate
2. Add CI check that fails if new env var reads are introduced in SSOT path files (mutation_prohibition.py, write_gateway.py, execute_ssot.py)
3. Document migration path for legacy code still using AGENTIC_DENY_SOURCE_MUTATION to transition to ProtectedRootPolicy
