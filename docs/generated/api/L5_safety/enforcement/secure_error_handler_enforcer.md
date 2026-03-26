# API Documentation: secure_error_handler_enforcer

**Target Audience**: developers, api_users

# secure_error_handler_enforcer API Documentation

**File**: `secure_error_handler_enforcer.py`
**Classes**: 7
**Functions**: 13

## Classes

- **SecureError** (inherits from Exception)
- **SecurityError** (inherits from SecureError)
- **ConfigurationError** (inherits from SecureError)
- **ValidationError** (inherits from SecureError)
- **ExecutionError** (inherits from SecureError)
- **ErrorSanitizer**
- **SecureErrorHandler**

## Functions

- **secure_exception**
- **handle_secure_error** -> SecureError
- **__init__**
- **to_dict** -> dict[str, Any]
- **sanitize_message** -> str
- **sanitize_stack_trace** -> str
- **create_secure_error** -> SecureError
- **decorator**
- **__init__**
- **handle_error** -> SecureError
- **raise_secure** -> None
- **heal_repository** -> dict[str, int]
- **sync_wrapper**


## Class: SecureError

**Description**: Base class for secure errors with sanitized messages.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, message, ErrorCode, context
**Description**: Initialize secure error.

        Args:
            message: Sanitized error message
            ErrorCode: Optional error code for tracking
            context: Optional context dictionary (sanitized)
        

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert error to dictionary for safe serialization.

        Returns:
            Dictionary with error details
        



## Class: SecurityError

**Description**: Raised for security-related errors.

**Inherits from**: SecureError



## Class: ConfigurationError

**Description**: Raised for configuration-related errors.

**Inherits from**: SecureError



## Class: ValidationError

**Description**: Raised for validation errors.

**Inherits from**: SecureError



## Class: ExecutionError

**Description**: Raised for execution errors.

**Inherits from**: SecureError



## Class: ErrorSanitizer

**Description**: Sanitizes error messages to prevent sensitive data leakage.

### Methods

#### sanitize_message
**Parameters**: cls, message
**Returns**: str
**Description**: Sanitize an error message.

        Args:
            message: Original error message

        Returns:
            Sanitized message
        

#### sanitize_stack_trace
**Parameters**: cls, tb_str
**Returns**: str
**Description**: Sanitize a stack trace.

        Args:
            tb_str: Stack trace string

        Returns:
            Sanitized stack trace
        

#### create_secure_error
**Parameters**: cls, error_type, original_error, ErrorCode, add_context
**Returns**: SecureError
**Description**: Create a secure error from an original exception.

        Args:
            error_type: Type of secure error to create
            original_error: Original exception
            ErrorCode: Optional error code
            add_context: Additional context to include

        Returns:
            Secure error instance
        



## Class: SecureErrorHandler

**Description**: Handles errors securely throughout the application.

### Methods

#### __init__
**Parameters**: self, logger_name
**Description**: Initialize the error handler.

        Args:
            logger_name: Name for the secure Logger
        

#### handle_error
**Parameters**: self, error, context, include_stack
**Returns**: SecureError
**Description**: Handle an error securely.

        Args:
            error: The error to handle
            context: Additional context
            include_stack: Whether to include stack trace

        Returns:
            Secure error instance
        

#### raise_secure
**Parameters**: self, error_type, message, ErrorCode, context
**Returns**: None
**Description**: Raise a secure error.

        Args:
            error_type: Type of error to raise
            message: Error message
            ErrorCode: Optional error code
            context: Optional context
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L5 safety agent - operational only.



## Function: secure_exception

**Parameters**: error_type, ErrorCode, sanitize_args
**Description**: Decorator to secure exceptions from functions.

    Args:
        error_type: Type of secure error to raise
        ErrorCode: Optional error code
        sanitize_args: Whether to sanitize function arguments in context

    Returns:
        Decorated function
    



## Function: handle_secure_error

**Parameters**: error, context
**Returns**: SecureError
**Description**: Handle an error using the default secure error handler.

    Args:
        error: Error to handle
        context: Optional context

    Returns:
        Secure error instance
    



## Function: __init__

**Parameters**: self, message, ErrorCode, context
**Description**: Initialize secure error.

        Args:
            message: Sanitized error message
            ErrorCode: Optional error code for tracking
            context: Optional context dictionary (sanitized)
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert error to dictionary for safe serialization.

        Returns:
            Dictionary with error details
        



## Function: sanitize_message

**Parameters**: cls, message
**Returns**: str
**Description**: Sanitize an error message.

        Args:
            message: Original error message

        Returns:
            Sanitized message
        



## Function: sanitize_stack_trace

**Parameters**: cls, tb_str
**Returns**: str
**Description**: Sanitize a stack trace.

        Args:
            tb_str: Stack trace string

        Returns:
            Sanitized stack trace
        



## Function: create_secure_error

**Parameters**: cls, error_type, original_error, ErrorCode, add_context
**Returns**: SecureError
**Description**: Create a secure error from an original exception.

        Args:
            error_type: Type of secure error to create
            original_error: Original exception
            ErrorCode: Optional error code
            add_context: Additional context to include

        Returns:
            Secure error instance
        



## Function: decorator

**Parameters**: func


## Function: __init__

**Parameters**: self, logger_name
**Description**: Initialize the error handler.

        Args:
            logger_name: Name for the secure Logger
        



## Function: handle_error

**Parameters**: self, error, context, include_stack
**Returns**: SecureError
**Description**: Handle an error securely.

        Args:
            error: The error to handle
            context: Additional context
            include_stack: Whether to include stack trace

        Returns:
            Secure error instance
        



## Function: raise_secure

**Parameters**: self, error_type, message, ErrorCode, context
**Returns**: None
**Description**: Raise a secure error.

        Args:
            error_type: Type of error to raise
            message: Error message
            ErrorCode: Optional error code
            context: Optional context
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L5 safety agent - operational only.



## Function: sync_wrapper



## Usage Examples

### Class Usage

```python
# Using SecureError
secureerror = SecureError()
secureerror.to_dict()
```

```python
# Using SecurityError
securityerror = SecurityError()
```

```python
# Using ConfigurationError
configurationerror = ConfigurationError()
```

### Function Usage

```python
# Using secure_exception
result = secure_exception(error_type, ErrorCode)
```

```python
# Using handle_secure_error
result = handle_secure_error(error, context)
```

```python
# Using __init__
result = __init__(message, ErrorCode)
```



---
**Generated**: 2026-03-26T09:39:04.933247
**Type**: api_reference
**Quality**: comprehensive
