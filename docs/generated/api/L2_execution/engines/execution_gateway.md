# API Documentation: execution_gateway

**Target Audience**: developers, api_users

# execution_gateway API Documentation

**File**: `execution_gateway.py`
**Classes**: 2
**Functions**: 4

## Classes

- **SignatureBoundaryError** (inherits from RuntimeError)
- **ExecutionGateway**

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **__init__**
- **create_envelope** -> SandboxEnvelope


## Class: SignatureBoundaryError

**Description**: Raised when SandboxEnvelope signature verification fails - fail-closed boundary.

**Inherits from**: RuntimeError



## Class: ExecutionGateway

**Description**: L2 execution engine that builds ExecutionTrace while enforcing budgets.

### Methods

#### __init__
**Parameters**: self

#### create_envelope
**Parameters**: self, tool_name, tool_args, instruction_packet_id, agent_id
**Returns**: SandboxEnvelope
**Description**: Create a signed SandboxEnvelope for execution.



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: run_id, capability_token, policy_hash, payload, target


## Function: __init__

**Parameters**: self


## Function: create_envelope

**Parameters**: self, tool_name, tool_args, instruction_packet_id, agent_id
**Returns**: SandboxEnvelope
**Description**: Create a signed SandboxEnvelope for execution.



## Usage Examples

### Class Usage

```python
# Using SignatureBoundaryError
signatureboundaryerror = SignatureBoundaryError()
```

```python
# Using ExecutionGateway
executiongateway = ExecutionGateway()
executiongateway.create_envelope()
```

### Function Usage

```python
# Using _invoke_authorize_and_execute
result = _invoke_authorize_and_execute(execution_context, target_callable)
```

```python
# Using _make_execution_context
result = _make_execution_context(run_id, capability_token)
```

```python
# Using __init__
result = __init__()
```



---
**Generated**: 2026-03-26T09:39:03.763057
**Type**: api_reference
**Quality**: comprehensive
