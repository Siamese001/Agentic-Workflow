# API Documentation: test_skip_detector_validator

**Target Audience**: developers, api_users

# test_skip_detector_validator API Documentation

**File**: `test_skip_detector_validator.py`
**Classes**: 1
**Functions**: 8

## Classes

- **TestSilentSkipDetector** (inherits from AntiPatternDetector)

## Functions

- **__init__** -> None
- **category** -> AntiPatternCategory
- **scan_file** -> DetectionResult
- **detect** -> list[AntiPatternViolation]
- **_check_broad_except** -> AntiPatternViolation | None
- **_handler_type_name** -> str | None
- **_find_availability_false** -> str | None
- **_has_whitelist** -> bool


## Class: TestSilentSkipDetector

**Description**: 
    Detects over-broad import guards in test files that cause all tests to be
    silently skipped whenever any error (not just ImportError) occurs during
    module setup.

    Only scans files whose name starts with ``test_`` or ends with ``_test.py``.
    Files in production directories are returned empty immediately.

    Sub-patterns detected
    ---------------------
    BROAD_EXCEPT_AVAILABILITY_FLAG
        ``except Exception/BaseException/bare:`` handler that sets an availability
        flag (``_AVAILABLE``, ``_LOADED``, …) to ``False``.  The broad catch
        swallows real bugs as "unavailable", making all ``skipif``-guarded tests
        permanently silent.
    

**Inherits from**: AntiPatternDetector

### Methods

#### __init__
**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files
**Returns**: None

#### category
**Parameters**: self
**Returns**: AntiPatternCategory

#### scan_file
**Parameters**: self, file_path
**Returns**: DetectionResult
**Description**: Return empty result for non-test files; delegate to base for test files.

#### detect
**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: Walk ExceptHandler nodes; flag broad handlers that set availability flags.

#### _check_broad_except
**Parameters**: self, handler, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: 
        Flag ``except <broad>: ... _AVAILABLE = False`` where <broad> is anything
        other than ImportError / ModuleNotFoundError.
        

#### _handler_type_name
**Parameters**: handler
**Returns**: str | None
**Description**: Return the bare name of the exception type, or None for bare except.

#### _find_availability_false
**Parameters**: stmts
**Returns**: str | None
**Description**: 
        Return the flag name if any top-level statement assigns an availability
        flag to ``False``.  Returns ``None`` if no such assignment found.
        

#### _has_whitelist
**Parameters**: self, source_lines, lineno
**Returns**: bool
**Description**: True when the guardian exemption comment appears within 4 lines above.

        4 lines covers the common try/except structure where the guardian comment
        precedes the ``try:`` statement, which itself precedes 1-2 import lines
        before the ``except`` handler.
        



## Function: __init__

**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files
**Returns**: None


## Function: category

**Parameters**: self
**Returns**: AntiPatternCategory


## Function: scan_file

**Parameters**: self, file_path
**Returns**: DetectionResult
**Description**: Return empty result for non-test files; delegate to base for test files.



## Function: detect

**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: Walk ExceptHandler nodes; flag broad handlers that set availability flags.



## Function: _check_broad_except

**Parameters**: self, handler, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: 
        Flag ``except <broad>: ... _AVAILABLE = False`` where <broad> is anything
        other than ImportError / ModuleNotFoundError.
        



## Function: _handler_type_name

**Parameters**: handler
**Returns**: str | None
**Description**: Return the bare name of the exception type, or None for bare except.



## Function: _find_availability_false

**Parameters**: stmts
**Returns**: str | None
**Description**: 
        Return the flag name if any top-level statement assigns an availability
        flag to ``False``.  Returns ``None`` if no such assignment found.
        



## Function: _has_whitelist

**Parameters**: self, source_lines, lineno
**Returns**: bool
**Description**: True when the guardian exemption comment appears within 4 lines above.

        4 lines covers the common try/except structure where the guardian comment
        precedes the ``try:`` statement, which itself precedes 1-2 import lines
        before the ``except`` handler.
        



## Usage Examples

### Class Usage

```python
# Using TestSilentSkipDetector
testsilentskipdetector = TestSilentSkipDetector()
testsilentskipdetector.category()
testsilentskipdetector.scan_file()
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
# Using scan_file
result = scan_file(file_path)
```



---
**Generated**: 2026-03-26T09:39:05.890762
**Type**: api_reference
**Quality**: comprehensive
