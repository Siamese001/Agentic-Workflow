# API Documentation: direct_prompt_compilation_validator

**Target Audience**: developers, api_users

# direct_prompt_compilation_validator API Documentation

**File**: `direct_prompt_compilation_validator.py`
**Classes**: 1
**Functions**: 8

## Classes

- **DirectPromptCompilationDetector** (inherits from AntiPatternDetector)

## Functions

- **_is_prompt_slot_name** -> bool
- **_names_in_node** -> list[str]
- **__init__**
- **category** -> AntiPatternCategory
- **detect** -> list[AntiPatternViolation]
- **_check_node** -> AntiPatternViolation | None
- **_is_assembly_module** -> bool
- **_is_whitelisted_line** -> bool


## Class: DirectPromptCompilationDetector

**Description**: 
    Detects direct prompt string construction outside the Assembly Stage.

    All final prompt strings MUST be composed via AirlockAssembler.
    Any f-string / concatenation / join involving prompt-slot variables
    outside assembly_stage.py is a governance violation.
    

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
**Description**: Detect direct prompt compilation patterns.

#### _check_node
**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None

#### _is_assembly_module
**Parameters**: self, file_path
**Returns**: bool
**Description**: Return True if this file IS the canonical assembly module (allowlisted).

#### _is_whitelisted_line
**Parameters**: self, source_lines, lineno
**Returns**: bool



## Function: _is_prompt_slot_name

**Parameters**: name
**Returns**: bool
**Description**: Return True if the name looks like a prompt slot variable.



## Function: _names_in_node

**Parameters**: node
**Returns**: list[str]
**Description**: Collect all Name and Attribute identifiers referenced in an expression.



## Function: __init__

**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files


## Function: category

**Parameters**: self
**Returns**: AntiPatternCategory


## Function: detect

**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: Detect direct prompt compilation patterns.



## Function: _check_node

**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None


## Function: _is_assembly_module

**Parameters**: self, file_path
**Returns**: bool
**Description**: Return True if this file IS the canonical assembly module (allowlisted).



## Function: _is_whitelisted_line

**Parameters**: self, source_lines, lineno
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using DirectPromptCompilationDetector
directpromptcompilationdetector = DirectPromptCompilationDetector()
directpromptcompilationdetector.category()
directpromptcompilationdetector.detect()
```

### Function Usage

```python
# Using _is_prompt_slot_name
result = _is_prompt_slot_name(name)
```

```python
# Using _names_in_node
result = _names_in_node(node)
```

```python
# Using __init__
result = __init__(enforcement_level, whitelisted_patterns)
```



---
**Generated**: 2026-03-26T09:39:05.787995
**Type**: api_reference
**Quality**: comprehensive
