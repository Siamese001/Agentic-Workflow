# API Documentation: config_with_logic_validator

**Target Audience**: developers, api_users

# config_with_logic_validator API Documentation

**File**: `config_with_logic_validator.py`
**Classes**: 1
**Functions**: 6

## Classes

- **ConfigWithLogicDetector** (inherits from AntiPatternDetector)

## Functions

- **__init__**
- **category** -> AntiPatternCategory
- **detect** -> list[AntiPatternViolation]
- **_is_config_name** -> bool
- **_check_value_for_logic** -> list[AntiPatternViolation]
- **_is_whitelisted_line** -> bool


## Class: ConfigWithLogicDetector

**Description**: 
    Detects logic (lambdas, conditionals) embedded in config-typed objects.

    Config-with-logic makes governance enforcement blurry because business
    rules buried in data structures are invisible to policy scanners and
    cannot be independently tested or versioned.
    

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
**Description**: Detect config-with-logic patterns in the AST.

#### _is_config_name
**Parameters**: self, node
**Returns**: bool
**Description**: Return True if the AST name node looks like a config variable.

#### _check_value_for_logic
**Parameters**: self, value, file_path, source_lines, lineno
**Returns**: list[AntiPatternViolation]
**Description**: Walk a value node and flag any lambda expressions found.

#### _is_whitelisted_line
**Parameters**: self, source_lines, lineno
**Returns**: bool
**Description**: Return True if the line or its predecessor contains the whitelist comment.



## Function: __init__

**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files


## Function: category

**Parameters**: self
**Returns**: AntiPatternCategory


## Function: detect

**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: Detect config-with-logic patterns in the AST.



## Function: _is_config_name

**Parameters**: self, node
**Returns**: bool
**Description**: Return True if the AST name node looks like a config variable.



## Function: _check_value_for_logic

**Parameters**: self, value, file_path, source_lines, lineno
**Returns**: list[AntiPatternViolation]
**Description**: Walk a value node and flag any lambda expressions found.



## Function: _is_whitelisted_line

**Parameters**: self, source_lines, lineno
**Returns**: bool
**Description**: Return True if the line or its predecessor contains the whitelist comment.



## Usage Examples

### Class Usage

```python
# Using ConfigWithLogicDetector
configwithlogicdetector = ConfigWithLogicDetector()
configwithlogicdetector.category()
configwithlogicdetector.detect()
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
**Generated**: 2026-03-26T09:39:05.758597
**Type**: api_reference
**Quality**: comprehensive
