# API Documentation: class_info

**Target Audience**: developers, api_users

# class_info API Documentation

**File**: `class_info.py`
**Classes**: 2
**Functions**: 12

## Classes

- **ClassInfo**
- **FileAnalysis**

## Functions

- **compute_file_hash** -> str
- **count_lines** -> int
- **get_snippet** -> str
- **parse_python_file** -> tuple[list[ClassInfo], list[str], list[str], str | None]
- **check_sovereignty_compliance** -> dict[str, bool]
- **find_modern_equivalent** -> tuple[str | None, str]
- **classify_migration_disposition** -> tuple[str, str, str, str]
- **determine_target_path** -> str
- **analyze_file** -> FileAnalysis
- **scan_archive_folder** -> list[FileAnalysis]
- **generate_markdown_report** -> str
- **main**


## Class: ClassInfo

**Description**: Information about a Python class.



## Class: FileAnalysis

**Description**: Complete analysis of a file.



## Function: compute_file_hash

**Parameters**: file_path
**Returns**: str
**Description**: Compute SHA256 hash of file contents.



## Function: count_lines

**Parameters**: file_path
**Returns**: int
**Description**: Count lines in a text file.



## Function: get_snippet

**Parameters**: file_path, chars
**Returns**: str
**Description**: Get first N characters of a file.



## Function: parse_python_file

**Parameters**: file_path
**Returns**: tuple[list[ClassInfo], list[str], list[str], str | None]
**Description**: Parse a Python file using AST.

    Returns:
        Tuple of (classes, imports, functions, module_docstring)
    



## Function: check_sovereignty_compliance

**Parameters**: file_path, content, classes
**Returns**: dict[str, bool]
**Description**: Check for sovereignty compliance issues.



## Function: find_modern_equivalent

**Parameters**: file_path, file_name
**Returns**: tuple[str | None, str]
**Description**: Find a modern equivalent in agentic_core.



## Function: classify_migration_disposition

**Parameters**: analysis
**Returns**: tuple[str, str, str, str]
**Description**: Classify file and determine action.

    Returns:
        (classification, recommended_action, justification, risk_level)
    



## Function: determine_target_path

**Parameters**: analysis
**Returns**: str
**Description**: Determine the target migration path.



## Function: analyze_file

**Parameters**: file_path, archive_base
**Returns**: FileAnalysis
**Description**: Perform complete analysis of a file.



## Function: scan_archive_folder

**Parameters**: archive_folder
**Returns**: list[FileAnalysis]
**Description**: Recursively scan an archive folder.



## Function: generate_markdown_report

**Parameters**: all_analyses
**Returns**: str
**Description**: Generate comprehensive markdown report.



## Function: main

**Description**: Main entry point.



## Usage Examples

### Class Usage

```python
# Using ClassInfo
classinfo = ClassInfo()
```

```python
# Using FileAnalysis
fileanalysis = FileAnalysis()
```

### Function Usage

```python
# Using compute_file_hash
result = compute_file_hash(file_path)
```

```python
# Using count_lines
result = count_lines(file_path)
```

```python
# Using get_snippet
result = get_snippet(file_path, chars)
```



---
**Generated**: 2026-03-26T09:39:02.800240
**Type**: api_reference
**Quality**: comprehensive
