# API Documentation: gemini_spy_util

**Target Audience**: developers, api_users

# gemini_spy_util API Documentation

**File**: `gemini_spy_util.py`
**Classes**: 1
**Functions**: 4

## Classes

- **GeminiSpy**

## Functions

- **__init__**
- **record_call** -> None
- **get_call_count** -> int
- **clear** -> None


## Class: GeminiSpy

**Description**: Monitors Gemini API calls for observability.

### Methods

#### __init__
**Parameters**: self

#### record_call
**Parameters**: self, endpoint, request, response
**Returns**: None
**Description**: Record a Gemini API call.

#### get_call_count
**Parameters**: self
**Returns**: int
**Description**: Get total number of recorded calls.

#### clear
**Parameters**: self
**Returns**: None
**Description**: Clear recorded calls.



## Function: __init__

**Parameters**: self


## Function: record_call

**Parameters**: self, endpoint, request, response
**Returns**: None
**Description**: Record a Gemini API call.



## Function: get_call_count

**Parameters**: self
**Returns**: int
**Description**: Get total number of recorded calls.



## Function: clear

**Parameters**: self
**Returns**: None
**Description**: Clear recorded calls.



## Usage Examples

### Class Usage

```python
# Using GeminiSpy
geminispy = GeminiSpy()
geminispy.record_call()
geminispy.get_call_count()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using record_call
result = record_call(endpoint, request)
```

```python
# Using get_call_count
result = get_call_count()
```



---
**Generated**: 2026-03-26T09:39:04.064759
**Type**: api_reference
**Quality**: comprehensive
