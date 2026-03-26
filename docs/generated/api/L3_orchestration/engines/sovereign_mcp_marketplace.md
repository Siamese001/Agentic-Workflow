# API Documentation: sovereign_mcp_marketplace

**Target Audience**: developers, api_users

# sovereign_mcp_marketplace API Documentation

**File**: `sovereign_mcp_marketplace.py`
**Classes**: 1
**Functions**: 3

## Classes

- **SovereignMcpMarketplace**

## Functions

- **__init__**
- **discover_and_register_safe** -> None
- **get_safe_tools** -> list[str]


## Class: SovereignMcpMarketplace

**Description**: Ultra-hardened marketplace integration — auto-register safe MCPs only.

### Methods

#### __init__
**Parameters**: self, manager

#### discover_and_register_safe
**Parameters**: self, marketplace_data
**Returns**: None
**Description**: Parse marketplace and register only sovereign-safe MCPs.

#### get_safe_tools
**Parameters**: self
**Returns**: list[str]



## Function: __init__

**Parameters**: self, manager


## Function: discover_and_register_safe

**Parameters**: self, marketplace_data
**Returns**: None
**Description**: Parse marketplace and register only sovereign-safe MCPs.



## Function: get_safe_tools

**Parameters**: self
**Returns**: list[str]


## Usage Examples

### Class Usage

```python
# Using SovereignMcpMarketplace
sovereignmcpmarketplace = SovereignMcpMarketplace()
sovereignmcpmarketplace.discover_and_register_safe()
sovereignmcpmarketplace.get_safe_tools()
```

### Function Usage

```python
# Using __init__
result = __init__(manager)
```

```python
# Using discover_and_register_safe
result = discover_and_register_safe(marketplace_data)
```

```python
# Using get_safe_tools
result = get_safe_tools()
```



---
**Generated**: 2026-03-26T09:39:04.219416
**Type**: api_reference
**Quality**: comprehensive
