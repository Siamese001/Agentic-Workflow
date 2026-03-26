# API Documentation: typed_tool_contract

**Target Audience**: developers, api_users

# typed_tool_contract API Documentation

**File**: `typed_tool_contract.py`
**Classes**: 11
**Functions**: 32

## Classes

- **ToolInputSchemaViolation** (inherits from ValueError)
- **ToolOutputSchemaViolation** (inherits from ValueError)
- **UnregisteredToolError** (inherits from RuntimeError)
- **UntypedToolExecutionError** (inherits from RuntimeError)
- **MissingToolContractError** (inherits from RuntimeError)
- **ToolSchema**
- **ToolRegistryEntry**
- **ToolContract**
- **ToolContractResult**
- **TypedToolRegistry**
- **ToolContractStore**

## Functions

- **invoke_typed_tool** -> ToolContractResult
- **get_typed_tool_registry** -> TypedToolRegistry
- **get_tool_contract_store** -> ToolContractStore
- **reset_typed_tool_registry** -> None
- **reset_tool_contract_store** -> None
- **_sha256** -> str
- **_persist_contract_result** -> None
- **to_dict** -> dict[str, Any]
- **hash** -> str
- **validate** -> list[str]
- **allows_caller** -> bool
- **meets_policy** -> bool
- **create** -> ToolContract
- **with_output** -> ToolContract
- **tool_contract_id** -> str
- **__init__** -> None
- **register** -> None
- **get** -> ToolRegistryEntry | None
- **is_registered** -> bool
- **all_entries** -> list[ToolRegistryEntry]
- **tool_names** -> list[str]
- **__init__** -> None
- **ingest** -> None
- **by_run_id** -> list[ToolContractResult]
- **by_trace_id** -> list[ToolContractResult]
- **by_tool_name** -> list[ToolContractResult]
- **by_action_class** -> list[ToolContractResult]
- **all_results** -> list[ToolContractResult]
- **missing_input_schema_hash** -> list[ToolContractResult]
- **missing_output_schema_hash** -> list[ToolContractResult]
- **uncontracted_executions** -> list[ToolContractResult]
- **result_count** -> int


## Class: ToolInputSchemaViolation

**Description**: Raised when tool input fails schema validation (spec §6 fail-closed).

    Gate B enforcement: tool_contract_id + input_schema_hash required.
    

**Inherits from**: ValueError



## Class: ToolOutputSchemaViolation

**Description**: Raised when tool output fails schema validation (spec §6 fail-closed).

    Gate C enforcement: output missing required fields must fail closed.
    

**Inherits from**: ValueError



## Class: UnregisteredToolError

**Description**: Raised when a tool is not present in the TypedToolRegistry.

    Gate D enforcement: only registered tools may execute.
    

**Inherits from**: RuntimeError



## Class: UntypedToolExecutionError

**Description**: Raised when a governed tool path uses getattr/importlib resolution.

    Gate E enforcement: prohibit getattr-style/importlib tool invocation.
    

**Inherits from**: RuntimeError



## Class: MissingToolContractError

**Description**: Raised when a governed tool executes without a ToolContract.

    Gate A enforcement: no uncontracted tool execution.
    

**Inherits from**: RuntimeError



## Class: ToolSchema

**Description**: Typed schema for tool input or output.

    required_fields: field names that must be present in payload.
    optional_fields: field names that may be present.
    schema_version:  version identifier for schema evolution.
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]

#### hash
**Parameters**: self
**Returns**: str

#### validate
**Parameters**: self, payload
**Returns**: list[str]
**Description**: Return list of missing required fields. Empty list = valid.



## Class: ToolRegistryEntry

**Description**: Registry entry for one tool version.

    Spec §4 fields: tool_name, tool_version, input_schema, output_schema,
    action_class, allowed_callers, policy_requirements.
    

### Methods

