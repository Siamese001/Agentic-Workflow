# API Documentation: side_effect_guard

**Target Audience**: developers, api_users

# side_effect_guard API Documentation

**File**: `side_effect_guard.py`
**Classes**: 2
**Functions**: 14

## Classes

- **UnverifiedSideEffectError** (inherits from RuntimeError)
- **SideEffectGuard**

## Functions

- **get_side_effect_guard** -> SideEffectGuard
- **require_verified** -> VerificationContext
- **set_verification_context** -> None
- **clear_verification_context** -> None
- **requires_verification**
- **__init__**
- **set_context** -> None
- **clear_context** -> None
- **require_verified** -> VerificationContext
- **disable** -> None
- **enable** -> None
- **has_context** -> bool
- **decorator**
- **wrapper**


## Class: UnverifiedSideEffectError

**Description**: Raised when side-effect is attempted without verification.

**Inherits from**: RuntimeError



## Class: SideEffectGuard

**Description**: Guard that enforces verification before side effects.

### Methods

#### __init__
**Parameters**: self

#### set_context
**Parameters**: self, context
**Returns**: None
**Description**: Set the active verification context.

#### clear_context
**Parameters**: self
**Returns**: None
**Description**: Clear the active verification context.

#### require_verified
**Parameters**: self, operation
**Returns**: VerificationContext
**Description**: 
        Require verified context before proceeding.

        Raises UnverifiedSideEffectError if no verified context is active.
        

#### disable
**Parameters**: self
**Returns**: None
**Description**: Disable the guard (for testing only).

#### enable
**Parameters**: self
**Returns**: None
**Description**: Enable the guard.

#### has_context
**Parameters**: self
**Returns**: bool
**Description**: Check if a verified context is currently active.



## Function: get_side_effect_guard

**Returns**: SideEffectGuard
**Description**: Get the global side-effect guard instance.



## Function: require_verified

**Parameters**: operation
**Returns**: VerificationContext
**Description**: 
    Require verified context before proceeding with side effect.

    Convenience function that raises UnverifiedSideEffectError if
    no verified context is active.
    



## Function: set_verification_context

**Parameters**: context
**Returns**: None
**Description**: Set the global verification context.



## Function: clear_verification_context

**Returns**: None
**Description**: Clear the global verification context.



## Function: requires_verification

**Parameters**: operation_name
**Description**: Decorator to require verification before function execution.



## Function: __init__

**Parameters**: self


## Function: set_context

**Parameters**: self, context
**Returns**: None
**Description**: Set the active verification context.



## Function: clear_context

**Parameters**: self
**Returns**: None
**Description**: Clear the active verification context.



## Function: require_verified

**Parameters**: self, operation
**Returns**: VerificationContext
**Description**: 
        Require verified context before proceeding.

        Raises UnverifiedSideEffectError if no verified context is active.
        



## Function: disable

**Parameters**: self
**Returns**: None
**Description**: Disable the guard (for testing only).



## Function: enable

**Parameters**: self
**Returns**: None
**Description**: Enable the guard.



## Function: has_context

**Parameters**: self
**Returns**: bool
**Description**: Check if a verified context is currently active.



## Function: decorator

**Parameters**: func


## Function: wrapper



## Usage Examples

### Class Usage

```python
# Using UnverifiedSideEffectError
unverifiedsideeffecterror = UnverifiedSideEffectError()
```

```python
# Using SideEffectGuard
sideeffectguard = SideEffectGuard()
sideeffectguard.set_context()
sideeffectguard.clear_context()
```

### Function Usage

```python
# Using get_side_effect_guard
result = get_side_effect_guard()
```

```python
# Using require_verified
result = require_verified(operation)
```

```python
# Using set_verification_context
result = set_verification_context(context)
```



---
**Generated**: 2026-03-26T09:39:05.469356
**Type**: api_reference
**Quality**: comprehensive
