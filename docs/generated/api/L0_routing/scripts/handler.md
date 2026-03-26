# API Documentation: handler

**Target Audience**: developers, api_users

# handler API Documentation

**File**: `handler.py`
**Classes**: 1
**Functions**: 4

## Classes

- **Handler** (inherits from <ast.Attribute object at 0x000001CBFADB2D50>)

## Functions

- **debug_dashboard**
- **serve**
- **__init__**
- **log_message**


## Class: Handler

**Inherits from**: http.server.SimpleHTTPRequestHandler

### Methods

#### __init__
**Parameters**: self

#### log_message
**Parameters**: self, format



## Function: debug_dashboard

**Description**: Use Playwright to deeply inspect dashboard loading.



## Function: serve



## Function: __init__

**Parameters**: self


## Function: log_message

**Parameters**: self, format


## Usage Examples

### Class Usage

```python
# Using Handler
handler = Handler()
handler.log_message()
```

### Function Usage

```python
# Using debug_dashboard
result = debug_dashboard()
```

```python
# Using serve
result = serve()
```

```python
# Using __init__
result = __init__()
```



---
**Generated**: 2026-03-26T09:39:03.158706
**Type**: api_reference
**Quality**: comprehensive
