# API Documentation: patch_validator

**Target Audience**: developers, api_users

# patch_validator API Documentation

**File**: `patch_validator.py`
**Classes**: 1
**Functions**: 1

## Classes

- **ValidatedPatch**

## Functions

- **validate_patch** -> ValidatedPatch


## Class: ValidatedPatch

**Description**: A patch that has passed HITL validation.



## Function: validate_patch

**Parameters**: patch
**Returns**: ValidatedPatch
**Description**: Validate a MODIFY_DIFF patch has all required HITL fields.

    Raises HumanPatchValidationError if any required field is missing or empty.
    Returns a ValidatedPatch on success.
    



## Usage Examples

### Class Usage

```python
# Using ValidatedPatch
validatedpatch = ValidatedPatch()
```

### Function Usage

```python
# Using validate_patch
result = validate_patch(patch)
```



---
**Generated**: 2026-03-26T09:39:05.014954
**Type**: api_reference
**Quality**: comprehensive
