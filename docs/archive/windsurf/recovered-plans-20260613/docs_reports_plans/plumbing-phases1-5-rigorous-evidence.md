# Plumbing Phases 1-5 Rigorous Evidence

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Scope

Phases 1-5 AST plumbing plan. Changed logic surfaces under audit:

- Phase 1.1: `agentic_core/L0_routing/seams/observability_seam.py` (G6 dead import fix)
- Phase 1.2: `apps_rg` test collection errors (G13 fix)
- Phase 2.1: `apps_shared/spine/d0_engine_adapter.py` (new)
- Phase 2.1: `apps_shared/spine/risk_gate_adapter.py` (new)
- Phase 2.1: `apps_shared/spine/vigilance_dispatcher_adapter.py` (new)
- Phase 2.1: `apps_lic/engines/lic_spine_adapter.py` (wiring updated)
- Phase 2.1: `apps_rg/engines/rg_spine_adapter.py` (wiring updated)
- Phase 2.5: `agentic_core/L0_routing/engines/execution_orchestrator.py` (l3_orchestrator + _delegate_to_l3 added)
- Phase 3.1: `agentic_core/L0_routing/seams/elevator_shaft_seam.py` (pure stub, no control flow)

## INSPECTED_FILES

- apps_shared/spine/d0_engine_adapter.py
- apps_shared/spine/risk_gate_adapter.py
- apps_shared/spine/vigilance_dispatcher_adapter.py
- apps_lic/engines/lic_spine_adapter.py
- apps_rg/engines/rg_spine_adapter.py
- agentic_core/L0_routing/engines/execution_orchestrator.py
- agentic_core/L0_routing/seams/elevator_shaft_seam.py
- tests/governance/test_plumbing_rigorous.py
- tests/governance/test_l0_seam_contracts.py
- tests/governance/test_healer_outcome_intake_wiring.py
- tests/unit/agentic_core/L0_routing/test_execution_orchestrator_l3_wiring.py
- tests/unit/apps/test_spine_adapter_wiring.py

## Authoritative Test Command

    python -m pytest -q --color=no

## Result

    8269 passed, 97 skipped, 7 xfailed, 0 failed in 425.06s
    Exit code: 0

## Collection vs Execution

    Collected: 8366 items (8269 executed + 97 skipped)
    Skipped reason: L3 orchestrator engine has broken upstream import (ssot_discovery_validator)
    No silent deselection. All markers registered in pytest.ini.

---

## BRANCH_INVENTORY

### Surface: D0EngineAdapter — apps_shared/spine/d0_engine_adapter.py

| # | Function | Branch Condition | Expected Outcome | Test Name |
|---|----------|-----------------|------------------|-----------|
| B-D0-1 | `__init__` | `_build_real_engine()` raises ImportError | `_real=False`, `_engine=None`, `_RoleFence=None` | `test_import_error_sets_null_fallback` |
| B-D0-2 | `__init__` | `_build_real_engine()` succeeds | `_real=True`, `_engine` and `_RoleFence` set | `test_successful_import_sets_real_true` |
| B-D0-3 | `render_d0` | `not self._real` → early return | return `d0_injections` unchanged | `test_render_d0_not_real_returns_any_string_unchanged` |
| B-D0-4 | `render_d0` | `_real=True` AND `d0_injections=""` | return `""` unchanged | `test_render_d0_empty_string_returns_empty` |
| B-D0-5 | `render_d0` | segment contains `:` | build `RoleFence`, append to list | `test_render_d0_single_valid_segment`, `test_render_d0_multiple_valid_segments` |
| B-D0-6 | `render_d0` | segment missing `:` | skip segment | `test_render_d0_no_colon_segment_skipped` |
| B-D0-7 | `render_d0` | `fence_id` empty after strip | skip segment | `test_render_d0_empty_fence_id_segment_skipped` |
| B-D0-8 | `render_d0` | `fences` list empty after all parsing | return `d0_injections` unchanged | `test_render_d0_all_invalid_segments_returns_original` |
| B-D0-9 | `render_d0` | `fences` non-empty | call `engine.render_d0`, return XML result | `test_render_d0_calls_engine_and_returns_xml` |

