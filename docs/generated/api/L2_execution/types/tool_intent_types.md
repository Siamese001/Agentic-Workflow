# API Documentation: tool_intent_types

**Target Audience**: developers, api_users

# tool_intent_types API Documentation

**File**: `tool_intent_types.py`
**Classes**: 3
**Functions**: 10

## Classes

- **ToolCapability** (inherits from str, Enum)
- **ToolViolation** (inherits from Exception)
- **ToolIntent**

## Functions

- **_sha256** -> str
- **is_mutating** -> bool
- **is_l1_cognition_active** -> bool
- **assert_l1_tool_allowed** -> None
- **l1_cognition_scope** -> Generator[None, None, None]
- **build_tool_intent** -> ToolIntent
- **__init__** -> None
- **__post_init__** -> None
- **canonical_bytes** -> bytes
- **to_dict** -> dict[str, Any]


## Class: ToolCapability

**Description**: 
    Capability class of a tool.

    NON_MUTATING      — read-only; safe to call from L1 directly.
    MUTATING_EXTERNAL — writes to external services (Redis, Pinecone, APIs).
    MUTATING_FS       — writes to the filesystem.
    MUTATING_STATEBUS — writes to the internal state bus / event bus.
    

**Inherits from**: str, Enum



## Class: ToolViolation

**Description**: 
    Raised when L1 attempts a direct mutating tool call, or when a ToolIntent
    is executed outside the L2.2 commit sandbox.

    Attributes
    ----------
    code   : str  — violation code string
    detail : str  — human-readable description
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, code, detail
**Returns**: None



## Class: ToolIntent

**Description**: 
    Declarative tool intent emitted by L1 cognition.

    Fields
    ------
    schema_version : int   — bumped on breaking changes
    tool_name      : str   — non-empty tool identifier
    capability     : ToolCapability
    args           : dict  — JSON-serializable tool arguments
    args_hash      : str   — sha256(canonical args); auto-computed if empty
    requires_commit: bool  — True for any MUTATING_* capability (enforced)
    policy_hash    : str   — active PolicyConfig hash
    model_hash     : str   — active ModelConfig hash
    budget_hash    : str   — active BudgetConfig hash
    routing_hash   : str   — active RoutingConfig hash
    intent_hash    : str   — sha256(canonical_bytes excluding intent_hash); auto-computed
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Deterministic serialisation excluding intent_hash (self-referential).

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Function: _sha256

**Parameters**: data
**Returns**: str


## Function: is_mutating

**Parameters**: capability
**Returns**: bool
**Description**: Return True if the capability class requires sandbox execution.



## Function: is_l1_cognition_active

**Returns**: bool
**Description**: Return True when L1 cognition context is active.



## Function: assert_l1_tool_allowed

**Parameters**: capability, tool_name
**Returns**: None
**Description**: 
    Raise ToolViolation(code="L1_TOOL_CALL_BLOCKED") if L1 cognition is active
    and the tool has a MUTATING_* capability.

    Call this at the top of any tool invocation seam.
    



## Function: l1_cognition_scope

**Returns**: Generator[None, None, None]
**Description**: 
    Context manager that activates the L1 cognition enforcement flag.

    Inside this scope, any direct call to a MUTATING_* tool raises ToolViolation.
    



## Function: build_tool_intent

**Parameters**: tool_name, capability, args
**Returns**: ToolIntent
**Description**: 
    Factory: build a ToolIntent from tool parameters.

    requires_commit is automatically set to True for MUTATING_* capabilities.
    



## Function: __init__

**Parameters**: self, code, detail
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: Deterministic serialisation excluding intent_hash (self-referential).



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Usage Examples

### Class Usage

```python
# Using ToolCapability
toolcapability = ToolCapability()
```

```python
# Using ToolViolation
toolviolation = ToolViolation()
```

```python
# Using ToolIntent
toolintent = ToolIntent()
toolintent.canonical_bytes()
toolintent.to_dict()
```

### Function Usage

```python
# Using _sha256
result = _sha256(data)
```

```python
# Using is_mutating
result = is_mutating(capability)
```

```python
# Using is_l1_cognition_active
result = is_l1_cognition_active()
```



---
**Generated**: 2026-03-26T09:39:04.016842
**Type**: api_reference
**Quality**: comprehensive
