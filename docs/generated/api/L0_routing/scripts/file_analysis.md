# API Documentation: file_analysis

**Target Audience**: developers, api_users

# file_analysis API Documentation

**File**: `file_analysis.py`
**Classes**: 1
**Functions**: 8

## Classes

- **FileAnalysis**

## Functions

- **extract_docstring** -> str
- **analyze_class** -> dict[str, Any]
- **analyze_function** -> dict[str, Any]
- **infer_domain** -> str
- **infer_purpose** -> str
- **analyze_file** -> FileAnalysis | None
- **find_similar_in_codebase** -> list[dict]
- **main**


## Class: FileAnalysis

**Description**: Analysis results for a single file.



## Function: extract_docstring

**Parameters**: node
**Returns**: str
**Description**: Extract docstring from AST node.



## Function: analyze_class

**Parameters**: node
**Returns**: dict[str, Any]
**Description**: Deep analysis of a class definition.



## Function: analyze_function

**Parameters**: node
**Returns**: dict[str, Any]
**Description**: Analyze a top-level function.



## Function: infer_domain

**Parameters**: content, classes, functions
**Returns**: str
**Description**: Infer the domain (resume/outreach/shared/infra) from content analysis.



## Function: infer_purpose

**Parameters**: classes, functions, docstring
**Returns**: str
**Description**: Infer the purpose of the file from its contents.



## Function: analyze_file

**Parameters**: file_path
**Returns**: FileAnalysis | None
**Description**: Perform deep AST analysis on a file.



## Function: find_similar_in_codebase

**Parameters**: analysis, current_dirs
**Returns**: list[dict]
**Description**: Find similar functionality in current codebase using AST comparison.



## Function: main



## Usage Examples

### Class Usage

```python
# Using FileAnalysis
fileanalysis = FileAnalysis()
```

### Function Usage

```python
# Using extract_docstring
result = extract_docstring(node)
```

```python
# Using analyze_class
result = analyze_class(node)
```

```python
# Using analyze_function
result = analyze_function(node)
```



---
**Generated**: 2026-03-26T09:39:03.107331
**Type**: api_reference
**Quality**: comprehensive
