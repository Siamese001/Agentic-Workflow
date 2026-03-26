# API Documentation: tool_policy_enforcer

**Target Audience**: developers, api_users

# tool_policy_enforcer API Documentation

**File**: `tool_policy_enforcer.py`
**Classes**: 1
**Functions**: 8

## Classes

- **ToolPolicyEnforcer**

## Functions

- **_stable_args_hash** -> str
- **get_tool_policy_enforcer** -> ToolPolicyEnforcer
- **set_tool_policy_enforcer** -> None
- **__init__** -> None
- **register_rule** -> None
- **resolve_slots** -> tuple[str, ...]
- **enforce** -> tuple[LawSlotOutcome, dict[str, Any], str, tuple[str, ...]]
- **build_artifact** -> ToolEnforcementArtifact


## Class: ToolPolicyEnforcer

**Description**: §Wave2.4 — Minimal law-slot enforcement handler.

    Resolves applicable law slots for a given tool + context and returns
    an enforcement decision (PASS / BLOCK / MODIFY).

    Default behavior (no policy rules configured): PASS with empty slots.

    Subclass or configure `_policy_rules` to implement real enforcement.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### register_rule
**Parameters**: self, tool_name
**Returns**: None
**Description**: Register a policy rule for a specific tool.

        Used primarily for testing and configuration.
        

#### resolve_slots
**Parameters**: self, tool_name, context
**Returns**: tuple[str, ...]
**Description**: Resolve applicable law slot IDs for this tool + context.

#### enforce
**Parameters**: self, tool_name, args, context
**Returns**: tuple[LawSlotOutcome, dict[str, Any], str, tuple[str, ...]]
**Description**: Enforce policy for a tool call.

        Returns:
            (outcome, new_args, rationale, applied_slots)
            - outcome: PASS, BLOCK, or MODIFY
            - new_args: original args if PASS/BLOCK; transformed args if MODIFY
            - rationale: human-readable explanation
            - applied_slots: tuple of law slot IDs that were applied
        

#### build_artifact
**Parameters**: self, tool_name, outcome, applied_slots, rationale, original_args_hash, modified_args_hash, trace_id, agent_id
**Returns**: ToolEnforcementArtifact
**Description**: Build a ToolEnforcementArtifact for emission.



## Function: _stable_args_hash

**Parameters**: args
**Returns**: str
**Description**: Compute deterministic SHA-256 hash of tool arguments.

    Uses sorted-key JSON serialization with default=str for non-serializable
    values, ensuring identical args always produce the same hash.
    



## Function: get_tool_policy_enforcer

**Returns**: ToolPolicyEnforcer
**Description**: Get or create the global ToolPolicyEnforcer instance.



## Function: set_tool_policy_enforcer

**Parameters**: enforcer
**Returns**: None
**Description**: Replace the global enforcer (for testing or reconfiguration).



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: register_rule

**Parameters**: self, tool_name
**Returns**: None
**Description**: Register a policy rule for a specific tool.

        Used primarily for testing and configuration.
        



## Function: resolve_slots

**Parameters**: self, tool_name, context
**Returns**: tuple[str, ...]
**Description**: Resolve applicable law slot IDs for this tool + context.



## Function: enforce

**Parameters**: self, tool_name, args, context
**Returns**: tuple[LawSlotOutcome, dict[str, Any], str, tuple[str, ...]]
**Description**: Enforce policy for a tool call.

        Returns:
            (outcome, new_args, rationale, applied_slots)
            - outcome: PASS, BLOCK, or MODIFY
            - new_args: original args if PASS/BLOCK; transformed args if MODIFY
            - rationale: human-readable explanation
            - applied_slots: tuple of law slot IDs that were applied
        



## Function: build_artifact

**Parameters**: self, tool_name, outcome, applied_slots, rationale, original_args_hash, modified_args_hash, trace_id, agent_id
**Returns**: ToolEnforcementArtifact
**Description**: Build a ToolEnforcementArtifact for emission.



## Usage Examples

### Class Usage

```python
# Using ToolPolicyEnforcer
toolpolicyenforcer = ToolPolicyEnforcer()
toolpolicyenforcer.register_rule()
toolpolicyenforcer.resolve_slots()
```

### Function Usage

```python
# Using _stable_args_hash
result = _stable_args_hash(args)
```

```python
# Using get_tool_policy_enforcer
result = get_tool_policy_enforcer()
```

```python
# Using set_tool_policy_enforcer
result = set_tool_policy_enforcer(enforcer)
```



---
**Generated**: 2026-03-26T09:39:03.741701
**Type**: api_reference
**Quality**: comprehensive
