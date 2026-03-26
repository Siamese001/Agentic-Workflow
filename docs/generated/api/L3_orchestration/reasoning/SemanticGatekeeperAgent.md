# API Documentation: SemanticGatekeeperAgent

**Target Audience**: developers, api_users

# SemanticGatekeeperAgent API Documentation

**File**: `SemanticGatekeeperAgent.py`
**Classes**: 1
**Functions**: 8

## Classes

- **SemanticGatekeeperAgent** (inherits from SovereignBaseAgent)

## Functions

- **get_gatekeeper** -> SemanticGatekeeperAgent
- **__init__** -> None
- **_run_self_tests** -> bool
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **get_dead_letters** -> list
- **clear_dead_letters** -> Any
- **get_stats** -> dict


## Class: SemanticGatekeeperAgent

**Description**: 
    Gatekeeper that controls agent execution with concurrency limits and timeouts.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, max_concurrent, timeout_seconds
**Returns**: None
**Description**: 
        Initialize the gatekeeper.

        Args:
            max_concurrent: Maximum number of concurrent executions
            timeout_seconds: Default timeout for operations
        

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L3 compliance.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 orchestration agent - operational only.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by SemanticGatekeeperAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        

#### get_dead_letters
**Parameters**: self
**Returns**: list
**Description**: Get all dead letter entries.

#### clear_dead_letters
**Parameters**: self
**Returns**: Any
**Description**: Clear the dead letter queue.

#### get_stats
**Parameters**: self
**Returns**: dict
**Description**: Get gatekeeper statistics.



## Function: get_gatekeeper

**Returns**: SemanticGatekeeperAgent
**Description**: Get or create the global gatekeeper instance.



## Function: __init__

**Parameters**: self, max_concurrent, timeout_seconds
**Returns**: None
**Description**: 
        Initialize the gatekeeper.

        Args:
            max_concurrent: Maximum number of concurrent executions
            timeout_seconds: Default timeout for operations
        



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L3 compliance.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 orchestration agent - operational only.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by SemanticGatekeeperAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Function: get_dead_letters

**Parameters**: self
**Returns**: list
**Description**: Get all dead letter entries.



## Function: clear_dead_letters

**Parameters**: self
**Returns**: Any
**Description**: Clear the dead letter queue.



## Function: get_stats

**Parameters**: self
**Returns**: dict
**Description**: Get gatekeeper statistics.



## Usage Examples

### Class Usage

```python
# Using SemanticGatekeeperAgent
semanticgatekeeperagent = SemanticGatekeeperAgent()
semanticgatekeeperagent.heal_repository()
semanticgatekeeperagent.heal()
```

### Function Usage

```python
# Using get_gatekeeper
result = get_gatekeeper()
```

```python
# Using __init__
result = __init__(max_concurrent, timeout_seconds)
```

```python
# Using _run_self_tests
result = _run_self_tests()
```



---
**Generated**: 2026-03-26T09:39:04.301689
**Type**: api_reference
**Quality**: comprehensive
