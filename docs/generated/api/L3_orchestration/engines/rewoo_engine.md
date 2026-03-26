# API Documentation: rewoo_engine

**Target Audience**: developers, api_users

# rewoo_engine API Documentation

**File**: `rewoo_engine.py`
**Classes**: 4
**Functions**: 6

## Classes

- **RewooPlanner**
- **RewooSolver**
- **RewooWorker**
- **RewooEngine**

## Functions

- **__init__** -> None
- **__init__** -> None
- **register_tool** -> None
- **_resolve_references** -> dict[str, Any]
- **update** -> None
- **__init__** -> None


## Class: RewooPlanner

**Description**: Generates a full task list with reasoning annotations before any execution.

    The planner_fn receives the goal and returns a list of dicts, each with:
      - task_id: str
      - description: str
      - reasoning: str   (why this task is needed)
      - tool_name: str
      - tool_input: dict
      - depends_on: list[str]  (task_ids that must complete first)
    

### Methods

#### __init__
**Parameters**: self, planner_fn
**Returns**: None



## Class: RewooSolver

**Description**: Executes tasks from the task list using registered tools.

    Tools are registered as callables: async fn(tool_input: dict) -> Any
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### register_tool
**Parameters**: self, name, fn
**Returns**: None

#### _resolve_references
**Parameters**: self, tool_input, results
**Returns**: dict[str, Any]
**Description**: Replace '#task_id' placeholders in string values with prior results.



## Class: RewooWorker

**Description**: Updates RewooContext with task results after each Solver execution.

### Methods

#### update
**Parameters**: self, context, task
**Returns**: None
**Description**: Persist task result into context for downstream tasks.



## Class: RewooEngine

**Description**: Orchestrates the full Rewoo pattern: Planner → Solver → Worker loop.

    Usage::

        engine = RewooEngine(planner, solver, worker, max_iterations=20)
        context = await engine.run(goal="Summarise and cite 3 sources", context={})
        print(context.final_answer)
    

### Methods

#### __init__
**Parameters**: self, planner, solver, worker, max_iterations, stop_on_first_failure
**Returns**: None



## Function: __init__

**Parameters**: self, planner_fn
**Returns**: None


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: register_tool

**Parameters**: self, name, fn
**Returns**: None


## Function: _resolve_references

**Parameters**: self, tool_input, results
**Returns**: dict[str, Any]
**Description**: Replace '#task_id' placeholders in string values with prior results.



## Function: update

**Parameters**: self, context, task
**Returns**: None
**Description**: Persist task result into context for downstream tasks.



## Function: __init__

**Parameters**: self, planner, solver, worker, max_iterations, stop_on_first_failure
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using RewooPlanner
rewooplanner = RewooPlanner()
```

```python
# Using RewooSolver
rewoosolver = RewooSolver()
rewoosolver.register_tool()
```

```python
# Using RewooWorker
rewooworker = RewooWorker()
rewooworker.update()
```

### Function Usage

```python
# Using __init__
result = __init__(planner_fn)
```

```python
# Using __init__
result = __init__()
```

```python
# Using register_tool
result = register_tool(name, fn)
```



---
**Generated**: 2026-03-26T09:39:04.210119
**Type**: api_reference
**Quality**: comprehensive
