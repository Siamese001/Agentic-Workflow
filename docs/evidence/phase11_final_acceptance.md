# Phase 11: Baseline-Aware Invariants & Deterministic PTC Storage

## Scope
- Semantic PowerShell ban (AST callsite only, no string literals)
- Baseline category gating (skip unseeded categories)
- Deterministic tool-call storage outside repo by default

## CODE_COMMIT
21ebdd746e546b4d0a512ba6ded574c8f0e5bfdc

## EVIDENCE_COMMIT
PENDING

## FILES_CHANGED_CODE
.gitignore

## Static Invariants Check
$ python tools/run_static_invariants.py
=== Static Invariants Checker ===

Loaded baseline with 1653 existing violations across 535 categories

1. Scanning for PowerShell usage...
OK: PowerShell Ban: No violations found

2. Scanning for direct writes...
FAIL: Direct Writes: 191 total violations found (0 new)

3. Scanning for non-deterministic serialization...
OK: Determinism Serialization: No violations found

4. Scanning for PTC invariants...
OK: PTC Invariants: No violations found

=== Summary ===
Total violations: 191 (0 new)
OK: No NEW violations found


## PTC Tests (Run 1)
$ pytest -q tests/unit_min_deps/ -k ptc
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 511 items / 447 deselected / 64 selected

