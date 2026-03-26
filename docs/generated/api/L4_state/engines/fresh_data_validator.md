# API Documentation: fresh_data_validator

**Target Audience**: developers, api_users

# fresh_data_validator API Documentation

**File**: `fresh_data_validator.py`
**Classes**: 3
**Functions**: 2

## Classes

- **StaleDataViolation** (inherits from Exception)
- **FreshnessPolicy**
- **VersionedData**

## Functions

- **validate_freshness** -> None
- **__init__**


## Class: StaleDataViolation

**Description**: Raised when data is served that is older than the freshness policy allows.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, data_timestamp, policy_max_age



## Class: FreshnessPolicy

**Description**: Defines the freshness window for a piece of data.



## Class: VersionedData

**Description**: Represents a piece of data with a timestamp for freshness validation.



## Function: validate_freshness

**Parameters**: data, policy
**Returns**: None
**Description**: 
    Validates that a piece of versioned data is not stale.

    This function enforces Guarantee #11 (Fresh data only at runtime) by comparing
    the data's timestamp against a configurable freshness window. It is a critical
    sovereign gate in L4 to prevent the use of outdated context or knowledge.

    Args:
        data: The versioned data to validate.
        policy: The freshness policy to apply.

    Raises:
        StaleDataViolation: If the data's timestamp is older than the allowed max age.
    



## Function: __init__

**Parameters**: self, data_timestamp, policy_max_age


## Usage Examples

### Class Usage

```python
# Using StaleDataViolation
staledataviolation = StaleDataViolation()
```

```python
# Using FreshnessPolicy
freshnesspolicy = FreshnessPolicy()
```

```python
# Using VersionedData
versioneddata = VersionedData()
```

### Function Usage

```python
# Using validate_freshness
result = validate_freshness(data, policy)
```

```python
# Using __init__
result = __init__(data_timestamp, policy_max_age)
```



---
**Generated**: 2026-03-26T09:39:04.535096
**Type**: api_reference
**Quality**: comprehensive
