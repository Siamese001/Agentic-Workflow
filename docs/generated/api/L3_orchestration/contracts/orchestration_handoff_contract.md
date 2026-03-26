# API Documentation: orchestration_handoff_contract

**Target Audience**: developers, api_users

# orchestration_handoff_contract API Documentation

**File**: `orchestration_handoff_contract.py`
**Classes**: 2
**Functions**: 4

## Classes

- **HandoffOutcome** (inherits from str, Enum)
- **OrchestrationHandoffContract**

## Functions

- **emit_agent_executes_agent** -> OrchestrationHandoffContract
- **create** -> OrchestrationHandoffContract
- **emit_agent_executes_agent** -> None
- **to_dict** -> dict[str, Any]


## Class: HandoffOutcome

**Description**: Lifecycle outcome of an orchestration handoff.

**Inherits from**: str, Enum



## Class: OrchestrationHandoffContract

**Description**: Immutable typed contract for one agent-to-agent handoff.

    Carries all 9 mandatory fields required by the P0/L3 spec.
    Emits an ``agent_executes_agent`` ADG edge signal on creation.

    Hard rule: if this contract is not present, the handoff is invalid.
    

### Methods

#### create
**Parameters**: cls, parent_agent_id, child_agent_id, run_id, capability_token, handoff_reason, input_payload, policy_hash, workflow_stage, trace_id, metadata
**Returns**: OrchestrationHandoffContract
**Description**: Factory: create a contract with deterministic hashes.

        Args:
            parent_agent_id: Dispatching agent name.
            child_agent_id: Receiving agent name.
            run_id: Current run/trace scope.
            capability_token: Token proving caller has authority.
            handoff_reason: Human-readable reason for this handoff.
            input_payload: Payload being handed off (any serialisable type).
            policy_hash: Hash of the current active policy.
            workflow_stage: Current workflow stage label.
            trace_id: Active trace ID (auto-resolved if empty).
            metadata: Extra key-value annotations.

        Returns:
            Immutable OrchestrationHandoffContract.
        

#### emit_agent_executes_agent
**Parameters**: self
**Returns**: None
**Description**: Re-emit the ADG edge signal (idempotent, for wiring call sites).

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Function: emit_agent_executes_agent

**Parameters**: parent_agent_id, child_agent_id, run_id, stage, capability_token, policy_hash, handoff_reason, input_payload
**Returns**: OrchestrationHandoffContract
**Description**: Convenience wrapper: emit one agent_executes_agent signal.

    Creates and returns an OrchestrationHandoffContract.  Call this at
    every agent-to-agent handoff site to make the topology graph-visible.

    ADG scanner (_AgentDispatchVisitor) detects calls to this function
    by name and emits agent_executes_agent edges.
    



## Function: create

**Parameters**: cls, parent_agent_id, child_agent_id, run_id, capability_token, handoff_reason, input_payload, policy_hash, workflow_stage, trace_id, metadata
**Returns**: OrchestrationHandoffContract
**Description**: Factory: create a contract with deterministic hashes.

        Args:
            parent_agent_id: Dispatching agent name.
            child_agent_id: Receiving agent name.
            run_id: Current run/trace scope.
            capability_token: Token proving caller has authority.
            handoff_reason: Human-readable reason for this handoff.
            input_payload: Payload being handed off (any serialisable type).
            policy_hash: Hash of the current active policy.
            workflow_stage: Current workflow stage label.
            trace_id: Active trace ID (auto-resolved if empty).
            metadata: Extra key-value annotations.

        Returns:
            Immutable OrchestrationHandoffContract.
        



## Function: emit_agent_executes_agent

**Parameters**: self
**Returns**: None
**Description**: Re-emit the ADG edge signal (idempotent, for wiring call sites).



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Usage Examples

### Class Usage

```python
# Using HandoffOutcome
handoffoutcome = HandoffOutcome()
```

```python
# Using OrchestrationHandoffContract
orchestrationhandoffcontract = OrchestrationHandoffContract()
orchestrationhandoffcontract.create()
orchestrationhandoffcontract.emit_agent_executes_agent()
```

### Function Usage

```python
# Using emit_agent_executes_agent
result = emit_agent_executes_agent(parent_agent_id, child_agent_id)
```

```python
# Using create
result = create(cls, parent_agent_id)
```

```python
# Using emit_agent_executes_agent
result = emit_agent_executes_agent()
```



---
**Generated**: 2026-03-26T09:39:04.098933
**Type**: api_reference
**Quality**: comprehensive
