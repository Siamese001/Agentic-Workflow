# API Documentation: execution_gateway

**Target Audience**: developers, api_users

# execution_gateway API Documentation

**File**: `execution_gateway.py`
**Classes**: 4
**Functions**: 15

## Classes

- **ExecutionGatewayError** (inherits from RuntimeError)
- **UnregisteredAgentError** (inherits from RuntimeError)
- **GatewayResult**
- **V15ExecutionGateway**

## Functions

- **_get_manifest_hash_validator**
- **_get_guardian_decision**
- **_get_enforce_healer_pipe_order**
- **__init__**
- **__init__** -> None
- **clock** -> SemanticClock
- **execute** -> GatewayResult
- **_enforce_agent_registered** -> None
- **_execute_with_envelope** -> GatewayResult
- **_validate_manifest** -> SurgicalManifest
- **_guardian_validate** -> None
- **_commit_mutation** -> GatewayResult
- **_heal_and_retry** -> GatewayResult
- **_pipe_advance** -> None
- **_policy_check** -> None


## Class: ExecutionGatewayError

**Description**: Raised when critical execution gateway operations fail.

**Inherits from**: RuntimeError

### Methods

#### __init__
**Parameters**: self, message, original_error



## Class: UnregisteredAgentError

**Description**: Raised when an agent is not found in AgentExecutionProfileRegistry.

**Inherits from**: RuntimeError



## Class: GatewayResult

**Description**: Result of a contract-enforced execution.



## Class: V15ExecutionGateway

**Description**: Contract-enforced execution gateway for healing paths.

    Usage:
        gateway = V15ExecutionGateway()
        result = gateway.execute(manifest, heal_fn, state_hash_fn)
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### clock
**Parameters**: self
**Returns**: SemanticClock
**Description**: Expose clock for test inspection.

#### execute
**Parameters**: self, execution_input, heal_fn, state_hash_fn, trace_id, agent_id
**Returns**: GatewayResult
**Description**: Execute a healing operation under full P2 contract enforcement.

        Args:
            execution_input: Must be a SurgicalManifest (§1.1).
            heal_fn: The actual healing callable. Receives the validated manifest.
            state_hash_fn: Returns (filesystem_hash, git_state_hash, agent_memory_hash).
            trace_id: Correlation trace ID for snapshots.

        Returns:
            GatewayResult with full audit trail.
        

#### _enforce_agent_registered
**Parameters**: self, agent_id
**Returns**: None
**Description**: Raise UnregisteredAgentError if agent_id is empty or not in AGENT_REGISTRY.

        Spec: L0 Authority Node, Guarantee #7 — no execution without a registered profile.
        

#### _execute_with_envelope
**Parameters**: self, execution_input, heal_fn, state_hash_fn, trace_id
**Returns**: GatewayResult
**Description**: Execute with explicit L2 envelope separation.

#### _validate_manifest
**Parameters**: self, execution_input, trace_id
**Returns**: SurgicalManifest
**Description**: L2.0: Validate execution input manifest.

#### _guardian_validate
**Parameters**: self, manifest, trace_id
**Returns**: None
**Description**: L2.1: Guardian validation (non-mutating).

#### _commit_mutation
**Parameters**: self, manifest, heal_fn, state_hash_fn, trace_id
**Returns**: GatewayResult
**Description**: L2.2: Sole mutation authority point.

#### _heal_and_retry
**Parameters**: self, manifest, heal_fn, state_hash_fn, trace_id
**Returns**: GatewayResult
**Description**: L2.3: Healing loop - non-mutating, re-enters L2.0.

#### _pipe_advance
**Parameters**: self, pipe, step, trace_id, observed_steps
**Returns**: None
**Description**: Advance pipe to *step*. Mode-aware: LOG_ONLY logs, HARD_FAIL raises.

#### _policy_check
**Parameters**: self, guard, current_config, trace_id
**Returns**: None
**Description**: Verify policy immutability. Mode-aware: LOG_ONLY logs, HARD_FAIL raises.



## Function: _get_manifest_hash_validator



## Function: _get_guardian_decision



## Function: _get_enforce_healer_pipe_order

**Description**: Lazy load enforce_healer_pipe_order to avoid upward import.



## Function: __init__

**Parameters**: self, message, original_error


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: clock

**Parameters**: self
**Returns**: SemanticClock
**Description**: Expose clock for test inspection.



## Function: execute

**Parameters**: self, execution_input, heal_fn, state_hash_fn, trace_id, agent_id
**Returns**: GatewayResult
**Description**: Execute a healing operation under full P2 contract enforcement.

        Args:
            execution_input: Must be a SurgicalManifest (§1.1).
            heal_fn: The actual healing callable. Receives the validated manifest.
            state_hash_fn: Returns (filesystem_hash, git_state_hash, agent_memory_hash).
            trace_id: Correlation trace ID for snapshots.

        Returns:
            GatewayResult with full audit trail.
        



## Function: _enforce_agent_registered

**Parameters**: self, agent_id
**Returns**: None
**Description**: Raise UnregisteredAgentError if agent_id is empty or not in AGENT_REGISTRY.

        Spec: L0 Authority Node, Guarantee #7 — no execution without a registered profile.
        



## Function: _execute_with_envelope

**Parameters**: self, execution_input, heal_fn, state_hash_fn, trace_id
**Returns**: GatewayResult
**Description**: Execute with explicit L2 envelope separation.



## Function: _validate_manifest

**Parameters**: self, execution_input, trace_id
**Returns**: SurgicalManifest
**Description**: L2.0: Validate execution input manifest.



## Function: _guardian_validate

**Parameters**: self, manifest, trace_id
**Returns**: None
**Description**: L2.1: Guardian validation (non-mutating).



## Function: _commit_mutation

**Parameters**: self, manifest, heal_fn, state_hash_fn, trace_id
**Returns**: GatewayResult
**Description**: L2.2: Sole mutation authority point.



## Function: _heal_and_retry

**Parameters**: self, manifest, heal_fn, state_hash_fn, trace_id
**Returns**: GatewayResult
**Description**: L2.3: Healing loop - non-mutating, re-enters L2.0.



## Function: _pipe_advance

**Parameters**: self, pipe, step, trace_id, observed_steps
**Returns**: None
**Description**: Advance pipe to *step*. Mode-aware: LOG_ONLY logs, HARD_FAIL raises.



## Function: _policy_check

**Parameters**: self, guard, current_config, trace_id
**Returns**: None
**Description**: Verify policy immutability. Mode-aware: LOG_ONLY logs, HARD_FAIL raises.



## Usage Examples

### Class Usage

```python
# Using ExecutionGatewayError
executiongatewayerror = ExecutionGatewayError()
```

```python
# Using UnregisteredAgentError
unregisteredagenterror = UnregisteredAgentError()
```

```python
# Using GatewayResult
gatewayresult = GatewayResult()
```

### Function Usage

```python
# Using _get_manifest_hash_validator
result = _get_manifest_hash_validator()
```

```python
# Using _get_guardian_decision
result = _get_guardian_decision()
```

```python
# Using _get_enforce_healer_pipe_order
result = _get_enforce_healer_pipe_order()
```



---
**Generated**: 2026-03-26T09:39:02.616592
**Type**: api_reference
**Quality**: comprehensive
