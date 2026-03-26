# API Documentation: verification_types

**Target Audience**: developers, api_users

# verification_types API Documentation

**File**: `verification_types.py`
**Classes**: 3
**Functions**: 6

## Classes

- **VerificationRequest**
- **VerificationResult**
- **VerificationGateProtocol** (inherits from ABC)

## Functions

- **__post_init__** -> None
- **__post_init__** -> None
- **verify_action** -> VerificationResult
- **is_available** -> bool
- **get_supported_actions** -> list[str]
- **validate_request** -> str | None


## Class: VerificationRequest

**Description**: Request for verification operation.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: VerificationResult

**Description**: Result of verification operation.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: VerificationGateProtocol

**Description**: Protocol for verification gate implementations.

    Implementations must verify that target nodes exist before allowing
    modifications. This prevents hallucinated fixes from being executed.
    

**Inherits from**: ABC

### Methods

#### verify_action
**Parameters**: self, request
**Returns**: VerificationResult
**Description**: Verify if an action can be performed.

        Args:
            request: Verification request with file path, action type, and target

        Returns:
            VerificationResult indicating success/failure with reason
        

#### is_available
**Parameters**: self
**Returns**: bool
**Description**: Check if verification gate is available and functional.

#### get_supported_actions
**Parameters**: self
**Returns**: list[str]
**Description**: Get list of supported action types.

#### validate_request
**Parameters**: self, request
**Returns**: str | None
**Description**: Validate request parameters.

        Returns:
            Error message if invalid, None if valid
        



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: verify_action

**Parameters**: self, request
**Returns**: VerificationResult
**Description**: Verify if an action can be performed.

        Args:
            request: Verification request with file path, action type, and target

        Returns:
            VerificationResult indicating success/failure with reason
        



## Function: is_available

**Parameters**: self
**Returns**: bool
**Description**: Check if verification gate is available and functional.



## Function: get_supported_actions

**Parameters**: self
**Returns**: list[str]
**Description**: Get list of supported action types.



## Function: validate_request

**Parameters**: self, request
**Returns**: str | None
**Description**: Validate request parameters.

        Returns:
            Error message if invalid, None if valid
        



## Usage Examples

### Class Usage

```python
# Using VerificationRequest
verificationrequest = VerificationRequest()
```

```python
# Using VerificationResult
verificationresult = VerificationResult()
```

```python
# Using VerificationGateProtocol
verificationgateprotocol = VerificationGateProtocol()
verificationgateprotocol.verify_action()
verificationgateprotocol.is_available()
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
# Using verify_action
result = verify_action(request)
```



---
**Generated**: 2026-03-26T09:39:05.597360
**Type**: api_reference
**Quality**: comprehensive
