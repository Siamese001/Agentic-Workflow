# API Documentation: global_mutation_validator

**Target Audience**: developers, api_users

# global_mutation_validator API Documentation

**File**: `global_mutation_validator.py`
**Classes**: 1
**Functions**: 7

## Classes

- **GlobalMutationDetector** (inherits from AntiPatternDetector)

## Functions

- **__init__**
- **category** -> AntiPatternCategory
- **detect** -> list[AntiPatternViolation]
- **_check_call** -> AntiPatternViolation | None
- **_check_subscript_assign** -> AntiPatternViolation | None
- **_create_violation** -> AntiPatternViolation
- **_generate_fix_suggestion** -> str


## Class: GlobalMutationDetector

**Description**: 
    Detects runtime global state modifications.

    Global mutations cause "spooky action at a distance" where
    one agent's changes affect other agents unexpectedly.
    

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
**Description**: Detect global mutation patterns in the AST.

#### _check_call
**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Check if a call modifies global state.

#### _check_subscript_assign
**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Check for os.environ['KEY'] = value patterns.

#### _create_violation
**Parameters**: self, node, file_path, pattern, mutation_target
**Returns**: AntiPatternViolation
**Description**: Create a violation for detected pattern.

#### _generate_fix_suggestion
**Parameters**: self, mutation_target
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
**Description**: Detect global mutation patterns in the AST.



## Function: _check_call

**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Check if a call modifies global state.



## Function: _check_subscript_assign

**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Check for os.environ['KEY'] = value patterns.



## Function: _create_violation

**Parameters**: self, node, file_path, pattern, mutation_target
**Returns**: AntiPatternViolation
**Description**: Create a violation for detected pattern.



## Function: _generate_fix_suggestion

**Parameters**: self, mutation_target
**Returns**: str
**Description**: Generate a fix suggestion for the violation.



## Usage Examples

### Class Usage

```python
# Using GlobalMutationDetector
globalmutationdetector = GlobalMutationDetector()
globalmutationdetector.category()
globalmutationdetector.detect()
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
**Generated**: 2026-03-26T09:39:05.790770
**Type**: api_reference
**Quality**: comprehensive
