# API Documentation: RedisSovereignAgent

**Target Audience**: developers, api_users

# RedisSovereignAgent API Documentation

**File**: `RedisSovereignAgent.py`
**Classes**: 1
**Functions**: 11

## Classes

- **RedisSovereignAgent** (inherits from SovereignBaseAgent)

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **__init__** -> None
- **_init** -> None
- **_run_self_tests** -> bool
- **get_client** -> redis.Redis
- **_audit** -> None
- **invalidate_file_cache** -> None
- **invalidate_by_path** -> None
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]


## Class: RedisSovereignAgent

**Description**: 
    Sovereign Redis controller — hardened, monitored, eternal.

    [PHASE 2 MIGRATION] Absorbed Auditing and Telemetry:
    - Centralized operation_stats for dashboard visualization.
    - Standardized audit logging for L4 compliance.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root, ctx
**Returns**: None
**Description**: 
        Initialize Redis connection with hardened pool.

        Args:
            project_root: Root directory of the project
            ctx: Optional validation context for state persistence

        Raises:
            ConnectionError: If Redis connection fails
        

#### _init
**Parameters**: self, project_root, ctx
**Returns**: None
**Description**: 
        Initialize Redis connection with hardened pool.

        Args:
            project_root: Root directory of the project
            ctx: Optional validation context for state persistence

        Raises:
            ConnectionError: If Redis connection fails
        

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L4 compliance.

#### get_client
**Parameters**: self
**Returns**: redis.Redis
**Description**: Get the Redis client instance.

#### _audit
**Parameters**: self, operation, key, success
**Returns**: None
**Description**: [PHASE 2] Record operation to internal audit plane.

#### invalidate_file_cache
**Parameters**: self, file_path
**Returns**: None
**Description**: 
        Wipes old embeddings if the file has evolved.

        Args:
            file_path: Path to file whose cache should be invalidated
        

#### invalidate_by_path
**Parameters**: self, file_path
**Returns**: None
**Description**: 
        Invalidate cache by exact file path (for moves/deletes).

        Args:
            file_path: Path to file whose cache should be invalidated
        Ensures no 'ghost' embeddings remain for a path that no longer exists.
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L4 state agent - operational only.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by RedisSovereignAgent.

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
        



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: payload, target


## Function: __init__

**Parameters**: self, project_root, ctx
**Returns**: None
**Description**: 
        Initialize Redis connection with hardened pool.

        Args:
            project_root: Root directory of the project
            ctx: Optional validation context for state persistence

        Raises:
            ConnectionError: If Redis connection fails
        



## Function: _init

**Parameters**: self, project_root, ctx
**Returns**: None
**Description**: 
        Initialize Redis connection with hardened pool.

        Args:
            project_root: Root directory of the project
            ctx: Optional validation context for state persistence

        Raises:
            ConnectionError: If Redis connection fails
        



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L4 compliance.



## Function: get_client

**Parameters**: self
**Returns**: redis.Redis
**Description**: Get the Redis client instance.



## Function: _audit

**Parameters**: self, operation, key, success
**Returns**: None
**Description**: [PHASE 2] Record operation to internal audit plane.



## Function: invalidate_file_cache

**Parameters**: self, file_path
**Returns**: None
**Description**: 
        Wipes old embeddings if the file has evolved.

        Args:
            file_path: Path to file whose cache should be invalidated
        



## Function: invalidate_by_path

**Parameters**: self, file_path
**Returns**: None
**Description**: 
        Invalidate cache by exact file path (for moves/deletes).

        Args:
            file_path: Path to file whose cache should be invalidated
        Ensures no 'ghost' embeddings remain for a path that no longer exists.
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L4 state agent - operational only.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by RedisSovereignAgent.

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
        



## Usage Examples

### Class Usage

```python
# Using RedisSovereignAgent
redissovereignagent = RedisSovereignAgent()
redissovereignagent.get_client()
redissovereignagent.invalidate_file_cache()
```

### Function Usage

```python
# Using _invoke_authorize_and_execute
result = _invoke_authorize_and_execute(execution_context, target_callable)
```

```python
# Using _make_execution_context
result = _make_execution_context(payload, target)
```

```python
# Using __init__
result = __init__(project_root, ctx)
```



---
**Generated**: 2026-03-26T09:39:03.871218
**Type**: api_reference
**Quality**: comprehensive
