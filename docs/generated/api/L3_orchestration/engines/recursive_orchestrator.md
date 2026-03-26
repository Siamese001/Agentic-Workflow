# API Documentation: recursive_orchestrator

**Target Audience**: developers, api_users

# recursive_orchestrator API Documentation

**File**: `recursive_orchestrator.py`
**Classes**: 3
**Functions**: 13

## Classes

- **TaskStatus** (inherits from Enum)
- **RetryContext**
- **RecursiveOrchestrator** (inherits from SovereignBaseAgent)

## Functions

- **add_failure** -> None
- **can_retry** -> bool
- **to_parameters** -> dict[str, Any]
- **__post_init__** -> None
- **handle_task_status** -> dict[str, Any]
- **handle_task_failure** -> dict[str, Any]
- **_spawn_retry_successor** -> dict[str, Any]
- **_get_or_create_retry_context** -> RetryContext
- **_get_node_function** -> str | None
- **_cleanup_retry_context** -> None
- **get_retry_status** -> dict[str, Any] | None
- **get_all_active_retries** -> dict[str, dict[str, Any]]
- **heal_repository** -> dict[str, int]


## Class: TaskStatus

**Description**: Status signals for task execution.

**Inherits from**: Enum



## Class: RetryContext

**Description**: Context passed to retry nodes containing failure history.

### Methods

#### add_failure
**Parameters**: self, reason, context
**Returns**: None
**Description**: Record a failure attempt.

#### can_retry
**Parameters**: self
**Returns**: bool
**Description**: Check if more retries are allowed.

#### to_parameters
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to parameters dict for HopSpec.



## Class: RecursiveOrchestrator

**Description**: 
    Forward-Rolling Recursion Orchestrator.

    Simulates agentic loops by spawning NEW downstream nodes instead of
    cycling backwards. This preserves DAG acyclicity while enabling
    retry/healing patterns.

    Architecture:
        [Node_v1] --FAIL--> [Node_v2] --FAIL--> [Node_v3] --SUCCESS-->
                    |               |               |
                    v               v               v
              (depth=1)       (depth=2)       (depth=3)

    The graph grows FORWARD, never backwards.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the orchestrator.

#### handle_task_status
**Parameters**: self, node_id, status, failure_reason, retry_function, additional_context
**Returns**: dict[str, Any]
**Description**: 
        Handle a task status signal from a node.

        Args:
            node_id: The ID of the node reporting status
            status: The task status (FAILED, NEEDS_REVISION, etc.)
            failure_reason: Why the task failed (required for FAILED/NEEDS_REVISION)
            retry_function: Function name to use for retry node
            additional_context: Extra context to pass to retry node

        Returns:
            Dict with action taken and result
        

#### handle_task_failure
**Parameters**: self, failed_node_id, failure_reason, retry_function, additional_context
**Returns**: dict[str, Any]
**Description**: 
        Handle a task failure by spawning a downstream retry node.

        This is the core of Forward-Rolling Recursion:
        1. Check if we can retry (max_attempts not exceeded)
        2. Create/update RetryContext with failure info
        3. Spawn a NEW successor node via DAGMutation
        4. The new node receives full failure history

        Args:
            failed_node_id: ID of the node that failed
            failure_reason: Why it failed
            retry_function: Function to use for retry (defaults to same function)
            additional_context: Extra context for the retry

        Returns:
            Dict with mutation result and retry info
        

#### _spawn_retry_successor
**Parameters**: self, failed_node_id, retry_function, retry_context
**Returns**: dict[str, Any]
**Description**: 
        Spawn a successor node using DAGMutation.

        This maintains DAG acyclicity by adding a NEW node downstream,
        never creating backward edges.
        

#### _get_or_create_retry_context
**Parameters**: self, node_id
**Returns**: RetryContext
**Description**: Get existing retry context or create new one.

#### _get_node_function
**Parameters**: self, node_id
**Returns**: str | None
**Description**: Get the function name for a node from the DAG.

