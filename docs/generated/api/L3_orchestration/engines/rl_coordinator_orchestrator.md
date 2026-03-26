# API Documentation: rl_coordinator_orchestrator

**Target Audience**: developers, api_users

# rl_coordinator_orchestrator API Documentation

**File**: `rl_coordinator_orchestrator.py`
**Classes**: 10
**Functions**: 31

## Classes

- **RLCoordinatorOrchestrator** (inherits from WorkflowCoordinator)
- **TerritoryCoordinator** (inherits from WorkflowCoordinator)
- **MCPCoordinator** (inherits from WorkflowCoordinator)
- **MissionCoordinator** (inherits from WorkflowCoordinator)
- **ModelCoordinator** (inherits from WorkflowCoordinator)
- **HealthCoordinator** (inherits from WorkflowCoordinator)
- **GovernanceCoordinator** (inherits from WorkflowCoordinator)
- **UtilityCoordinator** (inherits from WorkflowCoordinator)
- **CachingCoordinator** (inherits from WorkflowCoordinator)
- **SecurityCoordinator** (inherits from WorkflowCoordinator)

## Functions

- **register_all_coordinators**
- **__init__**
- **get_capabilities** -> list[CoordinatorCapability]
- **can_handle** -> bool
- **__init__**
- **get_capabilities** -> list[CoordinatorCapability]
- **can_handle** -> bool
- **__init__**
- **get_capabilities** -> list[CoordinatorCapability]
- **can_handle** -> bool
- **__init__**
- **get_capabilities** -> list[CoordinatorCapability]
- **can_handle** -> bool
- **__init__**
- **get_capabilities** -> list[CoordinatorCapability]
- **can_handle** -> bool
- **__init__**
- **get_capabilities** -> list[CoordinatorCapability]
- **can_handle** -> bool
- **__init__**
- **get_capabilities** -> list[CoordinatorCapability]
- **can_handle** -> bool
- **__init__**
- **get_capabilities** -> list[CoordinatorCapability]
- **can_handle** -> bool
- **__init__**
- **get_capabilities** -> list[CoordinatorCapability]
- **can_handle** -> bool
- **__init__**
- **get_capabilities** -> list[CoordinatorCapability]
- **can_handle** -> bool


## Class: RLCoordinatorOrchestrator

**Description**: 
    RL Coordinator - Unified RL interface with pluggable strategies.

    Replaces:
    - RLOrchestratorAgent
    - QLearningOrchestratorAgent
    - ActorCriticOrchestratorAgent
    

**Inherits from**: WorkflowCoordinator

### Methods

#### __init__
**Parameters**: self

#### get_capabilities
**Parameters**: self
**Returns**: list[CoordinatorCapability]

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Class: TerritoryCoordinator

**Description**: 
    Territory Coordinator - Unified territory management.

    Replaces:
    - SemanticTerritoryMapperAgent
    - P1CoreSemanticTerritoryMapperAgent
    - TerritoryChangeHandlerAgent
    - TerritoryHealerAgent
    - P1CoreTerritoryHealerAgent
    

**Inherits from**: WorkflowCoordinator

### Methods

#### __init__
**Parameters**: self

#### get_capabilities
**Parameters**: self
**Returns**: list[CoordinatorCapability]

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Class: MCPCoordinator

**Description**: 
    MCP Coordinator - Unified MCP/tool management.

    Replaces:
    - WorkflowMcpManagerAgent
    - MCPRouterSovereign
    - MCPRouter
    - tool_verification
    

**Inherits from**: WorkflowCoordinator

### Methods

#### __init__
**Parameters**: self

#### get_capabilities
**Parameters**: self
**Returns**: list[CoordinatorCapability]

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Class: MissionCoordinator

**Description**: 
    Mission Coordinator - Unified mission lifecycle.

    Replaces:
    - MissionOrchestratorAgent
    - MissionRunnerAgent
    - TestPilotAgent
    - RgResumeOrchestrator
    

**Inherits from**: WorkflowCoordinator

### Methods

#### __init__
**Parameters**: self

#### get_capabilities
**Parameters**: self
**Returns**: list[CoordinatorCapability]

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Class: ModelCoordinator

**Description**: 
    Model Coordinator - Unified model/provider management.

    Replaces:
    - ModelRouterImpl
    - ModelRouter
    - SovereignRagOrchestrator
    

**Inherits from**: WorkflowCoordinator

### Methods

#### __init__
**Parameters**: self

#### get_capabilities
**Parameters**: self
**Returns**: list[CoordinatorCapability]

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Class: HealthCoordinator

