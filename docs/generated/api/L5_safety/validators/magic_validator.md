# API Documentation: magic_validator

**Target Audience**: developers, api_users

# magic_validator API Documentation

**File**: `magic_validator.py`
**Classes**: 1
**Functions**: 8

## Classes

- **MagicConfigDetector** (inherits from AntiPatternDetector)

## Functions

- **__init__**
- **category** -> AntiPatternCategory
- **detect** -> list[AntiPatternViolation]
- **_check_function_defaults** -> list[AntiPatternViolation]
- **_check_assignment** -> list[AntiPatternViolation]
- **_check_call_arguments** -> list[AntiPatternViolation]
- **_create_violation** -> AntiPatternViolation
- **_generate_fix_suggestion** -> str


## Class: MagicConfigDetector

**Description**: 
    Detects hardcoded configuration values in business logic.

    Magic configuration prevents runtime tuning and
    environment-specific adaptation.
    

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
**Description**: Detect magic configuration patterns in the AST.

#### _check_function_defaults
**Parameters**: self, node, file_path, source_lines
**Returns**: list[AntiPatternViolation]
**Description**: Check function parameter defaults for magic values.

#### _check_assignment
**Parameters**: self, node, file_path, source_lines
**Returns**: list[AntiPatternViolation]
**Description**: Check assignments for magic configuration values.

#### _check_call_arguments
**Parameters**: self, node, file_path, source_lines
**Returns**: list[AntiPatternViolation]
**Description**: Check function call arguments for magic values.

#### _create_violation
**Parameters**: self, node, file_path, pattern, value, line_number
**Returns**: AntiPatternViolation
**Description**: Create a violation for detected pattern.

#### _generate_fix_suggestion
**Parameters**: self, pattern, value
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
**Description**: Detect magic configuration patterns in the AST.



## Function: _check_function_defaults

**Parameters**: self, node, file_path, source_lines
**Returns**: list[AntiPatternViolation]
**Description**: Check function parameter defaults for magic values.



## Function: _check_assignment

**Parameters**: self, node, file_path, source_lines
**Returns**: list[AntiPatternViolation]
**Description**: Check assignments for magic configuration values.



## Function: _check_call_arguments

**Parameters**: self, node, file_path, source_lines
**Returns**: list[AntiPatternViolation]
**Description**: Check function call arguments for magic values.



## Function: _create_violation

**Parameters**: self, node, file_path, pattern, value, line_number
**Returns**: AntiPatternViolation
**Description**: Create a violation for detected pattern.



## Function: _generate_fix_suggestion

**Parameters**: self, pattern, value
**Returns**: str
**Description**: Generate a fix suggestion for the violation.



## Usage Examples

### Class Usage

```python
# Using MagicConfigDetector
magicconfigdetector = MagicConfigDetector()
magicconfigdetector.category()
magicconfigdetector.detect()
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
**Generated**: 2026-03-26T09:39:05.841829
**Type**: api_reference
**Quality**: comprehensive
