# API Documentation: type_erasure_validator

**Target Audience**: developers, api_users

# type_erasure_validator API Documentation

**File**: `type_erasure_validator.py`
**Classes**: 1
**Functions**: 8

## Classes

- **TypeErasureDetector** (inherits from AntiPatternDetector)

## Functions

- **__init__**
- **category** -> AntiPatternCategory
- **detect** -> list[AntiPatternViolation]
- **_is_agent_class** -> bool
- **_check_function** -> AntiPatternViolation | None
- **_get_name** -> str | None
- **_get_annotation_string** -> str | None
- **_generate_fix_suggestion** -> str


## Class: TypeErasureDetector

**Description**: 
    Detects functions with type-erased return types.

    Type erasure causes downstream agents to hallucinate
    non-existent keys and leads to schema drift.
    

**Inherits from**: AntiPatternDetector

### Methods

#### __init__
**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files, check_agent_classes_only

#### category
**Parameters**: self
**Returns**: AntiPatternCategory

#### detect
**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: Detect type erasure patterns in the AST.

#### _is_agent_class
**Parameters**: self, node
**Returns**: bool
**Description**: Check if class is an Agent or Validator.

        [REFACTORED 2026-02-08] Aligned with classification kernel:
        - Agent: class name ends with 'Agent' (not just contains)
        - Validator: class name ends with 'Validator' or inherits from Validator
        - Excludes Mixin classes
        

#### _check_function
**Parameters**: self, node, file_path, source_lines, class_name
**Returns**: AntiPatternViolation | None
**Description**: Check if a function has type-erased return type.

#### _get_name
**Parameters**: self, node
**Returns**: str | None
**Description**: Get the name from an AST node.

#### _get_annotation_string
**Parameters**: self, node
**Returns**: str | None
**Description**: Convert an annotation AST node to string representation.

#### _generate_fix_suggestion
**Parameters**: self, method_name, return_type
**Returns**: str
**Description**: Generate a fix suggestion for the violation.



## Function: __init__

**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files, check_agent_classes_only


## Function: category

**Parameters**: self
**Returns**: AntiPatternCategory


## Function: detect

**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: Detect type erasure patterns in the AST.



## Function: _is_agent_class

**Parameters**: self, node
**Returns**: bool
**Description**: Check if class is an Agent or Validator.

        [REFACTORED 2026-02-08] Aligned with classification kernel:
        - Agent: class name ends with 'Agent' (not just contains)
        - Validator: class name ends with 'Validator' or inherits from Validator
        - Excludes Mixin classes
        



## Function: _check_function

**Parameters**: self, node, file_path, source_lines, class_name
**Returns**: AntiPatternViolation | None
**Description**: Check if a function has type-erased return type.



## Function: _get_name

**Parameters**: self, node
**Returns**: str | None
**Description**: Get the name from an AST node.



## Function: _get_annotation_string

**Parameters**: self, node
**Returns**: str | None
**Description**: Convert an annotation AST node to string representation.



## Function: _generate_fix_suggestion

**Parameters**: self, method_name, return_type
**Returns**: str
**Description**: Generate a fix suggestion for the violation.



## Usage Examples

### Class Usage

```python
# Using TypeErasureDetector
typeerasuredetector = TypeErasureDetector()
typeerasuredetector.category()
typeerasuredetector.detect()
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
**Generated**: 2026-03-26T09:39:05.894333
**Type**: api_reference
**Quality**: comprehensive
