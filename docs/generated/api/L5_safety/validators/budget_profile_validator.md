# API Documentation: budget_profile_validator

**Target Audience**: developers, api_users

# budget_profile_validator API Documentation

**File**: `budget_profile_validator.py`
**Classes**: 1
**Functions**: 1

## Classes

- **BudgetProfile** (inherits from BaseModel)

## Functions

- **validate_latency** -> int


## Class: BudgetProfile

**Description**: High-level budget profile for cost/latency envelopes.

    This duplicates some of the fields from ExecutionProfileSpec so that
    future callers can reason about budget in a single nested object.
    

**Inherits from**: BaseModel

### Methods

#### validate_latency
**Parameters**: cls, value
**Returns**: int
**Description**: [HARDENED] Ensure latency ceiling is positive.



## Function: validate_latency

**Parameters**: cls, value
**Returns**: int
**Description**: [HARDENED] Ensure latency ceiling is positive.



## Usage Examples

### Class Usage

```python
# Using BudgetProfile
budgetprofile = BudgetProfile()
budgetprofile.validate_latency()
```

### Function Usage

```python
# Using validate_latency
result = validate_latency(cls, value)
```



---
**Generated**: 2026-03-26T09:39:05.744561
**Type**: api_reference
**Quality**: comprehensive
