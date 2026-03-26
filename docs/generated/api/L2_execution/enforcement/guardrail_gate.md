# API Documentation: guardrail_gate

**Target Audience**: developers, api_users

# guardrail_gate API Documentation

**File**: `guardrail_gate.py`
**Classes**: 4
**Functions**: 14

## Classes

- **GuardrailVerdict** (inherits from str, Enum)
- **GuardrailCheckResult**
- **GuardrailViolationError** (inherits from PermissionError)
- **GuardrailGate**

## Functions

- **get_guardrail_gate** -> GuardrailGate
- **reset_guardrail_gate** -> None
- **allowed** -> bool
- **__init__** -> None
- **__init__** -> None
- **block_operation** -> None
- **check** -> GuardrailCheckResult
- **applies_guardrail**
- **guardrail_check** -> Callable
- **audit_log** -> list[GuardrailCheckResult]
- **allow_count** -> int
- **deny_count** -> int
- **decorator** -> Callable
- **wrapper**


## Class: GuardrailVerdict

**Description**: Result of a guardrail check.

**Inherits from**: str, Enum



## Class: GuardrailCheckResult

**Description**: Immutable result of a guardrail pre-execution check.

### Methods

#### allowed
**Parameters**: self
**Returns**: bool



## Class: GuardrailViolationError

**Description**: Raised when a guardrail check denies an operation.

**Inherits from**: PermissionError

### Methods

#### __init__
**Parameters**: self, result
**Returns**: None



## Class: GuardrailGate

**Description**: Pre-execution guardrail gate for L2 operations.

    All L2 modules with ``writes_to`` or ``calls`` edges should call
    ``check()`` (or use ``guarded_call()``) before performing the operation.

    Usage — explicit::

        gate = GuardrailGate(policy_hash="abc123")
        result = gate.check("write", "artifacts/output.json")
        if not result.allowed:
            raise GuardrailViolationError(result)

    Usage — context manager::

        with gate.applies_guardrail("write", "artifacts/output.json"):
            do_write(...)

    Usage — decorator::

        @gate.guardrail_check("execute", "tool/run_python")
        def run_python(self, code: str) -> str:
            ...
    

### Methods

#### __init__
**Parameters**: self, policy_hash, strict_mode
**Returns**: None

#### block_operation
**Parameters**: self, operation
**Returns**: None
**Description**: Register an operation as explicitly blocked.

#### check
**Parameters**: self, operation, target, metadata
**Returns**: GuardrailCheckResult
**Description**: Perform a guardrail pre-check for ``operation`` on ``target``.

        Returns a :class:`GuardrailCheckResult`.  In strict mode, raises
        :class:`GuardrailViolationError` if the verdict is DENY.
        

#### applies_guardrail
**Parameters**: self, operation, target, metadata
**Description**: Context manager: check guardrail before executing body.

        Satisfies the ``applies_guardrail`` ADG edge contract.
        

#### guardrail_check
**Parameters**: self, operation, target, metadata
**Returns**: Callable
**Description**: Decorator: apply guardrail check before every call.

        Usage::

            @gate.guardrail_check("write", "artifacts/")
            def save_result(self, data: dict) -> None:
                ...
        

#### audit_log
**Parameters**: self
**Returns**: list[GuardrailCheckResult]
**Description**: Return a copy of all guardrail check results.

#### allow_count
**Parameters**: self
**Returns**: int

#### deny_count
**Parameters**: self
**Returns**: int



## Function: get_guardrail_gate

**Parameters**: policy_hash
**Returns**: GuardrailGate
**Description**: Return the process-level guardrail gate.



## Function: reset_guardrail_gate

**Returns**: None
**Description**: Reset the global guardrail gate (for testing).



## Function: allowed

**Parameters**: self
**Returns**: bool


## Function: __init__

**Parameters**: self, result
**Returns**: None


## Function: __init__

**Parameters**: self, policy_hash, strict_mode
**Returns**: None


## Function: block_operation

**Parameters**: self, operation
**Returns**: None
**Description**: Register an operation as explicitly blocked.



## Function: check

**Parameters**: self, operation, target, metadata
**Returns**: GuardrailCheckResult
**Description**: Perform a guardrail pre-check for ``operation`` on ``target``.

        Returns a :class:`GuardrailCheckResult`.  In strict mode, raises
        :class:`GuardrailViolationError` if the verdict is DENY.
        



## Function: applies_guardrail

**Parameters**: self, operation, target, metadata
**Description**: Context manager: check guardrail before executing body.

        Satisfies the ``applies_guardrail`` ADG edge contract.
        



## Function: guardrail_check

**Parameters**: self, operation, target, metadata
**Returns**: Callable
**Description**: Decorator: apply guardrail check before every call.

        Usage::

            @gate.guardrail_check("write", "artifacts/")
            def save_result(self, data: dict) -> None:
                ...
        



## Function: audit_log

**Parameters**: self
**Returns**: list[GuardrailCheckResult]
**Description**: Return a copy of all guardrail check results.



## Function: allow_count

**Parameters**: self
**Returns**: int


## Function: deny_count

**Parameters**: self
**Returns**: int


## Function: decorator

**Parameters**: fn
**Returns**: Callable


## Function: wrapper



## Usage Examples

### Class Usage

```python
# Using GuardrailVerdict
guardrailverdict = GuardrailVerdict()
```

```python
# Using GuardrailCheckResult
guardrailcheckresult = GuardrailCheckResult()
guardrailcheckresult.allowed()
```

```python
# Using GuardrailViolationError
guardrailviolationerror = GuardrailViolationError()
```

### Function Usage

```python
# Using get_guardrail_gate
result = get_guardrail_gate(policy_hash)
```

```python
# Using reset_guardrail_gate
result = reset_guardrail_gate()
```

```python
# Using allowed
result = allowed()
```



---
**Generated**: 2026-03-26T09:39:03.705137
**Type**: api_reference
**Quality**: comprehensive
