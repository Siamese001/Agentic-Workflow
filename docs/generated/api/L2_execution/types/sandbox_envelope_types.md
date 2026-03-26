# API Documentation: sandbox_envelope_types

**Target Audience**: developers, api_users

# sandbox_envelope_types API Documentation

**File**: `sandbox_envelope_types.py`
**Classes**: 2
**Functions**: 7

## Classes

- **ToolBudget**
- **SandboxEnvelope**

## Functions

- **__post_init__** -> None
- **__post_init__** -> None
- **_signable_dict** -> dict[str, Any]
- **canonical_bytes** -> bytes
- **sign** -> SandboxEnvelope
- **verify** -> None
- **is_signed** -> bool


## Class: ToolBudget

**Description**: OS-level resource caps per tool invocation (spec contract [2]).

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: SandboxEnvelope

**Description**: Signed wrapper for L2 tool invocations.

    Fields
    ------
    envelope_id : str
        Deterministic identifier for this envelope (e.g. instruction_id + tool).
    tool_name : str
        Name of the tool being invoked.
    tool_args : dict[str, Any]
        Arguments passed to the tool (must be JSON-serialisable).
    instruction_packet_id : str
        ``instruction_id`` of the parent InstructionPacket being executed.
    invocation_metadata : dict[str, Any]
        Additional L2 metadata (agent, tick, etc.).
    budget : ToolBudget
        OS-level resource caps for this invocation (spec contract [2]).
    signature : str
        Lowercase hex HMAC-SHA256.  Empty string means unsigned.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None
**Description**: Enforce mandatory signing at construction.

#### _signable_dict
**Parameters**: self
**Returns**: dict[str, Any]

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Deterministic bytes over the signable surface.

#### sign
**Parameters**: self, secret
**Returns**: SandboxEnvelope
**Description**: Return a *new* SandboxEnvelope with HMAC-SHA256 signature set.

#### verify
**Parameters**: self, secret
**Returns**: None
**Description**: Raise SignatureVerificationError if signature is absent or wrong.

        Must be called before any tool execution, write, or network call.
        

#### is_signed
**Parameters**: self
**Returns**: bool
**Description**: True when a signature string is present (not verified).



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None
**Description**: Enforce mandatory signing at construction.



## Function: _signable_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: Deterministic bytes over the signable surface.



## Function: sign

**Parameters**: self, secret
**Returns**: SandboxEnvelope
**Description**: Return a *new* SandboxEnvelope with HMAC-SHA256 signature set.



## Function: verify

**Parameters**: self, secret
**Returns**: None
**Description**: Raise SignatureVerificationError if signature is absent or wrong.

        Must be called before any tool execution, write, or network call.
        



## Function: is_signed

**Parameters**: self
**Returns**: bool
**Description**: True when a signature string is present (not verified).



## Usage Examples

### Class Usage

```python
# Using ToolBudget
toolbudget = ToolBudget()
```

```python
# Using SandboxEnvelope
sandboxenvelope = SandboxEnvelope()
sandboxenvelope.canonical_bytes()
sandboxenvelope.sign()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _signable_dict
result = _signable_dict()
```



---
**Generated**: 2026-03-26T09:39:04.002974
**Type**: api_reference
**Quality**: comprehensive
