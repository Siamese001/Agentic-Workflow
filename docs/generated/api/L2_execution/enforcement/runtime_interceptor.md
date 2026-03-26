# API Documentation: runtime_interceptor

**Target Audience**: developers, api_users

# runtime_interceptor API Documentation

**File**: `runtime_interceptor.py`
**Classes**: 2
**Functions**: 11

## Classes

- **MutableReferenceError** (inherits from RuntimeError)
- **MutableReferenceTracker**

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **assert_immutable_reference** -> None
- **_is_mutable** -> bool
- **_is_allowed_mutable_in_seam** -> bool
- **get_mutable_ref_violations** -> list[str]
- **clear_mutable_ref_violations** -> None
- **immutable_references** -> Callable[..., T]
- **wrapper** -> T
- **__enter__** -> MutableReferenceTracker
- **__exit__** -> None


## Class: MutableReferenceError

**Description**: Raised when a mutable reference is detected outside allowed seams.

**Inherits from**: RuntimeError



## Class: MutableReferenceTracker

**Description**: Context manager for tracking mutable reference violations.

### Methods

#### __enter__
**Parameters**: self
**Returns**: MutableReferenceTracker

#### __exit__
**Parameters**: self, exc_type, exc_val, exc_tb
**Returns**: None



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: payload, target


## Function: assert_immutable_reference

**Parameters**: obj, context
**Returns**: None
**Description**: Assert that an object is immutable or passes through allowed seam.

    Args:
        obj: Object to check for immutability
        context: Context description for error reporting

    Raises:
        MutableReferenceError: If object is mutable and not in allowed seam
    



## Function: _is_mutable

**Parameters**: obj
**Returns**: bool
**Description**: Check if an object is mutable.



## Function: _is_allowed_mutable_in_seam

**Parameters**: obj, context
**Returns**: bool
**Description**: Check if mutable object is allowed in specific seam context.



## Function: get_mutable_ref_violations

**Returns**: list[str]
**Description**: Get list of recorded mutable reference violations.



## Function: clear_mutable_ref_violations

**Returns**: None
**Description**: Clear recorded mutable reference violations.



## Function: immutable_references

**Parameters**: func
**Returns**: Callable[..., T]
**Description**: Decorator to enforce immutable references in function calls.

    Args:
        func: Function to decorate

    Returns:
        Wrapped function that checks arguments for mutability
    



## Function: wrapper

**Returns**: T


## Function: __enter__

**Parameters**: self
**Returns**: MutableReferenceTracker


## Function: __exit__

**Parameters**: self, exc_type, exc_val, exc_tb
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using MutableReferenceError
mutablereferenceerror = MutableReferenceError()
```

```python
# Using MutableReferenceTracker
mutablereferencetracker = MutableReferenceTracker()
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
# Using assert_immutable_reference
result = assert_immutable_reference(obj, context)
```



---
**Generated**: 2026-03-26T09:39:03.725524
**Type**: api_reference
**Quality**: comprehensive
