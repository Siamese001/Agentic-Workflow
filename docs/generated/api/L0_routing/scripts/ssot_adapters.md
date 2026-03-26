# API Documentation: ssot_adapters

**Target Audience**: developers, api_users

# ssot_adapters API Documentation

**File**: `ssot_adapters.py`
**Classes**: 9
**Functions**: 48

## Classes

- **ReconcilerAdapter**
- **LocationAdapter**
- **FileClassAdapter**
- **HierarchyAdapter**
- **ArchGovAdapter**
- **GravityAdapter**
- **SysArchAdapter**
- **ObsProbeAdapter**
- **RootHygieneAdapter**

## Functions

- **_to_result** -> SubphaseResult
- **_noop** -> SubphaseResult
- **build_adapters** -> dict[str, Any]
- **__init__** -> None
- **pre_commit** -> SubphaseResult
- **validate** -> SubphaseResult
- **execute** -> SubphaseResult
- **heal** -> SubphaseResult
- **__init__** -> None
- **pre_commit** -> SubphaseResult
- **validate** -> SubphaseResult
- **execute** -> SubphaseResult
- **heal** -> SubphaseResult
- **__init__** -> None
- **pre_commit** -> SubphaseResult
- **validate** -> SubphaseResult
- **execute** -> SubphaseResult
- **heal** -> SubphaseResult
- **__init__** -> None
- **pre_commit** -> SubphaseResult
- **validate** -> SubphaseResult
- **execute** -> SubphaseResult
- **heal** -> SubphaseResult
- **__init__** -> None
- **pre_commit** -> SubphaseResult
- **validate** -> SubphaseResult
- **execute** -> SubphaseResult
- **heal** -> SubphaseResult
- **__init__** -> None
- **pre_commit** -> SubphaseResult
- **validate** -> SubphaseResult
- **execute** -> SubphaseResult
- **heal** -> SubphaseResult
- **__init__** -> None
- **pre_commit** -> SubphaseResult
- **validate** -> SubphaseResult
- **execute** -> SubphaseResult
- **heal** -> SubphaseResult
- **__init__** -> None
- **pre_commit** -> SubphaseResult
- **validate** -> SubphaseResult
- **execute** -> SubphaseResult
- **heal** -> SubphaseResult
- **__init__** -> None
- **pre_commit** -> SubphaseResult
- **validate** -> SubphaseResult
- **execute** -> SubphaseResult
- **heal** -> SubphaseResult


## Class: ReconcilerAdapter

**Description**: Adapter for FilesystemSSOTReconcilerAgent (roster key: 'reconciler').

### Methods

#### __init__
**Parameters**: self, agent
**Returns**: None

#### pre_commit
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### validate
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### execute
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### heal
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult



## Class: LocationAdapter

**Description**: Adapter for LocationAgent (roster key: 'location').

### Methods

#### __init__
**Parameters**: self, agent
**Returns**: None

#### pre_commit
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### validate
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### execute
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### heal
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult



## Class: FileClassAdapter

**Description**: Adapter for FileClassificationAgent (roster key: 'file_classification').

### Methods

#### __init__
**Parameters**: self, agent
**Returns**: None

#### pre_commit
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### validate
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### execute
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### heal
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult



## Class: HierarchyAdapter

**Description**: Adapter for HierarchyAgent (roster key: 'hierarchy').

### Methods

#### __init__
**Parameters**: self, agent
**Returns**: None

#### pre_commit
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### validate
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### execute
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### heal
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult



## Class: ArchGovAdapter

**Description**: Adapter for ArchitectureGovernorAgent (roster key: 'arch_governor').

    Intermediate state: _plan is set by execute(), consumed by heal(), then
    reset to None. This is deterministic because execute always precedes heal
    in the PIPELINE_SUBPHASES ordering enforced by run_pipeline.
    

### Methods

#### __init__
**Parameters**: self, agent
**Returns**: None

#### pre_commit
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### validate
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### execute
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### heal
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult



## Class: GravityAdapter

**Description**: Adapter for GravityLeakRepairAgent (roster key: 'gravity_repair').

### Methods

