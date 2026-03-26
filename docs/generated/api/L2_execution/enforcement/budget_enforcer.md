# API Documentation: budget_enforcer

**Target Audience**: developers, api_users

# budget_enforcer API Documentation

**File**: `budget_enforcer.py`
**Classes**: 2
**Functions**: 6

## Classes

- **BudgetExceeded** (inherits from RuntimeError)
- **BudgetEnforcer**

## Functions

- **_wall_clock_cap_unix**
- **_wall_clock_cap_threading**
- **_wall_clock_cap**
- **_handler**
- **_fire**
- **run** -> tuple[int, bytes]


## Class: BudgetExceeded

**Description**: Raised when a ToolBudget cap is breached.

**Inherits from**: RuntimeError



## Class: BudgetEnforcer

**Description**: Enforces ToolBudget caps around a tool callable.

    Cross-platform: uses SIGALRM on Unix main thread, threading.Timer elsewhere.
    Memory cap is Unix-only (no-op on Windows/macOS).
    stdout_bytes cap is always enforced.
    

### Methods

#### run
**Parameters**: self, envelope, tool_fn
**Returns**: tuple[int, bytes]
**Description**: Execute tool_fn under budget caps.

        Returns (exit_code, stdout_bytes) per PTC ToolResult contract [3].
        



## Function: _wall_clock_cap_unix

**Parameters**: ms
**Description**: SIGALRM-based wall-clock cap — Unix only.



## Function: _wall_clock_cap_threading

**Parameters**: ms
**Description**: threading.Timer-based wall-clock cap — cross-platform fallback.



## Function: _wall_clock_cap

**Parameters**: ms
**Description**: Return the appropriate wall-clock cap context manager for this platform.



## Function: _handler

**Parameters**: signum, frame


## Function: _fire



## Function: run

**Parameters**: self, envelope, tool_fn
**Returns**: tuple[int, bytes]
**Description**: Execute tool_fn under budget caps.

        Returns (exit_code, stdout_bytes) per PTC ToolResult contract [3].
        



## Usage Examples

### Class Usage

```python
# Using BudgetExceeded
budgetexceeded = BudgetExceeded()
```

```python
# Using BudgetEnforcer
budgetenforcer = BudgetEnforcer()
budgetenforcer.run()
```

### Function Usage

```python
# Using _wall_clock_cap_unix
result = _wall_clock_cap_unix(ms)
```

```python
# Using _wall_clock_cap_threading
result = _wall_clock_cap_threading(ms)
```

```python
# Using _wall_clock_cap
result = _wall_clock_cap(ms)
```



---
**Generated**: 2026-03-26T09:39:03.680723
**Type**: api_reference
**Quality**: comprehensive
