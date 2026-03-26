# API Documentation: call_formatting_router

**Target Audience**: developers, api_users

# call_formatting_router API Documentation

**File**: `call_formatting_router.py`
**Classes**: 1
**Functions**: 4

## Classes

- **CallFormattingApi**

## Functions

- **__init__** -> None
- **format** -> FormatResult
- **_transform** -> object
- **FormatData** -> FormatResult


## Class: CallFormattingApi

**Description**: Formatter for resume domain.



## Function: __init__

**Parameters**: self, config
**Returns**: None


## Function: format

**Parameters**: self, data, target
**Returns**: FormatResult
**Description**: Format input data into the required output structure.



## Function: _transform

**Parameters**: self, data
**Returns**: object
**Description**: Transform data.



## Function: FormatData

**Parameters**: data, config
**Returns**: FormatResult
**Description**: Format input data into the required output structure.



## Usage Examples

### Class Usage

```python
# Using CallFormattingApi
callformattingapi = CallFormattingApi()
```

### Function Usage

```python
# Using __init__
result = __init__(config)
```

```python
# Using format
result = format(data, target)
```

```python
# Using _transform
result = _transform(data)
```



---
**Generated**: 2026-03-26T09:39:04.143381
**Type**: api_reference
**Quality**: comprehensive
