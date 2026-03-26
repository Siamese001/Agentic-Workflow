# API Documentation: runtime_guard

**Target Audience**: developers, api_users

# runtime_guard API Documentation

**File**: `runtime_guard.py`
**Classes**: 0
**Functions**: 8


## Functions

- **_get_active_guards** -> set[str]
- **_get_correlation_id** -> str | None
- **runtime_guard** -> Callable[[F], F]
- **_guarded_call** -> Any
- **assert_v15_guarded** -> None
- **v15_runtime_boundary** -> Callable[[F], F]
- **decorator** -> F
- **sync_wrapper** -> Any


## Function: _get_active_guards

**Returns**: set[str]
**Description**: Return the set of currently active guard entry point IDs.



## Function: _get_correlation_id

**Returns**: str | None
**Description**: Return the current correlation_id if inside a guarded context.



## Function: runtime_guard

**Parameters**: entry_point_id
**Returns**: Callable[[F], F]
**Description**: Decorator that enforces V15 gateway routing for a runtime entry point.

    Args:
        entry_point_id: The inventory ID from Wave 2.1 (e.g. "A.run_mission.orchestrator_engine").

    When V15_ENFORCEMENT=1:
        - Creates a correlation_id for the execution
        - Registers the entry point as actively guarded
        - Logs entry/exit for audit trail

    When V15_ENFORCEMENT=0:
        - Pass-through with zero overhead
    



## Function: _guarded_call

**Parameters**: fn, entry_point_id, args, kwargs
**Returns**: Any
**Description**: Execute a synchronous function under V15 guard.



## Function: assert_v15_guarded

**Parameters**: entry_point_id
**Returns**: None
**Description**: Fail-closed assertion: raises V15EnforcementError if called outside a guard.

    Call this at the top of any enforcement boundary to prove the guard is active.
    Under V15_ENFORCEMENT=0, this is a no-op.
    



## Function: v15_runtime_boundary

**Parameters**: entry_point_id
**Returns**: Callable[[F], F]
**Description**: Canonical unified guard — safe for bootstrap and normal contexts.

    Identical semantics to ``runtime_guard`` but fail-closed safe:
    when ``V15_ENFORCEMENT=1`` and the guard infrastructure cannot initialise,
    the import error propagates (hard failure).  When enforcement is off,
    the decorator is a zero-cost identity wrapper.

    Use this instead of duplicating ``_optional_runtime_guard()`` in
    every bootstrap file.
    



## Function: decorator

**Parameters**: fn
**Returns**: F


## Function: sync_wrapper

**Returns**: Any


## Usage Examples

### Function Usage

```python
# Using _get_active_guards
result = _get_active_guards()
```

```python
# Using _get_correlation_id
result = _get_correlation_id()
```

```python
# Using runtime_guard
result = runtime_guard(entry_point_id)
```



---
**Generated**: 2026-03-26T09:39:02.633002
**Type**: api_reference
**Quality**: comprehensive
