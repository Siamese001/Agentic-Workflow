# Execute SSOT Mutation Fence Hardening — Phase 4 Evidence

## Wave 1 — Policy Inventory + Contract Surface

### Policy Locations
```
build_evidence.py:26:parts.append('\n## RCA (<=12 lines)\n- Runner previously allowed protected-root writes because enforcement was not structurally bound at the L2 write boundary.\n- A writable repo root meant agent behavior could persist mutations into agentic_core/ during SSOT runs.\n- Fix: add enforce_protected_root() (deterministic) and call it in write_gateway before any filesystem write.\n- Override is explicit via --allow-protected-root-mutation and is logged once, preventing accidental escalation.\n- Domain mode adds forced dry_run for protected domains when override is disabled, reducing accidental mutation attempts.\n')
build_phase2_evidence.py:59:parts.append('**Diagnostics:** Enhanced SourceMutationBlocked exception to include normalized target path and matched immutable root name. ')
build_phase3_evidence.py:56:parts.append('**Event Emission Design:** Added ProtectedRootBlockEvent dataclass with 4 fields: ts_utc (ISO8601), target (normalized path), matched_root (name), caller (module:function). ')
build_phase3_evidence.py:59:parts.append('Each block produces exactly one newline-terminated JSON line in logs/ssot_protected_root_blocks.jsonl.\n\n')
build_phase3_evidence.py:61:parts.append('Logging failures never prevent SourceMutationBlocked from being raised. ')
build_phase3_evidence.py:63:parts.append('**Safety:** No mutation authority added. Log destination (logs/) is outside IMMUTABLE_ROOTS. ')
build_phase3_evidence.py:68:parts.append('1. Add log rotation policy for logs/ssot_protected_root_blocks.jsonl to prevent unbounded growth\n')
scan_policy_locations.py:10:r'IMMUTABLE_ROOTS',
scan_policy_locations.py:11:r'enforce_protected_root',
scan_policy_locations.py:12:r'SourceMutationBlocked',
scan_policy_locations.py:13:r'ProtectedRootBlockEvent',
agentic_core\L0_routing\enforcement\mutation_prohibition.py:38:class SourceMutationBlocked(RuntimeError):
agentic_core\L0_routing\enforcement\mutation_prohibition.py:44:class ProtectedRootBlockEvent:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:59:event = ProtectedRootBlockEvent(
agentic_core\L0_routing\enforcement\mutation_prohibition.py:63:caller="mutation_prohibition:enforce_protected_root"
agentic_core\L0_routing\enforcement\mutation_prohibition.py:67:log_path = Path("logs/ssot_protected_root_blocks.jsonl")
agentic_core\L0_routing\enforcement\mutation_prohibition.py:83:IMMUTABLE_ROOTS = (
agentic_core\L0_routing\enforcement\mutation_prohibition.py:90:def enforce_protected_root(target_path: Path, *, allow_override: bool) -> None:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:98:SourceMutationBlocked: If target_path is under a protected root and override is disabled
agentic_core\L0_routing\enforcement\mutation_prohibition.py:111:for immutable_root in IMMUTABLE_ROOTS:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:115:raise SourceMutationBlocked(
agentic_core\L0_routing\enforcement\mutation_prohibition.py:124:raise SourceMutationBlocked(
agentic_core\L2_execution\tools\write_gateway.py:26:enforce_protected_root,
agentic_core\L2_execution\tools\write_gateway.py:27:SourceMutationBlocked,
agentic_core\L2_execution\tools\write_gateway.py:87:enforce_protected_root(p, allow_override=allow_override)
agentic_core\L2_execution\tools\write_gateway.py:98:enforce_protected_root(p, allow_override=allow_override)
tests\unit_min_deps\test_ssot_mutation_fence.py:10:enforce_protected_root,
tests\unit_min_deps\test_ssot_mutation_fence.py:11:SourceMutationBlocked,
tests\unit_min_deps\test_ssot_mutation_fence.py:20:def test_enforce_protected_root_blocks_agentic_core(self):
tests\unit_min_deps\test_ssot_mutation_fence.py:23:with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
tests\unit_min_deps\test_ssot_mutation_fence.py:24:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:26:def test_enforce_protected_root_allows_outside(self):
tests\unit_min_deps\test_ssot_mutation_fence.py:30:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:32:def test_enforce_protected_root_override_allows(self):
tests\unit_min_deps\test_ssot_mutation_fence.py:36:enforce_protected_root(target_path, allow_override=True)
tests\unit_min_deps\test_ssot_mutation_fence.py:38:def test_enforce_protected_root_blocks_tests(self):
tests\unit_min_deps\test_ssot_mutation_fence.py:41:with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
tests\unit_min_deps\test_ssot_mutation_fence.py:42:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:44:def test_enforce_protected_root_blocks_github(self):
tests\unit_min_deps\test_ssot_mutation_fence.py:47:with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
tests\unit_min_deps\test_ssot_mutation_fence.py:48:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:53:with pytest.raises(SourceMutationBlocked, match="matched_root=agentic_core"):
tests\unit_min_deps\test_ssot_mutation_fence.py:54:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:59:with pytest.raises(SourceMutationBlocked, match="matched_root=tests"):
tests\unit_min_deps\test_ssot_mutation_fence.py:60:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:65:with pytest.raises(SourceMutationBlocked, match=r"matched_root=\.github"):
tests\unit_min_deps\test_ssot_mutation_fence.py:66:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:78:with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
tests\unit_min_deps\test_ssot_mutation_fence.py:100:with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
tests\unit_min_deps\test_ssot_mutation_fence.py:119:mock_path_cls.side_effect = lambda x: Path(x) if x != "logs/ssot_protected_root_blocks.jsonl" else log_file
tests\unit_min_deps\test_ssot_mutation_fence.py:124:if "logs/ssot_protected_root_blocks.jsonl" in str(path):
tests\unit_min_deps\test_ssot_mutation_fence.py:129:with pytest.raises(SourceMutationBlocked):
tests\unit_min_deps\test_ssot_mutation_fence.py:130:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:144:assert event["caller"] == "mutation_prohibition:enforce_protected_root"
tests\unit_min_deps\test_ssot_mutation_fence.py:147:"""Test that logging failures do not mask SourceMutationBlocked."""
tests\unit_min_deps\test_ssot_mutation_fence.py:152:# Should still raise SourceMutationBlocked, not PermissionError
tests\unit_min_deps\test_ssot_mutation_fence.py:153:with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
tests\unit_min_deps\test_ssot_mutation_fence.py:154:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:161:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:162:assert False, "Should have raised SourceMutationBlocked"
tests\unit_min_deps\test_ssot_mutation_fence.py:163:except SourceMutationBlocked as e:
```

