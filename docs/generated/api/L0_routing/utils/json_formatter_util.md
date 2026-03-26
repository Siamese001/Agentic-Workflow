# API Documentation: json_formatter_util

**Target Audience**: developers, api_users

# json_formatter_util API Documentation

**File**: `json_formatter_util.py`
**Classes**: 1
**Functions**: 2

## Classes

- **JSONFormatter** (inherits from <ast.Attribute object at 0x000001CBFCC6A410>)

## Functions

- **setup_logging**
- **format** -> str


## Class: JSONFormatter

**Description**: 
    Formats log records as JSON objects for machine parsing.
    

**Inherits from**: logging.Formatter

### Methods

#### format
**Parameters**: self, record
**Returns**: str



## Function: setup_logging

**Description**: 
    Initialize application-wide logging.
    Call this once at application startup.
    



## Function: format

**Parameters**: self, record
**Returns**: str


## Usage Examples

### Class Usage

```python
# Using JSONFormatter
jsonformatter = JSONFormatter()
jsonformatter.format()
```

### Function Usage

```python
# Using setup_logging
result = setup_logging()
```

```python
# Using format
result = format(record)
```



---
**Generated**: 2026-03-26T09:39:03.534178
**Type**: api_reference
**Quality**: comprehensive
