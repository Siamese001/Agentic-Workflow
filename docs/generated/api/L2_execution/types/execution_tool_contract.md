# API Documentation: execution_tool_contract

**Target Audience**: developers, api_users

# execution_tool_contract API Documentation

**File**: `execution_tool_contract.py`
**Classes**: 3
**Functions**: 6

## Classes

- **ToolCategory** (inherits from str, Enum)
- **ToolCapabilityDescriptor**
- **ToolContract**

## Functions

- **register_tool_capability** -> None
- **get_tool_capability** -> ToolCapabilityDescriptor | None
- **registered_tools** -> list[str]
- **capability_hash** -> str
- **create** -> ToolContract
- **to_dict** -> dict[str, Any]


## Class: ToolCategory

**Description**: High-level category of a tool.

**Inherits from**: str, Enum



## Class: ToolCapabilityDescriptor

**Description**: Capability metadata for a single tool.

### Methods

#### capability_hash
**Parameters**: self
**Returns**: str



## Class: ToolContract

**Description**: Typed, immutable contract for a single tool invocation.

    Every L2 tool dispatch must be expressed as a ToolContract so
    that the ADG can trace ``execution_terminates_at_uwg`` edges.

    Usage::

        contract = ToolContract.create(
            tool_name="file_system.write",
            category=ToolCategory.FILE_SYSTEM,
            args={"path": "artifacts/out.json", "data": "{}"},
            trace_id=current_trace_id,
        )
        uwg.execute_from_contract(contract)
    

### Methods

#### create
**Parameters**: cls, tool_name, category, args, trace_id, requires_sandbox, metadata, capability_descriptor
**Returns**: ToolContract

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Function: register_tool_capability

**Parameters**: descriptor
**Returns**: None
**Description**: Register a tool's capability descriptor globally.



## Function: get_tool_capability

**Parameters**: tool_name
**Returns**: ToolCapabilityDescriptor | None
**Description**: Return the registered capability descriptor for ``tool_name``.



## Function: registered_tools

**Returns**: list[str]


## Function: capability_hash

**Parameters**: self
**Returns**: str


## Function: create

**Parameters**: cls, tool_name, category, args, trace_id, requires_sandbox, metadata, capability_descriptor
**Returns**: ToolContract


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Usage Examples

### Class Usage

```python
# Using ToolCategory
toolcategory = ToolCategory()
```

```python
# Using ToolCapabilityDescriptor
toolcapabilitydescriptor = ToolCapabilityDescriptor()
toolcapabilitydescriptor.capability_hash()
```

```python
# Using ToolContract
toolcontract = ToolContract()
toolcontract.create()
toolcontract.to_dict()
```

### Function Usage

```python
# Using register_tool_capability
result = register_tool_capability(descriptor)
```

```python
# Using get_tool_capability
result = get_tool_capability(tool_name)
```

```python
# Using registered_tools
result = registered_tools()
```



---
**Generated**: 2026-03-26T09:39:03.955366
**Type**: api_reference
**Quality**: comprehensive
