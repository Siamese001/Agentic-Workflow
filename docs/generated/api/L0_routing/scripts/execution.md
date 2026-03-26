# API Documentation: execution

**Target Audience**: developers, api_users

# execution API Documentation

**File**: `execution.py`
**Classes**: 9
**Functions**: 15

## Classes

- **ExecutionStatus** (inherits from Enum)
- **WorkflowContext**
- **WorkflowResult**
- **WorkflowStep**
- **ExecutionStrategy** (inherits from ABC)
- **DAGStrategy** (inherits from ExecutionStrategy)
- **StateMachineStrategy** (inherits from ExecutionStrategy)
- **EventDrivenStrategy** (inherits from ExecutionStrategy)
- **ReactiveStrategy** (inherits from ExecutionStrategy)

## Functions

- **get_strategy** -> ExecutionStrategy
- **get_name** -> str
- **can_handle** -> bool
- **__init__**
- **get_name** -> str
- **can_handle** -> bool
- **__init__**
- **get_name** -> str
- **can_handle** -> bool
- **__init__**
- **get_name** -> str
- **can_handle** -> bool
- **__init__**
- **get_name** -> str
- **can_handle** -> bool


## Class: ExecutionStatus

**Description**: Workflow execution status.

**Inherits from**: Enum



## Class: WorkflowContext

**Description**: Context for workflow execution.



## Class: WorkflowResult

**Description**: Result of workflow execution.



## Class: WorkflowStep

**Description**: Single step in workflow execution.



## Class: ExecutionStrategy

**Description**: Base execution strategy interface.

**Inherits from**: ABC

### Methods

#### get_name
**Parameters**: self
**Returns**: str
**Description**: Return strategy name.

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool
**Description**: Check if strategy can handle workflow type.



## Class: DAGStrategy

**Description**: DAG-based execution strategy.

**Inherits from**: ExecutionStrategy

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize DAG strategy.

#### get_name
**Parameters**: self
**Returns**: str

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Class: StateMachineStrategy

**Description**: State machine-based execution strategy.

**Inherits from**: ExecutionStrategy

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize state machine strategy.

#### get_name
**Parameters**: self
**Returns**: str

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Class: EventDrivenStrategy

**Description**: Event-driven execution strategy.

**Inherits from**: ExecutionStrategy

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize event-driven strategy.

#### get_name
**Parameters**: self
**Returns**: str

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Class: ReactiveStrategy

**Description**: Reactive stream-based execution strategy.

**Inherits from**: ExecutionStrategy

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize reactive strategy.

#### get_name
**Parameters**: self
**Returns**: str

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Function: get_strategy

**Parameters**: workflow_type
**Returns**: ExecutionStrategy
**Description**: Get appropriate strategy for workflow type.



## Function: get_name

**Parameters**: self
**Returns**: str
**Description**: Return strategy name.



## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool
**Description**: Check if strategy can handle workflow type.



## Function: __init__

**Parameters**: self
**Description**: Initialize DAG strategy.



## Function: get_name

**Parameters**: self
**Returns**: str


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Function: __init__

**Parameters**: self
**Description**: Initialize state machine strategy.



## Function: get_name

**Parameters**: self
**Returns**: str


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Function: __init__

**Parameters**: self
**Description**: Initialize event-driven strategy.



## Function: get_name

**Parameters**: self
**Returns**: str


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Function: __init__

**Parameters**: self
**Description**: Initialize reactive strategy.



## Function: get_name

**Parameters**: self
**Returns**: str


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using ExecutionStatus
executionstatus = ExecutionStatus()
```

```python
# Using WorkflowContext
workflowcontext = WorkflowContext()
```

```python
# Using WorkflowResult
workflowresult = WorkflowResult()
```

### Function Usage

```python
# Using get_strategy
result = get_strategy(workflow_type)
```

```python
# Using get_name
result = get_name()
```

```python
# Using can_handle
result = can_handle(workflow_type)
```



---
**Generated**: 2026-03-26T09:39:03.090198
**Type**: api_reference
**Quality**: comprehensive
