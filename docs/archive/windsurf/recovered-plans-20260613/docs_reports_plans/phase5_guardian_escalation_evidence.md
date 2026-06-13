# Phase 5 Evidence — Guardian Escalation: ViolationEvent + Time-Shifted Routing

## Commit Hash
**8787755be** — phase5: ViolationEvent schema + L4 store + time-shifted escalation routing + tests

## Modified / New Files
- `agentic_core/L4_state/types/violation_event_types.py` [NEW — Wave 1: ViolationEvent schema + emit_violation_event]
- `agentic_core/L4_state/enforcement/violation_event_store.py` [NEW — Wave 2: L4 prior-only persistence store]
- `agentic_core/L0_routing/engines/escalation_router.py` [NEW — Wave 3: decide_mode_from_prior_violations]
- `agentic_core/L4_state/config/versioned_configs.py` [MODIFIED — Wave 3: RoutingConfig extended with Phase 5 escalation policy fields]
- `tests/agentic_core/test_phase5_violation_event.py` [NEW — Wave 1: 25 tests]
- `tests/agentic_core/test_phase5_l4_violation_persistence.py` [NEW — Wave 2: 16 tests]
- `tests/agentic_core/test_phase5_timeshift_escalation_routing.py` [NEW — Wave 3: 20 tests]

---

## Wave Summary

### Wave 1 — ViolationEvent Schema (Versioned, Hashed) + Emission
- `violation_event.py`: `ViolationEvent` dataclass with `schema_version` (int, enforced == 1), `mission_id` (non-empty str), `commit_tick` (int >= 0), `guardian_decision` ("allow"|"block"|"escalate"), `violation_codes` (sorted list[str]), `severity_score` (float in [0.0, 1.0]), `created_at_utc` (str), `event_hash` (sha256 of canonical_bytes, auto-computed, excluded from canonical_bytes)
- `emit_violation_event()`: pure recording function — constructs ViolationEvent, optionally appends to in-memory registry, does NOT alter the guardian_decision
- `canonical_bytes()`: deterministic JSON with sorted keys; `violation_codes` always sorted; `event_hash` excluded (self-referential)
- `to_dict()` / `from_dict()`: round-trip serialisation

### Wave 2 — L4 Persistence + Prior-Only Fetch (No Same-Cycle)
- `ViolationEventStore`: in-process dict-backed store keyed by `event_hash`
- `store_violation_event(event)` → `event_hash`: idempotent (duplicate hash = no-op)
- `fetch_latest_violation(before_tick=T)`: returns max(commit_tick) where commit_tick < T; same-cycle (commit_tick == T) is structurally invisible
- `fetch_window(before_tick=T, window_ticks=W)`: returns events in [T-W, T), sorted ascending by (commit_tick, event_hash)
- Prior-only invariant: enforced by strict `<` comparison in all fetch methods

### Wave 3 — Policy-Coded Escalation → L0 Routing (Prior Only) + Default Parity
- `RoutingConfig` extended with: `escalation_window_ticks=10`, `escalation_severity_threshold=0.75`, `escalation_violation_code_denylist=()`, `escalation_mode="normal"` — all included in `canonical_bytes()` and `config_hash`
- `decide_mode_from_prior_violations(execution_start_tick, routing_config, violation_store)`: reads only prior events via `fetch_window(before_tick=execution_start_tick, ...)`; escalates if severity >= threshold OR any code in denylist; no hardcoded float literals (AST-audited)
- Default parity: `escalation_mode="normal"` → legacy routing unchanged; empty denylist → no code-triggered escalation
- Static AST audit: `test_no_hardcoded_severity_threshold_in_router_module` walks AST of `escalation_router.py` and asserts zero float literals in Compare nodes

---

