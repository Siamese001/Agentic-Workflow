# API Documentation: eval_guard

**Target Audience**: developers, api_users

# eval_guard API Documentation

**File**: `eval_guard.py`
**Classes**: 3
**Functions**: 7

## Classes

- **EvalGuardViolation** (inherits from RuntimeError)
- **EvalExecutionDeniedError** (inherits from EvalGuardViolation)
- **EvalGuard**

## Functions

- **get_eval_guard** -> type[EvalGuard]
- **__init__** -> None
- **check** -> dict[str, Any]
- **get_execution_log** -> list[dict[str, Any]]
- **clear_log** -> None
- **mode** -> str
- **_scan** -> list[str]


## Class: EvalGuardViolation

**Description**: Raised when an unauthorized eval/exec call is detected.

**Inherits from**: RuntimeError



## Class: EvalExecutionDeniedError

**Description**: Raised in enforce mode when dangerous code is blocked.

**Inherits from**: EvalGuardViolation



## Class: EvalGuard

**Description**: Guard against unauthorized eval()/exec() usage.

    Modes:
        - ``warn``: log violations but allow execution (default)
        - ``enforce``: raise ``EvalExecutionDeniedError`` on violations
    

### Methods

#### __init__
**Parameters**: self, mode
**Returns**: None

#### check
**Parameters**: self, operation, code
**Returns**: dict[str, Any]
**Description**: Check if code is safe to eval/exec/compile.

        Returns a result dict with ``verdict`` ('allow' or 'deny') and
        optional ``violations`` list.
        

#### get_execution_log
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Return the audit log of all checks.

#### clear_log
**Parameters**: self
**Returns**: None
**Description**: Clear the audit log.

#### mode
**Parameters**: self
**Returns**: str

#### _scan
**Parameters**: code
**Returns**: list[str]
**Description**: Return list of violation descriptions found in *code*.



## Function: get_eval_guard

**Returns**: type[EvalGuard]
**Description**: Get the EvalGuard class.



## Function: __init__

**Parameters**: self, mode
**Returns**: None


## Function: check

**Parameters**: self, operation, code
**Returns**: dict[str, Any]
**Description**: Check if code is safe to eval/exec/compile.

        Returns a result dict with ``verdict`` ('allow' or 'deny') and
        optional ``violations`` list.
        



## Function: get_execution_log

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Return the audit log of all checks.



## Function: clear_log

**Parameters**: self
**Returns**: None
**Description**: Clear the audit log.



## Function: mode

**Parameters**: self
**Returns**: str


## Function: _scan

**Parameters**: code
**Returns**: list[str]
**Description**: Return list of violation descriptions found in *code*.



## Usage Examples

### Class Usage

```python
# Using EvalGuardViolation
evalguardviolation = EvalGuardViolation()
```

```python
# Using EvalExecutionDeniedError
evalexecutiondeniederror = EvalExecutionDeniedError()
```

```python
# Using EvalGuard
evalguard = EvalGuard()
evalguard.check()
evalguard.get_execution_log()
```

### Function Usage

```python
# Using get_eval_guard
result = get_eval_guard()
```

```python
# Using __init__
result = __init__(mode)
```

```python
# Using check
result = check(operation, code)
```



---
**Generated**: 2026-03-26T09:39:04.818693
**Type**: api_reference
**Quality**: comprehensive