#### _cleanup_retry_context
**Parameters**: self, node_id
**Returns**: None
**Description**: Clean up retry context after success.

#### get_retry_status
**Parameters**: self, node_id
**Returns**: dict[str, Any] | None
**Description**: Get retry status for a node.

#### get_all_active_retries
**Parameters**: self
**Returns**: dict[str, dict[str, Any]]
**Description**: Get all active retry contexts.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        Heal repository - validates orchestrator state.

        Checks:
        - No orphaned retry contexts
        - DAG acyclicity maintained
        - Retry limits respected
        



## Function: add_failure

**Parameters**: self, reason, context
**Returns**: None
**Description**: Record a failure attempt.



## Function: can_retry

**Parameters**: self
**Returns**: bool
**Description**: Check if more retries are allowed.



## Function: to_parameters

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to parameters dict for HopSpec.



## Function: __post_init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the orchestrator.



## Function: handle_task_status

**Parameters**: self, node_id, status, failure_reason, retry_function, additional_context
**Returns**: dict[str, Any]
**Description**: 
        Handle a task status signal from a node.

        Args:
            node_id: The ID of the node reporting status
            status: The task status (FAILED, NEEDS_REVISION, etc.)
            failure_reason: Why the task failed (required for FAILED/NEEDS_REVISION)
            retry_function: Function name to use for retry node
            additional_context: Extra context to pass to retry node

        Returns:
            Dict with action taken and result
        



## Function: handle_task_failure

**Parameters**: self, failed_node_id, failure_reason, retry_function, additional_context
**Returns**: dict[str, Any]
**Description**: 
        Handle a task failure by spawning a downstream retry node.

        This is the core of Forward-Rolling Recursion:
        1. Check if we can retry (max_attempts not exceeded)
        2. Create/update RetryContext with failure info
        3. Spawn a NEW successor node via DAGMutation
        4. The new node receives full failure history

        Args:
            failed_node_id: ID of the node that failed
            failure_reason: Why it failed
            retry_function: Function to use for retry (defaults to same function)
            additional_context: Extra context for the retry

        Returns:
            Dict with mutation result and retry info
        



## Function: _spawn_retry_successor

**Parameters**: self, failed_node_id, retry_function, retry_context
**Returns**: dict[str, Any]
**Description**: 
        Spawn a successor node using DAGMutation.

        This maintains DAG acyclicity by adding a NEW node downstream,
        never creating backward edges.
        



## Function: _get_or_create_retry_context

**Parameters**: self, node_id
**Returns**: RetryContext
**Description**: Get existing retry context or create new one.



## Function: _get_node_function

**Parameters**: self, node_id
**Returns**: str | None
**Description**: Get the function name for a node from the DAG.



## Function: _cleanup_retry_context

**Parameters**: self, node_id
**Returns**: None
**Description**: Clean up retry context after success.



## Function: get_retry_status

**Parameters**: self, node_id
**Returns**: dict[str, Any] | None
**Description**: Get retry status for a node.



## Function: get_all_active_retries

**Parameters**: self
**Returns**: dict[str, dict[str, Any]]
**Description**: Get all active retry contexts.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        Heal repository - validates orchestrator state.

        Checks:
        - No orphaned retry contexts
        - DAG acyclicity maintained
        - Retry limits respected
        



## Usage Examples

### Class Usage

```python
# Using TaskStatus
taskstatus = TaskStatus()
```

```python
# Using RetryContext
retrycontext = RetryContext()
retrycontext.add_failure()
retrycontext.can_retry()
```

```python
# Using RecursiveOrchestrator
recursiveorchestrator = RecursiveOrchestrator()
recursiveorchestrator.handle_task_status()
recursiveorchestrator.handle_task_failure()
```

### Function Usage

```python
# Using add_failure
result = add_failure(reason, context)
```

```python
# Using can_retry
result = can_retry()
```

```python
# Using to_parameters
result = to_parameters()
```



---
**Generated**: 2026-03-26T09:39:04.202317
**Type**: api_reference
**Quality**: comprehensive