tests/unit_min_deps/test_ptc.py::test_tool_arg_validation [32mPASSED[0m[32m         [  3%][0m
tests/unit_min_deps/test_ptc.py::test_tool_spec_validation [32mPASSED[0m[32m        [  6%][0m
tests/unit_min_deps/test_ptc.py::test_tool_call_validation [32mPASSED[0m[32m        [ 10%][0m
tests/unit_min_deps/test_ptc.py::test_deterministic_registry_listing [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/test_ptc.py::test_duplicate_tool_id_rejected [32mPASSED[0m[32m  [ 17%][0m
tests/unit_min_deps/test_ptc.py::test_unsorted_args_rejected [32mPASSED[0m[32m      [ 20%][0m
tests/unit_min_deps/test_ptc.py::test_call_id_stable [32mPASSED[0m[32m              [ 24%][0m
tests/unit_min_deps/test_ptc.py::test_canonical_json [32mPASSED[0m[32m              [ 27%][0m
tests/unit_min_deps/test_ptc.py::test_sha256_hex [32mPASSED[0m[32m                  [ 31%][0m
tests/unit_min_deps/test_ptc.py::test_tool_spec_serialization [32mPASSED[0m[32m     [ 34%][0m
tests/unit_min_deps/test_ptc.py::test_global_registry [32mPASSED[0m[32m             [ 37%][0m
tests/unit_min_deps/test_ptc.py::test_tool_invoker_validation [32mPASSED[0m[32m     [ 41%][0m
tests/unit_min_deps/test_ptc.py::test_tool_invoker_powershell_ban [32mPASSED[0m[32m [ 44%][0m
tests/unit_min_deps/test_ptc.py::test_tool_invoker_truncation [32mPASSED[0m[32m     [ 48%][0m
tests/unit_min_deps/test_ptc.py::test_tool_call_store [32mPASSED[0m[32m             [ 51%][0m
tests/unit_min_deps/test_ptc.py::test_tool_call_store_deterministic_ordering [32mPASSED[0m[32m [ 55%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_repo_rg_tool [32mPASSED[0m[32m        [ 58%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool [32mPASSED[0m[32m      [ 62%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic [32mPASSED[0m[33m [ 65%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_tools_registration [32mPASSED[0m[33m  [ 68%][0m
tests/unit_min_deps/test_ptc.py::test_execute_ssot_ptc_integration [32mPASSED[0m[33m [ 72%][0m
tests/unit_min_deps/test_ptc.py::test_ptc_plan_output_stable [32mPASSED[0m[33m      [ 75%][0m
tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner [32mPASSED[0m[33m      [ 79%][0m
tests/unit_min_deps/test_ptc.py::test_static_includes_ptc [32mPASSED[0m[33m         [ 82%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_tool_registry_exists_and_must_route_via_write_gateway [32mPASSED[0m[33m [ 86%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_is_canonical_write_layer [32mPASSED[0m[33m [ 89%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_functions_accept_allow_override [32mPASSED[0m[33m [ 93%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_future_tool_contract_enforcement_ready [32mPASSED[0m[33m [ 96%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_l2_execution_tools_do_not_expose_raw_write_primitives [32mPASSED[0m[33m [100%][0m

[33m============================== warnings summary ===============================[0m
tests/unit_min_deps/test_ptc.py: 19 warnings
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:219: DeprecationWarning: ast.Num is deprecated and will be removed in Python 3.14; use ast.Constant instead
    if isinstance(node, ast.Num):  # Python < 3.8

tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:223: DeprecationWarning: ast.Str is deprecated and will be removed in Python 3.14; use ast.Constant instead
    elif isinstance(node, ast.Str):  # Python < 3.8

tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:225: DeprecationWarning: ast.NameConstant is deprecated and will be removed in Python 3.14; use ast.Constant instead
    elif isinstance(node, ast.NameConstant):

tests/unit_min_deps/test_ptc.py: 10 warnings
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:220: DeprecationWarning: Attribute n is deprecated and will be removed in Python 3.14; use value instead
    return node.n

tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner
tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner
  C:\Git\Agentic-Workflow\agentic_core\L5_safety\static_checks\ptc_invariants.py:64: DeprecationWarning: ast.Str is deprecated and will be removed in Python 3.14; use ast.Constant instead
    if isinstance(arg, ast.Str) or isinstance(arg, ast.Constant):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 29
Failed: 0
Errors: 0

\u2705 GUARDIAN STATUS: PASS
All architectural integrity checks passed.
======================================  =======================================
============================ slowest 10 durations =============================
44.91s call     tests/unit_min_deps/test_ptc.py::test_static_includes_ptc
0.21s call     tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner
0.18s call     tests/unit_min_deps/test_ptc.py::test_ptc_plan_output_stable
0.12s call     tests/unit_min_deps/test_ptc.py::test_execute_ssot_ptc_integration
0.07s call     tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_tool_registry_exists_and_must_route_via_write_gateway
0.02s call     tests/unit_min_deps/test_ptc.py::test_builtin_repo_rg_tool
0.01s call     tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_l2_execution_tools_do_not_expose_raw_write_primitives

(3 durations < 0.005s hidden.  Use -vv to show these durations.)
[33m============== [32m29 passed[0m, [33m[1m447 deselected[0m, [33m[1m47 warnings[0m[33m in 46.00s[0m[33m ===============[0m


## PTC Tests (Run 2 - Determinism Check)
$ pytest -q tests/unit_min_deps/ -k ptc
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 511 items / 447 deselected / 64 selected

tests/unit_min_deps/test_ptc.py::test_tool_arg_validation [32mPASSED[0m[32m         [  3%][0m
tests/unit_min_deps/test_ptc.py::test_tool_spec_validation [32mPASSED[0m[32m        [  6%][0m
tests/unit_min_deps/test_ptc.py::test_tool_call_validation [32mPASSED[0m[32m        [ 10%][0m
tests/unit_min_deps/test_ptc.py::test_deterministic_registry_listing [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/test_ptc.py::test_duplicate_tool_id_rejected [32mPASSED[0m[32m  [ 17%][0m
tests/unit_min_deps/test_ptc.py::test_unsorted_args_rejected [32mPASSED[0m[32m      [ 20%][0m
tests/unit_min_deps/test_ptc.py::test_call_id_stable [32mPASSED[0m[32m              [ 24%][0m
tests/unit_min_deps/test_ptc.py::test_canonical_json [32mPASSED[0m[32m              [ 27%][0m
tests/unit_min_deps/test_ptc.py::test_sha256_hex [32mPASSED[0m[32m                  [ 31%][0m
tests/unit_min_deps/test_ptc.py::test_tool_spec_serialization [32mPASSED[0m[32m     [ 34%][0m
tests/unit_min_deps/test_ptc.py::test_global_registry [32mPASSED[0m[32m             [ 37%][0m
tests/unit_min_deps/test_ptc.py::test_tool_invoker_validation [32mPASSED[0m[32m     [ 41%][0m
tests/unit_min_deps/test_ptc.py::test_tool_invoker_powershell_ban [32mPASSED[0m[32m [ 44%][0m
tests/unit_min_deps/test_ptc.py::test_tool_invoker_truncation [32mPASSED[0m[32m     [ 48%][0m
tests/unit_min_deps/test_ptc.py::test_tool_call_store [32mPASSED[0m[32m             [ 51%][0m
tests/unit_min_deps/test_ptc.py::test_tool_call_store_deterministic_ordering [32mPASSED[0m[32m [ 55%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_repo_rg_tool [32mPASSED[0m[32m        [ 58%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool [32mPASSED[0m[32m      [ 62%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic [32mPASSED[0m[33m [ 65%][0m
tests/unit_min_deps/test_ptc.py::test_builtin_tools_registration [32mPASSED[0m[33m  [ 68%][0m
tests/unit_min_deps/test_ptc.py::test_execute_ssot_ptc_integration [32mPASSED[0m[33m [ 72%][0m
tests/unit_min_deps/test_ptc.py::test_ptc_plan_output_stable [32mPASSED[0m[33m      [ 75%][0m
tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner [32mPASSED[0m[33m      [ 79%][0m
tests/unit_min_deps/test_ptc.py::test_static_includes_ptc [32mPASSED[0m[33m         [ 82%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_tool_registry_exists_and_must_route_via_write_gateway [32mPASSED[0m[33m [ 86%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_is_canonical_write_layer [32mPASSED[0m[33m [ 89%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_functions_accept_allow_override [32mPASSED[0m[33m [ 93%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_future_tool_contract_enforcement_ready [32mPASSED[0m[33m [ 96%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_l2_execution_tools_do_not_expose_raw_write_primitives [32mPASSED[0m[33m [100%][0m

[33m============================== warnings summary ===============================[0m
tests/unit_min_deps/test_ptc.py: 19 warnings
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:219: DeprecationWarning: ast.Num is deprecated and will be removed in Python 3.14; use ast.Constant instead
    if isinstance(node, ast.Num):  # Python < 3.8

tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:223: DeprecationWarning: ast.Str is deprecated and will be removed in Python 3.14; use ast.Constant instead
    elif isinstance(node, ast.Str):  # Python < 3.8

tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_expr_eval_tool
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
tests/unit_min_deps/test_ptc.py::test_builtin_tools_deterministic
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:225: DeprecationWarning: ast.NameConstant is deprecated and will be removed in Python 3.14; use ast.Constant instead
    elif isinstance(node, ast.NameConstant):

tests/unit_min_deps/test_ptc.py: 10 warnings
  C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\ptc\builtin_tools.py:220: DeprecationWarning: Attribute n is deprecated and will be removed in Python 3.14; use value instead
    return node.n

tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner
tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner
  C:\Git\Agentic-Workflow\agentic_core\L5_safety\static_checks\ptc_invariants.py:64: DeprecationWarning: ast.Str is deprecated and will be removed in Python 3.14; use ast.Constant instead
    if isinstance(arg, ast.Str) or isinstance(arg, ast.Constant):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 1
Passed: 29
Failed: 0
Errors: 0

\u2705 GUARDIAN STATUS: PASS
All architectural integrity checks passed.
======================================  =======================================
============================ slowest 10 durations =============================
39.41s call     tests/unit_min_deps/test_ptc.py::test_static_includes_ptc
0.21s call     tests/unit_min_deps/test_ptc.py::test_ptc_invariants_scanner
0.18s call     tests/unit_min_deps/test_ptc.py::test_ptc_plan_output_stable
0.09s call     tests/unit_min_deps/test_ptc.py::test_execute_ssot_ptc_integration
0.07s call     tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_tool_registry_exists_and_must_route_via_write_gateway
0.01s call     tests/unit_min_deps/test_ptc.py::test_builtin_repo_rg_tool
0.01s call     tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_l2_execution_tools_do_not_expose_raw_write_primitives

(3 durations < 0.005s hidden.  Use -vv to show these durations.)
[33m============== [32m29 passed[0m, [33m[1m447 deselected[0m, [33m[1m47 warnings[0m[33m in 40.19s[0m[33m ===============[0m


## Execute SSOT Plan Mode
$ python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --plan --ptc-plan
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

=== PROGRAMMATIC TOOL CALLING ===
{"artifact_ref":{"kind":"tool_call","logical_id":"55a25da241434a526dc174bd6d100c7111d6c352823047510b9aad82b270cbc9","path":"tool_call\\55a25da241434a526dc174bd6d100c7111d6c352823047510b9aad82b270cbc9\\v0014.json","version":14},"summary":"PTC executed 1 tool calls for plan context","tool_calls":[{"args":{"expr":"2 + 3 * 4"},"call_id":"55a25da241434a526dc174bd6d100c7111d6c352823047510b9aad82b270cbc9","exit_code":0,"stderr":"","stdout":"14","tool_id":"expr_eval","truncated":false}]}



## Git Status Check
$ git status --porcelain
 M "docs/technical/Drill-Down 1 - L1 [U0] Transformation & RAG Pipeline.md"
