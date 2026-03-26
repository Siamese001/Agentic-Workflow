# API Documentation: tool_safety_contract

**Target Audience**: developers, api_users

# tool_safety_contract API Documentation

**File**: `tool_safety_contract.py`
**Classes**: 9
**Functions**: 15

## Classes

- **ToolActionClass** (inherits from str, Enum)
- **ToolRegistryEntry**
- **UnregisteredToolError** (inherits from PermissionError)
- **ToolCapabilityError** (inherits from PermissionError)
- **ToolPolicyError** (inherits from PermissionError)
- **ToolGuardrailDeniedError** (inherits from PermissionError)
- **ToolRegistry**
- **ToolSafetyContract**
- **ToolDenialTrace**

## Functions

- **invoke_tool_safely** -> tuple[Any, ToolSafetyContract]
- **_run_guardrail** -> bool
- **_route_to_human_review** -> None
- **_emit_denial** -> None
- **_record_contract** -> None
- **get_tool_contract_ledger** -> list[ToolSafetyContract]
- **get_tool_registry** -> ToolRegistry
- **reset_tool_registry** -> None
- **__init__** -> None
- **register** -> None
- **get** -> ToolRegistryEntry | None
- **require** -> ToolRegistryEntry
- **registered_names** -> list[str]
- **classify** -> ToolActionClass | None
- **create** -> ToolSafetyContract


## Class: ToolActionClass

**Description**: Classification of tool invocations for policy enforcement.

**Inherits from**: str, Enum



## Class: ToolRegistryEntry

**Description**: A registered tool definition with policy requirements.



## Class: UnregisteredToolError

**Description**: Raised when an unregistered tool is invoked.

**Inherits from**: PermissionError



## Class: ToolCapabilityError

**Description**: Raised when capability token validation fails.

**Inherits from**: PermissionError



## Class: ToolPolicyError

**Description**: Raised when policy enforcement fails.

**Inherits from**: PermissionError



## Class: ToolGuardrailDeniedError

**Description**: Raised when guardrail check denies tool execution.

**Inherits from**: PermissionError



## Class: ToolRegistry

**Description**: Explicit tool registry — unregistered tools cannot execute.

    Per spec §5: every tool must have:
    - tool_name, action_class, allowed_callers, policy_requirements,
      human_review_requirement, network_requirement
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### register
**Parameters**: self, entry
**Returns**: None
**Description**: Register a tool entry. Overwrites if already registered.

#### get
**Parameters**: self, tool_name
**Returns**: ToolRegistryEntry | None

#### require
**Parameters**: self, tool_name
**Returns**: ToolRegistryEntry
**Description**: Return entry or raise UnregisteredToolError.

#### registered_names
**Parameters**: self
**Returns**: list[str]

#### classify
**Parameters**: self, tool_name
**Returns**: ToolActionClass | None



## Class: ToolSafetyContract

**Description**: Immutable artifact of one governed tool invocation (P1/L5 spec §2).

### Methods

#### create
**Parameters**: cls, tool_name, run_id, trace_id, actor_id, capability_token, policy_hash, action_class, tool_input, tool_output, allowed, denial_reason
**Returns**: ToolSafetyContract



## Class: ToolDenialTrace

**Description**: Immutable denial record for a blocked tool invocation.



## Function: invoke_tool_safely

**Parameters**: tool_name, payload, capability_token, actor_id, run_id, trace_id, policy_hash, tool_fn, registry
**Returns**: tuple[Any, ToolSafetyContract]
**Description**: Mandatory tool invocation entrypoint — P1/L5 spec §3.

    Steps (in order, all mandatory):
      1. Validate capability token
      2. Classify tool action (registry lookup)
      3. Enforce policy
      4. Run guardrail decision
      5. Attach policy hash
      6. Attach trace id
      7. Execute only on ALLOW
      8. Emit ToolSafetyContract artifact

    Args:
        tool_name:        Registered tool name.
        payload:          Tool input payload (dict or Any).
        capability_token: Caller's capability token (must be non-empty).
        actor_id:         Caller identity.
        run_id:           Run identifier.
        trace_id:         Trace context (auto-resolved from active trace if empty).
        policy_hash:      Policy hash to attach (uses process default if empty).
        tool_fn:          Optional callable to execute; if None, returns None output.
        registry:         ToolRegistry to use; falls back to process singleton.

    Returns:
        (result, ToolSafetyContract)

    Raises:
        ToolCapabilityError:      capability_token is missing.
        UnregisteredToolError:    tool_name not in registry.
        ToolPolicyError:          policy enforcement failed.
        ToolGuardrailDeniedError: guardrail check denied execution.
    



## Function: _run_guardrail

**Parameters**: tool_name, action_class, payload, policy_hash
**Returns**: bool
**Description**: Run guardrail decision. Returns True (ALLOW) or False (DENY).



## Function: _route_to_human_review

**Parameters**: tool_name, action_class, actor_id, run_id, trace_id
**Returns**: None
**Description**: Emit human review record for HUMAN_GATED / PRIVILEGED tools.



## Function: _emit_denial

**Parameters**: denial
**Returns**: None
**Description**: Emit denial trace for a blocked tool invocation.



## Function: _record_contract

**Parameters**: contract
**Returns**: None


## Function: get_tool_contract_ledger

**Returns**: list[ToolSafetyContract]
**Description**: Return a copy of all emitted ToolSafetyContract records.



## Function: get_tool_registry

**Returns**: ToolRegistry
**Description**: Return the process-level ToolRegistry singleton (pre-populated).



## Function: reset_tool_registry

**Returns**: None
**Description**: Reset the global tool registry (for testing).



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: register

**Parameters**: self, entry
**Returns**: None
**Description**: Register a tool entry. Overwrites if already registered.



## Function: get

**Parameters**: self, tool_name
**Returns**: ToolRegistryEntry | None


## Function: require

**Parameters**: self, tool_name
**Returns**: ToolRegistryEntry
**Description**: Return entry or raise UnregisteredToolError.



## Function: registered_names

**Parameters**: self
**Returns**: list[str]


## Function: classify

**Parameters**: self, tool_name
**Returns**: ToolActionClass | None


## Function: create

**Parameters**: cls, tool_name, run_id, trace_id, actor_id, capability_token, policy_hash, action_class, tool_input, tool_output, allowed, denial_reason
**Returns**: ToolSafetyContract


## Usage Examples

### Class Usage

```python
# Using ToolActionClass
toolactionclass = ToolActionClass()
```

```python
# Using ToolRegistryEntry
toolregistryentry = ToolRegistryEntry()
```

```python
# Using UnregisteredToolError
unregisteredtoolerror = UnregisteredToolError()
```

### Function Usage

```python
# Using invoke_tool_safely
result = invoke_tool_safely(tool_name, payload)
```

```python
# Using _run_guardrail
result = _run_guardrail(tool_name, action_class)
```

```python
# Using _route_to_human_review
result = _route_to_human_review(tool_name, action_class)
```



---
**Generated**: 2026-03-26T09:39:04.975404
**Type**: api_reference
**Quality**: comprehensive
