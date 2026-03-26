# API Documentation: rewoo_types

**Target Audience**: developers, api_users

# rewoo_types API Documentation

**File**: `rewoo_types.py`
**Classes**: 4
**Functions**: 2

## Classes

- **RewooTaskStatus** (inherits from Enum)
- **RewooTask**
- **RewooTaskList**
- **RewooContext**

## Functions

- **get_task** -> RewooTask | None
- **ready_tasks** -> list[RewooTask]


## Class: RewooTaskStatus

**Inherits from**: Enum



## Class: RewooTask

**Description**: A single task in the Rewoo task list.



## Class: RewooTaskList

**Description**: Ordered list of tasks produced by the Planner.

### Methods

#### get_task
**Parameters**: self, task_id
**Returns**: RewooTask | None

#### ready_tasks
**Parameters**: self
**Returns**: list[RewooTask]
**Description**: Return tasks whose dependencies are all completed.



## Class: RewooContext

**Description**: Accumulated context across Planner → Solver → Worker passes.



## Function: get_task

**Parameters**: self, task_id
**Returns**: RewooTask | None


## Function: ready_tasks

**Parameters**: self
**Returns**: list[RewooTask]
**Description**: Return tasks whose dependencies are all completed.



## Usage Examples

### Class Usage

```python
# Using RewooTaskStatus
rewootaskstatus = RewooTaskStatus()
```

```python
# Using RewooTask
rewootask = RewooTask()
```

```python
# Using RewooTaskList
rewootasklist = RewooTaskList()
rewootasklist.get_task()
rewootasklist.ready_tasks()
```

### Function Usage

```python
# Using get_task
result = get_task(task_id)
```

```python
# Using ready_tasks
result = ready_tasks()
```



---
**Generated**: 2026-03-26T09:39:04.410999
**Type**: api_reference
**Quality**: comprehensive
