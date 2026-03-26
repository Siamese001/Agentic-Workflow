# API Documentation: DagEngineAgent

**Target Audience**: developers, api_users

# DagEngineAgent API Documentation

**File**: `DagEngineAgent.py`
**Classes**: 5
**Functions**: 20

## Classes

- **TaskStatus** (inherits from Enum)
- **TaskType** (inherits from Enum)
- **Task**
- **DagExecutionResult**
- **DagEngineAgent** (inherits from SovereignBaseAgent)

## Functions

- **create_dag_from_config** -> DAGEngine
- **is_ready** -> bool
- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **__init__** -> None
- **_run_self_tests** -> bool
- **add_task** -> None
- **remove_task** -> None
- **validate_dag** -> list[str]
- **topological_sort** -> list[str]
- **_log_dag_start** -> None
- **_should_execute_task** -> bool
- **_create_dag_result** -> DAGExecutionResult
- **_evaluate_condition** -> bool
- **_evaluate_equality_condition** -> bool
- **get_task_status** -> TaskStatus | None
- **reset** -> None
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **has_cycle** -> bool


## Class: TaskStatus

**Description**: Status of a Task in the DAG.

**Inherits from**: Enum



## Class: TaskType

**Description**: Type of Task in the DAG.

**Inherits from**: Enum



## Class: Task

**Description**: Individual Task in the DAG.

### Methods

#### is_ready
**Parameters**: self, completed_tasks
**Returns**: bool
**Description**: Check if Task is ready to execute.

        Args:
            completed_tasks: Set of completed Task IDs

        Returns:
            True if all dependencies are met
        

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: DagExecutionResult

**Description**: Result from DAG execution.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: DagEngineAgent

**Description**: Lightweight DAG engine for workflow execution.

    Features:
    - Task dependency management
    - Conditional branching
    - Parallel execution support
    - Topological sorting
    - Cycle detection
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, enable_logging
**Returns**: None
**Description**: Initialize DAG engine.

        Args:
            enable_logging: Enable logging of execution
        

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L3 compliance.

#### add_task
**Parameters**: self, Task
**Returns**: None
**Description**: Add a Task to the DAG.

        Args:
            Task: Task to add
        

#### remove_task
**Parameters**: self, task_id
**Returns**: None
**Description**: Remove a Task from the DAG.

        Args:
            task_id: ID of Task to remove
        

#### validate_dag
**Parameters**: self
**Returns**: list[str]
**Description**: Validate the DAG for cycles and Missing dependencies.

        Returns:
            List of validation errors (empty if valid)
        

#### topological_sort
**Parameters**: self
**Returns**: list[str]
**Description**: Perform topological sort to determine execution order.

        Returns:
            List of Task IDs in execution order

        Raises:
            ValueError: If DAG has cycles
        

#### _log_dag_start
**Parameters**: self, execution_order
**Returns**: None
**Description**: Log DAG execution start.

#### _should_execute_task
**Parameters**: self, Task, task_id, completed_tasks, context, task_results, skipped_tasks
**Returns**: bool
**Description**: Check if Task should be executed.

#### _create_dag_result
**Parameters**: self, completed_tasks, failed_tasks, skipped_tasks, task_results, execution_order
**Returns**: DAGExecutionResult
**Description**: Create DAG execution result.

#### _evaluate_condition
**Parameters**: self, condition, context, task_results
**Returns**: bool
**Description**: Evaluate a Task condition.

        Args:
            condition: Condition expression
            context: Execution context
            task_results: Results from completed tasks

        Returns:
            True if condition is met
        

#### _evaluate_equality_condition
**Parameters**: self, condition, task_results
**Returns**: bool
**Description**: Evaluate equality condition with reduced nesting.

#### get_task_status
**Parameters**: self, task_id
**Returns**: TaskStatus | None
**Description**: Get status of a Task.

        Args:
            task_id: Task ID

        Returns:
            Task status or None if not found
        

