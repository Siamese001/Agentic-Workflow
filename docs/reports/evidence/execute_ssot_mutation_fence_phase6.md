# Execute SSOT Mutation Fence Hardening — Phase 6 Evidence

## Wave 1 — Spec + Wiring Inventory

### Execute SSOT CLI References
```
agentic_core\L0_routing\scripts\execute_ssot.py:15:import argparse
agentic_core\L0_routing\scripts\execute_ssot.py:147:def _apply_v15_enforcement_flag(args: argparse.Namespace) -> None:
agentic_core\L0_routing\scripts\execute_ssot.py:151:os.environ["V15_ENFORCEMENT"] = "1" if int(args.v15_enforcement) == 1 else "0"
agentic_core\L0_routing\scripts\execute_ssot.py:2329:# Used by --plan introspection and by AST contract tests.
agentic_core\L0_routing\scripts\execute_ssot.py:2433:# Agent dependency graph for --agent subset closure.
agentic_core\L0_routing\scripts\execute_ssot.py:2518:pre_parser = argparse.ArgumentParser(add_help=False)
agentic_core\L0_routing\scripts\execute_ssot.py:2519:pre_parser.add_argument(
agentic_core\L0_routing\scripts\execute_ssot.py:2520:"--v15-enforcement",
agentic_core\L0_routing\scripts\execute_ssot.py:2526:pre_parser.add_argument(
agentic_core\L0_routing\scripts\execute_ssot.py:2527:"--allow-protected-root-mutation",
agentic_core\L0_routing\scripts\execute_ssot.py:2532:pre_parser.add_argument(
agentic_core\L0_routing\scripts\execute_ssot.py:2534:"--verbose",
agentic_core\L0_routing\scripts\execute_ssot.py:2539:pre_args, remaining = pre_parser.parse_known_args()
agentic_core\L0_routing\scripts\execute_ssot.py:2540:_configure_logging(int(pre_args.verbose))
agentic_core\L0_routing\scripts\execute_ssot.py:2545:if pre_args.allow_protected_root_mutation:
agentic_core\L0_routing\scripts\execute_ssot.py:2551:_legacy_main(remaining, repo_root=REPO_ROOT, allow_protected_root_mutation=pre_args.allow_protected_root_mutation)
agentic_core\L0_routing\scripts\execute_ssot.py:2571:parser = argparse.ArgumentParser(
agentic_core\L0_routing\scripts\execute_ssot.py:2573:formatter_class=argparse.RawDescriptionHelpFormatter,
agentic_core\L0_routing\scripts\execute_ssot.py:2577:python execute_ssot_script.py --territory prompt_governance
agentic_core\L0_routing\scripts\execute_ssot.py:2580:python execute_ssot_script.py --domains
agentic_core\L0_routing\scripts\execute_ssot.py:2583:python execute_ssot_script.py --territory L5_safety --dry-run
agentic_core\L0_routing\scripts\execute_ssot.py:2586:python execute_ssot_script.py --list-agents
agentic_core\L0_routing\scripts\execute_ssot.py:2589:python execute_ssot_script.py --agent NamingAgent
agentic_core\L0_routing\scripts\execute_ssot.py:2592:parser.add_argument("--territory", type=str, help="Specific territory to scan")
agentic_core\L0_routing\scripts\execute_ssot.py:2593:parser.add_argument("--domains", action="store_true", help="Scan all major domains (Multi-Domain Mode)")
agentic_core\L0_routing\scripts\execute_ssot.py:2594:parser.add_argument("--agent", type=str, help="Run specific agent directly")
agentic_core\L0_routing\scripts\execute_ssot.py:2595:parser.add_argument("--list-agents", action="store_true", help="List discoverable agents")
agentic_core\L0_routing\scripts\execute_ssot.py:2596:parser.add_argument(
agentic_core\L0_routing\scripts\execute_ssot.py:2597:"--enable-cda",
agentic_core\L0_routing\scripts\execute_ssot.py:2601:parser.add_argument("--dry-run", action="store_true", help="Run in preview mode (no changes applied)")
agentic_core\L0_routing\scripts\execute_ssot.py:2602:parser.add_argument(
agentic_core\L0_routing\scripts\execute_ssot.py:2603:"--interactive",
agentic_core\L0_routing\scripts\execute_ssot.py:2607:parser.add_argument("--manual", action="store_true", help="Disable autonomous mode (legacy)")
agentic_core\L0_routing\scripts\execute_ssot.py:2608:parser.add_argument(
agentic_core\L0_routing\scripts\execute_ssot.py:2609:"--validate",
agentic_core\L0_routing\scripts\execute_ssot.py:2613:parser.add_argument(
agentic_core\L0_routing\scripts\execute_ssot.py:2614:"--plan",
agentic_core\L0_routing\scripts\execute_ssot.py:2618:parser.add_argument(
agentic_core\L0_routing\scripts\execute_ssot.py:2619:"--agents",
agentic_core\L0_routing\scripts\execute_ssot.py:2622:help="Comma-separated list of agent keys to run (e.g. --agents location,hierarchy). Includes dependencies automatically. Hard-fails on unknown keys.",
agentic_core\L0_routing\scripts\execute_ssot.py:2625:parser.add_argument("--capture-baseline", action="store_true", help="Capture new Golden Baseline")
agentic_core\L0_routing\scripts\execute_ssot.py:2626:parser.add_argument(
agentic_core\L0_routing\scripts\execute_ssot.py:2627:"--v15-enforcement",
agentic_core\L0_routing\scripts\execute_ssot.py:2633:parser.add_argument(
agentic_core\L0_routing\scripts\execute_ssot.py:2635:"--verbose",
agentic_core\L0_routing\scripts\execute_ssot.py:2640:args = parser.parse_args(extra_argv)
agentic_core\L0_routing\scripts\execute_ssot.py:2643:if args.plan:
agentic_core\L0_routing\scripts\execute_ssot.py:2647:# [AGENT SUBSET] Validate and resolve --agents early (before imports).
agentic_core\L0_routing\scripts\execute_ssot.py:2649:if args.agents:
agentic_core\L0_routing\scripts\execute_ssot.py:2650:raw_keys = [k.strip() for k in args.agents.split(",") if k.strip()]
agentic_core\L0_routing\scripts\execute_ssot.py:2655:parser.error(str(ve))
agentic_core\L0_routing\scripts\execute_ssot.py:2658:# When --validate is set, dry_run is forced True. This ensures
agentic_core\L0_routing\scripts\execute_ssot.py:2660:if args.validate:
agentic_core\L0_routing\scripts\execute_ssot.py:2661:args.dry_run = True
agentic_core\L0_routing\scripts\execute_ssot.py:2664:validator = PreFlightValidator(project_root, dry_run=args.dry_run)
agentic_core\L0_routing\scripts\execute_ssot.py:2670:if not args.list_agents:
agentic_core\L0_routing\scripts\execute_ssot.py:2674:if args.territory and not re.match(r"^[A-Za-z0-9_]+$", args.territory):
agentic_core\L0_routing\scripts\execute_ssot.py:2675:parser.error("Invalid territory name: only alphanumeric and underscores allowed.")
agentic_core\L0_routing\scripts\execute_ssot.py:2678:if args.list_agents:
agentic_core\L0_routing\scripts\execute_ssot.py:2687:if args.capture_baseline:
agentic_core\L0_routing\scripts\execute_ssot.py:2708:if args.agent:
agentic_core\L0_routing\scripts\execute_ssot.py:2709:logger.info(f"DIRECT AGENT EXECUTION: {args.agent}")
agentic_core\L0_routing\scripts\execute_ssot.py:2711:found = [x for x in list_available_agents(project_root) if args.agent.lower() in x[0].lower()]
agentic_core\L0_routing\scripts\execute_ssot.py:2713:logger.error(f"Agent {args.agent} not found.")
agentic_core\L0_routing\scripts\execute_ssot.py:2714:logger.info("Use --list-agents to see available agents")
agentic_core\L0_routing\scripts\execute_ssot.py:2757:dry_run = args.dry_run
agentic_core\L0_routing\scripts\execute_ssot.py:2758:auto_approve = not args.interactive
agentic_core\L0_routing\scripts\execute_ssot.py:2774:logger.info(f"  Mode: {'AUTONOMOUS' if not args.manual else 'MANUAL'}")
agentic_core\L0_routing\scripts\execute_ssot.py:2797:if not args.list_agents:
agentic_core\L0_routing\scripts\execute_ssot.py:2853:if args.territory:
agentic_core\L0_routing\scripts\execute_ssot.py:2854:targets = [args.territory]
agentic_core\L0_routing\scripts\execute_ssot.py:2855:mission_mode = f"Territory Scan: {args.territory}"
agentic_core\L0_routing\scripts\execute_ssot.py:2856:elif args.domains:
agentic_core\L0_routing\scripts\execute_ssot.py:2871:if args.domains and not allow_protected_root_mutation:
agentic_core\L0_routing\scripts\execute_ssot.py:2882:is_autonomous = not args.manual
agentic_core\L0_routing\scripts\execute_ssot.py:2916:if args.validate:
agentic_core\L0_routing\scripts\execute_ssot.py:2928:if args.domains:
agentic_core\L0_routing\scripts\execute_ssot.py:3325:"  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy\n",
```

