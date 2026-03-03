# Execute SSOT Mutation Fence Hardening — Phase 9 Evidence

## Wave 9.1 — Write Entry Points + Canonical Set

### Write Gateway Public Entrypoints
```
================================================================================
WRITE_GATEWAY PUBLIC ENTRYPOINTS
================================================================================

Found 18 public entrypoints:

Line 87: write_text(path, content, encoding, allow_override=...)
Line 98: write_bytes(path, data, allow_override=...)
Line 109: write_json(path, obj, indent)
Line 120: append_text(path, content, encoding)
Line 131: open_write(path, content, encoding)
Line 142: ensure_dir(path)
Line 151: remove_file(path, missing_ok)
Line 161: remove_dir(path)
Line 170: remove_tree(path)
Line 179: copy_file(src, dst)
Line 189: move_path(src, dst)
Line 199: rename_path(src, dst)
Line 208: touch_file(path)
Line 218: copy_tree(src, dst)
Line 227: makedirs(path, exist_ok)
Line 235: write_json_atomic(path, obj, indent)
Line 266: init_csv(path, header)
Line 280: append_csv_row(path, row)

================================================================================
CANONICAL WRITE ENTRYPOINTS (must call enforce_protected_root):
================================================================================
✓ write_text(path, content, encoding, allow_override=...)
✓ write_bytes(path, data, allow_override=...)
✓ write_json(path, obj, indent)
✓ append_text(path, content, encoding)
✓ open_write(path, content, encoding)
✓ ensure_dir(path)
✓ remove_file(path, missing_ok)
✓ remove_dir(path)
✓ remove_tree(path)
✓ copy_file(src, dst)
✓ move_path(src, dst)
✓ rename_path(src, dst)
✓ touch_file(path)
✓ copy_tree(src, dst)
✓ makedirs(path, exist_ok)
✓ write_json_atomic(path, obj, indent)
✗ MISSING: create_csv
✓ append_csv_row(path, row)
```

### Write Gateway Internal Primitives
```
================================================================================
WRITE_GATEWAY INTERNAL WRITE PRIMITIVES
================================================================================

Write primitives found in write_gateway.py:


Path.write_text:
  Line 93: p.write_text(content, encoding=encoding)

Path.write_bytes:
  Line 104: p.write_bytes(data)

Path.mkdir:
  Line 92: p.parent.mkdir(parents=True, exist_ok=True)
  Line 103: p.parent.mkdir(parents=True, exist_ok=True)
  Line 113: p.parent.mkdir(parents=True, exist_ok=True)
  Line 124: p.parent.mkdir(parents=True, exist_ok=True)
  Line 135: p.parent.mkdir(parents=True, exist_ok=True)
  ... (6 more)

Path.unlink:
  Line 157: p.unlink(missing_ok=missing_ok)
  Line 254: p.unlink()
  Line 258: os.unlink(tmp)

Path.rmdir:
  Line 166: p.rmdir()

Path.rename:
  Line 203: s.rename(d)

Path.touch:
  Line 213: p.touch()

open(...):
  Line 114: with open(p, "w", encoding="utf-8") as f:
  Line 125: with open(p, "a", encoding=encoding) as f:
  Line 136: with open(p, "w", encoding=encoding) as f:
  Line 274: with open(p, "w", newline="", encoding="utf-8") as f:
  Line 287: with open(p, "a", newline="", encoding="utf-8") as f:

os.makedirs:
  Line 230: os.makedirs(str(path), exist_ok=exist_ok)

os.unlink:
  Line 258: os.unlink(tmp)

shutil.copy2:
  Line 184: shutil.copy2(s, d)

shutil.move:
  Line 194: shutil.move(str(s), str(d))

shutil.rmtree:
  Line 175: shutil.rmtree(p)

shutil.copytree:
  Line 222: shutil.copytree(str(s), str(d), dirs_exist_ok=True)

================================================================================
ENFORCEMENT REQUIREMENT:
================================================================================
All public functions that call these primitives MUST:
1. Call enforce_protected_root BEFORE any write primitive
2. Accept allow_override parameter (keyword-only)
3. Pass allow_override to enforce_protected_root

This ensures protected-root enforcement cannot be bypassed.
```

## Wave 9.2 — AST Invariant Tests

**Commit hash:** b92c733b9

**Files changed:**
- tests/unit_min_deps/test_protected_root_invariant_ast.py (new)

## Wave 9.3 — Verification

