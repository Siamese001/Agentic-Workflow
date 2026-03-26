# API Documentation: coordinator_capability_orchestrator

**Target Audience**: developers, api_users

# coordinator_capability_orchestrator API Documentation

**File**: `coordinator_capability_orchestrator.py`
**Classes**: 3
**Functions**: 14

## Classes

- **CoordinatorCapability**
- **WorkflowCoordinator** (inherits from ABC)
- **CoordinatorRegistry**

## Functions

- **__init__**
- **get_capabilities** -> list[CoordinatorCapability]
- **can_handle** -> bool
- **get_statistics** -> dict[str, Any]
- **enable** -> None
- **disable** -> None
- **__init__**
- **register** -> None
- **unregister** -> None
- **get** -> WorkflowCoordinator | None
- **get_for_workflow** -> WorkflowCoordinator | None
- **get_all** -> list[WorkflowCoordinator]
- **get_enabled** -> list[WorkflowCoordinator]
- **get_statistics** -> dict[str, Any]


## Class: CoordinatorCapability

**Description**: Describes a coordinator capability.



## Class: WorkflowCoordinator

**Description**: 
    Base coordinator for specialized orchestration domains.

    Each coordinator:
    - Owns a specific domain (RL, Territory, MCP, etc.)
    - Has clear responsibilities
    - Can be registered with UnifiedWorkflowEngine
    - Supports async coordination
    

**Inherits from**: ABC

### Methods

#### __init__
**Parameters**: self, name
**Description**: Initialize coordinator.

#### get_capabilities
**Parameters**: self
**Returns**: list[CoordinatorCapability]
**Description**: 
        Return coordinator capabilities.

        Returns:
            List of capabilities
        

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool
**Description**: 
        Check if coordinator can handle workflow type.

        Args:
            workflow_type: Type of workflow

        Returns:
            True if coordinator can handle
        

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get coordinator statistics.

#### enable
**Parameters**: self
**Returns**: None
**Description**: Enable coordinator.

#### disable
**Parameters**: self
**Returns**: None
**Description**: Disable coordinator.



## Class: CoordinatorRegistry

**Description**: Registry for workflow coordinators.

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize registry.

#### register
**Parameters**: self, coordinator
**Returns**: None
**Description**: Register coordinator.

#### unregister
**Parameters**: self, name
**Returns**: None
**Description**: Unregister coordinator.

#### get
**Parameters**: self, name
**Returns**: WorkflowCoordinator | None
**Description**: Get coordinator by name.

#### get_for_workflow
**Parameters**: self, workflow_type
**Returns**: WorkflowCoordinator | None
**Description**: Get coordinator that can handle workflow type.

#### get_all
**Parameters**: self
**Returns**: list[WorkflowCoordinator]
**Description**: Get all coordinators.

#### get_enabled
**Parameters**: self
**Returns**: list[WorkflowCoordinator]
**Description**: Get enabled coordinators.

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get registry statistics.



## Function: __init__

**Parameters**: self, name
**Description**: Initialize coordinator.



## Function: get_capabilities

**Parameters**: self
**Returns**: list[CoordinatorCapability]
**Description**: 
        Return coordinator capabilities.

        Returns:
            List of capabilities
        



## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool
**Description**: 
        Check if coordinator can handle workflow type.

        Args:
            workflow_type: Type of workflow

        Returns:
            True if coordinator can handle
        



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get coordinator statistics.



## Function: enable

**Parameters**: self
**Returns**: None
**Description**: Enable coordinator.



## Function: disable

**Parameters**: self
**Returns**: None
**Description**: Disable coordinator.



## Function: __init__

**Parameters**: self
**Description**: Initialize registry.



## Function: register

**Parameters**: self, coordinator
**Returns**: None
**Description**: Register coordinator.



## Function: unregister

**Parameters**: self, name
**Returns**: None
**Description**: Unregister coordinator.



## Function: get

**Parameters**: self, name
**Returns**: WorkflowCoordinator | None
**Description**: Get coordinator by name.



## Function: get_for_workflow

**Parameters**: self, workflow_type
**Returns**: WorkflowCoordinator | None
**Description**: Get coordinator that can handle workflow type.



## Function: get_all

**Parameters**: self
**Returns**: list[WorkflowCoordinator]
**Description**: Get all coordinators.



## Function: get_enabled

**Parameters**: self
**Returns**: list[WorkflowCoordinator]
**Description**: Get enabled coordinators.



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get registry statistics.



## Usage Examples

### Class Usage

```python
# Using CoordinatorCapability
coordinatorcapability = CoordinatorCapability()
```

```python
# Using WorkflowCoordinator
workflowcoordinator = WorkflowCoordinator()
workflowcoordinator.get_capabilities()
workflowcoordinator.can_handle()
```

```python
# Using CoordinatorRegistry
coordinatorregistry = CoordinatorRegistry()
coordinatorregistry.register()
coordinatorregistry.unregister()
```

### Function Usage

```python
# Using __init__
result = __init__(name)
```

```python
# Using get_capabilities
result = get_capabilities()
```

```python
# Using can_handle
result = can_handle(workflow_type)
```



---
**Generated**: 2026-03-26T09:39:04.151619
**Type**: api_reference
**Quality**: comprehensive