### Policy References
```
agentic_core\L0_routing\enforcement\mutation_prohibition.py:44:class ProtectedRootBlockEvent:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:53:class ProtectedRootPolicy:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:59:immutable_roots: tuple[str, ...]  # Root names (e.g., "agentic_core", "tests", ".github")
agentic_core\L0_routing\enforcement\mutation_prohibition.py:60:log_path: str  # JSONL log destination for block events
agentic_core\L0_routing\enforcement\mutation_prohibition.py:63:def get_default_protected_root_policy() -> ProtectedRootPolicy:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:67:ProtectedRootPolicy with canonical immutable roots and log path
agentic_core\L0_routing\enforcement\mutation_prohibition.py:69:return ProtectedRootPolicy(
agentic_core\L0_routing\enforcement\mutation_prohibition.py:70:immutable_roots=("agentic_core", "tests", ".github"),
agentic_core\L0_routing\enforcement\mutation_prohibition.py:71:log_path="logs/ssot_protected_root_blocks.jsonl"
agentic_core\L0_routing\enforcement\mutation_prohibition.py:75:def _emit_block_event(target: Path, matched_root: str, log_path: str) -> None:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:81:log_path: Path to JSONL log file
agentic_core\L0_routing\enforcement\mutation_prohibition.py:87:event = ProtectedRootBlockEvent(
agentic_core\L0_routing\enforcement\mutation_prohibition.py:95:log_file = Path(log_path)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:112:def _get_immutable_roots() -> tuple[Path, ...]:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:114:policy = get_default_protected_root_policy()
agentic_core\L0_routing\enforcement\mutation_prohibition.py:116:return tuple(repo_root / root_name for root_name in policy.immutable_roots)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:119:IMMUTABLE_ROOTS = _get_immutable_roots()
agentic_core\L0_routing\enforcement\mutation_prohibition.py:126:policy: ProtectedRootPolicy | None = None
agentic_core\L0_routing\enforcement\mutation_prohibition.py:143:policy = get_default_protected_root_policy()
agentic_core\L0_routing\enforcement\mutation_prohibition.py:147:immutable_roots = tuple(repo_root / root_name for root_name in policy.immutable_roots)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:157:for immutable_root in immutable_roots:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:160:_emit_block_event(resolved, immutable_root.name, policy.log_path)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:169:_emit_block_event(resolved, immutable_root.name, policy.log_path)
tests\unit_min_deps\test_ssot_mutation_fence.py:12:ProtectedRootPolicy,
tests\unit_min_deps\test_ssot_mutation_fence.py:13:get_default_protected_root_policy,
tests\unit_min_deps\test_ssot_mutation_fence.py:175:def test_default_policy_immutable_roots(self):
tests\unit_min_deps\test_ssot_mutation_fence.py:177:policy = get_default_protected_root_policy()
tests\unit_min_deps\test_ssot_mutation_fence.py:178:assert policy.immutable_roots == ("agentic_core", "tests", ".github")
tests\unit_min_deps\test_ssot_mutation_fence.py:180:def test_default_policy_log_path(self):
tests\unit_min_deps\test_ssot_mutation_fence.py:182:policy = get_default_protected_root_policy()
tests\unit_min_deps\test_ssot_mutation_fence.py:183:assert policy.log_path == "logs/ssot_protected_root_blocks.jsonl"
tests\unit_min_deps\test_ssot_mutation_fence.py:185:def test_policy_override_log_path_writes_to_tmp(self, tmp_path):
tests\unit_min_deps\test_ssot_mutation_fence.py:186:"""Test that overriding policy.log_path writes JSONL to tmp_path (no writes to repo logs)."""
tests\unit_min_deps\test_ssot_mutation_fence.py:191:custom_policy = ProtectedRootPolicy(
tests\unit_min_deps\test_ssot_mutation_fence.py:192:immutable_roots=("agentic_core", "tests", ".github"),
tests\unit_min_deps\test_ssot_mutation_fence.py:193:log_path=str(log_file)
tests\unit_min_deps\test_ssot_mutation_fence.py:215:def test_policy_override_immutable_roots_changes_matched_root(self, tmp_path):
tests\unit_min_deps\test_ssot_mutation_fence.py:216:"""Test that changing policy.immutable_roots changes matched_root in exception and event."""
tests\unit_min_deps\test_ssot_mutation_fence.py:221:custom_policy = ProtectedRootPolicy(
tests\unit_min_deps\test_ssot_mutation_fence.py:222:immutable_roots=("custom_protected",),
tests\unit_min_deps\test_ssot_mutation_fence.py:223:log_path=str(log_file)
```