### CLI Override References
```
build_evidence.py:26:parts.append('\n## RCA (<=12 lines)\n- Runner previously allowed protected-root writes because enforcement was not structurally bound at the L2 write boundary.\n- A writable repo root meant agent behavior could persist mutations into agentic_core/ during SSOT runs.\n- Fix: add enforce_protected_root() (deterministic) and call it in write_gateway before any filesystem write.\n- Override is explicit via --allow-protected-root-mutation and is logged once, preventing accidental escalation.\n- Domain mode adds forced dry_run for protected domains when override is disabled, reducing accidental mutation attempts.\n')
scan_cli_override_refs.py:10:r'--allow-protected-root-mutation',
scan_cli_override_refs.py:11:r'allow_override',
scan_cli_override_refs.py:12:r'allow-override',
scan_cli_override_refs.py:13:r'AGENTIC_ALLOW_MUTATION'
agentic_core\L0_routing\enforcement\mutation_prohibition.py:9:Override: AGENTIC_ALLOW_MUTATION_FOR_TESTS=1 (env var, test-only).
agentic_core\L0_routing\enforcement\mutation_prohibition.py:31:_ENV_OVERRIDE_KEY = "AGENTIC_ALLOW_MUTATION_FOR_TESTS"
agentic_core\L0_routing\enforcement\mutation_prohibition.py:90:def enforce_protected_root(target_path: Path, *, allow_override: bool) -> None:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:95:allow_override: If True, bypass the protection (audited CLI override)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:100:if allow_override:
agentic_core\L0_routing\scripts\execute_ssot.py:2527:"--allow-protected-root-mutation",
agentic_core\L2_execution\scripts\remediation_dispatcher.py:114:def mutation_allowed(repo_root: Path, allow_override: bool) -> bool:
agentic_core\L2_execution\scripts\remediation_dispatcher.py:119:- allow_override is True (--allow-repo-mutation)
agentic_core\L2_execution\scripts\remediation_dispatcher.py:121:if allow_override:
agentic_core\L2_execution\tools\write_gateway.py:84:def write_text(path: str | Path, content: str, encoding: str = "utf-8", *, allow_override: bool = False) -> str:
agentic_core\L2_execution\tools\write_gateway.py:87:enforce_protected_root(p, allow_override=allow_override)
agentic_core\L2_execution\tools\write_gateway.py:95:def write_bytes(path: str | Path, data: bytes, *, allow_override: bool = False) -> str:
agentic_core\L2_execution\tools\write_gateway.py:98:enforce_protected_root(p, allow_override=allow_override)
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
tests\unit_min_deps\test_ssot_mutation_fence.py:24:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:30:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:36:enforce_protected_root(target_path, allow_override=True)
tests\unit_min_deps\test_ssot_mutation_fence.py:42:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:48:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:54:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:60:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:66:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:130:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:154:enforce_protected_root(target_path, allow_override=False)
tests\unit_min_deps\test_ssot_mutation_fence.py:161:enforce_protected_root(target_path, allow_override=False)
```

