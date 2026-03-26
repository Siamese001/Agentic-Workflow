# API Documentation: test_quality_detector_validator

**Target Audience**: developers, api_users

# test_quality_detector_validator API Documentation

**File**: `test_quality_detector_validator.py`
**Classes**: 1
**Functions**: 16

## Classes

- **TestQualityDetector** (inherits from AntiPatternDetector)

## Functions

- **_is_weak_assert** -> bool
- **_is_weak_expr** -> bool
- **_is_vacuous_expr** -> bool
- **_call_name** -> str
- **_has_write_call** -> str | None
- **_has_read_or_verify** -> bool
- **__init__** -> None
- **category** -> AntiPatternCategory
- **scan_file** -> DetectionResult
- **detect** -> list[AntiPatternViolation]
- **_check_vacuous** -> AntiPatternViolation | None
- **_check_sole_hasattr** -> AntiPatternViolation | None
- **_check_sole_type** -> AntiPatternViolation | None
- **_check_write_without_read** -> AntiPatternViolation | None
- **_has_whitelist** -> bool
- **_is_hasattr_only** -> bool


## Class: TestQualityDetector

**Description**: 
    Detects low-quality test assertions in test files.

    Only scans files named ``test_*.py`` or ``*_test.py``.
    See module docstring for sub-pattern details.
    

**Inherits from**: AntiPatternDetector

### Methods

#### __init__
**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files, skip_adg_stubs
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

#### _check_vacuous
**Parameters**: self, fn, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Detect any ``assert True`` / always-true assertion in a test function.

#### _check_sole_hasattr
**Parameters**: self, fn, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Detect test methods where every assertion is a bare hasattr() probe.

#### _check_sole_type
**Parameters**: self, fn, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Detect test methods where every assertion is a weak type/existence check.

#### _check_write_without_read
**Parameters**: self, fn, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: 
        Detect tests that call a write/create method but never verify via read-back.
        

#### _has_whitelist
**Parameters**: self, source_lines, lineno
**Returns**: bool
**Description**: True when guardian exemption appears within 3 lines above.



## Function: _is_weak_assert

**Parameters**: node
**Returns**: bool
**Description**: 
    Return True when the assertion provides no meaningful signal about behavior.

    Weak assertions:
    - ``assert True``
    - ``assert isinstance(x, T)``  — only checks type, not value
    - ``assert x is not None``      — only checks not-None
    - ``assert hasattr(x, 'attr')`` — only checks attribute existence
    - Combinations of the above via ``and``
    



## Function: _is_weak_expr

**Parameters**: expr
**Returns**: bool


## Function: _is_vacuous_expr

**Parameters**: expr
**Returns**: bool
**Description**: Return True when the expression is unconditionally True (always passes).



## Function: _call_name

**Parameters**: node
**Returns**: str
**Description**: Return the bare attribute or function name from a Call node.



## Function: _has_write_call

**Parameters**: fn
**Returns**: str | None
**Description**: Return the first write-like call name found, or None.

    Stdlib / pathlib IO primitives in ``_WRITE_EXCLUDED_STDLIB`` are skipped
    because they are typically used for fixture setup, not to exercise
    application persistence under test.
    



## Function: _has_read_or_verify

**Parameters**: fn
**Returns**: bool
**Description**: Return True when there is any read-back or direct assertion on write result.



## Function: __init__

**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files, skip_adg_stubs
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


## Function: _check_vacuous

**Parameters**: self, fn, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Detect any ``assert True`` / always-true assertion in a test function.



## Function: _check_sole_hasattr

**Parameters**: self, fn, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Detect test methods where every assertion is a bare hasattr() probe.



## Function: _check_sole_type

**Parameters**: self, fn, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: Detect test methods where every assertion is a weak type/existence check.



## Function: _check_write_without_read

**Parameters**: self, fn, file_path, source_lines
**Returns**: AntiPatternViolation | None
**Description**: 
        Detect tests that call a write/create method but never verify via read-back.
        



## Function: _has_whitelist

**Parameters**: self, source_lines, lineno
**Returns**: bool
**Description**: True when guardian exemption appears within 3 lines above.



## Function: _is_hasattr_only

**Parameters**: a
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using TestQualityDetector
testqualitydetector = TestQualityDetector()
testqualitydetector.category()
testqualitydetector.scan_file()
```

### Function Usage

```python
# Using _is_weak_assert
result = _is_weak_assert(node)
```

```python
# Using _is_weak_expr
result = _is_weak_expr(expr)
```

```python
# Using _is_vacuous_expr
result = _is_vacuous_expr(expr)
```



---
**Generated**: 2026-03-26T09:39:05.886062
**Type**: api_reference
**Quality**: comprehensive