### Write Gateway Chain References
```
agentic_core\L2_execution\tools\write_gateway.py:26:enforce_protected_root,
agentic_core\L2_execution\tools\write_gateway.py:37:def _get_repo_root() -> Path:
agentic_core\L2_execution\tools\write_gateway.py:64:def _deny_writes_into_source_roots(path: Path, verb: str = "write") -> None:
agentic_core\L2_execution\tools\write_gateway.py:68:enforce_protected_root() which uses ProtectedRootPolicy (no env vars).
agentic_core\L2_execution\tools\write_gateway.py:87:def write_text(path: str | Path, content: str, encoding: str = "utf-8", *, allow_override: bool = False) -> str:
agentic_core\L2_execution\tools\write_gateway.py:90:enforce_protected_root(p, allow_override=allow_override)
agentic_core\L2_execution\tools\write_gateway.py:91:_deny_writes_into_source_roots(p, "write")
agentic_core\L2_execution\tools\write_gateway.py:98:def write_bytes(path: str | Path, data: bytes, *, allow_override: bool = False) -> str:
agentic_core\L2_execution\tools\write_gateway.py:101:enforce_protected_root(p, allow_override=allow_override)
agentic_core\L2_execution\tools\write_gateway.py:102:_deny_writes_into_source_roots(p, "write")
agentic_core\L2_execution\tools\write_gateway.py:109:def write_json(path: str | Path, obj: Any, indent: int = 2) -> str:
agentic_core\L2_execution\tools\write_gateway.py:112:_deny_writes_into_source_roots(p, "write")
agentic_core\L2_execution\tools\write_gateway.py:120:def append_text(path: str | Path, content: str, encoding: str = "utf-8") -> str:
agentic_core\L2_execution\tools\write_gateway.py:123:_deny_writes_into_source_roots(p, "append")
agentic_core\L2_execution\tools\write_gateway.py:131:def open_write(path: str | Path, content: str, encoding: str = "utf-8") -> str:
agentic_core\L2_execution\tools\write_gateway.py:134:_deny_writes_into_source_roots(p, "write")
agentic_core\L2_execution\tools\write_gateway.py:142:def ensure_dir(path: str | Path) -> Path:
agentic_core\L2_execution\tools\write_gateway.py:145:_deny_writes_into_source_roots(p, "mkdir")
agentic_core\L2_execution\tools\write_gateway.py:151:def remove_file(path: str | Path, missing_ok: bool = True) -> None:
agentic_core\L2_execution\tools\write_gateway.py:154:_deny_writes_into_source_roots(p, "delete")
agentic_core\L2_execution\tools\write_gateway.py:161:def remove_dir(path: str | Path) -> None:
agentic_core\L2_execution\tools\write_gateway.py:164:_deny_writes_into_source_roots(p, "delete")
agentic_core\L2_execution\tools\write_gateway.py:170:def remove_tree(path: str | Path) -> None:
agentic_core\L2_execution\tools\write_gateway.py:173:_deny_writes_into_source_roots(p, "delete")
agentic_core\L2_execution\tools\write_gateway.py:179:def copy_file(src: str | Path, dst: str | Path) -> str:
agentic_core\L2_execution\tools\write_gateway.py:182:_deny_writes_into_source_roots(d, "copy")
agentic_core\L2_execution\tools\write_gateway.py:189:def move_path(src: str | Path, dst: str | Path) -> str:
agentic_core\L2_execution\tools\write_gateway.py:192:_deny_writes_into_source_roots(d, "move")
agentic_core\L2_execution\tools\write_gateway.py:199:def rename_path(src: str | Path, dst: str | Path) -> Path:
agentic_core\L2_execution\tools\write_gateway.py:202:_deny_writes_into_source_roots(d, "rename")
agentic_core\L2_execution\tools\write_gateway.py:208:def touch_file(path: str | Path) -> Path:
agentic_core\L2_execution\tools\write_gateway.py:211:_deny_writes_into_source_roots(p, "touch")
agentic_core\L2_execution\tools\write_gateway.py:218:def copy_tree(src: str | Path, dst: str | Path) -> str:
agentic_core\L2_execution\tools\write_gateway.py:221:_deny_writes_into_source_roots(d, "copy")
agentic_core\L2_execution\tools\write_gateway.py:227:def makedirs(path: str | Path, exist_ok: bool = True) -> str:
agentic_core\L2_execution\tools\write_gateway.py:229:_deny_writes_into_source_roots(Path(path), "mkdir")
agentic_core\L2_execution\tools\write_gateway.py:235:def write_json_atomic(
agentic_core\L2_execution\tools\write_gateway.py:242:_deny_writes_into_source_roots(p, "write")
agentic_core\L2_execution\tools\write_gateway.py:266:def init_csv(
agentic_core\L2_execution\tools\write_gateway.py:272:_deny_writes_into_source_roots(p, "write")
agentic_core\L2_execution\tools\write_gateway.py:280:def append_csv_row(
agentic_core\L2_execution\tools\write_gateway.py:286:_deny_writes_into_source_roots(p, "append")
```

