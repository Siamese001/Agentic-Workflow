# API Documentation: hierarchy_validator_enforcer

**Target Audience**: developers, api_users

# hierarchy_validator_enforcer API Documentation

**File**: `hierarchy_validator_enforcer.py`
**Classes**: 1
**Functions**: 6

## Classes

- **HierarchyValidator**

## Functions

- **get_hierarchy_validator** -> HierarchyValidator
- **__init__** -> None
- **_load_and_validate** -> dict[str, Any]
- **get_layer_level** -> int
- **is_import_allowed** -> bool
- **_matches** -> bool


## Class: HierarchyValidator

**Description**: Loads, validates, and hashes the layer hierarchy configuration.

### Methods

#### __init__
**Parameters**: self, config_path
**Returns**: None

#### _load_and_validate
**Parameters**: self, raw
**Returns**: dict[str, Any]

#### get_layer_level
**Parameters**: self, module_name
**Returns**: int
**Description**: Return numeric hierarchy level for module_name (-1 = external/unknown).

#### is_import_allowed
**Parameters**: self, source, target
**Returns**: bool
**Description**: Return True iff import from source to target is permitted by policy.

#### _matches
**Parameters**: module, pattern
**Returns**: bool



## Function: get_hierarchy_validator

**Parameters**: config_path
**Returns**: HierarchyValidator
**Description**: Return the global HierarchyValidator (lazy-initialized from default path).



## Function: __init__

**Parameters**: self, config_path
**Returns**: None


## Function: _load_and_validate

**Parameters**: self, raw
**Returns**: dict[str, Any]


## Function: get_layer_level

**Parameters**: self, module_name
**Returns**: int
**Description**: Return numeric hierarchy level for module_name (-1 = external/unknown).



## Function: is_import_allowed

**Parameters**: self, source, target
**Returns**: bool
**Description**: Return True iff import from source to target is permitted by policy.



## Function: _matches

**Parameters**: module, pattern
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using HierarchyValidator
hierarchyvalidator = HierarchyValidator()
hierarchyvalidator.get_layer_level()
hierarchyvalidator.is_import_allowed()
```

### Function Usage

```python
# Using get_hierarchy_validator
result = get_hierarchy_validator(config_path)
```

```python
# Using __init__
result = __init__(config_path)
```

```python
# Using _load_and_validate
result = _load_and_validate(raw)
```



---
**Generated**: 2026-03-26T09:39:04.838173
**Type**: api_reference
**Quality**: comprehensive