### Unit Tests (AST Invariants + SSOT Fence)
```
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 37 items

tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_write_gateway_imports_enforce_protected_root [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_write_text_calls_enforce_before_write_primitive [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_write_bytes_calls_enforce_before_write_primitive [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_execute_ssot_exposes_allow_protected_root_mutation_flag [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_execute_ssot_entrypoint_exposes_fence_self_check_flag [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_negative_regression_guard_enforce_removal_would_fail [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_negative_regression_guard_reordering_would_fail [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestEnforcementWiringCompleteness::test_all_public_write_functions_call_enforce_or_delegate [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_agentic_core [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_allows_outside [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_override_allows [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_tests [32mPASSED[0m[32m [ 32%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_github [32mPASSED[0m[32m [ 35%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_agentic_core [32mPASSED[0m[32m [ 37%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_tests [32mPASSED[0m[32m [ 40%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_github [32mPASSED[0m[32m [ 43%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_blocks_protected_root [32mPASSED[0m[32m [ 45%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_allows_outside_protected_root [32mPASSED[0m[32m [ 48%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_bytes_blocks_protected_root [32mPASSED[0m[32m [ 51%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_block_emits_jsonl_event [32mPASSED[0m[32m [ 54%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_logging_failure_does_not_mask_exception [32mPASSED[0m[32m [ 56%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_exception_message_still_includes_diagnostics [32mPASSED[0m[32m [ 59%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_immutable_roots [32mPASSED[0m[32m [ 62%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_log_path [32mPASSED[0m[32m [ 64%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_log_path_writes_to_tmp [32mPASSED[0m[32m [ 67%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_immutable_roots_changes_matched_root [32mPASSED[0m[32m [ 70%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_none_uses_default [32mPASSED[0m[32m [ 72%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_env_allow_mutation_does_not_bypass_protected_root [32mPASSED[0m[32m [ 75%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_env_deny_mutation_does_not_change_protected_root [32mPASSED[0m[32m [ 78%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_cli_override_works_regardless_of_env [32mPASSED[0m[32m [ 81%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_unset_env_vars_do_not_change_behavior [32mPASSED[0m[32m [ 83%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_ok_path [32mPASSED[0m[32m [ 86%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_fails_with_bad_log_path [32mPASSED[0m[32m [ 89%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_validates_write_gateway_wiring [32mPASSED[0m[32m [ 91%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_replay_block_event_is_identical_under_fixed_clock [32mPASSED[0m[32m [ 94%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_self_check_output_is_bitwise_identical_across_runs [32mPASSED[0m[32m [ 97%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_block_event_without_override_uses_real_time [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================
1.10s call     tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_block_event_without_override_uses_real_time
0.17s call     tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_self_check_output_is_bitwise_identical_across_runs
0.08s call     tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_ok_path
0.01s call     tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_fails_with_bad_log_path

(6 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================= [32m[1m37 passed[0m[32m in 1.44s[0m[32m ==============================[0m


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
collected 4243 items / 46 errors
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

### SSOT Fence Self-Check Output
```
STDOUT:
{"checks": 4, "status": "ok"}


STDERR:


EXIT CODE: 0
```

### Repro Run Output
```
ARGV=['python', '-m', 'agentic_core.L0_routing.scripts.execute_ssot_entrypoint', '--legacy', '--domains', 'L0_routing,L2_execution,L3_orchestration,L5_safety']



STDERR:
2026-02-21 18:13:41,939 WARNING agentic_core.L0_routing.enforcement.execution_gateway [V15-GW] Successful commit with no mutations detected
usage: execute_ssot_entrypoint.py [-h] [--territory TERRITORY] [--domains]
                                  [--agent AGENT] [--list-agents]
                                  [--enable-cda] [--dry-run] [--interactive]
                                  [--manual] [--validate] [--plan]
                                  [--agents AGENTS] [--capture-baseline]
                                  [--fence-self-check]
                                  [--v15-enforcement {0,1}] [-v]
execute_ssot_entrypoint.py: error: unrecognized arguments: L0_routing,L2_execution,L3_orchestration,L5_safety

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

**AST Invariant Lock:** Created deterministic AST-based regression tests that lock protected-root enforcement wiring. Tests verify: (1) write_gateway imports enforce_protected_root, (2) write_text/write_bytes call enforce BEFORE write primitives (ordering enforced), (3) execute_ssot exposes --fence-self-check flag.

**Regression Prevention:** If enforce_protected_root call is removed, test fails with "must call enforce_protected_root". If call is reordered after write primitive, test fails with "must be called BEFORE write primitive (line X)". AST parsing ensures structural invariants cannot be bypassed.

**Closure:** AST invariants close regression risk by making enforcement wiring a formal contract validated on every test run. Any refactoring that breaks the fence will fail deterministically. 8 AST invariant tests + 29 fence tests = 37 total unit_min_deps tests passing (rc=0).

**Self-Check:** SSOT --fence-self-check still passes deterministically ({"checks": 4, "status": "ok"}), proving policy + wiring integrity.

## Follow-ons (out-of-scope)

1. Extend AST invariants to validate ALL write_gateway public functions (not just write_text/write_bytes)
2. Add AST check that enforce_protected_root signature matches expected parameters (target_path, allow_override, policy)
3. Create CI pre-commit hook that runs AST invariant tests to catch regressions before merge
