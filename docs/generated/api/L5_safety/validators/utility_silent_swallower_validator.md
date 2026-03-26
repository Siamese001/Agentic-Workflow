# API Documentation: utility_silent_swallower_validator

**Target Audience**: developers, api_users

# utility_silent_swallower_validator API Documentation

**File**: `utility_silent_swallower_validator.py`
**Classes**: 3
**Functions**: 12

## Classes

- **UtilityScriptClassifier**
- **RetryPatternDetector**
- **UtilitySilentSwallowerDetector** (inherits from AntiPatternDetector)

## Functions

- **classify_script** -> str
- **__init__**
- **is_compliant_retry** -> bool
- **__init__**
- **category** -> AntiPatternCategory
- **detect** -> list[AntiPatternViolation]
- **_check_try_except** -> AntiPatternViolation | None
- **_is_broad_exception** -> bool
- **_has_guardian_annotation** -> bool
- **_has_reraise** -> bool
- **_has_failure_signal** -> bool
- **_create_violation** -> AntiPatternViolation


## Class: UtilityScriptClassifier

**Description**: Classifies utility scripts by operational category.

### Methods

#### classify_script
**Parameters**: cls, file_path
**Returns**: str
**Description**: Classify a script by its operational category.



## Class: RetryPatternDetector

**Description**: Detects retry-with-reraise patterns that are compliant.

### Methods

#### __init__
**Parameters**: self

#### is_compliant_retry
**Parameters**: self, node, source_lines
**Returns**: bool
**Description**: Check if this try-except is part of a compliant retry pattern.



## Class: UtilitySilentSwallowerDetector

**Description**: Enhanced silent swallower detector for utility scripts.

**Inherits from**: AntiPatternDetector

### Methods

#### __init__
**Parameters**: self, project_root

#### category
**Parameters**: self
**Returns**: AntiPatternCategory

#### detect
**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: Detect utility silent swallower violations in the given AST.

#### _check_try_except
**Parameters**: self, node, file_path, source_lines, script_category
**Returns**: AntiPatternViolation | None
**Description**: Check a try-except node for silent swallower violations.

#### _is_broad_exception
**Parameters**: self, handler
**Returns**: bool
**Description**: Check if handler catches Exception broadly.

#### _has_guardian_annotation
**Parameters**: self, handler, source_lines
**Returns**: bool
**Description**: Check if handler has guardian annotation (hyphens or underscores accepted).

#### _has_reraise
**Parameters**: self, handler
**Returns**: bool
**Description**: Check if handler re-raises the exception.

#### _has_failure_signal
**Parameters**: self, handler
**Returns**: bool
**Description**: Check if handler emits a failure signal.

#### _create_violation
**Parameters**: self, file_path, handler, message, enforcement_level
**Returns**: AntiPatternViolation
**Description**: Create an anti-pattern violation.



## Function: classify_script

**Parameters**: cls, file_path
**Returns**: str
**Description**: Classify a script by its operational category.



## Function: __init__

**Parameters**: self


## Function: is_compliant_retry

**Parameters**: self, node, source_lines
**Returns**: bool
**Description**: Check if this try-except is part of a compliant retry pattern.



## Function: __init__

**Parameters**: self, project_root


## Function: category

**Parameters**: self
**Returns**: AntiPatternCategory


## Function: detect

**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: Detect utility silent swallower violations in the given AST.



## Function: _check_try_except

**Parameters**: self, node, file_path, source_lines, script_category
**Returns**: AntiPatternViolation | None
**Description**: Check a try-except node for silent swallower violations.



## Function: _is_broad_exception

**Parameters**: self, handler
**Returns**: bool
**Description**: Check if handler catches Exception broadly.



## Function: _has_guardian_annotation

**Parameters**: self, handler, source_lines
**Returns**: bool
**Description**: Check if handler has guardian annotation (hyphens or underscores accepted).



## Function: _has_reraise

**Parameters**: self, handler
**Returns**: bool
**Description**: Check if handler re-raises the exception.



## Function: _has_failure_signal

**Parameters**: self, handler
**Returns**: bool
**Description**: Check if handler emits a failure signal.



## Function: _create_violation

**Parameters**: self, file_path, handler, message, enforcement_level
**Returns**: AntiPatternViolation
**Description**: Create an anti-pattern violation.



## Usage Examples

### Class Usage

```python
# Using UtilityScriptClassifier
utilityscriptclassifier = UtilityScriptClassifier()
utilityscriptclassifier.classify_script()
```

```python
# Using RetryPatternDetector
retrypatterndetector = RetryPatternDetector()
retrypatterndetector.is_compliant_retry()
```

```python
# Using UtilitySilentSwallowerDetector
utilitysilentswallowerdetector = UtilitySilentSwallowerDetector()
utilitysilentswallowerdetector.category()
utilitysilentswallowerdetector.detect()
```

### Function Usage

```python
# Using classify_script
result = classify_script(cls, file_path)
```

```python
# Using __init__
result = __init__()
```

```python
# Using is_compliant_retry
result = is_compliant_retry(node, source_lines)
```



---
**Generated**: 2026-03-26T09:39:05.898308
**Type**: api_reference
**Quality**: comprehensive
