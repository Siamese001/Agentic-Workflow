# API Documentation: error_recovery_guardrail

**Target Audience**: developers, api_users

# error_recovery_guardrail API Documentation

**File**: `error_recovery_guardrail.py`
**Classes**: 5
**Functions**: 6

## Classes

- **ErrorCategory** (inherits from Enum)
- **RecoveryStrategy** (inherits from Enum)
- **ErrorContext**
- **RecoveryResult**
- **ErrorRecoveryGuardrail**

## Functions

- **__init__**
- **_classify_error** -> ErrorContext
- **_select_strategy** -> RecoveryStrategy
- **_fallback_recovery** -> RecoveryResult
- **get_statistics** -> dict[str, Any]
- **get_error_log** -> list[dict[str, Any]]


## Class: ErrorCategory

**Description**: Error categories for classification.

**Inherits from**: Enum



## Class: RecoveryStrategy

**Description**: Recovery strategies.

**Inherits from**: Enum



## Class: ErrorContext

**Description**: Context for error recovery.



## Class: RecoveryResult

**Description**: Result of recovery attempt.



## Class: ErrorRecoveryGuardrail

**Description**: 
    Consolidated Error Recovery Guardrail.

    Provides unified error handling with:
    - Error classification by category and severity
    - Recovery strategy selection
    - Self-healing mechanisms
    - Audit trail for all errors
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize error recovery guardrail.

#### _classify_error
**Parameters**: self, error, context
**Returns**: ErrorContext
**Description**: Classify error by category and severity.

#### _select_strategy
**Parameters**: self, error_ctx
**Returns**: RecoveryStrategy
**Description**: Select recovery strategy based on error context.

#### _fallback_recovery
**Parameters**: self, error_ctx
**Returns**: RecoveryResult
**Description**: Fallback recovery strategy.

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get error handling statistics.

#### get_error_log
**Parameters**: self, limit
**Returns**: list[dict[str, Any]]
**Description**: Get recent error log.



## Function: __init__

**Parameters**: self
**Description**: Initialize error recovery guardrail.



## Function: _classify_error

**Parameters**: self, error, context
**Returns**: ErrorContext
**Description**: Classify error by category and severity.



## Function: _select_strategy

**Parameters**: self, error_ctx
**Returns**: RecoveryStrategy
**Description**: Select recovery strategy based on error context.



## Function: _fallback_recovery

**Parameters**: self, error_ctx
**Returns**: RecoveryResult
**Description**: Fallback recovery strategy.



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get error handling statistics.



## Function: get_error_log

**Parameters**: self, limit
**Returns**: list[dict[str, Any]]
**Description**: Get recent error log.



## Usage Examples

### Class Usage

```python
# Using ErrorCategory
errorcategory = ErrorCategory()
```

```python
# Using RecoveryStrategy
recoverystrategy = RecoveryStrategy()
```

```python
# Using ErrorContext
errorcontext = ErrorContext()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using _classify_error
result = _classify_error(error, context)
```

```python
# Using _select_strategy
result = _select_strategy(error_ctx)
```



---
**Generated**: 2026-03-26T09:39:04.815130
**Type**: api_reference
**Quality**: comprehensive