#### allows_caller
**Parameters**: self, caller_agent_id
**Returns**: bool
**Description**: Return True if caller is allowed (wildcard '*' allows all).

#### meets_policy
**Parameters**: self, policy_hash
**Returns**: bool
**Description**: Return True if no policy requirements or policy_hash present.



## Class: ToolContract

**Description**: Immutable typed tool contract — 12 required spec fields (spec §2).

    Created before every governed tool invocation.
    

### Methods

#### create
**Parameters**: cls
**Returns**: ToolContract

#### with_output
**Parameters**: self, output_payload
**Returns**: ToolContract
**Description**: Return a new ToolContract with output_payload_hash populated.



## Class: ToolContractResult

**Description**: Result of a typed tool invocation with full contract linkage.

### Methods

#### tool_contract_id
**Parameters**: self
**Returns**: str



## Class: TypedToolRegistry

**Description**: Thread-safe registry of typed tool definitions.

    Spec §4: only registered tools may execute (Gate D).
    Provides lookup by tool_name (latest version) or (tool_name, tool_version).
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### register
**Parameters**: self, entry
**Returns**: None
**Description**: Register a tool entry. Re-registration of same name+version overwrites.

#### get
**Parameters**: self, tool_name, tool_version
**Returns**: ToolRegistryEntry | None
**Description**: Lookup by (name, version). 'latest' returns highest lexicographic version.

#### is_registered
**Parameters**: self, tool_name, tool_version
**Returns**: bool

#### all_entries
**Parameters**: self
**Returns**: list[ToolRegistryEntry]

#### tool_names
**Parameters**: self
**Returns**: list[str]



## Class: ToolContractStore

**Description**: In-memory queryable store for all emitted ToolContractResult instances.

    Queryable by run_id, trace_id, tool_name, action_class.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### ingest
**Parameters**: self, result
**Returns**: None

#### by_run_id
**Parameters**: self, run_id
**Returns**: list[ToolContractResult]

#### by_trace_id
**Parameters**: self, trace_id
**Returns**: list[ToolContractResult]

#### by_tool_name
**Parameters**: self, tool_name
**Returns**: list[ToolContractResult]

#### by_action_class
**Parameters**: self, action_class
**Returns**: list[ToolContractResult]

#### all_results
**Parameters**: self
**Returns**: list[ToolContractResult]

#### missing_input_schema_hash
**Parameters**: self
**Returns**: list[ToolContractResult]
**Description**: Results where input_schema_hash is empty (Gate B violation).

#### missing_output_schema_hash
**Parameters**: self
**Returns**: list[ToolContractResult]
**Description**: Results where output_schema_hash is empty (Gate C violation).

#### uncontracted_executions
**Parameters**: self
**Returns**: list[ToolContractResult]
**Description**: Results without a tool_contract_id (Gate A violation).

#### result_count
**Parameters**: self
**Returns**: int



## Function: invoke_typed_tool

**Parameters**: tool_contract, typed_input
**Returns**: ToolContractResult
**Description**: Mandatory typed tool entrypoint — P2/L2 spec §3.

    Steps (in order, all mandatory):
      1. validate input against declared schema
      2. verify tool registry entry (UnregisteredToolError if absent)
      3. bind policy hash
      4. execute tool
      5. validate output against declared schema (fail-closed on missing fields)
      6. persist tool contract result

    Args:
        tool_contract:  Pre-built ToolContract (all 12 fields required).
        typed_input:    Dict payload that must satisfy input_schema.
        registry:       TypedToolRegistry to verify registration (uses global if None).
        tool_callable:  Callable to execute; falls back to registry entry callable.

    Returns:
        ToolContractResult with completed contract and typed output.

    Raises:
        MissingToolContractError:  tool_contract_id is empty.
        ToolInputSchemaViolation:  input fails schema validation.
        UnregisteredToolError:     tool not found in registry.
        ToolOutputSchemaViolation: output missing required schema fields.
    