### Surface: RiskGateAdapter — apps_shared/spine/risk_gate_adapter.py

| # | Function | Branch Condition | Expected Outcome | Test Name |
|---|----------|-----------------|------------------|-----------|
| B-RG-1 | `__init__` | `_build_real_gate()` raises ImportError | `_real=False`, `_gate=None` | `test_import_error_sets_null_fallback` |
| B-RG-2 | `__init__` | import succeeds | `_real=True`, `_gate` set | `test_successful_import_sets_real_true` |
| B-RG-3 | `evaluate` | `not self._real` → early return | `RiskResult(allow=True)` returned | `test_null_fallback_evaluate_returns_allow_true` |
| B-RG-4 | `evaluate` | `d0_injections` is `str` | passed as-is to gate | `test_evaluate_str_d0_injections_passed_through` |
| B-RG-5 | `evaluate` | `d0_injections` not `str` | converted via `str()` | `test_evaluate_non_str_d0_injections_converted` |
| B-RG-6 | `evaluate` | real gate called, returns `RiskDecision` | converted to `RiskResult` | `test_evaluate_real_gate_clean_payload_allows` |
| B-RG-7 | `evaluate` | `decision.allow=True` | `RiskResult.allow=True` | `test_evaluate_real_gate_clean_payload_allows` |
| B-RG-8 | `evaluate` | `decision.allow=False` (DENY_EXECUTION) | `RiskResult.allow=False`, `level="HIGH"` | `test_evaluate_real_gate_deny_execution_blocks` |
| B-RG-9 | `evaluate` | `decision.level.value` | `RiskResult.level` is string | `test_evaluate_level_is_string` |
| B-RG-10 | `evaluate` | `decision.reasons` | `RiskResult.reasons` is tuple | `test_evaluate_reasons_is_tuple` |
| B-RG-Bd1 | `evaluate` | `check_ids` length == 4 (boundary-1) | `level="LOW"` | `test_evaluate_exactly_4_check_ids_is_low` |
| B-RG-Bd2 | `evaluate` | `check_ids` length == 5 (exact boundary) | `level="MEDIUM"`, `"MANY_CHECK_IDS"` in reasons | `test_evaluate_exactly_5_check_ids_is_medium` |
| B-RG-Bd3 | `evaluate` | `check_ids` length == 6 (boundary+1) | `level="MEDIUM"` | `test_evaluate_6_check_ids_is_medium` |
| B-RG-Bd4 | `evaluate` | `check_ids` length == 0 (minimum) | `level="LOW"` | `test_evaluate_0_check_ids_is_low` |

### Surface: VigilanceDispatcherAdapter — apps_shared/spine/vigilance_dispatcher_adapter.py

