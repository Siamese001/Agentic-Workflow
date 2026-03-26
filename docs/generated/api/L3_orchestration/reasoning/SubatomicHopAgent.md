# API Documentation: SubatomicHopAgent

**Target Audience**: developers, api_users

# SubatomicHopAgent API Documentation

**File**: `SubatomicHopAgent.py`
**Classes**: 2
**Functions**: 10

## Classes

- **SovereignDependencyError** (inherits from Exception)
- **SubatomicHopAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__** -> None
- **_run_self_tests** -> bool
- **_ensure_dep** -> Any
- **_v15_build_operation_manifest** -> SurgicalManifest | None
- **_assess_task_risk** -> str
- **_handle_error** -> None
- **heal_repository** -> dict[str, int]
- **heal**
- **_noop_heal**
- **_state_hash**


## Class: SovereignDependencyError

**Description**: Raised when a required dependency is not injected into a Sovereign component.

**Inherits from**: Exception



## Class: SubatomicHopAgent

**Description**: 
    Sovereign SubatomicHop with Dependency Injection.

    This is a 'Pure Engine.' It has no knowledge of higher layers (L3-L5)
    at the import level. All required logic is injected at runtime.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, role, config, storage, genealogy, PiiVault, CostGovernor, overseer, membrane, airlock, SupremeCourt, mcp_manager, sandbox, StructuredEngineAgent, gatekeeper, telemetry
**Returns**: None
**Description**: Initialize SubatomicHop with injected dependencies.

        Args:
            role: Agent role identifier
            config: configuration dictionary
            storage: LocalDiskAdapter instance (injected)
            genealogy: GenealogyRegistry instance (injected)
            PiiVault: PIIVault instance (injected)
            CostGovernor: CostGovernor instance (injected)
            overseer: ConstitutionalOverseer instance (injected)
            membrane: InputMembrane instance (injected)
            airlock: AirlockProtocol instance (injected)
            SupremeCourt: SupremeCourt instance (injected)
            mcp_manager: MCPConnectionManager instance (injected)
            sandbox: DockerSandbox instance (injected)
            StructuredEngineAgent: StructuredEngineAgent instance (injected)
            gatekeeper: semantic_gatekeeper instance (injected)
            telemetry: TelemetryRecorder instance (injected)

        Raises:
            SovereignDependencyError: If required dependencies are Missing
        

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L3 compliance.

#### _ensure_dep
**Parameters**: self, dep, name
**Returns**: Any
**Description**: Validate that a required dependency was injected.

        Args:
            dep: The dependency instance
            name: Human-readable name for error messages

        Returns:
            The validated dependency

        Raises:
            SovereignDependencyError: If dependency is None
        

#### _v15_build_operation_manifest
**Parameters**: self, operation, target_layer
**Returns**: SurgicalManifest | None
**Description**: §8.1b — Construct SurgicalManifest for hop-level operation (AGGREGATE).

#### _assess_task_risk
**Parameters**: self, Task
**Returns**: str
**Description**: Assess the risk level of a Task.

#### _handle_error
**Parameters**: self, trace_id, error
**Returns**: None
**Description**: Handle execution errors with unified telemetry.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 orchestration agent - operational only.

#### heal
**Parameters**: self, violation



## Function: __init__

**Parameters**: self, role, config, storage, genealogy, PiiVault, CostGovernor, overseer, membrane, airlock, SupremeCourt, mcp_manager, sandbox, StructuredEngineAgent, gatekeeper, telemetry
**Returns**: None
**Description**: Initialize SubatomicHop with injected dependencies.

        Args:
            role: Agent role identifier
            config: configuration dictionary
            storage: LocalDiskAdapter instance (injected)
            genealogy: GenealogyRegistry instance (injected)
            PiiVault: PIIVault instance (injected)
            CostGovernor: CostGovernor instance (injected)
            overseer: ConstitutionalOverseer instance (injected)
            membrane: InputMembrane instance (injected)
            airlock: AirlockProtocol instance (injected)
            SupremeCourt: SupremeCourt instance (injected)
            mcp_manager: MCPConnectionManager instance (injected)
            sandbox: DockerSandbox instance (injected)
            StructuredEngineAgent: StructuredEngineAgent instance (injected)
            gatekeeper: semantic_gatekeeper instance (injected)
            telemetry: TelemetryRecorder instance (injected)

        Raises:
            SovereignDependencyError: If required dependencies are Missing
        



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L3 compliance.



## Function: _ensure_dep

**Parameters**: self, dep, name
**Returns**: Any
**Description**: Validate that a required dependency was injected.

        Args:
            dep: The dependency instance
            name: Human-readable name for error messages

        Returns:
            The validated dependency

        Raises:
            SovereignDependencyError: If dependency is None
        



## Function: _v15_build_operation_manifest

**Parameters**: self, operation, target_layer
**Returns**: SurgicalManifest | None
**Description**: §8.1b — Construct SurgicalManifest for hop-level operation (AGGREGATE).



## Function: _assess_task_risk

**Parameters**: self, Task
**Returns**: str
**Description**: Assess the risk level of a Task.



## Function: _handle_error

**Parameters**: self, trace_id, error
**Returns**: None
**Description**: Handle execution errors with unified telemetry.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 orchestration agent - operational only.



## Function: heal

**Parameters**: self, violation


## Function: _noop_heal

**Parameters**: m


## Function: _state_hash



## Usage Examples

### Class Usage

```python
# Using SovereignDependencyError
sovereigndependencyerror = SovereignDependencyError()
```

```python
# Using SubatomicHopAgent
subatomichopagent = SubatomicHopAgent()
subatomichopagent.heal_repository()
subatomichopagent.heal()
```

### Function Usage

```python
# Using __init__
result = __init__(role, config)
```

```python
# Using _run_self_tests
result = _run_self_tests()
```

```python
# Using _ensure_dep
result = _ensure_dep(dep, name)
```



---
**Generated**: 2026-03-26T09:39:04.319386
**Type**: api_reference
**Quality**: comprehensive