## Function: get_typed_tool_registry

**Returns**: TypedToolRegistry
**Description**: Return the process-level TypedToolRegistry singleton.



## Function: get_tool_contract_store

**Returns**: ToolContractStore
**Description**: Return the process-level ToolContractStore singleton.



## Function: reset_typed_tool_registry

**Returns**: None
**Description**: Reset global registry (for testing).



## Function: reset_tool_contract_store

**Returns**: None
**Description**: Reset global store (for testing).



## Function: _sha256

**Parameters**: value
**Returns**: str


## Function: _persist_contract_result

**Parameters**: result
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: hash

**Parameters**: self
**Returns**: str


## Function: validate

**Parameters**: self, payload
**Returns**: list[str]
**Description**: Return list of missing required fields. Empty list = valid.



## Function: allows_caller

**Parameters**: self, caller_agent_id
**Returns**: bool
**Description**: Return True if caller is allowed (wildcard '*' allows all).



## Function: meets_policy

**Parameters**: self, policy_hash
**Returns**: bool
**Description**: Return True if no policy requirements or policy_hash present.



## Function: create

**Parameters**: cls
**Returns**: ToolContract


## Function: with_output

**Parameters**: self, output_payload
**Returns**: ToolContract
**Description**: Return a new ToolContract with output_payload_hash populated.



## Function: tool_contract_id

**Parameters**: self
**Returns**: str


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: register

**Parameters**: self, entry
**Returns**: None
**Description**: Register a tool entry. Re-registration of same name+version overwrites.



## Function: get

**Parameters**: self, tool_name, tool_version
**Returns**: ToolRegistryEntry | None
**Description**: Lookup by (name, version). 'latest' returns highest lexicographic version.



## Function: is_registered

**Parameters**: self, tool_name, tool_version
**Returns**: bool


## Function: all_entries

**Parameters**: self
**Returns**: list[ToolRegistryEntry]


## Function: tool_names

**Parameters**: self
**Returns**: list[str]


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: ingest

**Parameters**: self, result
**Returns**: None


## Function: by_run_id

**Parameters**: self, run_id
**Returns**: list[ToolContractResult]


## Function: by_trace_id

**Parameters**: self, trace_id
**Returns**: list[ToolContractResult]


## Function: by_tool_name

**Parameters**: self, tool_name
**Returns**: list[ToolContractResult]


## Function: by_action_class

**Parameters**: self, action_class
**Returns**: list[ToolContractResult]


## Function: all_results

**Parameters**: self
**Returns**: list[ToolContractResult]


## Function: missing_input_schema_hash

**Parameters**: self
**Returns**: list[ToolContractResult]
**Description**: Results where input_schema_hash is empty (Gate B violation).



## Function: missing_output_schema_hash

**Parameters**: self
**Returns**: list[ToolContractResult]
**Description**: Results where output_schema_hash is empty (Gate C violation).



## Function: uncontracted_executions

**Parameters**: self
**Returns**: list[ToolContractResult]
**Description**: Results without a tool_contract_id (Gate A violation).



## Function: result_count

**Parameters**: self
**Returns**: int


## Usage Examples

### Class Usage

```python
# Using ToolInputSchemaViolation
toolinputschemaviolation = ToolInputSchemaViolation()
```

```python
# Using ToolOutputSchemaViolation
tooloutputschemaviolation = ToolOutputSchemaViolation()
```

```python
# Using UnregisteredToolError
unregisteredtoolerror = UnregisteredToolError()
```

### Function Usage

```python
# Using invoke_typed_tool
result = invoke_typed_tool(tool_contract, typed_input)
```

```python
# Using get_typed_tool_registry
result = get_typed_tool_registry()
```

```python
# Using get_tool_contract_store
result = get_tool_contract_store()
```



---
**Generated**: 2026-03-26T09:39:03.652391
**Type**: api_reference
**Quality**: comprehensive
