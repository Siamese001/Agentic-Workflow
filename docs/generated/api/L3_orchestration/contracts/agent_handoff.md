# API Documentation: agent_handoff

**Target Audience**: developers, api_users

# agent_handoff API Documentation

**File**: `agent_handoff.py`
**Classes**: 4
**Functions**: 12

## Classes

- **HandoffStatus** (inherits from str, Enum)
- **AgentHandoff**
- **HandoffRecord**
- **HandoffDispatcher**

## Functions

- **get_handoff_dispatcher** -> HandoffDispatcher
- **reset_handoff_dispatcher** -> None
- **create** -> AgentHandoff
- **to_dict** -> dict[str, Any]
- **mark_dispatched** -> None
- **mark_completed** -> None
- **mark_failed** -> None
- **__init__** -> None
- **register** -> None
- **dispatch** -> HandoffRecord
- **ledger** -> list[HandoffRecord]
- **registered_agents** -> list[str]


## Class: HandoffStatus

**Description**: Lifecycle status of an agent handoff.

**Inherits from**: str, Enum



## Class: AgentHandoff

**Description**: Typed, immutable agent-to-agent handoff contract.

    Every ``agent_executes_agent`` dispatch must be expressed as an
    ``AgentHandoff`` so that:
    - The source and destination agents are statically named (not L_UNKNOWN).
    - The task context travels with the handoff (not via mutable side channels).
    - The handoff can be logged, replayed, and audited.
    

### Methods

#### create
**Parameters**: cls, src, dst, context, task_id, coordination_bundle_id, metadata
**Returns**: AgentHandoff
**Description**: Factory: create a new handoff with computed trace linkage.

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: HandoffRecord

**Description**: Mutable audit record tracking the lifecycle of a single handoff.

### Methods

#### mark_dispatched
**Parameters**: self
**Returns**: None

#### mark_completed
**Parameters**: self, result
**Returns**: None

#### mark_failed
**Parameters**: self, error
**Returns**: None



## Class: HandoffDispatcher

**Description**: Dispatcher that executes ``AgentHandoff`` contracts.

    Callers register agent executors by name; the dispatcher resolves the
    ``dst`` field to a concrete callable, making all dispatch statically
    visible to the ADG.

    Usage::

        dispatcher = HandoffDispatcher()
        dispatcher.register("SummaryAgent", summary_agent_fn)
        record = dispatcher.dispatch(handoff)
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### register
**Parameters**: self, agent_name, executor
**Returns**: None
**Description**: Register a named agent executor.

#### dispatch
**Parameters**: self, handoff, capability_name
**Returns**: HandoffRecord
**Description**: Dispatch an ``AgentHandoff`` to the registered executor.

        P2/L3: Resolves dst through CapabilityRegistry before execution.
        Raises UnregisteredDispatchError if dst not registered.
        Raises CapabilityNotFoundError / CapabilityPermissionError on registry rejection.
        

#### ledger
**Parameters**: self
**Returns**: list[HandoffRecord]
**Description**: Return a copy of all handoff records.

#### registered_agents
**Parameters**: self
**Returns**: list[str]
**Description**: Return all registered agent names.



## Function: get_handoff_dispatcher

**Returns**: HandoffDispatcher
**Description**: Return the process-level handoff dispatcher.



## Function: reset_handoff_dispatcher

**Returns**: None
**Description**: Reset the global dispatcher (for testing).



## Function: create

**Parameters**: cls, src, dst, context, task_id, coordination_bundle_id, metadata
**Returns**: AgentHandoff
**Description**: Factory: create a new handoff with computed trace linkage.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: mark_dispatched

**Parameters**: self
**Returns**: None


## Function: mark_completed

**Parameters**: self, result
**Returns**: None


## Function: mark_failed

**Parameters**: self, error
**Returns**: None


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: register

**Parameters**: self, agent_name, executor
**Returns**: None
**Description**: Register a named agent executor.



## Function: dispatch

**Parameters**: self, handoff, capability_name
**Returns**: HandoffRecord
**Description**: Dispatch an ``AgentHandoff`` to the registered executor.

        P2/L3: Resolves dst through CapabilityRegistry before execution.
        Raises UnregisteredDispatchError if dst not registered.
        Raises CapabilityNotFoundError / CapabilityPermissionError on registry rejection.
        



## Function: ledger

**Parameters**: self
**Returns**: list[HandoffRecord]
**Description**: Return a copy of all handoff records.



## Function: registered_agents

**Parameters**: self
**Returns**: list[str]
**Description**: Return all registered agent names.



## Usage Examples

### Class Usage

```python
# Using HandoffStatus
handoffstatus = HandoffStatus()
```

```python
# Using AgentHandoff
agenthandoff = AgentHandoff()
agenthandoff.create()
agenthandoff.to_dict()
```

```python
# Using HandoffRecord
handoffrecord = HandoffRecord()
handoffrecord.mark_dispatched()
handoffrecord.mark_completed()
```

### Function Usage

```python
# Using get_handoff_dispatcher
result = get_handoff_dispatcher()
```

```python
# Using reset_handoff_dispatcher
result = reset_handoff_dispatcher()
```

```python
# Using create
result = create(cls, src)
```



---
**Generated**: 2026-03-26T09:39:04.090569
**Type**: api_reference
**Quality**: comprehensive
