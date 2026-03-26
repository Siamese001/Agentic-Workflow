# API Documentation: unified_workflow_config

**Target Audience**: developers, api_users

# unified_workflow_config API Documentation

**File**: `unified_workflow_config.py`
**Classes**: 11
**Functions**: 24

## Classes

- **MissionFocus** (inherits from Enum)
- **Coordinator** (inherits from ABC)
- **ReasoningCoordinator** (inherits from Coordinator)
- **ExecutionCoordinator** (inherits from Coordinator)
- **SafetyCoordinator** (inherits from Coordinator)
- **ValidationCoordinator** (inherits from Coordinator)
- **HealingCoordinator** (inherits from Coordinator)
- **ObservabilityCoordinator** (inherits from Coordinator)
- **OptimizationCoordinator** (inherits from Coordinator)
- **DefaultCoordinator** (inherits from Coordinator)
- **UnifiedWorkflowEngine**

## Functions

- **_get_assert_activation_allowed**
- **__init__**
- **execute** -> dict[str, Any]
- **record_execution**
- **__init__**
- **execute** -> dict[str, Any]
- **__init__**
- **execute** -> dict[str, Any]
- **__init__**
- **execute** -> dict[str, Any]
- **__init__**
- **execute** -> dict[str, Any]
- **__init__**
- **execute** -> dict[str, Any]
- **__init__**
- **execute** -> dict[str, Any]
- **__init__**
- **execute** -> dict[str, Any]
- **__init__**
- **execute** -> dict[str, Any]
- **__init__**
- **orchestrate** -> dict[str, Any]
- **get_statistics** -> dict[str, Any]
- **register_coordinator** -> None


## Class: MissionFocus

**Description**: Mission focus types for coordinator selection.

**Inherits from**: Enum



## Class: Coordinator

**Description**: Base coordinator interface - specialized orchestration strategy.

**Inherits from**: ABC

### Methods

#### __init__
**Parameters**: self, name
**Description**: Initialize coordinator.

#### execute
**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: 
        Execute mission using specialized coordination strategy.

        Returns:
            {
                "status": "success" | "failure",
                "result": Any,
                "coordinator": str,
                "metadata": Dict
            }
        

#### record_execution
**Parameters**: self, success
**Description**: Record mission execution.



## Class: ReasoningCoordinator

**Description**: Coordinates reasoning-focused missions (deep thought, analysis, planning).

**Inherits from**: Coordinator

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize reasoning coordinator.

#### execute
**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute reasoning mission.



## Class: ExecutionCoordinator

**Description**: Coordinates execution-focused missions (tool calls, actions, operations).

**Inherits from**: Coordinator

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize execution coordinator.

#### execute
**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute execution mission.



## Class: SafetyCoordinator

**Description**: Coordinates safety-focused missions (validation, enforcement, guardrails).

**Inherits from**: Coordinator

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize safety coordinator.

#### execute
**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute safety mission.



## Class: ValidationCoordinator

**Description**: Coordinates validation-focused missions (compliance, schema, integrity).

**Inherits from**: Coordinator

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize validation coordinator.

#### execute
**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute validation mission.



## Class: HealingCoordinator

**Description**: Coordinates healing-focused missions (repair, recovery, restoration).

**Inherits from**: Coordinator

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize healing coordinator.

#### execute
**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute healing mission.



## Class: ObservabilityCoordinator

**Description**: Coordinates observability-focused missions (monitoring, tracing, metrics).

**Inherits from**: Coordinator

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize observability coordinator.

#### execute
**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute observability mission.



## Class: OptimizationCoordinator

**Description**: Coordinates optimization-focused missions (performance, efficiency, tuning).

**Inherits from**: Coordinator

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize optimization coordinator.

#### execute
**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute optimization mission.



## Class: DefaultCoordinator

**Description**: Default coordinator for unspecified mission focuses.

**Inherits from**: Coordinator

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize default coordinator.

#### execute
**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute default mission.



## Class: UnifiedWorkflowEngine

