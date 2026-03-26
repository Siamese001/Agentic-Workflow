# API Documentation: _constants

**Target Audience**: developers, api_users

# _constants API Documentation

**File**: `_constants.py`
**Classes**: 2
**Functions**: 4

## Classes

- **SubfolderDefinition** (inherits from TypedDict)
- **TerritoryDefinition** (inherits from TypedDict)

## Functions

- **_build_lcd_subfolders_template** -> dict[str, SubfolderDefinition]
- **_build_layer_definition** -> dict[str, Any]
- **build_sovereign_territories** -> dict[str, TerritoryDefinition]
- **_deep_freeze** -> Any


## Class: SubfolderDefinition

**Inherits from**: TypedDict



## Class: TerritoryDefinition

**Inherits from**: TypedDict



## Function: _build_lcd_subfolders_template

**Returns**: dict[str, SubfolderDefinition]
**Description**: Build the common LCD subfolder template shared by all layers.



## Function: _build_layer_definition

**Parameters**: layer_name
**Returns**: dict[str, Any]
**Description**: Build a complete layer definition from template + overrides.



## Function: build_sovereign_territories

**Returns**: dict[str, TerritoryDefinition]
**Description**: Build the complete SOVEREIGN_TERRITORIES from templates + overrides.

    DEPRECATED: This function and SOVEREIGN_TERRITORIES are deprecated.
    Use the new territory API in territories.py instead:
    - get_territory_metadata(name) for single territory lookup
    - get_all_territories() for full territory map
    - is_valid_root_folder(name) for root validation
    



## Function: _deep_freeze

**Parameters**: obj
**Returns**: Any
**Description**: Recursively convert mutable containers to immutable equivalents.

    - dict  → MappingProxyType (wrapping recursed values)
    - list  → tuple (of recursed elements)
    - set   → frozenset (of recursed elements)
    - other → returned as-is (str, int, bool, None, etc.)
    



## Usage Examples

### Class Usage

```python
# Using SubfolderDefinition
subfolderdefinition = SubfolderDefinition()
```

```python
# Using TerritoryDefinition
territorydefinition = TerritoryDefinition()
```

### Function Usage

```python
# Using _build_lcd_subfolders_template
result = _build_lcd_subfolders_template()
```

```python
# Using _build_layer_definition
result = _build_layer_definition(layer_name)
```

```python
# Using build_sovereign_territories
result = build_sovereign_territories()
```



---
**Generated**: 2026-03-26T09:39:05.958442
**Type**: api_reference
**Quality**: comprehensive
