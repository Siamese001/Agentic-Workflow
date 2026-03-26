# API Documentation: scan_util

**Target Audience**: developers, api_users

# scan_util API Documentation

**File**: `scan_util.py`
**Classes**: 0
**Functions**: 6


## Functions

- **guarded_rglob** -> Iterator[Path]
- **guarded_glob** -> Iterator[Path]
- **deprecate_rglob**
- **count_rglob_calls_in_file** -> int
- **audit_rglob_usage** -> dict
- **wrapper**


## Function: guarded_rglob

**Parameters**: path, pattern, caller
**Returns**: Iterator[Path]
**Description**: 
    Audit utility to track and discourage expensive rglob calls.

    Logs a DeprecationWarning suggesting FileCache before executing the scan.
    Use this as a drop-in replacement for path.rglob() during migration.

    Args:
        path: The path to scan
        pattern: The glob pattern (e.g., "*.py")
        caller: Optional caller identifier for logging

    Returns:
        Iterator of matching Path objects (same as rglob)

    Example:
        # Instead of: path.rglob("*.py")
        files = list(guarded_rglob(path, "*.py"))
    



## Function: guarded_glob

**Parameters**: path, pattern, caller
**Returns**: Iterator[Path]
**Description**: 
    Audit utility to track and discourage expensive glob calls.

    Logs a DeprecationWarning suggesting FileCache before executing the scan.
    Use this as a drop-in replacement for path.glob() during migration.

    Args:
        path: The path to scan
        pattern: The glob pattern (e.g., "*.py")
        caller: Optional caller identifier for logging

    Returns:
        Iterator of matching Path objects (same as glob)
    



## Function: deprecate_rglob

**Parameters**: func
**Description**: 
    Decorator to mark functions that use rglob as deprecated.

    Usage:
        @deprecate_rglob
        def my_function_with_rglob():
            return path.rglob("*.py")
    



## Function: count_rglob_calls_in_file

**Parameters**: file_path
**Returns**: int
**Description**: 
    Count the number of rglob/glob calls in a Python file.

    Useful for auditing and tracking migration progress.

    Args:
        file_path: Path to the Python file to analyze

    Returns:
        Count of rglob/glob calls found
    



## Function: audit_rglob_usage

**Parameters**: project_root
**Returns**: dict
**Description**: 
    Audit all rglob/glob usage in the project.

    Returns a report of files with rglob/glob calls and their counts.

    Args:
        project_root: Root directory of the project

    Returns:
        Dict with audit results
    



## Function: wrapper



## Usage Examples

### Function Usage

```python
# Using guarded_rglob
result = guarded_rglob(path, pattern)
```

```python
# Using guarded_glob
result = guarded_glob(path, pattern)
```

```python
# Using deprecate_rglob
result = deprecate_rglob(func)
```



---
**Generated**: 2026-03-26T09:39:03.541574
**Type**: api_reference
**Quality**: comprehensive