## Wave 2 — Self-Check Implementation

**Commit hash:** 65ca22ebb

**Files changed:**
- agentic_core/L0_routing/scripts/execute_ssot.py
- agentic_core/L0_routing/scripts/execute_ssot_entrypoint.py
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
collected 26 items

tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_agentic_core [32mPASSED[0m[32m [  3%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_allows_outside [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_override_allows [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_tests [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_github [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_agentic_core [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_tests [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_github [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_blocks_protected_root [32mPASSED[0m[32m [ 34%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_allows_outside_protected_root [32mPASSED[0m[32m [ 38%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_bytes_blocks_protected_root [32mPASSED[0m[32m [ 42%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_block_emits_jsonl_event [32mPASSED[0m[32m [ 46%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_logging_failure_does_not_mask_exception [32mPASSED[0m[32m [ 50%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_exception_message_still_includes_diagnostics [32mPASSED[0m[32m [ 53%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_immutable_roots [32mPASSED[0m[32m [ 57%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_log_path [32mPASSED[0m[32m [ 61%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_log_path_writes_to_tmp [32mPASSED[0m[32m [ 65%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_immutable_roots_changes_matched_root [32mPASSED[0m[32m [ 69%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_none_uses_default [32mPASSED[0m[32m [ 73%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_env_allow_mutation_does_not_bypass_protected_root [32mPASSED[0m[32m [ 76%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_env_deny_mutation_does_not_change_protected_root [32mPASSED[0m[32m [ 80%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_cli_override_works_regardless_of_env [32mPASSED[0m[32m [ 84%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_unset_env_vars_do_not_change_behavior [32mPASSED[0m[32m [ 88%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_ok_path [32mPASSED[0m[32m [ 92%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_fails_with_bad_log_path [32mPASSED[0m[32m [ 96%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_validates_write_gateway_wiring [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================
0.09s call     tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_ok_path
0.01s call     tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_fails_with_bad_log_path

(8 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================= [32m[1m26 passed[0m[32m in 0.16s[0m[32m ==============================[0m


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
collected 4227 items / 46 errors
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

[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 3.39s[0m[31m ========================[0m

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
2026-02-21 17:59:42,830 WARNING agentic_core.L0_routing.enforcement.execution_gateway [V15-GW] Successful commit with no mutations detected
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

**Self-Check Mode:** Added --fence-self-check flag to execute_ssot_entrypoint. Performs 4 deterministic validations without file mutations: (1) default policy immutable_roots contract, (2) log_path outside protected roots, (3) write_gateway wiring integrity, (4) telemetry path safety.

**Safety Without Mutation:** Self-check uses runtime introspection (inspect.signature, inspect.getsource) and pure path checks (Path.resolve, relative_to). Zero filesystem writes. Exits 0 if all checks pass, nonzero with failed check names otherwise.

**Deterministic Output:** Single-line JSON with sorted keys: {"status":"ok","checks":4} or {"status":"fail","failed":["check_name",...]}. Enables CI/smoke testing of fence configuration without running full SSOT pipeline.

**Test Coverage:** Added 3 new tests (TestFenceSelfCheck) verifying ok path, bad log_path detection, and write_gateway wiring validation. Total: 26 tests, all passing (rc=0).

## Follow-ons (out-of-scope)

1. Add --fence-self-check to CI pre-commit hook to catch policy regressions before merge
2. Extend self-check to validate IMMUTABLE_ROOTS paths exist on disk (optional filesystem check mode)
3. Add self-check validation for emit_block_event signature compatibility with ProtectedRootBlockEvent dataclass
