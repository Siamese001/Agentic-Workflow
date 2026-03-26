# API Documentation: ptc_tool_contracts_types

**Target Audience**: developers, api_users

# ptc_tool_contracts_types API Documentation

**File**: `ptc_tool_contracts_types.py`
**Classes**: 3
**Functions**: 3

## Classes

- **ToolContractViolation** (inherits from ValueError)
- **ToolCall**
- **ToolResult**

## Functions

- **__post_init__** -> None
- **__post_init__** -> None
- **from_budget_enforcer** -> ToolResult


## Class: ToolContractViolation

**Description**: Raised when a ToolResult violates exit_code or stdout_bytes contract.

**Inherits from**: ValueError



## Class: ToolCall

**Description**: Represents a single tool invocation request.

    Spec: Contract [3] PTC ToolCall.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: ToolResult

**Description**: Immutable result of a single tool invocation.

    Spec: Contract [3] PTC ToolResult — stdout-only, exit_code in {0, 1}.

    Constraints enforced at construction:
      - exit_code MUST be 0 or 1 (no other values permitted)
      - len(stdout) MUST be <= stdout_bytes_cap when cap is provided
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### from_budget_enforcer
**Parameters**: cls, exit_code, stdout_bytes, stdout_bytes_cap
**Returns**: ToolResult
**Description**: Construct and validate ToolResult from BudgetEnforcer output.

        Raises ToolContractViolation if exit_code or stdout length violates contract.
        



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: from_budget_enforcer

**Parameters**: cls, exit_code, stdout_bytes, stdout_bytes_cap
**Returns**: ToolResult
**Description**: Construct and validate ToolResult from BudgetEnforcer output.

        Raises ToolContractViolation if exit_code or stdout length violates contract.
        



## Usage Examples

### Class Usage

```python
# Using ToolContractViolation
toolcontractviolation = ToolContractViolation()
```

```python
# Using ToolCall
toolcall = ToolCall()
```

```python
# Using ToolResult
toolresult = ToolResult()
toolresult.from_budget_enforcer()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using from_budget_enforcer
result = from_budget_enforcer(cls, exit_code)
```



---
**Generated**: 2026-03-26T09:39:03.995266
**Type**: api_reference
**Quality**: comprehensive