#### __init__
**Parameters**: self, agent
**Returns**: None

#### pre_commit
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### validate
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### execute
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### heal
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult



## Class: SysArchAdapter

**Description**: Adapter for SystemArchitectAgent (roster key: 'system_architect').

    SystemArchitectAgent explicitly returns manual_required for mutations.
    execute and heal are no-ops by design.
    

### Methods

#### __init__
**Parameters**: self, agent
**Returns**: None

#### pre_commit
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### validate
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### execute
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### heal
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult



## Class: ObsProbeAdapter

**Description**: Adapter for ObservabilityProbeExecutorAgent (roster key: 'observability_probe').

    Observability is read-only; execute and heal are no-ops.
    

### Methods

#### __init__
**Parameters**: self, agent
**Returns**: None

#### pre_commit
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### validate
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### execute
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### heal
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult



## Class: RootHygieneAdapter

**Description**: Adapter for RootHygieneAgent (roster key: 'root_hygiene').

    Previously dead code — violations were read from state that was never
    written. Now invoked directly via this adapter.
    

### Methods

#### __init__
**Parameters**: self, agent
**Returns**: None

#### pre_commit
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### validate
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### execute
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult

#### heal
**Parameters**: self, territory, ctx
**Returns**: SubphaseResult



## Function: _to_result

**Parameters**: raw
**Returns**: SubphaseResult
**Description**: Normalise an agent return dict into SubphaseResult.

    Agents return a variety of dict shapes. We extract violations where
    possible; anything else maps to an empty-violations clean result.
    



## Function: _noop

**Returns**: SubphaseResult
**Description**: Return a clean no-op result (for agents that don't support a subphase).



## Function: build_adapters

**Parameters**: agents, project_root
**Returns**: dict[str, Any]
**Description**: Instantiate agents and wrap each in the appropriate adapter.

    Args:
        agents:       Dict mapping roster key -> agent class (as in _legacy_main).
        project_root: Passed to agent constructors.

    Returns:
        Dict mapping roster key -> adapter instance implementing L2AgentProtocol.
    



## Function: __init__

**Parameters**: self, agent
**Returns**: None


## Function: pre_commit

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: validate

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: execute

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: heal

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: __init__

**Parameters**: self, agent
**Returns**: None


## Function: pre_commit

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: validate

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: execute

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: heal

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: __init__

**Parameters**: self, agent
**Returns**: None


## Function: pre_commit

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: validate

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: execute

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: heal

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: __init__

**Parameters**: self, agent
**Returns**: None


## Function: pre_commit

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: validate

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: execute

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: heal

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: __init__

**Parameters**: self, agent
**Returns**: None


## Function: pre_commit

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: validate

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: execute

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: heal

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: __init__

**Parameters**: self, agent
**Returns**: None


## Function: pre_commit

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: validate

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: execute

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: heal

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: __init__

**Parameters**: self, agent
**Returns**: None


## Function: pre_commit

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: validate

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: execute

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: heal

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: __init__

**Parameters**: self, agent
**Returns**: None


## Function: pre_commit

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: validate

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: execute

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: heal

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: __init__

**Parameters**: self, agent
**Returns**: None


## Function: pre_commit

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: validate

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: execute

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Function: heal

**Parameters**: self, territory, ctx
**Returns**: SubphaseResult


## Usage Examples

### Class Usage

```python
# Using ReconcilerAdapter
reconcileradapter = ReconcilerAdapter()
reconcileradapter.pre_commit()
reconcileradapter.validate()
```

```python
# Using LocationAdapter
locationadapter = LocationAdapter()
locationadapter.pre_commit()
locationadapter.validate()
```

```python
# Using FileClassAdapter
fileclassadapter = FileClassAdapter()
fileclassadapter.pre_commit()
fileclassadapter.validate()
```

### Function Usage

```python
# Using _to_result
result = _to_result(raw)
```

```python
# Using _noop
result = _noop()
```

```python
# Using build_adapters
result = build_adapters(agents, project_root)
```



---
**Generated**: 2026-03-26T09:39:03.266794
**Type**: api_reference
**Quality**: comprehensive
