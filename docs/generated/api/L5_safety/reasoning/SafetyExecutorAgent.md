# API Documentation: SafetyExecutorAgent

**Target Audience**: developers, api_users

# SafetyExecutorAgent API Documentation

**File**: `SafetyExecutorAgent.py`
**Classes**: 6
**Functions**: 13

## Classes

- **ExecutionStatus** (inherits from Enum)
- **BlockReason** (inherits from Enum)
- **ExecutionResult**
- **SafetyGate**
- **ExecutorConfig**
- **SafetyExecutorAgent** (inherits from SovereignBaseAgent)

## Functions

- **create_legacy_integrity_executor** -> SafetyExecutorAgent
- **create_legacy_safety_executor** -> SafetyExecutorAgent
- **heal_repository** -> dict[str, Any]
- **__init__**
- **_init_default_gates** -> None
- **add_gate** -> None
- **execute** -> ExecutionResult
- **_run_safety_checks** -> ExecutionResult
- **_run_gates** -> ExecutionResult
- **check_and_block** -> tuple[bool, str]
- **get_stats** -> dict[str, Any]
- **get_results** -> list[ExecutionResult]
- **heal** -> dict


## Class: ExecutionStatus

**Description**: Status of execution.

**Inherits from**: Enum



## Class: BlockReason

**Description**: Reasons for blocking execution.

**Inherits from**: Enum



## Class: ExecutionResult

**Description**: Result of an execution attempt.



## Class: SafetyGate

**Description**: Represents a safety gate check.



## Class: ExecutorConfig

**Description**: configuration for safety executor.



## Class: SafetyExecutorAgent

**Description**: 
    Unified safety executor with integrity gates.

    Consolidates:
    - IntegrityGateExecutorAgent
    - L5IntegrityGateExecutorAgent
    - SafetyExecutorAgent

    Usage:
        executor = SafetyExecutorAgent()

        # Execute with safety checks
        result = executor.execute(my_function, arg1, arg2)

        # Add custom gate
        executor.add_gate("custom_check", lambda: check_something())
    

**Inherits from**: SovereignBaseAgent

### Methods

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        

#### __init__
**Parameters**: self, agent_config, detector

#### _init_default_gates
**Parameters**: self
**Returns**: None
**Description**: Initialize default safety gates.

#### add_gate
**Parameters**: self, name, check_fn, severity, blocking
**Returns**: None
**Description**: Add a custom safety gate.

#### execute
**Parameters**: self, fn
**Returns**: ExecutionResult
**Description**: 
        Execute a function with safety checks.

        Args:
            fn: Function to execute
            *args: Positional arguments
            context: Execution context for gate checks
            **kwargs: Keyword arguments

        Returns:
            ExecutionResult with status and result
        

#### _run_safety_checks
**Parameters**: self, context
**Returns**: ExecutionResult
**Description**: Run safety detector checks.

#### _run_gates
**Parameters**: self, context
**Returns**: ExecutionResult
**Description**: Run integrity gates.

#### check_and_block
**Parameters**: self, input_text, source
**Returns**: tuple[bool, str]
**Description**: 
        Quick check if input should be blocked.

        Args:
            input_text: Input to check
            source: Source of input

        Returns:
            Tuple of (should_block, reason)
        

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get execution statistics.

#### get_results
**Parameters**: self
**Returns**: list[ExecutionResult]
**Description**: Get all execution results.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal safety execution violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (blocked, failed, integrity)
                - block_reason: Reason for blocking
                - agent_id: Agent that was blocked

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: create_legacy_integrity_executor

**Returns**: SafetyExecutorAgent
**Description**: Create executor with integrity gates only.



## Function: create_legacy_safety_executor

**Returns**: SafetyExecutorAgent
**Description**: Create executor with safety checks only.



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        



## Function: __init__

**Parameters**: self, agent_config, detector


## Function: _init_default_gates

**Parameters**: self
**Returns**: None
**Description**: Initialize default safety gates.



## Function: add_gate

**Parameters**: self, name, check_fn, severity, blocking
**Returns**: None
**Description**: Add a custom safety gate.



## Function: execute

**Parameters**: self, fn
**Returns**: ExecutionResult
**Description**: 
        Execute a function with safety checks.

        Args:
            fn: Function to execute
            *args: Positional arguments
            context: Execution context for gate checks
            **kwargs: Keyword arguments

        Returns:
            ExecutionResult with status and result
        



## Function: _run_safety_checks

**Parameters**: self, context
**Returns**: ExecutionResult
**Description**: Run safety detector checks.



## Function: _run_gates

**Parameters**: self, context
**Returns**: ExecutionResult
**Description**: Run integrity gates.



## Function: check_and_block

**Parameters**: self, input_text, source
**Returns**: tuple[bool, str]
**Description**: 
        Quick check if input should be blocked.

        Args:
            input_text: Input to check
            source: Source of input

        Returns:
            Tuple of (should_block, reason)
        



## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get execution statistics.



## Function: get_results

**Parameters**: self
**Returns**: list[ExecutionResult]
**Description**: Get all execution results.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal safety execution violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (blocked, failed, integrity)
                - block_reason: Reason for blocking
                - agent_id: Agent that was blocked

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using ExecutionStatus
executionstatus = ExecutionStatus()
```

```python
# Using BlockReason
blockreason = BlockReason()
```

```python
# Using ExecutionResult
executionresult = ExecutionResult()
```

### Function Usage

```python
# Using create_legacy_integrity_executor
result = create_legacy_integrity_executor()
```

```python
# Using create_legacy_safety_executor
result = create_legacy_safety_executor()
```

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```



---
**Generated**: 2026-03-26T09:39:05.387517
**Type**: api_reference
**Quality**: comprehensive
