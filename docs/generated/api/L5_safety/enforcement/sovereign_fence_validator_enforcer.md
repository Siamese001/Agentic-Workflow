# API Documentation: sovereign_fence_validator_enforcer

**Target Audience**: developers, api_users

# sovereign_fence_validator_enforcer API Documentation

**File**: `sovereign_fence_validator_enforcer.py`
**Classes**: 2
**Functions**: 3

## Classes

- **SovereignFenceViolation** (inherits from Exception)
- **FenceValidationResult**

## Functions

- **validate** -> FenceValidationResult
- **__init__**
- **to_digest_contribution** -> dict[str, Any]


## Class: SovereignFenceViolation

**Description**: Raised when a proposal violates a sovereign safety fence.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, reason_code, message



## Class: FenceValidationResult

**Description**: The result of a fence validation check.

### Methods

#### to_digest_contribution
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Returns a dictionary suitable for inclusion in a determinism digest.



## Function: validate

**Parameters**: proposal, policy
**Returns**: FenceValidationResult
**Description**: 
    Validates a proposal against a sovereign policy fence.

    This is a hard boundary. It is not advisory. A validation failure here must
    block any state change (e.g., before a STAMP operation).

    Args:
        proposal: The proposed action or state change.
        policy: The sovereign policy to validate against.

    Returns:
        A FenceValidationResult indicating if the proposal is valid.
    



## Function: __init__

**Parameters**: self, reason_code, message


## Function: to_digest_contribution

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Returns a dictionary suitable for inclusion in a determinism digest.



## Usage Examples

### Class Usage

```python
# Using SovereignFenceViolation
sovereignfenceviolation = SovereignFenceViolation()
```

```python
# Using FenceValidationResult
fencevalidationresult = FenceValidationResult()
fencevalidationresult.to_digest_contribution()
```

### Function Usage

```python
# Using validate
result = validate(proposal, policy)
```

```python
# Using __init__
result = __init__(reason_code, message)
```

```python
# Using to_digest_contribution
result = to_digest_contribution()
```



---
**Generated**: 2026-03-26T09:39:04.935350
**Type**: api_reference
**Quality**: comprehensive
