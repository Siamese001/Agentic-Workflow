# API Documentation: work_coordination_bundle

**Target Audience**: developers, api_users

# work_coordination_bundle API Documentation

**File**: `work_coordination_bundle.py`
**Classes**: 4
**Functions**: 18

## Classes

- **BundlePhase** (inherits from str, Enum)
- **AgentCompletion**
- **BundleSnapshot**
- **WorkCoordinationBundle**

## Functions

- **get_coordination_bundle** -> WorkCoordinationBundle
- **release_coordination_bundle** -> None
- **active_bundle_ids** -> list[str]
- **__init__** -> None
- **create** -> WorkCoordinationBundle
- **bundle_id** -> str
- **phase** -> BundlePhase
- **contract_hash** -> str
- **_trace_id** -> str
- **stamp_work_contract** -> str
- **observe_runtime_state** -> None
- **read_shared** -> Any
- **record_agent_completion** -> AgentCompletion
- **snapshot** -> BundleSnapshot
- **complete** -> BundleSnapshot
- **completion_count** -> int
- **snapshot_history** -> list[BundleSnapshot]
- **completions** -> list[AgentCompletion]


## Class: BundlePhase

**Description**: Lifecycle phase of a WorkCoordinationBundle.

**Inherits from**: str, Enum



## Class: AgentCompletion

**Description**: Immutable record of a single agent's completion within the bundle.



## Class: BundleSnapshot

**Description**: Point-in-time snapshot of bundle coordination state.



## Class: WorkCoordinationBundle

**Description**: Shared coordination case file for a multi-agent orchestration run.

    All agent dispatches and completions are recorded here; the bundle
    acts as the single source of coordination truth for L3.

    Usage::

        bundle = WorkCoordinationBundle.create("campaign-research-001")
        bundle.stamp_work_contract("Generate campaign brief")

        # agent starts
        bundle.observe_runtime_state("rag_results", rag_data)

        # agent completes
        bundle.record_agent_completion("ResearchAgent", "fetch_sources", result)
        snap = bundle.snapshot()
    

### Methods

#### __init__
**Parameters**: self, bundle_id, task_description
**Returns**: None

#### create
**Parameters**: cls, bundle_id, task_description
**Returns**: WorkCoordinationBundle
**Description**: Factory: create and activate a bundle, stamping its work contract.

#### bundle_id
**Parameters**: self
**Returns**: str

#### phase
**Parameters**: self
**Returns**: BundlePhase

#### contract_hash
**Parameters**: self
**Returns**: str

#### _trace_id
**Parameters**: self
**Returns**: str

#### stamp_work_contract
**Parameters**: self, task_description
**Returns**: str
**Description**: Stamp an immutable work contract for this orchestration run.

        Emits ``stamps_work_contract`` ADG edge. Returns the contract hash.
        

#### observe_runtime_state
**Parameters**: self, key, value
**Returns**: None
**Description**: Observe and store a runtime state value.

        Emits ``observes_runtime_state`` + ``reads_runtime_state`` ADG edges.
        

#### read_shared
**Parameters**: self, key, default
**Returns**: Any
**Description**: Read a value from the shared coordination state.

#### record_agent_completion
**Parameters**: self, agent_name, task_key, result, success
**Returns**: AgentCompletion
**Description**: Record that an agent has completed its assigned task.

        Triggers an automatic snapshot.
        

#### snapshot
**Parameters**: self
**Returns**: BundleSnapshot
**Description**: Capture a point-in-time snapshot of the coordination state.

        Emits ``snapshots_state`` ADG edge.
        

#### complete
**Parameters**: self, success
**Returns**: BundleSnapshot
**Description**: Mark the bundle as completed and take a final snapshot.

#### completion_count
**Parameters**: self
**Returns**: int

#### snapshot_history
**Parameters**: self
**Returns**: list[BundleSnapshot]

#### completions
**Parameters**: self
**Returns**: list[AgentCompletion]



## Function: get_coordination_bundle

**Parameters**: bundle_id, task_description
**Returns**: WorkCoordinationBundle
**Description**: Get or create a :class:`WorkCoordinationBundle` for ``bundle_id``.



## Function: release_coordination_bundle

**Parameters**: bundle_id
**Returns**: None
**Description**: Release the bundle for ``bundle_id`` after the run ends.



## Function: active_bundle_ids

**Returns**: list[str]


## Function: __init__

**Parameters**: self, bundle_id, task_description
**Returns**: None


## Function: create

**Parameters**: cls, bundle_id, task_description
**Returns**: WorkCoordinationBundle
**Description**: Factory: create and activate a bundle, stamping its work contract.



## Function: bundle_id

**Parameters**: self
**Returns**: str


## Function: phase

**Parameters**: self
**Returns**: BundlePhase


## Function: contract_hash

**Parameters**: self
**Returns**: str


## Function: _trace_id

**Parameters**: self
**Returns**: str


## Function: stamp_work_contract

**Parameters**: self, task_description
**Returns**: str
**Description**: Stamp an immutable work contract for this orchestration run.

        Emits ``stamps_work_contract`` ADG edge. Returns the contract hash.
        



## Function: observe_runtime_state

**Parameters**: self, key, value
**Returns**: None
**Description**: Observe and store a runtime state value.

        Emits ``observes_runtime_state`` + ``reads_runtime_state`` ADG edges.
        



## Function: read_shared

**Parameters**: self, key, default
**Returns**: Any
**Description**: Read a value from the shared coordination state.



## Function: record_agent_completion

**Parameters**: self, agent_name, task_key, result, success
**Returns**: AgentCompletion
**Description**: Record that an agent has completed its assigned task.

        Triggers an automatic snapshot.
        



## Function: snapshot

**Parameters**: self
**Returns**: BundleSnapshot
**Description**: Capture a point-in-time snapshot of the coordination state.

        Emits ``snapshots_state`` ADG edge.
        



## Function: complete

**Parameters**: self, success
**Returns**: BundleSnapshot
**Description**: Mark the bundle as completed and take a final snapshot.



## Function: completion_count

**Parameters**: self
**Returns**: int


## Function: snapshot_history

**Parameters**: self
**Returns**: list[BundleSnapshot]


## Function: completions

**Parameters**: self
**Returns**: list[AgentCompletion]


## Usage Examples

### Class Usage

```python
# Using BundlePhase
bundlephase = BundlePhase()
```

```python
# Using AgentCompletion
agentcompletion = AgentCompletion()
```

```python
# Using BundleSnapshot
bundlesnapshot = BundleSnapshot()
```

### Function Usage

```python
# Using get_coordination_bundle
result = get_coordination_bundle(bundle_id, task_description)
```

```python
# Using release_coordination_bundle
result = release_coordination_bundle(bundle_id)
```

```python
# Using active_bundle_ids
result = active_bundle_ids()
```



---
**Generated**: 2026-03-26T09:39:04.108804
**Type**: api_reference
**Quality**: comprehensive