## Required Proof Commands (Verbatim, captured from clean tree after commit 8787755be)

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
8787755be41d33fb09ec84696f47e0c065727b7f
```

### 6. git log -1 --oneline
```
8787755be (HEAD -> Codemap_defects) phase5: ViolationEvent schema + L4 store + time-shifted escalation routing + tests
```

### 7. python -m pytest -q tests/agentic_core/test_phase5_violation_event.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 25 items

tests/agentic_core/test_phase5_violation_event.py::TestViolationEventHash::test_violation_event_hash_stable PASSED [  4%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventHash::test_hash_changes_with_mission_id PASSED [  8%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventHash::test_hash_changes_with_commit_tick PASSED [ 12%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventHash::test_hash_changes_with_decision PASSED [ 16%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventHash::test_hash_changes_with_severity PASSED [ 20%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventHash::test_event_hash_excluded_from_canonical_bytes PASSED [ 24%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventHash::test_canonical_bytes_deterministic PASSED [ 28%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventCodesSorted::test_violation_event_codes_sorted_in_canonical_bytes PASSED [ 32%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventCodesSorted::test_violation_codes_stored_sorted PASSED [ 36%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventCodesSorted::test_empty_violation_codes_allowed PASSED [ 40%]
tests/agentic_core/test_phase5_violation_event.py::TestSeverityScoreRange::test_severity_score_range_enforced_zero PASSED [ 44%]
tests/agentic_core/test_phase5_violation_event.py::TestSeverityScoreRange::test_severity_score_range_enforced_one PASSED [ 48%]
tests/agentic_core/test_phase5_violation_event.py::TestSeverityScoreRange::test_severity_score_below_zero_raises PASSED [ 52%]
tests/agentic_core/test_phase5_violation_event.py::TestSeverityScoreRange::test_severity_score_above_one_raises PASSED [ 56%]
tests/agentic_core/test_phase5_violation_event.py::TestSeverityScoreRange::test_severity_score_midpoint PASSED [ 60%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventValidation::test_invalid_schema_version_raises PASSED [ 64%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventValidation::test_empty_mission_id_raises PASSED [ 68%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventValidation::test_negative_commit_tick_raises PASSED [ 72%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventValidation::test_invalid_guardian_decision_raises PASSED [ 76%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventValidation::test_valid_decisions_accepted PASSED [ 80%]
tests/agentic_core/test_phase5_violation_event.py::TestViolationEventValidation::test_non_list_violation_codes_raises PASSED [ 84%]
tests/agentic_core/test_phase5_violation_event.py::TestEmitViolationEvent::test_emit_returns_violation_event PASSED [ 88%]
tests/agentic_core/test_phase5_violation_event.py::TestEmitViolationEvent::test_emit_appends_to_registry PASSED [ 92%]
tests/agentic_core/test_phase5_violation_event.py::TestEmitViolationEvent::test_emit_does_not_alter_decision PASSED [ 96%]
tests/agentic_core/test_phase5_violation_event.py::TestEmitViolationEvent::test_to_dict_round_trip PASSED [100%]

============================ slowest 10 durations =============================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 25 passed in 0.06s ==============================
```

### 8. python -m pytest -q tests/agentic_core/test_phase5_l4_violation_persistence.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 16 items

