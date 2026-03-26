# API Documentation: sovereign_filesystem_mcp

**Target Audience**: developers, api_users

# sovereign_filesystem_mcp API Documentation

**File**: `sovereign_filesystem_mcp.py`
**Classes**: 1
**Functions**: 4

## Classes

- **SovereignFilesystemMcp**

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **__init__**
- **_validate_path** -> str


## Class: SovereignFilesystemMcp

**Description**: Ultra-hardened filesystem client — enforcing atomic sovereignty.

### Methods

#### __init__
**Parameters**: self, manager, mission_id

#### _validate_path
**Parameters**: self, path
**Returns**: str
**Description**: L5 path sovereignty check. Blocks traversals and absolute escapes.



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: payload, target


## Function: __init__

**Parameters**: self, manager, mission_id


## Function: _validate_path

**Parameters**: self, path
**Returns**: str
**Description**: L5 path sovereignty check. Blocks traversals and absolute escapes.



## Usage Examples

### Class Usage

```python
# Using SovereignFilesystemMcp
sovereignfilesystemmcp = SovereignFilesystemMcp()
```

### Function Usage

```python
# Using _invoke_authorize_and_execute
result = _invoke_authorize_and_execute(execution_context, target_callable)
```

```python
# Using _make_execution_context
result = _make_execution_context(payload, target)
```

```python
# Using __init__
result = __init__(manager, mission_id)
```



---
**Generated**: 2026-03-26T09:39:03.734265
**Type**: api_reference
**Quality**: comprehensive
