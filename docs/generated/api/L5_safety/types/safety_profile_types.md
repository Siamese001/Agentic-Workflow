# API Documentation: safety_profile_types

**Target Audience**: developers, api_users

# safety_profile_types API Documentation

**File**: `safety_profile_types.py`
**Classes**: 1
**Functions**: 1

## Classes

- **SafetyProfile** (inherits from BaseModel)

## Functions

- **validate_safety_tier** -> str


## Class: SafetyProfile

**Description**: Safety configuration profile used by execution profiles.

    This is intentionally string/primitive based to avoid cycles and
    mirrors the SafetyTier + policy toggles used in ExecutionProfileSpec.
    

**Inherits from**: BaseModel

### Methods

#### validate_safety_tier
**Parameters**: cls, v
**Returns**: str
**Description**: [HARDENED] Ensure safety tier is valid.



## Function: validate_safety_tier

**Parameters**: cls, v
**Returns**: str
**Description**: [HARDENED] Ensure safety tier is valid.



## Usage Examples

### Class Usage

```python
# Using SafetyProfile
safetyprofile = SafetyProfile()
safetyprofile.validate_safety_tier()
```

### Function Usage

```python
# Using validate_safety_tier
result = validate_safety_tier(cls, v)
```



---
**Generated**: 2026-03-26T09:39:05.556212
**Type**: api_reference
**Quality**: comprehensive
