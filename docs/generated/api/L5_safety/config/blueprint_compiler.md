# API Documentation: blueprint_compiler

**Target Audience**: developers, api_users

# blueprint_compiler API Documentation

**File**: `blueprint_compiler.py`
**Classes**: 1
**Functions**: 8

## Classes

- **CompiledBlueprint**

## Functions

- **make_lcd_layer** -> Mapping[str, Any]
- **_extract_subfolder_names** -> list[str]
- **_extract_nested_subfolders** -> Mapping[str, Sequence[str]]
- **_build_subfolder_metadata** -> Mapping[str, Any]
- **_identify_l4_folders** -> tuple[Mapping[str, Mapping[str, Sequence[str]]], frozenset[str]]
- **_identify_variable_depth_subfolders** -> frozenset[str]
- **compile_blueprint** -> CompiledBlueprint
- **verify_blueprint_consistency** -> list[str]


## Class: CompiledBlueprint

**Description**: Immutable compiled blueprint derived from SOVEREIGN_TERRITORIES.



## Function: make_lcd_layer

**Parameters**: layer_name, purpose, extras, forbidden_capabilities, notes
**Returns**: Mapping[str, Any]
**Description**: 
    Generate a standard LCD layer definition with optional extras.

    Args:
        layer_name: e.g., "L0_routing"
        purpose: Layer purpose description
        extras: Additional subfolders beyond the standard 6 (e.g., ["scripts"])
        forbidden_capabilities: Capabilities this layer must not have
        notes: Additional notes

    Returns:
        Layer definition dict suitable for SOVEREIGN_TERRITORIES
    



## Function: _extract_subfolder_names

**Parameters**: subfolders
**Returns**: list[str]
**Description**: Extract subfolder names from various formats in SOVEREIGN_TERRITORIES.



## Function: _extract_nested_subfolders

**Parameters**: subfolders
**Returns**: Mapping[str, Sequence[str]]
**Description**: Extract nested subfolder structure for apps/tests.



## Function: _build_subfolder_metadata

**Parameters**: territory_name, territory_def
**Returns**: Mapping[str, Any]
**Description**: Build metadata entry for a territory.



## Function: _identify_l4_folders

**Parameters**: territories
**Returns**: tuple[Mapping[str, Mapping[str, Sequence[str]]], frozenset[str]]
**Description**: Identify L4-depth folders and their specializations.



## Function: _identify_variable_depth_subfolders

**Parameters**: territories
**Returns**: frozenset[str]
**Description**: Identify subfolders that allow variable depth.



## Function: compile_blueprint

**Parameters**: territories
**Returns**: CompiledBlueprint
**Description**: 
    Compile SOVEREIGN_TERRITORIES into all derived registries.

    This is the core function that eliminates duplication by deriving
    CORE_SUBFOLDER_MAP, SUBFOLDER_METADATA, and other registries from
    the single SSOT.

    Args:
        territories: The SOVEREIGN_TERRITORIES mapping

    Returns:
        CompiledBlueprint with all derived registries
    



## Function: verify_blueprint_consistency

**Parameters**: compiled, legacy_core_map, legacy_metadata
**Returns**: list[str]
**Description**: 
    Verify that compiled blueprint matches legacy registries.

    Returns list of discrepancies (empty if consistent).
    



## Usage Examples

### Class Usage

```python
# Using CompiledBlueprint
compiledblueprint = CompiledBlueprint()
```

### Function Usage

```python
# Using make_lcd_layer
result = make_lcd_layer(layer_name, purpose)
```

```python
# Using _extract_subfolder_names
result = _extract_subfolder_names(subfolders)
```

```python
# Using _extract_nested_subfolders
result = _extract_nested_subfolders(subfolders)
```



---
**Generated**: 2026-03-26T09:39:04.736101
**Type**: api_reference
**Quality**: comprehensive