| # | Function | Branch Condition | Expected Outcome | Test Name |
|---|----------|-----------------|------------------|-----------|
| B-VD-1 | `__init__` | `_build_real_dispatcher()` raises ImportError | `_real=False`, `_dispatcher=None` | `test_import_error_sets_null_fallback` |
| B-VD-2 | `__init__` | import succeeds | `_real=True`, `_dispatcher` set | `test_successful_import_sets_real_true` |
| B-VD-3 | `dispatch` | `not self._real` → early return | no-op, nothing enqueued | `test_null_fallback_dispatch_does_not_enqueue` |
| B-VD-4 | `dispatch` | `raw_signals` is `str` | wrapped in `(signals,)` tuple | `test_dispatch_signals_str_wrapped_in_tuple` |
| B-VD-5 | `dispatch` | `raw_signals` is tuple/list | converted via `tuple()` | `test_dispatch_signals_tuple_passed`, `test_dispatch_signals_list_converted_to_tuple` |
| B-VD-6 | `dispatch` | `trace_id=None` | `str("None")` accepted | `test_dispatch_none_trace_id_does_not_raise` |
| B-VD-7 | `dispatch` | `summary=None` | `str("None")` accepted | `test_dispatch_none_summary_does_not_raise` |
| B-VD-8 | `dispatch` | event created and dispatched | event enqueued in `_EVENT_QUEUE` | `test_dispatch_enqueues_event` |
| B-VD-9a | `dispatch` | `_ArtifactCls.create` raises any Exception | swallowed, not re-raised | `test_dispatch_exception_swallowed_never_reraises` |
| B-VD-9b | `dispatch` | `_dispatcher.dispatch` raises ValueError | swallowed, not re-raised | `test_dispatch_dispatcher_raises_swallowed` |
| B-VD-9c | `dispatch` | unrelated exception (MemoryError) in try block | swallowed, not re-raised | `test_dispatch_unexpected_exception_swallowed` |
| B-VD-Bd1 | `dispatch` (queue) | 256 items enqueued (exact boundary) | `len(_EVENT_QUEUE)==256` | `test_event_queue_exactly_256_items` |
| B-VD-Bd2 | `dispatch` (queue) | 255 items enqueued (boundary-1) | `len(_EVENT_QUEUE)==255` | `test_event_queue_255_items_under_max` |
| B-VD-Bd3 | `dispatch` (queue) | 300 items enqueued (boundary+44) | `len(_EVENT_QUEUE)==256` (maxlen clamp) | `test_event_queue_bounded_at_256` |

### Surface: ExecutionOrchestrator — agentic_core/L0_routing/engines/execution_orchestrator.py

| # | Function | Branch Condition | Expected Outcome | Test Name |
|---|----------|-----------------|------------------|-----------|
| B-EO-1 | `__init__` | `l3_orchestrator` not provided | `self.l3_orchestrator is None` | `test_l3_orchestrator_defaults_to_none` |
| B-EO-2 | `__init__` | `l3_orchestrator` provided | stored as `self.l3_orchestrator` | `test_l3_orchestrator_stored_when_provided` |
| B-EO-3 | `_delegate_to_l3` | `self.l3_orchestrator is None` | `orchestration={}` | `test_delegate_to_l3_no_orchestrator_returns_empty_orchestration` |
| B-EO-4 | `_delegate_to_l3` | orchestrator present, call succeeds | `orchestration` populated from result | `test_delegate_to_l3_with_orchestrator_populates_orchestration` |
| B-EO-5a | `_delegate_to_l3` | `orchestrate()` raises RuntimeError | `orchestration={error:..., completed:False}` | `test_delegate_to_l3_exception_captured_not_raised[RuntimeError]` |
| B-EO-5b | `_delegate_to_l3` | `orchestrate()` raises ValueError | same as above | `test_delegate_to_l3_exception_captured_not_raised[ValueError]` |
| B-EO-5c | `_delegate_to_l3` | `orchestrate()` raises KeyError | same as above | `test_delegate_to_l3_exception_captured_not_raised[KeyError]` |
| B-EO-6 | `_delegate_to_l3` | result lacks `completed/stage/signals/metadata` attrs | `getattr` defaults used | `test_delegate_to_l3_result_missing_attrs_uses_defaults` |
| B-EO-7 | `execute` | `risk.allow=False` AND `should_retry=True` | `state="retry"` | `test_execute_risk_blocked_should_retry_returns_retry` |
| B-EO-8 | `execute` | `risk.allow=False` AND `should_retry=False` | `state="blocked"` | `test_execute_risk_blocked_no_retry_returns_blocked` |
| B-EO-9a | `execute` | `path.value=="B"` in `_L3_PATHS` | calls `_delegate_to_l3` | `test_execute_l3_path_calls_delegate[B]` |
| B-EO-9b | `execute` | `path.value=="C"` in `_L3_PATHS` | calls `_delegate_to_l3` | `test_execute_l3_path_calls_delegate[C]` |
| B-EO-9c | `execute` | `path.value=="D"` in `_L3_PATHS` | calls `_delegate_to_l3` | `test_execute_l3_path_calls_delegate[D]` |
| B-EO-10 | `execute` | `path.value=="A"` NOT in `_L3_PATHS` | `state="success"`, no L3 call | `test_execute_path_a_no_orchestration_key` |
| B-EO-11 | class constant | `_L3_PATHS` content | frozenset `{"B","C","D"}`, not `"A"` | `test_l3_paths_contains_b_c_d`, `test_l3_paths_does_not_contain_a` |