tests/agentic_core/test_phase5_l4_violation_persistence.py::TestStoreAndFetch::test_store_returns_event_hash PASSED [  6%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestStoreAndFetch::test_store_idempotent PASSED [ 12%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestStoreAndFetch::test_store_rejects_non_event PASSED [ 18%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestStoreAndFetch::test_store_and_fetch_latest_prior_only PASSED [ 25%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestStoreAndFetch::test_fetch_latest_returns_highest_tick_below_boundary PASSED [ 31%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestStoreAndFetch::test_fetch_latest_returns_none_when_no_prior PASSED [ 37%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestStoreAndFetch::test_fetch_latest_returns_none_on_empty_store PASSED [ 43%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestSameCycleExclusion::test_fetch_disallows_same_cycle_event PASSED [ 50%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestSameCycleExclusion::test_fetch_window_excludes_same_cycle PASSED [ 56%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestSameCycleExclusion::test_same_cycle_event_stored_but_invisible_at_boundary PASSED [ 62%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestFetchWindow::test_fetch_window_returns_sorted_by_tick_then_hash PASSED [ 68%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestFetchWindow::test_fetch_window_respects_lower_bound PASSED [ 75%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestFetchWindow::test_fetch_window_empty_when_no_events_in_range PASSED [ 81%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestFetchWindow::test_fetch_window_negative_window_ticks_raises PASSED [ 87%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestFetchWindow::test_fetch_window_zero_ticks_returns_empty PASSED [ 93%]
tests/agentic_core/test_phase5_l4_violation_persistence.py::TestFetchWindow::test_fetch_window_returns_all_in_range PASSED [100%]

============================ slowest 10 durations =============================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 16 passed in 0.05s ==============================
```

### 9. python -m pytest -q tests/agentic_core/test_phase5_timeshift_escalation_routing.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 20 items

tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestRoutingUsesPriorViolationsOnly::test_routing_uses_prior_violations_only PASSED [  5%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestRoutingUsesPriorViolationsOnly::test_same_cycle_violation_alone_does_not_trigger_escalation PASSED [ 10%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestRoutingUsesPriorViolationsOnly::test_prior_violation_below_threshold_does_not_escalate PASSED [ 15%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestRoutingUsesPriorViolationsOnly::test_prior_violation_at_threshold_triggers_escalation PASSED [ 20%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestRoutingUsesPriorViolationsOnly::test_violation_outside_window_does_not_escalate PASSED [ 25%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestRoutingUsesPriorViolationsOnly::test_violation_inside_window_escalates PASSED [ 30%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestDenylistTriggersEscalation::test_denylist_code_triggers_escalation_regardless_of_severity PASSED [ 35%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestDenylistTriggersEscalation::test_non_denylist_code_does_not_trigger_via_denylist PASSED [ 40%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestDenylistTriggersEscalation::test_empty_denylist_does_not_trigger_code_path PASSED [ 45%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestDefaultConfigPreservesLegacyRouting::test_default_config_preserves_legacy_routing PASSED [ 50%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestDefaultConfigPreservesLegacyRouting::test_default_config_escalation_mode_is_normal PASSED [ 55%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestDefaultConfigPreservesLegacyRouting::test_default_config_denylist_is_empty PASSED [ 60%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestDefaultConfigPreservesLegacyRouting::test_default_config_window_ticks_positive PASSED [ 65%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestDefaultConfigPreservesLegacyRouting::test_default_config_severity_threshold_in_range PASSED [ 70%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestDefaultConfigPreservesLegacyRouting::test_routing_config_hash_stable PASSED [ 75%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestDefaultConfigPreservesLegacyRouting::test_routing_config_hash_changes_with_threshold PASSED [ 80%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestDefaultConfigPreservesLegacyRouting::test_routing_config_hash_changes_with_mode PASSED [ 85%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestStaticAuditNoHardcodedThreshold::test_no_hardcoded_severity_threshold_in_router_module PASSED [ 90%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestStaticAuditNoHardcodedThreshold::test_router_module_exists PASSED [ 95%]
tests/agentic_core/test_phase5_timeshift_escalation_routing.py::TestStaticAuditNoHardcodedThreshold::test_router_references_routing_config_threshold PASSED [100%]

============================ slowest 10 durations =============================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 20 passed in 0.06s ==============================
```

---

## PASS/FAIL Table

| Objective | Test / Proof | Status |
|-----------|-------------|--------|
| git status --porcelain=v1 is EMPTY | proof cmd 3 | PASS |
| git diff --name-only is EMPTY | proof cmd 4 | PASS |
| git rev-parse HEAD = 8787755be41d33fb09ec84696f47e0c065727b7f | proof cmd 5 | PASS |
| **Obj 1: ViolationEvent schema_version enforced** | test_invalid_schema_version_raises | PASS |
| **Obj 1: ViolationEvent guardian_decision validated** | test_invalid_guardian_decision_raises | PASS |
| **Obj 1: ViolationEvent severity_score in [0,1]** | test_severity_score_range_enforced_zero/one + _below_zero_raises + _above_one_raises | PASS |
| **Obj 1: event_hash is sha256(canonical_bytes), stable** | test_violation_event_hash_stable | PASS |
| **Obj 1: violation_codes sorted in canonical_bytes** | test_violation_event_codes_sorted_in_canonical_bytes | PASS |
| **Obj 1: event_hash excluded from canonical_bytes** | test_event_hash_excluded_from_canonical_bytes | PASS |
| **Obj 1: emit_violation_event does not alter decision** | test_emit_does_not_alter_decision | PASS |
| **Obj 2: store_and_fetch_latest returns prior-only** | test_store_and_fetch_latest_prior_only | PASS |
| **Obj 2: fetch_disallows_same_cycle_event** | test_fetch_disallows_same_cycle_event | PASS |
| **Obj 2: same-cycle event stored but invisible at boundary** | test_same_cycle_event_stored_but_invisible_at_boundary | PASS |
| **Obj 2: fetch_window sorted by (tick, hash)** | test_fetch_window_returns_sorted_by_tick_then_hash | PASS |
| **Obj 2: fetch_window excludes same-cycle** | test_fetch_window_excludes_same_cycle | PASS |
| **Obj 3: routing uses prior violations only (core time-shift)** | test_routing_uses_prior_violations_only | PASS |
| **Obj 3: same-cycle violation alone does not trigger escalation** | test_same_cycle_violation_alone_does_not_trigger_escalation | PASS |
| **Obj 3: denylist code triggers escalation regardless of severity** | test_denylist_code_triggers_escalation_regardless_of_severity | PASS |
| **Obj 4: default config preserves legacy routing ("normal")** | test_default_config_preserves_legacy_routing | PASS |
| **Obj 4: default escalation_mode is "normal"** | test_default_config_escalation_mode_is_normal | PASS |
| **Obj 4: RoutingConfig.config_hash stable** | test_routing_config_hash_stable | PASS |
| **Static audit: no hardcoded float literals in router Compare nodes** | test_no_hardcoded_severity_threshold_in_router_module | PASS |
| **Static audit: router references escalation_severity_threshold from config** | test_router_references_routing_config_threshold | PASS |
| **Total: 61 tests, 0 failures** | all three test files | PASS |

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

