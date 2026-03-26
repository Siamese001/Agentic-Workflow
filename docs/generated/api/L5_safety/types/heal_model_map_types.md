# API Documentation: heal_model_map_types

**Target Audience**: developers, api_users

# heal_model_map_types API Documentation

**File**: `heal_model_map_types.py`
**Classes**: 0
**Functions**: 1


## Functions

- **map_tier_to_model_id** -> str


## Function: map_tier_to_model_id

**Parameters**: tier
**Returns**: str
**Description**: Map a reasoning tier to a model identifier.

    Args:
        tier: The reasoning tier (LOW or HIGH)

    Returns:
        Model identifier string ("local_low" or "local_high")
    



## Usage Examples

### Function Usage

```python
# Using map_tier_to_model_id
result = map_tier_to_model_id(tier)
```



---
**Generated**: 2026-03-26T09:39:05.516671
**Type**: api_reference
**Quality**: comprehensive
