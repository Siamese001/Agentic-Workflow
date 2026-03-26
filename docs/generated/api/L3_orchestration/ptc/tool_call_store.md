# API Documentation: tool_call_store

**Target Audience**: developers, api_users

# tool_call_store API Documentation

**File**: `tool_call_store.py`
**Classes**: 1
**Functions**: 8

## Classes

- **ToolCallStore**

## Functions

- **get_tool_call_store** -> ToolCallStore
- **record_tool_call** -> StoredArtifactRef
- **list_tool_calls** -> list[dict[str, Any]]
- **__init__**
- **record_call** -> StoredArtifactRef
- **list_calls** -> list[dict[str, Any]]
- **get_call** -> dict[str, Any] | None
- **_get_code_commit** -> str


## Class: ToolCallStore

**Description**: Append-only storage for tool call records.

### Methods

#### __init__
**Parameters**: self, root_dir
**Description**: Initialize with persistent store.

        Args:
            root_dir: Root directory for storage (defaults to repo root/docs/store)
        

#### record_call
**Parameters**: self, call, result, spec, policy
**Returns**: StoredArtifactRef
**Description**: Record a tool call and its result.

        Args:
            call: Tool call that was made
            result: Result of the tool call
            spec: Tool specification
            policy: Policy used for the call

        Returns:
            Reference to stored artifact
        

#### list_calls
**Parameters**: self, tool_id, limit
**Returns**: list[dict[str, Any]]
**Description**: List stored tool calls.

        Args:
            tool_id: Optional tool ID filter
            limit: Maximum number of calls to return

        Returns:
            List of tool call records
        

#### get_call
**Parameters**: self, tool_id, call_id
**Returns**: dict[str, Any] | None
**Description**: Get a specific tool call record.

        Args:
            tool_id: Tool identifier
            call_id: Call identifier

        Returns:
            Tool call record or None if not found
        

#### _get_code_commit
**Parameters**: self
**Returns**: str
**Description**: Get current git commit hash.

        Returns:
            Git commit hash or "unknown"
        



## Function: get_tool_call_store

**Returns**: ToolCallStore
**Description**: Get the global tool call store.

    Returns:
        Global ToolCallStore instance
    



## Function: record_tool_call

**Parameters**: call, result, spec, policy
**Returns**: StoredArtifactRef
**Description**: Record a tool call in the global store.

    Args:
        call: Tool call that was made
        result: Result of the tool call
        spec: Tool specification
        policy: Policy used for the call

    Returns:
        Reference to stored artifact
    



## Function: list_tool_calls

**Parameters**: tool_id, limit
**Returns**: list[dict[str, Any]]
**Description**: List tool calls from the global store.

    Args:
        tool_id: Optional tool ID filter
        limit: Maximum number of calls to return

    Returns:
        List of tool call records
    



## Function: __init__

**Parameters**: self, root_dir
**Description**: Initialize with persistent store.

        Args:
            root_dir: Root directory for storage (defaults to repo root/docs/store)
        



## Function: record_call

**Parameters**: self, call, result, spec, policy
**Returns**: StoredArtifactRef
**Description**: Record a tool call and its result.

        Args:
            call: Tool call that was made
            result: Result of the tool call
            spec: Tool specification
            policy: Policy used for the call

        Returns:
            Reference to stored artifact
        



## Function: list_calls

**Parameters**: self, tool_id, limit
**Returns**: list[dict[str, Any]]
**Description**: List stored tool calls.

        Args:
            tool_id: Optional tool ID filter
            limit: Maximum number of calls to return

        Returns:
            List of tool call records
        



## Function: get_call

**Parameters**: self, tool_id, call_id
**Returns**: dict[str, Any] | None
**Description**: Get a specific tool call record.

        Args:
            tool_id: Tool identifier
            call_id: Call identifier

        Returns:
            Tool call record or None if not found
        



## Function: _get_code_commit

**Parameters**: self
**Returns**: str
**Description**: Get current git commit hash.

        Returns:
            Git commit hash or "unknown"
        



## Usage Examples

### Class Usage

```python
# Using ToolCallStore
toolcallstore = ToolCallStore()
toolcallstore.record_call()
toolcallstore.list_calls()
```

### Function Usage

```python
# Using get_tool_call_store
result = get_tool_call_store()
```

```python
# Using record_tool_call
result = record_tool_call(call, result)
```

```python
# Using list_tool_calls
result = list_tool_calls(tool_id, limit)
```



---
**Generated**: 2026-03-26T09:39:04.248013
**Type**: api_reference
**Quality**: comprehensive
