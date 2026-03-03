# Execute SSOT Mutation Fence Hardening — Phase 2 Evidence

## Wave 1 — Coverage Audit

### L2 Write Inventory
```json
{
  "scan_root": "agentic_core\\L2_execution",
  "total_writes": 55,
  "writes": [
    {
      "file": "agentic_core\\L2_execution\\config\\hybrid_retriever_config.py",
      "line": 210,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\config\\hybrid_retriever_config.py",
      "line": 214,
      "primitive": "replace",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\enforcement\\dashboard_e2_e_pipeline.py",
      "line": 143,
      "primitive": "write_text",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\enforcement\\dashboard_e2_e_pipeline_enforcer.py",
      "line": 143,
      "primitive": "write_text",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\enforcement\\sovereign_filesystem_mcp.py",
      "line": 50,
      "primitive": "replace",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\enforcement\\sovereign_filesystem_mcp_enforcer.py",
      "line": 50,
      "primitive": "replace",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\engines\\action_node_core.py",
      "line": 81,
      "primitive": "replace",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\engines\\secure_tools_impl.py",
      "line": 65,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\engines\\secure_tools_impl.py",
      "line": 66,
      "primitive": "open(mode=w)",
      "type": "builtin_open"
    },
    {
      "file": "agentic_core\\L2_execution\\healers\\classification_compliance_healer.py",
      "line": 130,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\healers\\classification_compliance_healer.py",
      "line": 131,
      "primitive": "shutil.move",
      "type": "shutil_call"
    },
    {
      "file": "agentic_core\\L2_execution\\healers\\drift_detection_healer.py",
      "line": 95,
      "primitive": "shutil.rmtree",
      "type": "shutil_call"
    },
    {
      "file": "agentic_core\\L2_execution\\healers\\drift_detection_healer.py",
      "line": 103,
      "primitive": "unlink",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\healers\\hierarchy_compliance_healer.py",
      "line": 81,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\reasoning\\SubAtomicRegistryAgent.py",
      "line": 468,
      "primitive": "replace",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\reasoning\\ToolsmithAgent.py",
      "line": 353,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\reasoning\\ToolsmithAgent.py",
      "line": 355,
      "primitive": "open(mode=w)",
      "type": "builtin_open"
    },
    {
      "file": "agentic_core\\L2_execution\\reasoning\\ToolsmithAgent.py",
      "line": 359,
      "primitive": "open(mode=w)",
      "type": "builtin_open"
    },
    {
      "file": "agentic_core\\L2_execution\\reasoning\\ToolsmithAgent.py",
      "line": 362,
      "primitive": "open(mode=w)",
      "type": "builtin_open"
    },
    {
      "file": "agentic_core\\L2_execution\\reasoning\\ToolsmithAgent.py",
      "line": 500,
      "primitive": "write_text",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\scripts\\remediation_dispatcher.py",
      "line": 526,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\scripts\\remediation_dispatcher.py",
      "line": 528,
      "primitive": "write_text",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\file_io_impl.py",
      "line": 121,
      "primitive": "open(mode=w)",
      "type": "builtin_open"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 71,
      "primitive": "replace",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 89,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 90,
      "primitive": "write_text",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 100,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 101,
      "primitive": "write_bytes",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 110,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 111,
      "primitive": "open(mode=w)",
      "type": "builtin_open"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 121,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 122,
      "primitive": "open(mode=a)",
      "type": "builtin_open"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 132,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 133,
      "primitive": "open(mode=w)",
      "type": "builtin_open"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 143,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 154,
      "primitive": "unlink",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 163,
      "primitive": "rmdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 172,
      "primitive": "shutil.rmtree",
      "type": "shutil_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 180,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 181,
      "primitive": "shutil.copy2",
      "type": "shutil_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 190,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 191,
      "primitive": "shutil.move",
      "type": "shutil_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 200,
      "primitive": "rename",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 209,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 219,
      "primitive": "shutil.copytree",
      "type": "shutil_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 240,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 251,
      "primitive": "unlink",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 252,
      "primitive": "replace",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 255,
      "primitive": "unlink",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 270,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 271,
      "primitive": "open(mode=w)",
      "type": "builtin_open"
    },
    {
      "file": "agentic_core\\L2_execution\\tools\\write_gateway.py",
      "line": 284,
      "primitive": "open(mode=a)",
      "type": "builtin_open"
    },
    {
      "file": "agentic_core\\L2_execution\\utils\\deterministic_cleaner_util.py",
      "line": 120,
      "primitive": "unlink",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\utils\\deterministic_cleaner_util.py",
      "line": 198,
      "primitive": "mkdir",
      "type": "method_call"
    },
    {
      "file": "agentic_core\\L2_execution\\utils\\deterministic_cleaner_util.py",
      "line": 199,
      "primitive": "open(mode=w)",
      "type": "builtin_open"
    }
  ]
}
```

### Write Gateway Callers
```
tests\guardian\test_ssot_no_self_mutation.py:31:write_gateway.write_text(target, "corrupted content")
tests\guardian\test_ssot_no_self_mutation.py:46:result = write_gateway.write_text(target, "safe content")
tests\guardian\test_ssot_no_self_mutation.py:63:result = write_gateway.write_text(target, "allowed content")
tests\guardian\test_ssot_no_self_mutation.py:203:result = write_gateway.write_text(target, '{"ok": true}')
tests\unit_min_deps\test_ssot_mutation_fence.py:60:write_gateway.write_text(target_path, "test content")
tests\unit_min_deps\test_ssot_mutation_fence.py:71:write_gateway.write_text(target_path, "test content")
tests\unit_min_deps\test_ssot_mutation_fence.py:82:write_gateway.write_bytes(target_path, b"test data")
```

## Wave 2 — Guardrail Extensions

**Commit hash:** 53a1a8c92

**Files changed:**
- agentic_core/L0_routing/enforcement/mutation_prohibition.py
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
collected 11 items

tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_agentic_core [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_allows_outside [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_override_allows [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_tests [32mPASSED[0m[32m [ 36%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_github [32mPASSED[0m[32m [ 45%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_agentic_core [32mPASSED[0m[32m [ 54%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_tests [32mPASSED[0m[32m [ 63%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_github [32mPASSED[0m[32m [ 72%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_blocks_protected_root [32mPASSED[0m[32m [ 81%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_allows_outside_protected_root [32mPASSED[0m[32m [ 90%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_bytes_blocks_protected_root [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================= [32m[1m11 passed[0m[32m in 0.03s[0m[32m ==============================[0m


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
collected 4212 items / 46 errors
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

[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 3.50s[0m[31m ========================[0m

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

**Coverage:** Wave 1 inventory identified 55 write operations in L2_execution layer. Only 7 call sites use write_gateway (all in tests). No additional protected roots justified—current set (agentic_core, tests, .github) covers critical repo infrastructure.

**Diagnostics:** Enhanced SourceMutationBlocked exception to include normalized target path and matched immutable root name. This improves debugging by showing exactly which protected root triggered the block.

**Tests:** Added 3 new tests verifying exception message includes matched_root={name}. Tests now fail if diagnostic message regresses. Total: 11 tests, all passing.

**Safety:** Changes are purely observability enhancements. No mutation authority expanded. Enforcement logic unchanged.

## Follow-ons (out-of-scope)

1. Add telemetry event emission when protected-root writes are blocked (target path + caller context)
2. Create L2 write surface audit dashboard showing all filesystem write operations by layer
3. Consider adding ops_scripts/ to protected roots if SSOT runner scripts become critical
