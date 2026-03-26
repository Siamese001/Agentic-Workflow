# API Documentation: http_guard

**Target Audience**: developers, api_users

# http_guard API Documentation

**File**: `http_guard.py`
**Classes**: 2
**Functions**: 6

## Classes

- **ExternalHttpDeniedError** (inherits from Exception)
- **HTTPGuard**

## Functions

- **get_http_guard** -> HTTPGuard
- **set_http_guard_mode** -> None
- **__init__** -> None
- **check** -> dict[str, Any]
- **get_request_log** -> list[dict[str, Any]]
- **clear_log** -> None


## Class: ExternalHttpDeniedError

**Description**: Raised when an external HTTP call is denied by guardrail.

**Inherits from**: Exception



## Class: HTTPGuard

**Description**: 
    Guardrail for external HTTP call operations.

    Enforces domain allowlist/denylist policy and logging before
    allowing outbound HTTP requests.
    

### Methods

#### __init__
**Parameters**: self, mode
**Returns**: None
**Description**: 
        Initialize HTTPGuard.

        Args:
            mode: "warn" (log violations) or "enforce" (block violations)
        

#### check
**Parameters**: self, operation, url, metadata
**Returns**: dict[str, Any]
**Description**: 
        Pre-request guardrail check for external HTTP operations.

        Args:
            operation: HTTP method ("get", "post", "put", "delete", etc.)
            url: Target URL (if available)
            metadata: Additional context

        Returns:
            dict with verdict and details

        Raises:
            ExternalHttpDeniedError: If request is denied in enforce mode
        

#### get_request_log
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get full request log.

#### clear_log
**Parameters**: self
**Returns**: None
**Description**: Clear request log.



## Function: get_http_guard

**Returns**: HTTPGuard
**Description**: Get global HTTPGuard instance.



## Function: set_http_guard_mode

**Parameters**: mode
**Returns**: None
**Description**: Set global HTTPGuard mode ("warn" or "enforce").



## Function: __init__

**Parameters**: self, mode
**Returns**: None
**Description**: 
        Initialize HTTPGuard.

        Args:
            mode: "warn" (log violations) or "enforce" (block violations)
        



## Function: check

**Parameters**: self, operation, url, metadata
**Returns**: dict[str, Any]
**Description**: 
        Pre-request guardrail check for external HTTP operations.

        Args:
            operation: HTTP method ("get", "post", "put", "delete", etc.)
            url: Target URL (if available)
            metadata: Additional context

        Returns:
            dict with verdict and details

        Raises:
            ExternalHttpDeniedError: If request is denied in enforce mode
        



## Function: get_request_log

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get full request log.



## Function: clear_log

**Parameters**: self
**Returns**: None
**Description**: Clear request log.



## Usage Examples

### Class Usage

```python
# Using ExternalHttpDeniedError
externalhttpdeniederror = ExternalHttpDeniedError()
```

```python
# Using HTTPGuard
httpguard = HTTPGuard()
httpguard.check()
httpguard.get_request_log()
```

### Function Usage

```python
# Using get_http_guard
result = get_http_guard()
```

```python
# Using set_http_guard_mode
result = set_http_guard_mode(mode)
```

```python
# Using __init__
result = __init__(mode)
```



---
**Generated**: 2026-03-26T09:39:04.843369
**Type**: api_reference
**Quality**: comprehensive
