# API Documentation: elevator_shaft_consistency_enforcer

**Target Audience**: developers, api_users

# elevator_shaft_consistency_enforcer API Documentation

**File**: `elevator_shaft_consistency_enforcer.py`
**Classes**: 5
**Functions**: 10

## Classes

- **ClockSyncViolation** (inherits from RuntimeError)
- **MonotonicityViolation** (inherits from RuntimeError)
- **WallClockContaminationError** (inherits from RuntimeError)
- **LayerClockRecord**
- **ElevatorShaftConsistencyEnforcer**

## Functions

- **assert_clock_synchronized** -> None
- **assert_no_wall_clock_in_module** -> None
- **get_enforcer** -> ElevatorShaftConsistencyEnforcer
- **reset_enforcer** -> None
- **__init__** -> None
- **record_advance** -> None
- **assert_layers_synchronized** -> None
- **register_module** -> None
- **layer_tick** -> int | None
- **summary** -> dict[str, Any]


## Class: ClockSyncViolation

**Description**: Raised when two SemanticClockSnapshots are not sufficiently synchronized.

**Inherits from**: RuntimeError



## Class: MonotonicityViolation

**Description**: Raised when a new clock tick is less than the previously recorded tick.

**Inherits from**: RuntimeError



## Class: WallClockContaminationError

**Description**: Raised when a module contains forbidden wall-clock calls.

**Inherits from**: RuntimeError



## Class: LayerClockRecord

**Description**: Tracks the last-known semantic clock tick for a single layer.



## Class: ElevatorShaftConsistencyEnforcer

**Description**: Runtime enforcer for elevator shaft state synchronization.

    Maintains the canonical tick per layer and enforces:
    - Monotonicity: ticks must not go backward.
    - Drift: cross-layer drift must stay within tolerance.
    - Wall-clock isolation: modules submitted for registration are AST-scanned.

    Usage::

        enforcer = ElevatorShaftConsistencyEnforcer(drift_tolerance=3)
        enforcer.record_advance("L0", snapshot_l0)
        enforcer.record_advance("L2", snapshot_l2)
        enforcer.assert_layers_synchronized("L0", "L2")
    

### Methods

#### __init__
**Parameters**: self, drift_tolerance
**Returns**: None

#### record_advance
**Parameters**: self, layer, snapshot
**Returns**: None
**Description**: Record a clock advancement for *layer*.

        Raises:
            MonotonicityViolation: if the new tick is less than the last recorded tick.
        

#### assert_layers_synchronized
**Parameters**: self, layer_a, layer_b
**Returns**: None
**Description**: Assert that two layers are within drift tolerance.

        Raises:
            ClockSyncViolation: if drift exceeds tolerance.
            KeyError: if either layer has not been recorded yet.
        

#### register_module
**Parameters**: self, module_path
**Returns**: None
**Description**: Register a module after asserting it contains no wall-clock calls.

        Raises:
            WallClockContaminationError: if the module has wall-clock violations.
        

#### layer_tick
**Parameters**: self, layer
**Returns**: int | None
**Description**: Return the last recorded tick for *layer*, or None if not yet recorded.

#### summary
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return a summary of all tracked layers.



## Function: assert_clock_synchronized

**Parameters**: snapshot_a, snapshot_b
**Returns**: None
**Description**: Assert that two SemanticClockSnapshots are within *tolerance* ticks of each other.

    Args:
        snapshot_a: First clock snapshot (e.g. from the caller layer).
        snapshot_b: Second clock snapshot (e.g. from the callee layer).
        tolerance: Maximum allowed tick difference before raising.
        context: Optional context string for error messages.

    Raises:
        ClockSyncViolation: if ``abs(a.tick - b.tick) > tolerance``.
    



## Function: assert_no_wall_clock_in_module

**Parameters**: module_path, context
**Returns**: None
**Description**: Assert that *module_path* contains no wall-clock calls.

    Delegates to ``scan_module_for_wallclock`` (L6 observability AST scanner).

    Raises:
        WallClockContaminationError: if any wall-clock violation is found.
    



## Function: get_enforcer

**Parameters**: drift_tolerance
**Returns**: ElevatorShaftConsistencyEnforcer
**Description**: Return the global ElevatorShaftConsistencyEnforcer instance.



## Function: reset_enforcer

**Returns**: None
**Description**: Reset the global enforcer (for testing only).



## Function: __init__

**Parameters**: self, drift_tolerance
**Returns**: None


## Function: record_advance

**Parameters**: self, layer, snapshot
**Returns**: None
**Description**: Record a clock advancement for *layer*.

        Raises:
            MonotonicityViolation: if the new tick is less than the last recorded tick.
        



## Function: assert_layers_synchronized

**Parameters**: self, layer_a, layer_b
**Returns**: None
**Description**: Assert that two layers are within drift tolerance.

        Raises:
            ClockSyncViolation: if drift exceeds tolerance.
            KeyError: if either layer has not been recorded yet.
        



## Function: register_module

**Parameters**: self, module_path
**Returns**: None
**Description**: Register a module after asserting it contains no wall-clock calls.

        Raises:
            WallClockContaminationError: if the module has wall-clock violations.
        



## Function: layer_tick

**Parameters**: self, layer
**Returns**: int | None
**Description**: Return the last recorded tick for *layer*, or None if not yet recorded.



## Function: summary

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return a summary of all tracked layers.



## Usage Examples

### Class Usage

```python
# Using ClockSyncViolation
clocksyncviolation = ClockSyncViolation()
```

```python
# Using MonotonicityViolation
monotonicityviolation = MonotonicityViolation()
```

```python
# Using WallClockContaminationError
wallclockcontaminationerror = WallClockContaminationError()
```

### Function Usage

```python
# Using assert_clock_synchronized
result = assert_clock_synchronized(snapshot_a, snapshot_b)
```

```python
# Using assert_no_wall_clock_in_module
result = assert_no_wall_clock_in_module(module_path, context)
```

```python
# Using get_enforcer
result = get_enforcer(drift_tolerance)
```



---
**Generated**: 2026-03-26T09:39:04.490800
**Type**: api_reference
**Quality**: comprehensive