**Description**: 
    Health Coordinator - Unified system health monitoring.

    Replaces:
    - AutonomicMonitorImpl
    - ProactiveAuditorAgent
    - DeadlockDetectorAgent
    - MemoryLeakDetectorAgent
    

**Inherits from**: WorkflowCoordinator

### Methods

#### __init__
**Parameters**: self

#### get_capabilities
**Parameters**: self
**Returns**: list[CoordinatorCapability]

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Class: GovernanceCoordinator

**Description**: 
    Governance Coordinator - Unified policy enforcement.

    Replaces:
    - ArchitectureGovernorAgent
    - AgentPermissionManagerAgent
    - AgentRegistryValidatorAgent
    

**Inherits from**: WorkflowCoordinator

### Methods

#### __init__
**Parameters**: self

#### get_capabilities
**Parameters**: self
**Returns**: list[CoordinatorCapability]

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Class: UtilityCoordinator

**Description**: 
    Utility Coordinator - Support functions.

    Replaces:
    - ConversationalRepairAgent
    - ContextCuratorImpl
    - OrchestrationHandshakeAgent
    - ThinkActObserveAgent
    - TelephathyAgent
    

**Inherits from**: WorkflowCoordinator

### Methods

#### __init__
**Parameters**: self

#### get_capabilities
**Parameters**: self
**Returns**: list[CoordinatorCapability]

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Class: CachingCoordinator

**Description**: 
    Caching Coordinator - Optimization through caching.
    

**Inherits from**: WorkflowCoordinator

### Methods

#### __init__
**Parameters**: self

#### get_capabilities
**Parameters**: self
**Returns**: list[CoordinatorCapability]

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Class: SecurityCoordinator

**Description**: 
    Security Coordinator - Hardening and security.
    

**Inherits from**: WorkflowCoordinator

### Methods

#### __init__
**Parameters**: self

#### get_capabilities
**Parameters**: self
**Returns**: list[CoordinatorCapability]

#### can_handle
**Parameters**: self, workflow_type
**Returns**: bool



## Function: register_all_coordinators

**Description**: Register all coordinators with the global registry.



## Function: __init__

**Parameters**: self


## Function: get_capabilities

**Parameters**: self
**Returns**: list[CoordinatorCapability]


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Function: __init__

**Parameters**: self


## Function: get_capabilities

**Parameters**: self
**Returns**: list[CoordinatorCapability]


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Function: __init__

**Parameters**: self


## Function: get_capabilities

**Parameters**: self
**Returns**: list[CoordinatorCapability]


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Function: __init__

**Parameters**: self


## Function: get_capabilities

**Parameters**: self
**Returns**: list[CoordinatorCapability]


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Function: __init__

**Parameters**: self


## Function: get_capabilities

**Parameters**: self
**Returns**: list[CoordinatorCapability]


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Function: __init__

**Parameters**: self


## Function: get_capabilities

**Parameters**: self
**Returns**: list[CoordinatorCapability]


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Function: __init__

**Parameters**: self


## Function: get_capabilities

**Parameters**: self
**Returns**: list[CoordinatorCapability]


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Function: __init__

**Parameters**: self


## Function: get_capabilities

**Parameters**: self
**Returns**: list[CoordinatorCapability]


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Function: __init__

**Parameters**: self


## Function: get_capabilities

**Parameters**: self
**Returns**: list[CoordinatorCapability]


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Function: __init__

**Parameters**: self


## Function: get_capabilities

**Parameters**: self
**Returns**: list[CoordinatorCapability]


## Function: can_handle

**Parameters**: self, workflow_type
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using RLCoordinatorOrchestrator
rlcoordinatororchestrator = RLCoordinatorOrchestrator()
rlcoordinatororchestrator.get_capabilities()
rlcoordinatororchestrator.can_handle()
```

```python
# Using TerritoryCoordinator
territorycoordinator = TerritoryCoordinator()
territorycoordinator.get_capabilities()
territorycoordinator.can_handle()
```

```python
# Using MCPCoordinator
mcpcoordinator = MCPCoordinator()
mcpcoordinator.get_capabilities()
mcpcoordinator.can_handle()
```

### Function Usage

```python
# Using register_all_coordinators
result = register_all_coordinators()
```

```python
# Using __init__
result = __init__()
```

```python
# Using get_capabilities
result = get_capabilities()
```



---
**Generated**: 2026-03-26T09:39:04.216834
**Type**: api_reference
**Quality**: comprehensive