---

## ROBUSTNESS_MATRIX

### D0EngineAdapter

| Changed Surface | Success Tests | Edge Tests | Failure Tests | Recovery Tests | Determinism Tests | Side-Effect Tests |
|----------------|--------------|-----------|--------------|----------------|-------------------|------------------|
| `__init__` import guard | B-D0-2 | B-D0-1 (ImportError) | B-D0-1 | n/a (no retry) | test_successful_import_sets_real_true | test_null_fallback_never_calls_engine |
| `render_d0` parsing | B-D0-5, B-D0-9 | B-D0-4 (empty), B-D0-8 (no fences), boundary-1/boundary | B-D0-6 (no colon), B-D0-7 (empty id) | B-D0-3 (null fallback) | test_render_d0_deterministic_identical_input | test_render_d0_not_real_returns_any_string_unchanged |
| pipe/colon parsing | test_render_d0_multiple_valid_segments | test_render_d0_pipe_only_no_fences, test_render_d0_colon_in_text_allowed | test_render_d0_whitespace_only_fence_id_skipped | n/a | test_render_d0_sorted_fence_order_deterministic | test_different_inputs_different_outputs |

### RiskGateAdapter

| Changed Surface | Success Tests | Edge Tests | Failure Tests | Recovery Tests | Determinism Tests | Side-Effect Tests |
|----------------|--------------|-----------|--------------|----------------|-------------------|------------------|
| `__init__` import guard | B-RG-2 | B-RG-1 (ImportError) | B-RG-1 | n/a | test_successful_import_sets_real_true | test_null_fallback_never_blocks |
| `evaluate` null path | B-RG-3 | empty d0_injections | DENY_EXECUTION (null still allows) | n/a | test_evaluate_deterministic_same_input | test_null_fallback_never_blocks |
| `evaluate` real path | B-RG-6, B-RG-7 | B-RG-Bd1..Bd4 (boundary) | B-RG-8 (DENY_EXECUTION blocks) | n/a | test_evaluate_deterministic_same_input | test_deny_execution_has_no_side_effects_on_adapter_state |
| missing attrs | test_evaluate_payload_missing_sanitized_attr | test_evaluate_payload_missing_check_ids_attr | n/a | n/a | n/a | n/a |
| Matrix sanitized×deny | test_evaluate_matrix[False,"",True] | test_evaluate_matrix[True,"",True] | test_evaluate_matrix[*,DENY,False] | n/a | all 4 matrix cells | n/a |

### VigilanceDispatcherAdapter

| Changed Surface | Success Tests | Edge Tests | Failure Tests | Recovery Tests | Determinism Tests | Side-Effect Tests |
|----------------|--------------|-----------|--------------|----------------|-------------------|------------------|
| `__init__` import guard | B-VD-2 | B-VD-1 (ImportError) | B-VD-1 | n/a | n/a | test_null_fallback_dispatch_is_no_op |
| `dispatch` null path | B-VD-3 | empty signals | n/a | n/a | n/a | test_null_fallback_dispatch_does_not_enqueue |
| `dispatch` real path | B-VD-8 | B-VD-4/5/6/7 (signals str/list/None trace/summary) | B-VD-9a/b/c (exceptions) | B-VD-9 (fail-open) | test_dispatch_deterministic_event_content | test_dispatch_does_not_mutate_adapter_state |
| queue boundary | B-VD-Bd2 (255) | B-VD-Bd1 (256) | B-VD-Bd3 (300→clamped) | test_drain_then_reenqueue_is_clean | n/a | test_drain_then_reenqueue_is_clean |

### ExecutionOrchestrator

