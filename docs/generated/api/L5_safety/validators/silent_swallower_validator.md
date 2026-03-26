# API Documentation: silent_swallower_validator

**Target Audience**: developers, api_users

# silent_swallower_validator API Documentation

**File**: `silent_swallower_validator.py`
**Classes**: 1
**Functions**: 5

## Classes

- **SilentSwallowerDetector** (inherits from AntiPatternDetector)

## Functions

- **__init__**
- **category** -> AntiPatternCategory
- **detect** -> list[AntiPatternViolation]
- **_check_except_handler** -> AntiPatternViolation | None
- **_generate_fix_suggestion** -> str


## Class: SilentSwallowerDetector

**Description**: 
    Detects exception handlers that silently swallow errors.

    These patterns prevent proper error propagation and cause
    downstream agents to operate on failed state.
    

**Inherits from**: AntiPatternDetector

### Methods

#### __init__
**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files

#### category
**Parameters**: self
**Returns**: AntiPatternCategory

#### detect
**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: Detect silent swallower patterns in the AST.

#### _check_except_handler
**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Check if an except handler is a silent swallower.

#### _generate_fix_suggestion
**Parameters**: self, node, exception_name
**Returns**: str
**Description**: Generate a fix suggestion for the violation.



## Function: __init__

**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files


## Function: category

**Parameters**: self
**Returns**: AntiPatternCategory


## Function: detect

**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: Detect silent swallower patterns in the AST.



## Function: _check_except_handler

**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Check if an except handler is a silent swallower.



## Function: _generate_fix_suggestion

**Parameters**: self, node, exception_name
**Returns**: str
**Description**: Generate a fix suggestion for the violation.



## Usage Examples

### Class Usage

```python
# Using SilentSwallowerDetector
silentswallowerdetector = SilentSwallowerDetector()
silentswallowerdetector.category()
silentswallowerdetector.detect()
```

### Function Usage

```python
# Using __init__
result = __init__(enforcement_level, whitelisted_patterns)
```

```python
# Using category
result = category()
```

```python
# Using detect
result = detect(file_path, tree)
```



---
**Generated**: 2026-03-26T09:39:05.878694
**Type**: api_reference
**Quality**: comprehensive