## Wave 2 — Policy Contract

**Commit hash:** ad0cd65a8

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
collected 19 items

tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_agentic_core [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_allows_outside [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_override_allows [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_tests [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_github [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_agentic_core [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_tests [32mPASSED[0m[32m [ 36%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_github [32mPASSED[0m[32m [ 42%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_blocks_protected_root [32mPASSED[0m[32m [ 47%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_allows_outside_protected_root [32mPASSED[0m[32m [ 52%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_bytes_blocks_protected_root [32mPASSED[0m[32m [ 57%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_block_emits_jsonl_event [32mPASSED[0m[32m [ 63%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_logging_failure_does_not_mask_exception [32mPASSED[0m[32m [ 68%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_exception_message_still_includes_diagnostics [32mPASSED[0m[32m [ 73%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_immutable_roots [32mPASSED[0m[32m [ 78%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_log_path [32mPASSED[0m[32m [ 84%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_log_path_writes_to_tmp [32mPASSED[0m[32m [ 89%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_immutable_roots_changes_matched_root [32mPASSED[0m[32m [ 94%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_none_uses_default [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================= [32m[1m19 passed[0m[32m in 0.04s[0m[32m ==============================[0m


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
collected 4220 items / 46 errors
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

[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 3.44s[0m[31m ========================[0m

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

**Policy Contract:** Added ProtectedRootPolicy dataclass centralizing immutable_roots tuple and log_path string. Function get_default_protected_root_policy() returns canonical policy: ("agentic_core","tests",".github") + "logs/ssot_protected_root_blocks.jsonl".

**Auditability:** Policy is now explicitly queryable via get_default_protected_root_policy(). Tests assert exact immutable_roots contract. Any future policy change requires test update, preventing silent drift.

**Test Isolation:** enforce_protected_root accepts optional policy parameter. Unit tests inject custom policy with tmp_path log_path, ensuring zero writes to repo logs/ during test runs.

**Enforcement Unchanged:** Block logic remains identical. Policy contract adds zero mutation authority. IMMUTABLE_ROOTS constant preserved for backward compatibility, derived from default policy.

## Follow-ons (out-of-scope)

1. Add CLI command to query current protected-root policy (e.g., `python -m agentic_core.L0_routing.enforcement.mutation_prohibition --show-policy`)
2. Create policy validation test in CI that fails if immutable_roots changes without explicit approval
3. Add policy versioning metadata (e.g., policy_version field) for future evolution tracking
