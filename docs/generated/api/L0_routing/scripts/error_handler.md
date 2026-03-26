# API Documentation: error_handler

**Target Audience**: developers, api_users

# error_handler API Documentation

**File**: `error_handler.py`
**Classes**: 3
**Functions**: 6

## Classes

- **WorkflowMetrics**
- **ErrorHandler**
- **UnifiedWorkflowEngine**

## Functions

- **__init__**
- **__init__**
- **register_coordinator** -> None
- **register_strategy** -> None
- **get_statistics** -> dict[str, Any]
- **get_active_workflows** -> list[str]


## Class: WorkflowMetrics

**Description**: Metrics for workflow execution.



## Class: ErrorHandler

**Description**: Unified error handling for workflows.

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize error handler.



## Class: UnifiedWorkflowEngine

**Description**: 
    Unified Workflow Engine - Single entry point for all orchestration.

    Replaces 8 core engines with:
    - Pluggable execution strategies (DAG, state machine, event-driven, reactive)
    - Unified error handling and recovery
    - Centralized logging and metrics
    - Coordinator registry for specialized domains
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize unified workflow engine.

#### register_coordinator
**Parameters**: self, coordinator
**Returns**: None
**Description**: Register coordinator with engine.

#### register_strategy
**Parameters**: self, name, strategy
**Returns**: None
**Description**: Register execution strategy.

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get engine statistics.

#### get_active_workflows
**Parameters**: self
**Returns**: list[str]
**Description**: Get list of active workflow IDs.



## Function: __init__

**Parameters**: self
**Description**: Initialize error handler.



## Function: __init__

**Parameters**: self
**Description**: Initialize unified workflow engine.



## Function: register_coordinator

**Parameters**: self, coordinator
**Returns**: None
**Description**: Register coordinator with engine.



## Function: register_strategy

**Parameters**: self, name, strategy
**Returns**: None
**Description**: Register execution strategy.



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get engine statistics.



## Function: get_active_workflows

**Parameters**: self
**Returns**: list[str]
**Description**: Get list of active workflow IDs.



## Usage Examples

### Class Usage

```python
# Using WorkflowMetrics
workflowmetrics = WorkflowMetrics()
```

```python
# Using ErrorHandler
errorhandler = ErrorHandler()
```

```python
# Using UnifiedWorkflowEngine
unifiedworkflowengine = UnifiedWorkflowEngine()
unifiedworkflowengine.register_coordinator()
unifiedworkflowengine.register_strategy()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using __init__
result = __init__()
```

```python
# Using register_coordinator
result = register_coordinator(coordinator)
```



---
**Generated**: 2026-03-26T09:39:02.875137
**Type**: api_reference
**Quality**: comprehensive
