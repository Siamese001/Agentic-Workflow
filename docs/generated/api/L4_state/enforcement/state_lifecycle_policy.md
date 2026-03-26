# API Documentation: state_lifecycle_policy

**Target Audience**: developers, api_users

# state_lifecycle_policy API Documentation

**File**: `state_lifecycle_policy.py`
**Classes**: 4
**Functions**: 9

## Classes

- **StateLifecycleStage** (inherits from str, Enum)
- **LifecycleTransition**
- **StateLifecycleViolationError** (inherits from RuntimeError)
- **StateLifecyclePolicy**

## Functions

- **__init__** -> None
- **stage** -> StateLifecycleStage
- **transition** -> LifecycleTransition
- **activate** -> LifecycleTransition
- **freeze** -> LifecycleTransition
- **archive** -> LifecycleTransition
- **purge** -> LifecycleTransition
- **is_writable** -> bool
- **history** -> list[LifecycleTransition]


## Class: StateLifecycleStage

**Description**: Lifecycle stages for L4 state objects.

**Inherits from**: str, Enum



## Class: LifecycleTransition

**Description**: Record of a single state lifecycle transition.



## Class: StateLifecycleViolationError

**Description**: Raised when an invalid lifecycle transition is attempted.

**Inherits from**: RuntimeError



## Class: StateLifecyclePolicy

**Description**: Enforces lifecycle transitions for a run-scoped state object.

    Usage::

        policy = StateLifecyclePolicy("run-abc")
        policy.transition(StateLifecycleStage.ACTIVE)
        policy.transition(StateLifecycleStage.FROZEN)
        policy.transition(StateLifecycleStage.ARCHIVED)
        policy.transition(StateLifecycleStage.PURGED)
    

### Methods

#### __init__
**Parameters**: self, run_id
**Returns**: None

#### stage
**Parameters**: self
**Returns**: StateLifecycleStage

#### transition
**Parameters**: self, target, reason
**Returns**: LifecycleTransition
**Description**: Execute a lifecycle transition.

        Emits ``enforce_lifecycle`` ADG edge. Raises on invalid transitions.
        

#### activate
**Parameters**: self
**Returns**: LifecycleTransition

#### freeze
**Parameters**: self
**Returns**: LifecycleTransition

#### archive
**Parameters**: self
**Returns**: LifecycleTransition

#### purge
**Parameters**: self
**Returns**: LifecycleTransition

#### is_writable
**Parameters**: self
**Returns**: bool

#### history
**Parameters**: self
**Returns**: list[LifecycleTransition]



## Function: __init__

**Parameters**: self, run_id
**Returns**: None


## Function: stage

**Parameters**: self
**Returns**: StateLifecycleStage


## Function: transition

**Parameters**: self, target, reason
**Returns**: LifecycleTransition
**Description**: Execute a lifecycle transition.

        Emits ``enforce_lifecycle`` ADG edge. Raises on invalid transitions.
        



## Function: activate

**Parameters**: self
**Returns**: LifecycleTransition


## Function: freeze

**Parameters**: self
**Returns**: LifecycleTransition


## Function: archive

**Parameters**: self
**Returns**: LifecycleTransition


## Function: purge

**Parameters**: self
**Returns**: LifecycleTransition


## Function: is_writable

**Parameters**: self
**Returns**: bool


## Function: history

**Parameters**: self
**Returns**: list[LifecycleTransition]


## Usage Examples

### Class Usage

```python
# Using StateLifecycleStage
statelifecyclestage = StateLifecycleStage()
```

```python
# Using LifecycleTransition
lifecycletransition = LifecycleTransition()
```

```python
# Using StateLifecycleViolationError
statelifecycleviolationerror = StateLifecycleViolationError()
```

### Function Usage

```python
# Using __init__
result = __init__(run_id)
```

```python
# Using stage
result = stage()
```

```python
# Using transition
result = transition(target, reason)
```



---
**Generated**: 2026-03-26T09:39:04.521267
**Type**: api_reference
**Quality**: comprehensive
