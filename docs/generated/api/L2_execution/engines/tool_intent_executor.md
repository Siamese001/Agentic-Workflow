# API Documentation: tool_intent_executor

**Target Audience**: developers, api_users

# tool_intent_executor API Documentation

**File**: `tool_intent_executor.py`
**Classes**: 2
**Functions**: 9

## Classes

- **ToolResult**
- **ToolIntentExecutor**

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **_sha256** -> str
- **__post_init__** -> None
- **canonical_bytes** -> bytes
- **to_dict** -> dict[str, Any]
- **__enter__** -> Generator[ToolIntentExecutor, None, None]
- **__exit__** -> None
- **execute** -> ToolResult


## Class: ToolResult

**Description**: 
    Typed result of a ToolIntent execution.

    Fields
    ------
    schema_version : int   — bumped on breaking changes
    tool_name      : str   — matches the originating ToolIntent.tool_name
    args_hash      : str   — matches the originating ToolIntent.args_hash
    success        : bool  — True if execution completed without error
    output_summary : str   — deterministic string summary of the output
    anchor_ids     : list  — chunk_ids of any retrieved content (may be empty)
    result_hash    : str   — sha256(canonical_bytes excluding result_hash)
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Deterministic serialisation excluding result_hash (self-referential).

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: ToolIntentExecutor

**Description**: 
    Executes a ToolIntent inside the L2.2 commit sandbox.

    Usage
    -----
    with ToolIntentExecutor() as executor:
        result = executor.execute(intent, fn=my_tool_fn)

    Guarantees
    ----------
    - If intent.requires_commit and sandbox not active → ToolViolation("TOOL_WRITE_OUTSIDE_SANDBOX")
    - Non-mutating intents (requires_commit=False) may be executed anywhere.
    - fn is called with intent.args; must return a dict with at least "output_summary".
    

### Methods

#### __enter__
**Parameters**: self
**Returns**: Generator[ToolIntentExecutor, None, None]

#### __exit__
**Parameters**: self
**Returns**: None

#### execute
**Parameters**: self, intent, fn
**Returns**: ToolResult
**Description**: 
        Execute a ToolIntent.

        Parameters
        ----------
        intent : ToolIntent
        fn     : callable(args: dict) -> dict
            Must return a dict with at least "output_summary" (str) and
            optionally "anchor_ids" (list[str]).

        Raises
        ------
        ToolViolation(code="TOOL_WRITE_OUTSIDE_SANDBOX")
            If intent.requires_commit and sandbox is not active.
        



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: payload, target


## Function: _sha256

**Parameters**: data
**Returns**: str


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: Deterministic serialisation excluding result_hash (self-referential).



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: __enter__

**Parameters**: self
**Returns**: Generator[ToolIntentExecutor, None, None]


## Function: __exit__

**Parameters**: self
**Returns**: None


## Function: execute

**Parameters**: self, intent, fn
**Returns**: ToolResult
**Description**: 
        Execute a ToolIntent.

        Parameters
        ----------
        intent : ToolIntent
        fn     : callable(args: dict) -> dict
            Must return a dict with at least "output_summary" (str) and
            optionally "anchor_ids" (list[str]).

        Raises
        ------
        ToolViolation(code="TOOL_WRITE_OUTSIDE_SANDBOX")
            If intent.requires_commit and sandbox is not active.
        



## Usage Examples

### Class Usage

```python
# Using ToolResult
toolresult = ToolResult()
toolresult.canonical_bytes()
toolresult.to_dict()
```

```python
# Using ToolIntentExecutor
toolintentexecutor = ToolIntentExecutor()
toolintentexecutor.execute()
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
# Using _sha256
result = _sha256(data)
```



---
**Generated**: 2026-03-26T09:39:03.773609
**Type**: api_reference
**Quality**: comprehensive
