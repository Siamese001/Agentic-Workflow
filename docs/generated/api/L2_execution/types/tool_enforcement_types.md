# API Documentation: tool_enforcement_types

**Target Audience**: developers, api_users

# tool_enforcement_types API Documentation

**File**: `tool_enforcement_types.py`
**Classes**: 3
**Functions**: 2

## Classes

- **LawSlotOutcome** (inherits from Enum)
- **ToolEnforcementArtifact**
- **ToolPolicyBlocked** (inherits from Exception)

## Functions

- **__post_init__** -> None
- **__init__** -> None


## Class: LawSlotOutcome

**Description**: §Wave2.4 — Enforcement outcomes at the tool choke point.

**Inherits from**: Enum



## Class: ToolEnforcementArtifact

**Description**: §Wave2.4 — Enforcement record emitted exactly once per tool call.

    Captures the enforcement decision, applied law slots, argument hashes,
    and rationale for audit trail.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: ToolPolicyBlocked

**Description**: §Wave2.4 — Raised when a tool call is blocked by enforcement policy.

    Preserves the enforcement rationale and artifact for upstream handling.
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, tool_name, rationale, artifact
**Returns**: None



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, tool_name, rationale, artifact
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using LawSlotOutcome
lawslotoutcome = LawSlotOutcome()
```

```python
# Using ToolEnforcementArtifact
toolenforcementartifact = ToolEnforcementArtifact()
```

```python
# Using ToolPolicyBlocked
toolpolicyblocked = ToolPolicyBlocked()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __init__
result = __init__(tool_name, rationale)
```



---
**Generated**: 2026-03-26T09:39:04.014234
**Type**: api_reference
**Quality**: comprehensive
