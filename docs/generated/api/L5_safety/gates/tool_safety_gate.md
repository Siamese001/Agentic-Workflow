# API Documentation: tool_safety_gate

**Target Audience**: developers, api_users

# tool_safety_gate API Documentation

**File**: `tool_safety_gate.py`
**Classes**: 4
**Functions**: 15

## Classes

- **ToolRiskLevel** (inherits from str, Enum)
- **ToolInvocationRecord**
- **ToolNotSandboxedError** (inherits from PermissionError)
- **ToolSafetyGate**

## Functions

- **get_tool_safety_gate** -> ToolSafetyGate
- **reset_tool_safety_gate** -> None
- **__init__** -> None
- **_trace_id** -> str
- **_classify** -> ToolRiskLevel
- **check_tool** -> ToolInvocationRecord
- **enters_sandbox**
- **guarded_tool** -> Callable
- **validate_by_safety_plane** -> bool
- **audit_log** -> list[ToolInvocationRecord]
- **allow_count** -> int
- **deny_count** -> int
- **sandboxed_count** -> int
- **decorator** -> Callable
- **wrapper**


## Class: ToolRiskLevel

**Description**: Risk classification for tool invocations.

**Inherits from**: str, Enum



## Class: ToolInvocationRecord

**Description**: Audit record for a single tool invocation through the safety gate.



## Class: ToolNotSandboxedError

**Description**: Raised when a CRITICAL tool is invoked outside a sandbox.

**Inherits from**: PermissionError



## Class: ToolSafetyGate

**Description**: Pre-invocation safety gate for all L5 tool calls.

    Wraps ``invokes_eval``, ``invokes_dynamic``, ``external_http_call``,
    and other high-risk operations with policy enforcement and optional
    sandbox isolation.

    Usage::

        gate = ToolSafetyGate(policy_hash="abc123")

        # Context manager
        with gate.enters_sandbox("eval", ToolRiskLevel.CRITICAL):
            result = eval(code)

        # Decorator
        @gate.guarded_tool("external_http_call", ToolRiskLevel.HIGH)
        def call_api(self, url: str) -> dict:
            ...

        # Explicit
        record = gate.check_tool("run_python", ToolRiskLevel.HIGH)
    

### Methods

#### __init__
**Parameters**: self, policy_hash, require_sandbox_for_critical, pep
**Returns**: None

#### _trace_id
**Parameters**: self
**Returns**: str

#### _classify
**Parameters**: self, tool_name, risk_level
**Returns**: ToolRiskLevel

#### check_tool
**Parameters**: self, tool_name, risk_level, sandboxed, metadata
**Returns**: ToolInvocationRecord
**Description**: Check whether ``tool_name`` may be invoked.

        Performs policy enforcement point check and sandbox validation.
        Returns a :class:`ToolInvocationRecord`.
        

#### enters_sandbox
**Parameters**: self, tool_name, risk_level, metadata
**Description**: Context manager: declare sandbox boundary for a tool invocation.

        Satisfies the ``enters_sandbox`` + ``applies_guardrail`` ADG edge
        contracts from L5.
        

#### guarded_tool
**Parameters**: self, tool_name, risk_level, sandboxed
**Returns**: Callable
**Description**: Decorator: apply tool safety gate before every invocation.

        Usage::

            @gate.guarded_tool("eval", ToolRiskLevel.CRITICAL, sandboxed=True)
            def run_eval(self, code: str) -> Any:
                return eval(code)
        

#### validate_by_safety_plane
**Parameters**: self, tool_name, metadata
**Returns**: bool
**Description**: Validate a tool invocation against the safety plane.

        Emits ``validated_by_safety_plane`` ADG edge. Returns True if
        the safety plane approves the invocation.
        

#### audit_log
**Parameters**: self
**Returns**: list[ToolInvocationRecord]

#### allow_count
**Parameters**: self
**Returns**: int

#### deny_count
**Parameters**: self
**Returns**: int

#### sandboxed_count
**Parameters**: self
**Returns**: int



## Function: get_tool_safety_gate

**Parameters**: policy_hash
**Returns**: ToolSafetyGate
**Description**: Return the process-level ToolSafetyGate.



## Function: reset_tool_safety_gate

**Returns**: None
**Description**: Reset the global gate (for testing).



## Function: __init__

**Parameters**: self, policy_hash, require_sandbox_for_critical, pep
**Returns**: None


## Function: _trace_id

**Parameters**: self
**Returns**: str


## Function: _classify

**Parameters**: self, tool_name, risk_level
**Returns**: ToolRiskLevel


## Function: check_tool

**Parameters**: self, tool_name, risk_level, sandboxed, metadata
**Returns**: ToolInvocationRecord
**Description**: Check whether ``tool_name`` may be invoked.

        Performs policy enforcement point check and sandbox validation.
        Returns a :class:`ToolInvocationRecord`.
        



## Function: enters_sandbox

**Parameters**: self, tool_name, risk_level, metadata
**Description**: Context manager: declare sandbox boundary for a tool invocation.

        Satisfies the ``enters_sandbox`` + ``applies_guardrail`` ADG edge
        contracts from L5.
        



## Function: guarded_tool

**Parameters**: self, tool_name, risk_level, sandboxed
**Returns**: Callable
**Description**: Decorator: apply tool safety gate before every invocation.

        Usage::

            @gate.guarded_tool("eval", ToolRiskLevel.CRITICAL, sandboxed=True)
            def run_eval(self, code: str) -> Any:
                return eval(code)
        



## Function: validate_by_safety_plane

**Parameters**: self, tool_name, metadata
**Returns**: bool
**Description**: Validate a tool invocation against the safety plane.

        Emits ``validated_by_safety_plane`` ADG edge. Returns True if
        the safety plane approves the invocation.
        



## Function: audit_log

**Parameters**: self
**Returns**: list[ToolInvocationRecord]


## Function: allow_count

**Parameters**: self
**Returns**: int


## Function: deny_count

**Parameters**: self
**Returns**: int


## Function: sandboxed_count

**Parameters**: self
**Returns**: int


## Function: decorator

**Parameters**: fn
**Returns**: Callable


## Function: wrapper



## Usage Examples

### Class Usage

```python
# Using ToolRiskLevel
toolrisklevel = ToolRiskLevel()
```

```python
# Using ToolInvocationRecord
toolinvocationrecord = ToolInvocationRecord()
```

```python
# Using ToolNotSandboxedError
toolnotsandboxederror = ToolNotSandboxedError()
```

### Function Usage

```python
# Using get_tool_safety_gate
result = get_tool_safety_gate(policy_hash)
```

```python
# Using reset_tool_safety_gate
result = reset_tool_safety_gate()
```

```python
# Using __init__
result = __init__(policy_hash, require_sandbox_for_critical)
```



---
**Generated**: 2026-03-26T09:39:04.996658
**Type**: api_reference
**Quality**: comprehensive
