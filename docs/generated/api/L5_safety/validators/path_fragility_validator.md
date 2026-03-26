# API Documentation: path_fragility_validator

**Target Audience**: developers, api_users

# path_fragility_validator API Documentation

**File**: `path_fragility_validator.py`
**Classes**: 1
**Functions**: 8

## Classes

- **PathFragilityDetector** (inherits from AntiPatternDetector)

## Functions

- **__init__**
- **category** -> AntiPatternCategory
- **detect** -> list[AntiPatternViolation]
- **_check_call** -> AntiPatternViolation | None
- **_check_string_concat** -> AntiPatternViolation | None
- **_create_violation** -> AntiPatternViolation
- **_generate_fix_suggestion** -> str
- **contains_path_separator** -> bool


## Class: PathFragilityDetector

**Description**: 
    Detects string-based path manipulation.

    String paths cause cross-platform incompatibility between
    Windows and Unix systems.
    

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
**Description**: Detect path fragility patterns in the AST.

#### _check_call
**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Check if a call uses os.path functions.

#### _check_string_concat
**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Check for string concatenation patterns that look like path building.

#### _create_violation
**Parameters**: self, node, file_path, pattern
**Returns**: AntiPatternViolation
**Description**: Create a violation for detected pattern.

#### _generate_fix_suggestion
**Parameters**: self, pattern
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
**Description**: Detect path fragility patterns in the AST.



## Function: _check_call

**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Check if a call uses os.path functions.



## Function: _check_string_concat

**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Check for string concatenation patterns that look like path building.



## Function: _create_violation

**Parameters**: self, node, file_path, pattern
**Returns**: AntiPatternViolation
**Description**: Create a violation for detected pattern.



## Function: _generate_fix_suggestion

**Parameters**: self, pattern
**Returns**: str
**Description**: Generate a fix suggestion for the violation.



## Function: contains_path_separator

**Parameters**: n
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using PathFragilityDetector
pathfragilitydetector = PathFragilityDetector()
pathfragilitydetector.category()
pathfragilitydetector.detect()
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
**Generated**: 2026-03-26T09:39:05.858598
**Type**: api_reference
**Quality**: comprehensive