**Description**: 
    Unified workflow engine - canonical orchestration entrypoint.

    Consolidates 51+ orchestrators into single engine with 19 specialized coordinators.
    Replaces scattered orchestration logic with single dispatch point.
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize unified workflow engine with all coordinators.

#### orchestrate
**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: 
        Orchestrate mission using appropriate coordinator.

        All execution routes through the P5.1 capability chokepoint.

        Args:
            mission: Mission dict with 'focus' key and mission-specific data
            capability_token: Required CapabilityTokenArtifact (FAIL-CLOSED if None).
            semantic_clock: Required SemanticClockSnapshot for chokepoint decisions.

        Returns:
            Orchestration result from selected coordinator

        Raises:
            PermissionError: If token is missing/invalid (FAIL-CLOSED).
            ValueError: If semantic_clock is missing.
        

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get orchestration statistics.

#### register_coordinator
**Parameters**: self, focus, coordinator
**Returns**: None
**Description**: Register custom coordinator for mission focus.



## Function: _get_assert_activation_allowed

**Description**: Lazy load assert_activation_allowed to avoid upward import.



## Function: __init__

**Parameters**: self, name
**Description**: Initialize coordinator.



## Function: execute

**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: 
        Execute mission using specialized coordination strategy.

        Returns:
            {
                "status": "success" | "failure",
                "result": Any,
                "coordinator": str,
                "metadata": Dict
            }
        



## Function: record_execution

**Parameters**: self, success
**Description**: Record mission execution.



## Function: __init__

**Parameters**: self
**Description**: Initialize reasoning coordinator.



## Function: execute

**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute reasoning mission.



## Function: __init__

**Parameters**: self
**Description**: Initialize execution coordinator.



## Function: execute

**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute execution mission.



## Function: __init__

**Parameters**: self
**Description**: Initialize safety coordinator.



## Function: execute

**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute safety mission.



## Function: __init__

**Parameters**: self
**Description**: Initialize validation coordinator.



## Function: execute

**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute validation mission.



## Function: __init__

**Parameters**: self
**Description**: Initialize healing coordinator.



## Function: execute

**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute healing mission.



## Function: __init__

**Parameters**: self
**Description**: Initialize observability coordinator.



## Function: execute

**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute observability mission.



## Function: __init__

**Parameters**: self
**Description**: Initialize optimization coordinator.



## Function: execute

**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute optimization mission.



## Function: __init__

**Parameters**: self
**Description**: Initialize default coordinator.



## Function: execute

**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: Execute default mission.



## Function: __init__

**Parameters**: self
**Description**: Initialize unified workflow engine with all coordinators.



## Function: orchestrate

**Parameters**: self, mission
**Returns**: dict[str, Any]
**Description**: 
        Orchestrate mission using appropriate coordinator.

        All execution routes through the P5.1 capability chokepoint.

        Args:
            mission: Mission dict with 'focus' key and mission-specific data
            capability_token: Required CapabilityTokenArtifact (FAIL-CLOSED if None).
            semantic_clock: Required SemanticClockSnapshot for chokepoint decisions.

        Returns:
            Orchestration result from selected coordinator

        Raises:
            PermissionError: If token is missing/invalid (FAIL-CLOSED).
            ValueError: If semantic_clock is missing.
        



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get orchestration statistics.



## Function: register_coordinator

**Parameters**: self, focus, coordinator
**Returns**: None
**Description**: Register custom coordinator for mission focus.



## Usage Examples

### Class Usage

```python
# Using MissionFocus
missionfocus = MissionFocus()
```

```python
# Using Coordinator
coordinator = Coordinator()
coordinator.execute()
coordinator.record_execution()
```

```python
# Using ReasoningCoordinator
reasoningcoordinator = ReasoningCoordinator()
reasoningcoordinator.execute()
```

### Function Usage

```python
# Using _get_assert_activation_allowed
result = _get_assert_activation_allowed()
```

```python
# Using __init__
result = __init__(name)
```

```python
# Using execute
result = execute(mission)
```



---
**Generated**: 2026-03-26T09:39:03.642243
**Type**: api_reference
**Quality**: comprehensive
