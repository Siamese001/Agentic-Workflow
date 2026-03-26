# API Documentation: silent_degradation_validator

**Target Audience**: developers, api_users

# silent_degradation_validator API Documentation

**File**: `silent_degradation_validator.py`
**Classes**: 2
**Functions**: 25

## Classes

- **_ShallowWalker** (inherits from <ast.Attribute object at 0x000001CBFAE36450>)
- **SilentDegradationDetector** (inherits from AntiPatternDetector)

## Functions

- **_is_none_or_empty** -> bool
- **_body_first_empty_return** -> ast.Return | None
- **_is_neg_avail_test** -> bool
- **_extract_avail_attr_name** -> str
- **_shallow_walk** -> list[ast.AST]
- **__init__** -> None
- **visit** -> None
- **__init__** -> None
- **category** -> AntiPatternCategory
- **detect** -> list[AntiPatternViolation]
- **_check_availability_guard** -> AntiPatternViolation | None
- **_check_silent_success_on_noop** -> AntiPatternViolation | None
- **_is_is_not_none_compare** -> bool
- **_is_null_and_guard** -> bool
- **_check_phantom_module_import** -> AntiPatternViolation | None
- **_find_mcp_phantom_import** -> str | None
- **_handler_catches_import_error** -> bool
- **_check_except_import_pass** -> AntiPatternViolation | None
- **_is_import_error_handler** -> bool
- **_has_raise_or_error_return** -> bool
- **_check_log_and_return_mock** -> AntiPatternViolation | None
- **_has_mock_log_call** -> bool
- **_check_skip_string_return** -> AntiPatternViolation | None
- **_has_whitelist** -> bool
- **_is_is_none** -> bool


## Class: _ShallowWalker

**Description**: Visit all nodes in a statement list without descending into nested functions/classes.

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### visit
**Parameters**: self, node
**Returns**: None



## Class: SilentDegradationDetector

**Description**: 
    Detects silent degradation patterns — operations that silently no-op or
    return fake success instead of raising.  Enforces §5.2 Fail-Closed.

    Six sub-patterns are covered; each may be individually exempted with:
        # guardian: allow-silent-degradation -- <specific justification>
    placed on the line immediately preceding the flagged statement.
    

**Inherits from**: AntiPatternDetector

### Methods

#### __init__
**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files
**Returns**: None

#### category
**Parameters**: self
**Returns**: AntiPatternCategory

#### detect
**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: Scan *tree* for all silent degradation sub-patterns.

#### _check_availability_guard
**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None

#### _check_silent_success_on_noop
**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None

#### _is_is_not_none_compare
**Parameters**: node
**Returns**: bool

#### _is_null_and_guard
**Parameters**: node
**Returns**: bool
**Description**: True when node is `A is None` or `A is None and B is None ...`.

#### _check_phantom_module_import
**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None

#### _find_mcp_phantom_import
**Parameters**: body
**Returns**: str | None
**Description**: Return the mcp<N> module name if a phantom import is found, else None.

#### _handler_catches_import_error
**Parameters**: handler
**Returns**: bool

#### _check_except_import_pass
**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None

#### _is_import_error_handler
**Parameters**: node
**Returns**: bool

#### _has_raise_or_error_return
**Parameters**: body
**Returns**: bool
**Description**: True when the handler body contains a raise or an explicit error return.

#### _check_log_and_return_mock
**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None

#### _has_mock_log_call
**Parameters**: body
**Returns**: bool
**Description**: True when any logger call in *body* contains a mock/fallback keyword.

#### _check_skip_string_return
**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None

#### _has_whitelist
**Parameters**: self, source_lines, lineno
**Returns**: bool
**Description**: True when the guardian exemption comment appears within 5 lines above the violation.

        Searches up to 5 lines back so comments placed above a `try:` block
        (rather than immediately above the flagged statement) are respected.
        



## Function: _is_none_or_empty

**Parameters**: value
**Returns**: bool
**Description**: True when the return value is None, [], {}, '', 0, or False.



## Function: _body_first_empty_return

**Parameters**: body
**Returns**: ast.Return | None
**Description**: Return the first empty/null return statement in *body*, else None.



## Function: _is_neg_avail_test

**Parameters**: test
**Returns**: bool
**Description**: True when *test* is `not self._X<avail_suffix>` or a negated availability call.



## Function: _extract_avail_attr_name

**Parameters**: test
**Returns**: str
**Description**: Extract the availability attribute name from a `not self._X` test.



## Function: _shallow_walk

**Parameters**: stmts
**Returns**: list[ast.AST]
**Description**: Return all descendant nodes from *stmts*, not crossing into nested functions.



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: visit

**Parameters**: self, node
**Returns**: None


## Function: __init__

**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files
**Returns**: None


## Function: category

**Parameters**: self
**Returns**: AntiPatternCategory


## Function: detect

**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: Scan *tree* for all silent degradation sub-patterns.



## Function: _check_availability_guard

**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None


## Function: _check_silent_success_on_noop

**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None


## Function: _is_is_not_none_compare

**Parameters**: node
**Returns**: bool


## Function: _is_null_and_guard

**Parameters**: node
**Returns**: bool
**Description**: True when node is `A is None` or `A is None and B is None ...`.



## Function: _check_phantom_module_import

**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None


## Function: _find_mcp_phantom_import

**Parameters**: body
**Returns**: str | None
**Description**: Return the mcp<N> module name if a phantom import is found, else None.



## Function: _handler_catches_import_error

**Parameters**: handler
**Returns**: bool


## Function: _check_except_import_pass

**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None


## Function: _is_import_error_handler

**Parameters**: node
**Returns**: bool


## Function: _has_raise_or_error_return

**Parameters**: body
**Returns**: bool
**Description**: True when the handler body contains a raise or an explicit error return.



## Function: _check_log_and_return_mock

**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None


## Function: _has_mock_log_call

**Parameters**: body
**Returns**: bool
**Description**: True when any logger call in *body* contains a mock/fallback keyword.



## Function: _check_skip_string_return

**Parameters**: self, node, file_path, source_lines
**Returns**: AntiPatternViolation | None


## Function: _has_whitelist

**Parameters**: self, source_lines, lineno
**Returns**: bool
**Description**: True when the guardian exemption comment appears within 5 lines above the violation.

        Searches up to 5 lines back so comments placed above a `try:` block
        (rather than immediately above the flagged statement) are respected.
        



## Function: _is_is_none

**Parameters**: n
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using _ShallowWalker
_shallowwalker = _ShallowWalker()
_shallowwalker.visit()
```

```python
# Using SilentDegradationDetector
silentdegradationdetector = SilentDegradationDetector()
silentdegradationdetector.category()
silentdegradationdetector.detect()
```

### Function Usage

```python
# Using _is_none_or_empty
result = _is_none_or_empty(value)
```

```python
# Using _body_first_empty_return
result = _body_first_empty_return(body)
```

```python
# Using _is_neg_avail_test
result = _is_neg_avail_test(test)
```



---
**Generated**: 2026-03-26T09:39:05.875504
**Type**: api_reference
**Quality**: comprehensive
