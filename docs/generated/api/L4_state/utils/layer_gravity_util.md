# API Documentation: layer_gravity_util

**Target Audience**: developers, api_users

# layer_gravity_util API Documentation

**File**: `layer_gravity_util.py`
**Classes**: 0
**Functions**: 5


## Functions

- **extract_layer_from_path** -> str | None
- **extract_layer_from_module** -> str | None
- **is_gravity_violation** -> bool
- **get_allowed_layers** -> set[str]
- **get_layer_order** -> int


## Function: extract_layer_from_path

**Parameters**: path
**Returns**: str | None
**Description**: 
    Extract layer identifier from file path.

    Args:
        path: File path (Path object or string)

    Returns:
        Layer identifier (e.g., "L5") or None if not in a layer

    Example:
        >>> extract_layer_from_path("agentic_core/L5_safety/validators/GovernanceAgent.py")
        'L5'
        >>> extract_layer_from_path("apps_rg/engines/tool.py")
        None
    



## Function: extract_layer_from_module

**Parameters**: module
**Returns**: str | None
**Description**: 
    Extract layer identifier from module path.

    Args:
        module: Module path (e.g., "agentic_core.L3_orchestration.reasoning")

    Returns:
        Layer identifier (e.g., "L3") or None if not in a layer

    Example:
        >>> extract_layer_from_module("agentic_core.L3_orchestration.reasoning")
        'L3'
        >>> extract_layer_from_module("apps_shared.common_utils")
        None
    



## Function: is_gravity_violation

**Parameters**: source_layer, target_layer
**Returns**: bool
**Description**: 
    Check if importing target_layer from source_layer violates gravity.

    Gravity violation occurs when a lower layer imports from a higher layer.

    Args:
        source_layer: Layer of the importing file (e.g., "L3")
        target_layer: Layer being imported (e.g., "L5")

    Returns:
        True if this is a gravity violation (upward import)

    Example:
        >>> is_gravity_violation("L3", "L5")  # L3 importing L5
        True
        >>> is_gravity_violation("L5", "L3")  # L5 importing L3
        False
        >>> is_gravity_violation("L3", "L3")  # Same layer
        False
    



## Function: get_allowed_layers

**Parameters**: source_layer
**Returns**: set[str]
**Description**: 
    Get the set of layers that a source layer is allowed to import from.

    Args:
        source_layer: Layer of the importing file

    Returns:
        Set of allowed layer identifiers

    Example:
        >>> get_allowed_layers("L3")
        {'L0', 'L1', 'L2', 'L3'}
    



## Function: get_layer_order

**Parameters**: layer
**Returns**: int
**Description**: 
    Get the numeric order of a layer (lower = more foundational).

    Args:
        layer: Layer identifier (e.g., "L3")

    Returns:
        Numeric order (0-6) or -1 if not a valid layer

    Example:
        >>> get_layer_order("L3")
        3
        >>> get_layer_order("invalid")
        -1
    



## Usage Examples

### Function Usage

```python
# Using extract_layer_from_path
result = extract_layer_from_path(path)
```

```python
# Using extract_layer_from_module
result = extract_layer_from_module(module)
```

```python
# Using is_gravity_violation
result = is_gravity_violation(source_layer, target_layer)
```



---
**Generated**: 2026-03-26T09:39:04.672887
**Type**: api_reference
**Quality**: comprehensive
