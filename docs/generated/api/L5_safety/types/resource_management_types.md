# API Documentation: resource_management_types

**Target Audience**: developers, api_users

# resource_management_types API Documentation

**File**: `resource_management_types.py`
**Classes**: 4
**Functions**: 8

## Classes

- **ResourceType** (inherits from Enum)
- **ResourceQuota**
- **ResourceCheckResult**
- **ResourceManagementGuardrail**

## Functions

- **remaining** -> float
- **usage_percent** -> float
- **__init__**
- **calculate_cost** -> float
- **set_quota** -> None
- **reset_quotas** -> None
- **get_quota_status** -> dict[str, Any]
- **get_statistics** -> dict[str, Any]


## Class: ResourceType

**Description**: Types of managed resources.

**Inherits from**: Enum



## Class: ResourceQuota

**Description**: Resource quota definition.

### Methods

#### remaining
**Parameters**: self
**Returns**: float

#### usage_percent
**Parameters**: self
**Returns**: float



## Class: ResourceCheckResult

**Description**: Result of resource check.



## Class: ResourceManagementGuardrail

**Description**: 
    Consolidated Resource Management Guardrail.

    Provides unified resource control with:
    - Cost limits and budgeting
    - Resource quotas (tokens, API calls, memory)
    - Control plane management
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize resource management guardrail.

#### calculate_cost
**Parameters**: self, model, tokens
**Returns**: float
**Description**: 
        Calculate cost for token usage.

        Args:
            model: Model name
            tokens: Number of tokens

        Returns:
            Cost in USD
        

#### set_quota
**Parameters**: self, resource_type, limit
**Returns**: None
**Description**: Set quota for resource type.

#### reset_quotas
**Parameters**: self
**Returns**: None
**Description**: Reset all quota usage.

#### get_quota_status
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get status of all quotas.

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get resource management statistics.



## Function: remaining

**Parameters**: self
**Returns**: float


## Function: usage_percent

**Parameters**: self
**Returns**: float


## Function: __init__

**Parameters**: self
**Description**: Initialize resource management guardrail.



## Function: calculate_cost

**Parameters**: self, model, tokens
**Returns**: float
**Description**: 
        Calculate cost for token usage.

        Args:
            model: Model name
            tokens: Number of tokens

        Returns:
            Cost in USD
        



## Function: set_quota

**Parameters**: self, resource_type, limit
**Returns**: None
**Description**: Set quota for resource type.



## Function: reset_quotas

**Parameters**: self
**Returns**: None
**Description**: Reset all quota usage.



## Function: get_quota_status

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get status of all quotas.



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get resource management statistics.



## Usage Examples

### Class Usage

```python
# Using ResourceType
resourcetype = ResourceType()
```

```python
# Using ResourceQuota
resourcequota = ResourceQuota()
resourcequota.remaining()
resourcequota.usage_percent()
```

```python
# Using ResourceCheckResult
resourcecheckresult = ResourceCheckResult()
```

### Function Usage

```python
# Using remaining
result = remaining()
```

```python
# Using usage_percent
result = usage_percent()
```

```python
# Using __init__
result = __init__()
```



---
**Generated**: 2026-03-26T09:39:05.547302
**Type**: api_reference
**Quality**: comprehensive
