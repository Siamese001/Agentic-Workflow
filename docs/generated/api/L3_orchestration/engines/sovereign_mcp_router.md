# API Documentation: sovereign_mcp_router

**Target Audience**: developers, api_users

# sovereign_mcp_router API Documentation

**File**: `sovereign_mcp_router.py`
**Classes**: 1
**Functions**: 3

## Classes

- **SovereignMcpRouter** (inherits from SovereignBaseAgent)

## Functions

- **_run_self_tests** -> dict
- **__init__**
- **_get_ValidationContext**


## Class: SovereignMcpRouter

**Description**: Ultra-hardened L3 MCP switchboard — zero tolerance for failure

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, role, config_path

#### _get_ValidationContext
**Description**: Lazy loader for ValidationContext (upward L3->L4 seam).



## Function: _run_self_tests

**Parameters**: self
**Returns**: dict
**Description**: Run internal self-tests.



## Function: __init__

**Parameters**: self, role, config_path


## Function: _get_ValidationContext

**Description**: Lazy loader for ValidationContext (upward L3->L4 seam).



## Usage Examples

### Class Usage

```python
# Using SovereignMcpRouter
sovereignmcprouter = SovereignMcpRouter()
```

### Function Usage

```python
# Using _run_self_tests
result = _run_self_tests()
```

```python
# Using __init__
result = __init__(role, config_path)
```

```python
# Using _get_ValidationContext
result = _get_ValidationContext()
```



---
**Generated**: 2026-03-26T09:39:04.222914
**Type**: api_reference
**Quality**: comprehensive
