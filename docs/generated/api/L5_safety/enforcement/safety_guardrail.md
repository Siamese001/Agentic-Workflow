# API Documentation: safety_guardrail

**Target Audience**: developers, api_users

# safety_guardrail API Documentation

**File**: `safety_guardrail.py`
**Classes**: 1
**Functions**: 2

## Classes

- **SafetyGuardrail**

## Functions

- **__init__**
- **verify_change** -> tuple[bool, str]


## Class: SafetyGuardrail

**Description**: Enforces Zero-Loss principles during mutation.

### Methods

#### __init__
**Parameters**: self, deletion_limit
**Description**: 
        Initialize SafetyGuardrail.

        Args:
            deletion_limit: Maximum number of lines that can be deleted in standard mode
        

#### verify_change
**Parameters**: self, original_code, new_code, fission_active
**Returns**: tuple[bool, str]
**Description**: 
        Verify that code changes are safe and don't violate zero-loss principles.

        Args:
            original_code: Original code before mutation
            new_code: New code after mutation
            fission_active: Whether atomic fission is active (allows mass deletion)

        Returns:
            Tuple of (is_safe, message)
        



## Function: __init__

**Parameters**: self, deletion_limit
**Description**: 
        Initialize SafetyGuardrail.

        Args:
            deletion_limit: Maximum number of lines that can be deleted in standard mode
        



## Function: verify_change

**Parameters**: self, original_code, new_code, fission_active
**Returns**: tuple[bool, str]
**Description**: 
        Verify that code changes are safe and don't violate zero-loss principles.

        Args:
            original_code: Original code before mutation
            new_code: New code after mutation
            fission_active: Whether atomic fission is active (allows mass deletion)

        Returns:
            Tuple of (is_safe, message)
        



## Usage Examples

### Class Usage

```python
# Using SafetyGuardrail
safetyguardrail = SafetyGuardrail()
safetyguardrail.verify_change()
```

### Function Usage

```python
# Using __init__
result = __init__(deletion_limit)
```

```python
# Using verify_change
result = verify_change(original_code, new_code)
```



---
**Generated**: 2026-03-26T09:39:04.922877
**Type**: api_reference
**Quality**: comprehensive