#### reset
**Parameters**: self
**Returns**: None
**Description**: Reset all Task statuses.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        Wired DAG Healing - Validates task graphs and removes dead or circular tasks.

        WIRED CAPABILITIES:
        - validate_dag(): Checks for circular dependencies and orphaned nodes.
        - _cleanup_orphaned_tasks(): Removes tasks with no parents/children.
        - reconcile_task_states(): Ensures in-memory task states match the state ledger.
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by DagEngineAgent.

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
        



## Function: create_dag_from_config

**Parameters**: config
**Returns**: DAGEngine
**Description**: Factory function to create a DAG from configuration.



## Function: is_ready

**Parameters**: self, completed_tasks
**Returns**: bool
**Description**: Check if Task is ready to execute.

        Args:
            completed_tasks: Set of completed Task IDs

        Returns:
            True if all dependencies are met
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: __init__

**Parameters**: self, enable_logging
**Returns**: None
**Description**: Initialize DAG engine.

        Args:
            enable_logging: Enable logging of execution
        



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L3 compliance.



## Function: add_task

**Parameters**: self, Task
**Returns**: None
**Description**: Add a Task to the DAG.

        Args:
            Task: Task to add
        



## Function: remove_task

**Parameters**: self, task_id
**Returns**: None
**Description**: Remove a Task from the DAG.

        Args:
            task_id: ID of Task to remove
        



## Function: validate_dag

**Parameters**: self
**Returns**: list[str]
**Description**: Validate the DAG for cycles and Missing dependencies.

        Returns:
            List of validation errors (empty if valid)
        



## Function: topological_sort

**Parameters**: self
**Returns**: list[str]
**Description**: Perform topological sort to determine execution order.

        Returns:
            List of Task IDs in execution order

        Raises:
            ValueError: If DAG has cycles
        



## Function: _log_dag_start

**Parameters**: self, execution_order
**Returns**: None
**Description**: Log DAG execution start.



## Function: _should_execute_task

**Parameters**: self, Task, task_id, completed_tasks, context, task_results, skipped_tasks
**Returns**: bool
**Description**: Check if Task should be executed.



## Function: _create_dag_result

**Parameters**: self, completed_tasks, failed_tasks, skipped_tasks, task_results, execution_order
**Returns**: DAGExecutionResult
**Description**: Create DAG execution result.



## Function: _evaluate_condition

**Parameters**: self, condition, context, task_results
**Returns**: bool
**Description**: Evaluate a Task condition.

        Args:
            condition: Condition expression
            context: Execution context
            task_results: Results from completed tasks

        Returns:
            True if condition is met
        



## Function: _evaluate_equality_condition

**Parameters**: self, condition, task_results
**Returns**: bool
**Description**: Evaluate equality condition with reduced nesting.



## Function: get_task_status

**Parameters**: self, task_id
**Returns**: TaskStatus | None
**Description**: Get status of a Task.

        Args:
            task_id: Task ID

        Returns:
            Task status or None if not found
        



## Function: reset

**Parameters**: self
**Returns**: None
**Description**: Reset all Task statuses.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        Wired DAG Healing - Validates task graphs and removes dead or circular tasks.

        WIRED CAPABILITIES:
        - validate_dag(): Checks for circular dependencies and orphaned nodes.
        - _cleanup_orphaned_tasks(): Removes tasks with no parents/children.
        - reconcile_task_states(): Ensures in-memory task states match the state ledger.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by DagEngineAgent.

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
        



## Function: has_cycle

**Parameters**: task_id
**Returns**: bool
**Description**: DFS to detect cycles.



## Usage Examples

### Class Usage

```python
# Using TaskStatus
taskstatus = TaskStatus()
```

```python
# Using TaskType
tasktype = TaskType()
```

```python
# Using Task
task = Task()
task.is_ready()
task.to_dict()
```

### Function Usage

```python
# Using create_dag_from_config
result = create_dag_from_config(config)
```

```python
# Using is_ready
result = is_ready(completed_tasks)
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:04.263728
**Type**: api_reference
**Quality**: comprehensive
