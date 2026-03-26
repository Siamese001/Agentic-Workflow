# API Documentation: unsafe_io_detector

**Target Audience**: developers, api_users

# unsafe_io_detector API Documentation

**File**: `unsafe_io_detector.py`
**Classes**: 2
**Functions**: 11

## Classes

- **UnsafePattern**
- **UnsafePatternVisitor** (inherits from <ast.Attribute object at 0x000001CBFB9BCDD0>)

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **scan_for_unsafe_patterns** -> list[UnsafePattern]
- **scan_directory_for_unsafe_patterns** -> list[UnsafePattern]
- **get_scoped_directories** -> list[Path]
- **is_protected_root_path** -> bool
- **__init__**
- **visit_Call**
- **add_finding**
- **_get_context** -> str
- **visit** -> list[UnsafePattern]


## Class: UnsafePattern

**Description**: Represents an unsafe pattern found in code.



## Class: UnsafePatternVisitor

**Description**: AST visitor to detect unsafe I/O and subprocess patterns.

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self, file_path

#### visit_Call
**Parameters**: self, node
**Description**: Visit function calls to detect unsafe patterns.

#### add_finding
**Parameters**: self, node, pattern_type
**Description**: Add a finding to the list.

#### _get_context
**Parameters**: self, node
**Returns**: str
**Description**: Get context line for the finding.

#### visit
**Parameters**: self, node, source
**Returns**: list[UnsafePattern]
**Description**: Visit AST with optional source code for context.



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: payload, target


## Function: scan_for_unsafe_patterns

**Parameters**: code, file_path
**Returns**: list[UnsafePattern]
**Description**: 
    Scan Python code for unsafe I/O and subprocess patterns.

    Args:
        code: Python source code to scan
        file_path: Path to the file being scanned (for reporting)

    Returns:
        List of unsafe patterns found
    



## Function: scan_directory_for_unsafe_patterns

**Parameters**: directory, recursive, file_pattern
**Returns**: list[UnsafePattern]
**Description**: 
    Scan a directory for unsafe patterns in Python files.

    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories
        file_pattern: File pattern to match (default: *.py)

    Returns:
        List of unsafe patterns found
    



## Function: get_scoped_directories

**Parameters**: repo_root
**Returns**: list[Path]
**Description**: Get the list of directories that should be scanned for unsafe patterns.



## Function: is_protected_root_path

**Parameters**: path_str
**Returns**: bool
**Description**: Check if a path string points to a protected root.



## Function: __init__

**Parameters**: self, file_path


## Function: visit_Call

**Parameters**: self, node
**Description**: Visit function calls to detect unsafe patterns.



## Function: add_finding

**Parameters**: self, node, pattern_type
**Description**: Add a finding to the list.



## Function: _get_context

**Parameters**: self, node
**Returns**: str
**Description**: Get context line for the finding.



## Function: visit

**Parameters**: self, node, source
**Returns**: list[UnsafePattern]
**Description**: Visit AST with optional source code for context.



## Usage Examples

### Class Usage

```python
# Using UnsafePattern
unsafepattern = UnsafePattern()
```

```python
# Using UnsafePatternVisitor
unsafepatternvisitor = UnsafePatternVisitor()
unsafepatternvisitor.visit_Call()
unsafepatternvisitor.add_finding()
```

### Function Usage

```python
# Using _invoke_authorize_and_execute
result = _invoke_authorize_and_execute(execution_context, target_callable)
```

```python
# Using _make_execution_context
result = _make_execution_context(payload, target)
```

```python
# Using scan_for_unsafe_patterns
result = scan_for_unsafe_patterns(code, file_path)
```



---
**Generated**: 2026-03-26T09:39:03.930037
**Type**: api_reference
**Quality**: comprehensive
