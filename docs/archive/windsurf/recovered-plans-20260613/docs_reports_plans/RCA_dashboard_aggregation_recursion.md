# RCA: Dashboard Aggregation Infinite Recursion (Three Paths)

**Status:** ✅ RESOLVED
**Date:** 2026-03-15
**Severity:** Critical (Production Crash — unbounded RecursionError on any runtime call)

---

## Executive Summary

Three independent infinite-recursion paths existed in the dashboard aggregation subsystem.
Any production runtime call that invoked `_emit_records_execution_trace()` (present in
**1,368+ source files**) would immediately trigger an unbounded recursive stack that ended in
`RecursionError`, crashing the calling thread. The previous RCA
(`RCA_dashboard_aggregation_slowdown.md`) identified only the *ADG scan* performance symptom
and patched it with an `ADG_SCAN_ACTIVE` env-var guard — but did **not** fix the underlying
architectural violation. The three root-cause bugs were still present and fully active in
production runtime (where `ADG_SCAN_ACTIVE` is never set).

---

## Root Cause Analysis

### Bug #1 — Mutual Recursion in `_emit_records_execution_trace` (CRITICAL)

**File:** `agentic_core/runtime/lifecycle_trace_contract.py:204–231`

`_emit_records_execution_trace` is a **pure ADG-edge emitter** — its entire contract is to
write one `logging.debug` line. It was modified to also call `aggregate_simple_dashboard()`,
creating an immediate mutual recursion:

```
_emit_records_execution_trace()
  → aggregate_simple_dashboard()
    → aggregate_runtime_observability()
      → _emit_records_execution_trace()   ← BACK TO START
        → aggregate_simple_dashboard()
          → ...  (RecursionError in ~500 frames)
```

**Present in:** Every one of the 1,368 files that call `_emit_records_execution_trace`.
**Impact:** Any runtime operation (routing, reasoning, execution, policy checks) crashes.

**Root architectural violation:** A pure telemetry emitter must never have side effects.
Dashboard aggregation is the *caller's* responsibility, not the emitter's.

---

### Bug #2 — Recursion via `DashboardAggregateRegistry.get_instance()` (CRITICAL)

**File:** `agentic_core/L6_observability/dashboard/dashboard_aggregate.py:205–219`

`get_instance()` called `_emit_records_execution_trace()`, creating a second independent path:

```
get_instance()
  → _emit_records_execution_trace()
    → aggregate_simple_dashboard()
      → aggregate_runtime_observability()
        → get_dashboard_registry()
          → get_instance()   ← BACK TO START
```

**Impact:** Even if Bug #1 were patched, importing the dashboard module for the first time
(which calls `get_instance()`) would still recurse.

---

### Bug #3 — Recursion at Dataclass Instantiation via `get_clock()` (CRITICAL)

**File:** `agentic_core/L6_observability/dashboard/dashboard_aggregate.py:166`

`DashboardAggregate.computed_at_tick` used `get_clock().now_epoch()` as its dataclass field
default. With the production `WallClock`, `now()` calls `_emit_records_execution_trace()`,
creating a third recursion path triggered at object creation time:

```
DashboardAggregate(...)   ← dataclass __init__
  → computed_at_tick = get_clock().now_epoch()
    → WallClock.now()
      → _emit_records_execution_trace()
        → aggregate_simple_dashboard()
          → aggregate_runtime_observability()
            → _persist_dashboard_snapshot()
              → DashboardAggregate.create()   ← dataclass __init__ AGAIN
```

**Impact:** `DashboardAggregate` could not be instantiated in production without recursing.

---

### Why the Previous RCA (`RCA_dashboard_aggregation_slowdown.md`) Was Insufficient

The previous fix set `ADG_SCAN_ACTIVE=1` in ADG generation scripts. This suppressed the
recursion *during static analysis*, but:

1. **Production runtime never sets `ADG_SCAN_ACTIVE`** — all three paths remained active.
2. The fix treated the symptom (slow ADG scan) not the disease (architectural violation).
3. The `os.environ.get("ADG_SCAN_ACTIVE")` guard was a band-aid on an emitter that should
   never have had side effects in the first place.

---

## Evidence

### Static analysis — call sites of `_emit_records_execution_trace`
- `agentic_core/adg/extraction/static_scanner.py`: 46 call sites
- Total files across codebase: **1,368 files** (grep confirmed)
- Every call site was a latent crash vector

### Recursion paths confirmed by code trace
All three paths traced above are confirmed by direct source inspection.

### Test evidence — 39 regression tests, all pass
```
tests/unit/agentic_core/L6_observability/dashboard/test_dashboard_aggregation_rca.py
  TestBug1NoRecursionFromEmitter           — 5 tests
  TestBug2NoRecursionFromGetInstance       — 4 tests
  TestBug3NoDashboardAggregateRecursion    — 3 tests
  TestDashboardAggregationIntegration      — 9 tests
  TestDashboardSnapshotCorrectness         — 9 tests
  TestDashboardAggregateRegistryCorrectness — 9 tests

RESULT: 39 passed in 0.19s
```

---

## Fixes Applied

### Fix #1 — Strip side effects from `_emit_records_execution_trace`

**File:** `agentic_core/runtime/lifecycle_trace_contract.py`