| Changed Surface | Success Tests | Edge Tests | Failure Tests | Recovery Tests | Determinism Tests | Side-Effect Tests |
|----------------|--------------|-----------|--------------|----------------|-------------------|------------------|
| `l3_orchestrator` param | B-EO-2 | B-EO-1 (None) | n/a | n/a | test_execute_deterministic_same_input | n/a |
| `_delegate_to_l3` no L3 | B-EO-3 | n/a | n/a | n/a | n/a | n/a |
| `_delegate_to_l3` with L3 | B-EO-4 | B-EO-6 (missing attrs) | B-EO-5a/b/c (exceptions) | B-EO-5 (error captured) | test_execute_deterministic_same_input | test_execute_blocked_no_side_effects |
| `execute` risk-blocked | B-EO-7 (retry) | B-EO-Bd (max_reentry=1,2) | B-EO-8 (blocked) | B-EO-7 (retry as recovery) | n/a | test_execute_blocked_does_not_call_l3, test_execute_retry_does_not_call_l3 |
| `execute` L3 dispatch | B-EO-9a/b/c | B-EO-10 (path A no L3) | test_execute_l3_exception_degrades_gracefully | B-EO-5 (error dict) | test_execute_deterministic_same_input | test_execute_blocked_no_side_effects |
| Matrix path×allow×l3×retry | 9 matrix cells | n/a | blocked/retry cells | retry cells | identical-input rows | blocked no-L3-call cells |

---

## DEFECT_MODEL

| Defect Class | Surface | Targeted By |
|-------------|---------|-------------|
| Null fallback not activated on ImportError | D0EngineAdapter, RiskGateAdapter, VigilanceDispatcherAdapter | B-D0-1, B-RG-1, B-VD-1 |
| Null fallback incorrectly blocks (fail-permissive becomes fail-closed) | RiskGateAdapter | test_null_fallback_never_blocks, test_null_fallback_evaluate_returns_allow_true |
| Segment without colon crashes render_d0 | D0EngineAdapter | B-D0-6, test_render_d0_all_segments_missing_colon_returns_input |
| Empty fence_id accepted as valid fence | D0EngineAdapter | B-D0-7, test_render_d0_only_empty_fence_id_returns_input |
| render_d0 non-deterministic across instances | D0EngineAdapter | test_render_d0_deterministic_identical_input |
| DENY_EXECUTION sentinel not detected | RiskGateAdapter | test_evaluate_real_gate_deny_execution_blocks |
| check_ids boundary off-by-one (4 vs 5) | RiskGateAdapter | B-RG-Bd1..Bd4 |
| Vigilance dispatch blocks execution on exception | VigilanceDispatcherAdapter | B-VD-9a/b/c |
| Event queue unbounded — memory leak | VigilanceDispatcherAdapter | B-VD-Bd1..Bd3 |
| L3 exception propagates and crashes L0 routing | ExecutionOrchestrator._delegate_to_l3 | B-EO-5a/b/c, test_execute_l3_exception_degrades_gracefully |
| L3 called when risk blocks (side-effect before guard) | ExecutionOrchestrator.execute | test_execute_blocked_does_not_call_l3, test_execute_retry_does_not_call_l3 |
| Path A incorrectly delegates to L3 | ExecutionOrchestrator.execute | test_execute_path_a_no_orchestration_key, test_l3_paths_does_not_contain_a |
| _L3_PATHS is mutable (frozenset enforcement) | ExecutionOrchestrator | test_l3_paths_is_frozenset |
| getattr result-attribute defaults wrong | ExecutionOrchestrator._delegate_to_l3 | B-EO-6, test_execute_l3_returns_none_uses_defaults |
| Repeated execute mutates orchestrator state | ExecutionOrchestrator | test_execute_repeated_calls_same_orchestrator |
| Error message lost on L3 exception | ExecutionOrchestrator._delegate_to_l3 | test_execute_l3_error_message_preserved_exactly |
| Seam contains control flow (If/Try) breaking invariant | elevator_shaft_seam | test_load_context_jit_no_control_flow_in_seam (governance) + test_seam_has_no_routing_logic (unit) |

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

