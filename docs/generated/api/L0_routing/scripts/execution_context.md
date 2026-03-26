# API Documentation: execution_context

**Target Audience**: developers, api_users

# execution_context API Documentation

**File**: `execution_context.py`
**Classes**: 7
**Functions**: 14

## Classes

- **ConfigSurface**
- **ExecutionContext**
- **BaseRefiner**
- **BaseTaskExecutor** (inherits from SovereignBaseAgent, SubatomicTestingMixin)
- **BaseDiagnoser**
- **PolicyResult**
- **SubatomicTestingMixin**

## Functions

- **_get_subatomic_testing_mixin**
- **compute_hash** -> str
- **to_dict** -> dict[str, Any]
- **set_config_surface** -> None
- **__init__**
- **refine** -> dict[str, Any]
- **__init__**
- **execute** -> dict[str, Any]
- **_do_execute** -> Any
- **heal_repository** -> dict
- **__init__**
- **diagnose** -> dict[str, Any]
- **_check_issues** -> list[str]
- **final_verdict** -> str


## Class: ConfigSurface

**Description**: A container for all sovereign configuration values that affect determinism.

### Methods

#### compute_hash
**Parameters**: self
**Returns**: str
**Description**: Computes a deterministic hash of the entire configuration surface.



## Class: ExecutionContext

**Description**: 
    Shared execution context for all domain operations.
    Previously duplicated 15+ times across codebase.

    Usage:
        from apps_shared.utils.common_patterns import ExecutionContext

    Replay-mode fields (Phase 0.5 — SSOT Mixin Integration):
        replay_mode: bool — True if execution is a deterministic replay.
        active_policy_hash: str | None — L4 policy hash anchoring all state.
        safety_status: str — L5 safety gate status (PENDING|CLEARED|FAILED).
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.

#### set_config_surface
**Parameters**: self, config_surface
**Returns**: None
**Description**: Computes and sets the config surface hash for this context.



## Class: BaseRefiner

**Description**: 
    Base class for refinement operations.
    Previously duplicated 11+ times as refine() function.

    Usage:
        from apps_shared.utils.common_patterns import BaseRefiner

        class MyRefiner(BaseRefiner):
            def refine(self, data, weights):
                return super().refine(data, weights)
    

### Methods

#### __init__
**Parameters**: self, config

#### refine
**Parameters**: self, data, weights
**Returns**: dict[str, Any]
**Description**: 
        Apply refinement weights to data.

        Args:
            data: Input data to refine
            weights: Optional weight overrides

        Returns:
            Refined data with weights applied
        



## Class: BaseTaskExecutor

**Description**: 
    Base class for task execution with error handling.
    Previously duplicated 7+ times as execute() function.

    Usage:
        from apps_shared.utils.common_patterns import BaseTaskExecutor
    

**Inherits from**: SovereignBaseAgent, SubatomicTestingMixin

### Methods

#### __init__
**Parameters**: self, config

#### execute
**Parameters**: self, task
**Returns**: dict[str, Any]
**Description**: 
        Execute a task with retry and timeout handling.

        Args:
            task: Task specification

        Returns:
            Execution result
        

#### _do_execute
**Parameters**: self, task
**Returns**: Any
**Description**: Override in subclass to implement actual execution.

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: Invoke healing chain via super().



## Class: BaseDiagnoser

**Description**: 
    Base class for diagnostic operations.
    Previously duplicated 6+ times as diagnose() function.

    Usage:
        from apps_shared.utils.common_patterns import BaseDiagnoser
    

### Methods

#### __init__
**Parameters**: self, config

#### diagnose
**Parameters**: self, target
**Returns**: dict[str, Any]
**Description**: 
        Run diagnostics on a target.

        Args:
            target: Object to diagnose

        Returns:
            Diagnostic report
        

#### _check_issues
**Parameters**: self, target
**Returns**: list[str]
**Description**: Override in subclass to implement specific checks.



## Class: PolicyResult

**Description**: 
    Result of a policy evaluation.
    Previously duplicated 3+ times.

    Usage:
        from apps_shared.utils.common_patterns import PolicyResult
    

### Methods

#### final_verdict
**Parameters**: self
**Returns**: str
**Description**: Return the final verdict string.



## Class: SubatomicTestingMixin



## Function: _get_subatomic_testing_mixin



## Function: compute_hash

**Parameters**: self
**Returns**: str
**Description**: Computes a deterministic hash of the entire configuration surface.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: set_config_surface

**Parameters**: self, config_surface
**Returns**: None
**Description**: Computes and sets the config surface hash for this context.



## Function: __init__

**Parameters**: self, config


## Function: refine

**Parameters**: self, data, weights
**Returns**: dict[str, Any]
**Description**: 
        Apply refinement weights to data.

        Args:
            data: Input data to refine
            weights: Optional weight overrides

        Returns:
            Refined data with weights applied
        



## Function: __init__

**Parameters**: self, config


## Function: execute

**Parameters**: self, task
**Returns**: dict[str, Any]
**Description**: 
        Execute a task with retry and timeout handling.

        Args:
            task: Task specification

        Returns:
            Execution result
        



## Function: _do_execute

**Parameters**: self, task
**Returns**: Any
**Description**: Override in subclass to implement actual execution.



## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: Invoke healing chain via super().



## Function: __init__

**Parameters**: self, config


## Function: diagnose

**Parameters**: self, target
**Returns**: dict[str, Any]
**Description**: 
        Run diagnostics on a target.

        Args:
            target: Object to diagnose

        Returns:
            Diagnostic report
        



## Function: _check_issues

**Parameters**: self, target
**Returns**: list[str]
**Description**: Override in subclass to implement specific checks.



## Function: final_verdict

**Parameters**: self
**Returns**: str
**Description**: Return the final verdict string.



## Usage Examples

### Class Usage

```python
# Using ConfigSurface
configsurface = ConfigSurface()
configsurface.compute_hash()
```

```python
# Using ExecutionContext
executioncontext = ExecutionContext()
executioncontext.to_dict()
executioncontext.set_config_surface()
```

```python
# Using BaseRefiner
baserefiner = BaseRefiner()
baserefiner.refine()
```

### Function Usage

```python
# Using _get_subatomic_testing_mixin
result = _get_subatomic_testing_mixin()
```

```python
# Using compute_hash
result = compute_hash()
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:03.092747
**Type**: api_reference
**Quality**: comprehensive