Removed the entire dashboard aggregation block (lines 213–231 pre-fix).
The function now contains only the `_TRACE_LOG.debug(...)` call it was designed to have.
Also removed the now-unused `import os` at the top of the file.

**Before (broken):**
```python
def _emit_records_execution_trace(root_trace_id, layer, operation):
    _TRACE_LOG.debug(...)
    if not os.environ.get("ADG_SCAN_ACTIVE"):       # ← band-aid guard
        from ...dashboard_orchestrator import aggregate_simple_dashboard
        snapshot = aggregate_simple_dashboard(...)  # ← RECURSION
```

**After (fixed):**
```python
def _emit_records_execution_trace(root_trace_id, layer, operation):
    """Pure ADG-edge emitter — no side effects. Dashboard aggregation is
    the caller's responsibility, not the emitter's."""
    _TRACE_LOG.debug(...)
```

---

### Fix #2 — Remove `_emit_records_execution_trace` from `get_instance()`

**File:** `agentic_core/L6_observability/dashboard/dashboard_aggregate.py`

Removed the `_emit_records_execution_trace` call from `DashboardAggregateRegistry.get_instance()`.
Singleton accessors must not emit execution traces — they are called as part of the dashboard
aggregation path itself and must remain side-effect-free.

---

### Fix #3 — Replace `get_clock().now_epoch()` with `time.time()` in `DashboardAggregate`

**File:** `agentic_core/L6_observability/dashboard/dashboard_aggregate.py`

Changed `DashboardAggregate.computed_at_tick` default from:
```python
computed_at_tick: float = field(default_factory=lambda: get_clock().now_epoch())
```
to:
```python
computed_at_tick: float = field(default_factory=time.time)
```

`WallClock.now()` emits execution traces, creating a third recursion trigger at dataclass
instantiation. `time.time()` is the correct primitive for a timestamp default — no indirection,
no side effects, no recursion risk. Also removed the `get_clock` and `LayerSegment` imports
that were no longer needed, and removed the unused `_emit_records_execution_trace` import.

---

### Fix #4 — Add `reset_dashboard_registry` to `dashboard_orchestrator.py` imports

**File:** `agentic_core/L6_observability/dashboard/dashboard_orchestrator.py`

`reset_dashboard_registry` was listed in `dashboard/__init__.py`'s re-export of orchestrator
symbols but was not actually imported there — causing `ImportError` at test collection.
Added explicit import from `dashboard_aggregate` (where it is defined).

---

## Files Modified

| File | Change |
|------|--------|
| `agentic_core/runtime/lifecycle_trace_contract.py` | Remove dashboard aggregation from `_emit_records_execution_trace`; remove `import os` |
| `agentic_core/L6_observability/dashboard/dashboard_aggregate.py` | Remove `_emit_records_execution_trace` from `get_instance()`; replace `get_clock().now_epoch()` with `time.time()`; remove unused imports |
| `agentic_core/L6_observability/dashboard/dashboard_orchestrator.py` | Add `reset_dashboard_registry` to imports |
| `tests/unit/agentic_core/L6_observability/dashboard/__init__.py` | New (empty) test package init |
| `tests/unit/agentic_core/L6_observability/dashboard/test_dashboard_aggregation_rca.py` | New — 39 regression tests covering all three recursion paths |

---

## Regression Test Coverage

| Test Class | Coverage |
|---|---|
| `TestBug1NoRecursionFromEmitter` | Verifies emitter makes 0 aggregate calls; 1000-call stress test; return-None contract |
| `TestBug2NoRecursionFromGetInstance` | Verifies no trace emission in get_instance; 200-call stress; singleton contract; 20-thread concurrency |
| `TestBug3NoDashboardAggregateRecursion` | Verifies no clock emit at instantiation; epoch range check; 500-object bulk stress |
| `TestDashboardAggregationIntegration` | Full 5-step pipeline; snapshot persistence; 5-call accumulation; 5-component health flags; Gates B/D/E; 10-thread concurrency |
| `TestDashboardSnapshotCorrectness` | Gates A/B/C/D/E; immutability |
| `TestDashboardAggregateRegistryCorrectness` | Persist/retrieve; latest snapshot; time-window query; count; missing-id None; Gate A/D; reset |

---

## Preventive Measures

- [x] Remove all side effects from `_emit_records_execution_trace` (architectural rule enforced)
- [x] Remove all `_emit_records_execution_trace` calls from singleton accessors
- [x] Remove clock-provider indirection from dataclass defaults
- [x] 39 deterministic regression tests committed that will catch any reintroduction
- [x] Code comments on `_emit_records_execution_trace` explicitly document the no-side-effects contract
- [ ] Add lint rule prohibiting `import` of `dashboard_orchestrator` inside `lifecycle_trace_contract` (future)
- [ ] Add architectural constraint in ADG schema: emitter functions → no outbound dashboard calls (future)

---

## Conclusion

The root cause was an **architectural violation** introduced when `_emit_records_execution_trace`
was extended with dashboard aggregation side effects. This created three independent recursion
paths, any one of which would crash any production runtime call. The `ADG_SCAN_ACTIVE` guard
from the previous RCA masked the crash during static analysis but left production fully exposed.

**Fix:** Restore `_emit_records_execution_trace` to its correct single-responsibility contract
(pure logger, no side effects), and remove all recursion-capable calls from the dashboard
aggregate stack. All 39 regression tests confirm the fix is complete and correct.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

