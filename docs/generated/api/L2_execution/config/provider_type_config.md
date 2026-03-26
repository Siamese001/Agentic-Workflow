# API Documentation: provider_type_config

**Target Audience**: developers, api_users

# provider_type_config API Documentation

**File**: `provider_type_config.py`
**Classes**: 1
**Functions**: 3

## Classes

- **ProviderType** (inherits from Enum)

## Functions

- **get_default_module** -> str | None
- **get_default_class** -> str | None
- **register_provider** -> None


## Class: ProviderType

**Description**: Supported MCP Provider types.

**Inherits from**: Enum



## Function: get_default_module

**Parameters**: Provider
**Returns**: str | None
**Description**: Get default module name for a Provider.

    Args:
        Provider: Provider type string

    Returns:
        Module name or None if stub
    



## Function: get_default_class

**Parameters**: Provider
**Returns**: str | None
**Description**: Get default class name for a Provider.

    Args:
        Provider: Provider type string

    Returns:
        Class name or None
    



## Function: register_provider

**Parameters**: Provider, module, class_name
**Returns**: None
**Description**: Register a custom Provider mapping.

    Args:
        Provider: Provider identifier
        module: Python module path
        class_name: Class name within module
    



## Usage Examples

### Class Usage

```python
# Using ProviderType
providertype = ProviderType()
```

### Function Usage

```python
# Using get_default_module
result = get_default_module(Provider)
```

```python
# Using get_default_class
result = get_default_class(Provider)
```

```python
# Using register_provider
result = register_provider(Provider, module)
```



---
**Generated**: 2026-03-26T09:39:03.628990
**Type**: api_reference
**Quality**: comprehensive
