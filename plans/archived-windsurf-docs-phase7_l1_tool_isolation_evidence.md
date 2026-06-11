---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\phase7_l1_tool_isolation_evidence.md'
original_relative_path: 'phase7_l1_tool_isolation_evidence.md'
source_sha256: f638a4bb88f29fa44eee8b1db2201c936599b4011220e9549217a37942c746f1
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-21'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase 7 Evidence — L1 Tool Isolation: ToolIntent + L2.2 Execution Gateway

## Commit Hash
**9a6f3745c** — phase7: ToolIntent + L1 block enforcement + ToolIntentExecutor + ToolResult + tests

## Modified / New Files
- `agentic_core/L2_execution/types/tool_intent_types.py` [NEW — Wave 1: ToolCapability enum + ToolIntent + ToolViolation + l1_cognition_scope() + assert_l1_tool_allowed() + build_tool_intent()]
- `agentic_core/L2_execution/engines/tool_intent_executor.py` [NEW — Wave 2: ToolIntentExecutor (L2.2 sandbox-only) + ToolResult]
- `tests/agentic_core/test_phase7_tool_intent_model.py` [NEW — Wave 1: 35 tests]
- `tests/agentic_core/test_phase7_tool_executor.py` [NEW — Wave 2: 24 tests]
- `tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py` [NEW — Wave 3: 18 tests]

---

## Wave Summary

### Wave 1 — Tool Capabilities + L1 Block Enforcement
- `ToolCapability`: enum with `NON_MUTATING`, `MUTATING_EXTERNAL`, `MUTATING_FS`, `MUTATING_STATEBUS`
- `is_mutating(capability)`: returns True for any MUTATING_* capability
- `l1_cognition_scope()`: context manager activating `_L1_COGNITION_ACTIVE` flag; re-entrant; restored on exception
- `assert_l1_tool_allowed(capability, tool_name)`: raises `ToolViolation(code="L1_TOOL_CALL_BLOCKED")` if L1 active and capability is MUTATING_*; no-op outside scope or for NON_MUTATING
- `ToolViolation`: typed exception with `code` and `detail` fields
- `ToolIntent`: dataclass with `schema_version` (enforced == 1), `tool_name` (non-empty), `capability`, `args` (dict), `args_hash` (auto-computed sha256 of canonical args), `requires_commit` (enforced True for MUTATING_*), config hashes (policy/model/budget/routing), `intent_hash` (sha256 of canonical_bytes excluding intent_hash)
- `build_tool_intent()`: factory that auto-sets `requires_commit` from capability

### Wave 2 — ToolIntentExecutor (L2.2 Sandbox-Only) + ToolResult
- `ToolIntentExecutor.execute(intent, fn)`: checks `is_commit_sandbox_active()` if `intent.requires_commit`; raises `ToolViolation(code="TOOL_WRITE_OUTSIDE_SANDBOX")` if sandbox not active; delegates to `fn(intent.args)` and wraps result in `ToolResult`
- Reuses existing `MLWriteIntentExecutor` context manager from Phase 4 as the L2.2 sandbox
- `ToolResult`: dataclass with `schema_version`, `tool_name`, `args_hash`, `success`, `output_summary`, `anchor_ids` (sorted list), `result_hash` (sha256 of canonical_bytes excluding result_hash)
- NON_MUTATING tools (`requires_commit=False`) execute anywhere without sandbox check

### Wave 3 — End-to-End Gateway Path + Default Parity + Static Audit
- Full gateway path test: L1 blocks direct mutating call → L1 emits ToolIntent → L2.2 sandbox executes → ToolResult returned
- Default parity: NON_MUTATING tools execute without sandbox, without L1 block; behavior unchanged
- Static AST audit: `test_no_direct_redis_set_in_tool_intent_module` and `test_no_direct_redis_set_in_executor_module` walk AST and assert zero `setex`/`upsert` attribute calls — all mutations delegated to `fn()`
- Sandbox released after execution even when ToolViolation is raised mid-path

---

