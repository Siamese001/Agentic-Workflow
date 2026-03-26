# API Documentation: tool_contract

**Target Audience**: developers, api_users

# tool_contract API Documentation

**File**: `tool_contract.py`
**Classes**: 4
**Functions**: 11

## Classes

- **ToolArg**
- **ToolSpec**
- **ToolCall**
- **ToolCallResult**

## Functions

- **canonical_json** -> str
- **sha256_hex** -> str
- **generate_call_id** -> str
- **hash_result_data** -> dict[str, str]
- **tool_spec_to_json** -> str
- **tool_call_to_json** -> str
- **tool_call_result_to_json** -> str
- **__post_init__**
- **__post_init__**
- **__post_init__**
- **__post_init__**


## Class: ToolArg

**Description**: Immutable argument specification for a tool.

### Methods

#### __post_init__
**Parameters**: self
**Description**: Validate argument specification.



## Class: ToolSpec

**Description**: Immutable specification for a tool.

### Methods

#### __post_init__
**Parameters**: self
**Description**: Validate tool specification.



## Class: ToolCall

**Description**: Immutable tool call invocation.

### Methods

#### __post_init__
**Parameters**: self
**Description**: Validate tool call.



## Class: ToolCallResult

**Description**: Immutable result of a tool call.

### Methods

#### __post_init__
**Parameters**: self
**Description**: Validate tool call result.



## Function: canonical_json

**Parameters**: obj
**Returns**: str
**Description**: Serialize object to canonical JSON.

    Args:
        obj: Object to serialize

    Returns:
        Canonical JSON string
    



## Function: sha256_hex

**Parameters**: data
**Returns**: str
**Description**: Calculate SHA256 hash of string data.

    Args:
        data: String data to hash

    Returns:
        Hexadecimal SHA256 hash
    



## Function: generate_call_id

**Parameters**: tool_id, args
**Returns**: str
**Description**: Generate deterministic call ID from tool ID and arguments.

    Args:
        tool_id: Tool identifier
        args: Tool arguments

    Returns:
        SHA256 hash for call ID
    



## Function: hash_result_data

**Parameters**: result
**Returns**: dict[str, str]
**Description**: Generate hashes for result data.

    Args:
        result: Tool call result

    Returns:
        Dictionary with hashes
    



## Function: tool_spec_to_json

**Parameters**: spec
**Returns**: str
**Description**: Serialize ToolSpec to deterministic JSON.



## Function: tool_call_to_json

**Parameters**: call
**Returns**: str
**Description**: Serialize ToolCall to deterministic JSON.



## Function: tool_call_result_to_json

**Parameters**: result
**Returns**: str
**Description**: Serialize ToolCallResult to deterministic JSON.



## Function: __post_init__

**Parameters**: self
**Description**: Validate argument specification.



## Function: __post_init__

**Parameters**: self
**Description**: Validate tool specification.



## Function: __post_init__

**Parameters**: self
**Description**: Validate tool call.



## Function: __post_init__

**Parameters**: self
**Description**: Validate tool call result.



## Usage Examples

### Class Usage

```python
# Using ToolArg
toolarg = ToolArg()
```

```python
# Using ToolSpec
toolspec = ToolSpec()
```

```python
# Using ToolCall
toolcall = ToolCall()
```

### Function Usage

```python
# Using canonical_json
result = canonical_json(obj)
```

```python
# Using sha256_hex
result = sha256_hex(data)
```

```python
# Using generate_call_id
result = generate_call_id(tool_id, args)
```



---
**Generated**: 2026-03-26T09:39:04.249045
**Type**: api_reference
**Quality**: comprehensive
