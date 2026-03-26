# API Documentation: derived

**Target Audience**: developers, api_users

# derived API Documentation

**File**: `derived.py`
**Classes**: 0
**Functions**: 6


## Functions

- **_derive_depth_rules** -> dict[str, int]
- **_derive_core_subfolder_map** -> dict[str, list[str]]
- **_derive_subfolder_metadata** -> dict[str, dict[str, Any]]
- **_derive_apps_subfolder_map** -> dict[str, list[str]]
- **_derive_tests_subfolder_map** -> dict[str, list[str]]
- **verify_derived_registries** -> list[str]


## Function: _derive_depth_rules

**Returns**: dict[str, int]
**Description**: Derive DEPTH_RULES from territory definitions.



## Function: _derive_core_subfolder_map

**Returns**: dict[str, list[str]]
**Description**: Derive CORE_SUBFOLDER_MAP from territory definitions.



## Function: _derive_subfolder_metadata

**Returns**: dict[str, dict[str, Any]]
**Description**: Derive SUBFOLDER_METADATA from territory definitions.



## Function: _derive_apps_subfolder_map

**Parameters**: territory_name
**Returns**: dict[str, list[str]]
**Description**: Derive APPS_*_SUBFOLDER_MAP from territory definitions.



## Function: _derive_tests_subfolder_map

**Returns**: dict[str, list[str]]
**Description**: Build tests subfolder map from the SSOT territory declaration.

    Territory definitions use mappingproxy objects (not plain dicts), so we
    check for a 'keys' attribute (Mapping duck-type) rather than isinstance(dict).
    



## Function: verify_derived_registries

**Returns**: list[str]
**Description**: Verify derived registries are consistent with SOVEREIGN_TERRITORIES.



## Usage Examples

### Function Usage

```python
# Using _derive_depth_rules
result = _derive_depth_rules()
```

```python
# Using _derive_core_subfolder_map
result = _derive_core_subfolder_map()
```

```python
# Using _derive_subfolder_metadata
result = _derive_subfolder_metadata()
```



---
**Generated**: 2026-03-26T09:39:05.917073
**Type**: api_reference
**Quality**: comprehensive