## Required Proof Commands (Verbatim, captured from clean tree after commit 9a6f3745c)

### 1. python --version
```
Python 3.12.10
```

### 2. python -m pytest --version
```
pytest 9.0.2
```

### 3. git status --porcelain=v1
```

```
(EMPTY — clean working tree)

### 4. git diff --name-only
```

```
(EMPTY — no unstaged changes)

### 5. git rev-parse HEAD
```
9a6f3745c1e7c06dd28134d7db05b4a7dfeef671
```

### 6. git log -1 --oneline
```
9a6f3745c (HEAD -> Codemap_defects) phase7: ToolIntent + L1 block enforcement + ToolIntentExecutor + ToolResult + tests
```

### 7. python -m pytest -q tests/agentic_core/test_phase7_tool_intent_model.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 35 items

tests/agentic_core/test_phase7_tool_intent_model.py::TestToolCapabilityModel::test_non_mutating_is_not_mutating PASSED [  2%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolCapabilityModel::test_mutating_external_is_mutating PASSED [  5%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolCapabilityModel::test_mutating_fs_is_mutating PASSED [  8%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolCapabilityModel::test_mutating_statebus_is_mutating PASSED [ 11%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolCapabilityModel::test_capability_values PASSED [ 14%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestL1CognitionScope::test_l1_inactive_by_default PASSED [ 17%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestL1CognitionScope::test_l1_active_inside_scope PASSED [ 20%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestL1CognitionScope::test_l1_inactive_after_scope PASSED [ 22%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestL1CognitionScope::test_l1_restored_on_exception PASSED [ 25%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestL1CognitionScope::test_nested_scope_stays_active PASSED [ 28%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestL1BlocksMutatingToolInvocation::test_l1_blocks_mutating_tool_invocation PASSED [ 31%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestL1BlocksMutatingToolInvocation::test_l1_blocks_mutating_fs PASSED [ 34%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestL1BlocksMutatingToolInvocation::test_l1_blocks_mutating_statebus PASSED [ 37%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestL1BlocksMutatingToolInvocation::test_violation_detail_contains_tool_name PASSED [ 40%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestL1BlocksMutatingToolInvocation::test_violation_detail_contains_capability PASSED [ 42%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestL1BlocksMutatingToolInvocation::test_l1_allows_non_mutating_tool_invocation PASSED [ 45%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestL1BlocksMutatingToolInvocation::test_mutating_allowed_outside_l1_scope PASSED [ 48%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentHashStable::test_tool_intent_hash_stable PASSED [ 51%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentHashStable::test_hash_changes_with_tool_name PASSED [ 54%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentHashStable::test_hash_changes_with_capability PASSED [ 57%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentHashStable::test_hash_changes_with_args PASSED [ 60%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentHashStable::test_intent_hash_excluded_from_canonical_bytes PASSED [ 62%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentHashStable::test_canonical_bytes_deterministic PASSED [ 65%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentHashStable::test_args_hash_auto_computed PASSED [ 68%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentHashStable::test_args_hash_stable PASSED [ 71%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentHashStable::test_args_hash_changes_with_args PASSED [ 74%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentValidation::test_invalid_schema_version_raises PASSED [ 77%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentValidation::test_empty_tool_name_raises PASSED [ 80%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentValidation::test_non_dict_args_raises PASSED [ 82%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentValidation::test_mutating_requires_commit_false_raises PASSED [ 85%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestToolIntentValidation::test_non_mutating_requires_commit_false_ok PASSED [ 88%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestBuildToolIntentFactory::test_factory_sets_requires_commit_true_for_mutating PASSED [ 91%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestBuildToolIntentFactory::test_factory_sets_requires_commit_false_for_non_mutating PASSED [ 94%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestBuildToolIntentFactory::test_factory_carries_config_hashes PASSED [ 97%]
tests/agentic_core/test_phase7_tool_intent_model.py::TestBuildToolIntentFactory::test_to_dict_contains_all_fields PASSED [100%]

============================ slowest 10 durations =============================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 35 passed in 0.07s ==============================
```

### 8. python -m pytest -q tests/agentic_core/test_phase7_tool_executor.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 24 items

tests/agentic_core/test_phase7_tool_executor.py::TestToolIntentExecBlockedOutsideSandbox::test_tool_intent_exec_blocked_outside_sandbox PASSED [  4%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolIntentExecBlockedOutsideSandbox::test_mutating_fs_blocked_outside_sandbox PASSED [  8%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolIntentExecBlockedOutsideSandbox::test_mutating_statebus_blocked_outside_sandbox PASSED [ 12%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolIntentExecBlockedOutsideSandbox::test_violation_detail_contains_tool_name PASSED [ 16%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolIntentExecAllowedInsideSandbox::test_tool_intent_exec_allowed_inside_sandbox PASSED [ 20%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolIntentExecAllowedInsideSandbox::test_non_mutating_allowed_outside_sandbox PASSED [ 25%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolIntentExecAllowedInsideSandbox::test_mutating_fs_allowed_inside_sandbox PASSED [ 29%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolIntentExecAllowedInsideSandbox::test_result_args_hash_matches_intent PASSED [ 33%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolIntentExecAllowedInsideSandbox::test_result_tool_name_matches_intent PASSED [ 37%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolIntentExecAllowedInsideSandbox::test_result_anchor_ids_sorted PASSED [ 41%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolIntentExecAllowedInsideSandbox::test_failing_fn_produces_success_false PASSED [ 45%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultHashStable::test_tool_result_hash_stable PASSED [ 50%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultHashStable::test_hash_changes_with_tool_name PASSED [ 54%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultHashStable::test_hash_changes_with_success PASSED [ 58%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultHashStable::test_hash_changes_with_output_summary PASSED [ 62%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultHashStable::test_hash_changes_with_anchor_ids PASSED [ 66%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultHashStable::test_result_hash_excluded_from_canonical_bytes PASSED [ 70%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultHashStable::test_canonical_bytes_deterministic PASSED [ 75%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultHashStable::test_anchor_ids_sorted_in_canonical_bytes PASSED [ 79%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultHashStable::test_to_dict_contains_all_fields PASSED [ 83%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultValidation::test_invalid_schema_version_raises PASSED [ 87%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultValidation::test_empty_tool_name_raises PASSED [ 91%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultValidation::test_empty_args_hash_raises PASSED [ 95%]
tests/agentic_core/test_phase7_tool_executor.py::TestToolResultValidation::test_non_list_anchor_ids_raises PASSED [100%]

============================ slowest 10 durations =============================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 24 passed in 0.06s ==============================
```

### 9. python -m pytest -q tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 18 items

tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestEndToEndGatewayPath::test_l1_cognition_blocks_mutating_tool_deterministically PASSED [  5%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestEndToEndGatewayPath::test_l1_cognition_blocks_all_mutating_capabilities PASSED [ 11%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestEndToEndGatewayPath::test_tool_intent_executed_inside_l22_sandbox_succeeds PASSED [ 16%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestEndToEndGatewayPath::test_full_gateway_path_l1_emit_l2_execute PASSED [ 22%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestEndToEndGatewayPath::test_retrieval_result_carries_anchor_ids PASSED [ 27%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestEndToEndGatewayPath::test_sandbox_released_after_execution PASSED [ 33%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestDefaultParityNonMutatingTools::test_default_config_preserves_non_mutating_tool_behavior PASSED [ 38%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestDefaultParityNonMutatingTools::test_non_mutating_tool_allowed_inside_l1_scope PASSED [ 44%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestDefaultParityNonMutatingTools::test_non_mutating_tool_result_hash_stable PASSED [ 50%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestDefaultParityNonMutatingTools::test_intent_hash_stable_across_executions PASSED [ 55%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestStaticAuditNoDirectMutatingCallsInL1::test_tool_intent_module_exists PASSED [ 61%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestStaticAuditNoDirectMutatingCallsInL1::test_executor_module_exists PASSED [ 66%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestStaticAuditNoDirectMutatingCallsInL1::test_executor_imports_commit_sandbox_check PASSED [ 72%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestStaticAuditNoDirectMutatingCallsInL1::test_executor_raises_tool_violation_not_generic PASSED [ 77%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestStaticAuditNoDirectMutatingCallsInL1::test_tool_intent_module_defines_l1_cognition_scope PASSED [ 83%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestStaticAuditNoDirectMutatingCallsInL1::test_tool_intent_module_defines_assert_l1_tool_allowed PASSED [ 88%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestStaticAuditNoDirectMutatingCallsInL1::test_no_direct_redis_set_in_tool_intent_module PASSED [ 94%]
tests/agentic_core/test_phase7_end_to_end_gateway_tool_isolation.py::TestStaticAuditNoDirectMutatingCallsInL1::test_no_direct_redis_set_in_executor_module PASSED [100%]

============================ slowest 10 durations =============================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 18 passed in 0.06s ==============================
```

---

## PASS/FAIL Table

| Objective | Test / Proof | Status |
|-----------|-------------|--------|
| git status --porcelain=v1 is EMPTY | proof cmd 3 | PASS |
| git diff --name-only is EMPTY | proof cmd 4 | PASS |
| git rev-parse HEAD = 9a6f3745c1e7c06dd28134d7db05b4a7dfeef671 | proof cmd 5 | PASS |
| **Obj 1: MUTATING_EXTERNAL blocked in L1 (redis_set)** | test_l1_blocks_mutating_tool_invocation | PASS |
| **Obj 1: MUTATING_FS blocked in L1 (file_write)** | test_l1_blocks_mutating_fs | PASS |
| **Obj 1: MUTATING_STATEBUS blocked in L1 (event_emit)** | test_l1_blocks_mutating_statebus | PASS |
| **Obj 1: NON_MUTATING allowed in L1** | test_l1_allows_non_mutating_tool_invocation | PASS |
| **Obj 1: violation carries L1_TOOL_CALL_BLOCKED code** | test_violation_detail_contains_tool_name | PASS |
| **Obj 2: ToolIntent executed outside sandbox raises TOOL_WRITE_OUTSIDE_SANDBOX** | test_tool_intent_exec_blocked_outside_sandbox | PASS |
| **Obj 2: ToolIntent executed inside L2.2 sandbox succeeds** | test_tool_intent_exec_allowed_inside_sandbox | PASS |
| **Obj 2: NON_MUTATING executes without sandbox** | test_non_mutating_allowed_outside_sandbox | PASS |
| **Obj 3: ToolResult carries tool_name, args_hash, anchor_ids** | test_to_dict_contains_all_fields | PASS |
| **Obj 3: ToolResult result_hash stable** | test_tool_result_hash_stable | PASS |
| **Obj 3: anchor_ids sorted in ToolResult** | test_anchor_ids_sorted_in_canonical_bytes | PASS |
| **Obj 4a: ToolIntent hash stable** | test_tool_intent_hash_stable | PASS |
| **Obj 4b: full gateway path L1→ToolIntent→L2.2→ToolResult** | test_full_gateway_path_l1_emit_l2_execute | PASS |
| **Obj 4c: default parity — non-mutating tools unchanged** | test_default_config_preserves_non_mutating_tool_behavior | PASS |
| **Obj 4d: end-to-end gateway blocks mutating call deterministically** | test_l1_cognition_blocks_mutating_tool_deterministically | PASS |
| **Static audit: no direct setex/upsert in tool_intent.py** | test_no_direct_redis_set_in_tool_intent_module | PASS |
| **Static audit: no direct setex/upsert in tool_intent_executor.py** | test_no_direct_redis_set_in_executor_module | PASS |
| **Static audit: executor imports is_commit_sandbox_active** | test_executor_imports_commit_sandbox_check | PASS |
| **Total: 77 tests, 0 failures** | all three test files | PASS |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

