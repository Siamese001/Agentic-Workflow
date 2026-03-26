# API Documentation: bloat_analysis_util

**Target Audience**: developers, api_users

# bloat_analysis_util API Documentation

**File**: `bloat_analysis_util.py`
**Classes**: 0
**Functions**: 9


## Functions

- **get_file_stats**
- **find_large_files**
- **find_duplicate_filenames**
- **find_empty_or_stub_files**
- **find_deprecated_markers**
- **find_test_files_outside_tests**
- **find_unused_imports**
- **find_script_candidates**
- **main**


## Function: get_file_stats

**Description**: Get file statistics by extension and folder.



## Function: find_large_files

**Parameters**: min_size_kb
**Description**: Find files larger than threshold.



## Function: find_duplicate_filenames

**Description**: Find files with duplicate names.



## Function: find_empty_or_stub_files

**Description**: Find empty or stub Python files.



## Function: find_deprecated_markers

**Description**: Find files with deprecation markers.



## Function: find_test_files_outside_tests

**Description**: Find test files outside tests/ folder.



## Function: find_unused_imports

**Description**: Find files with potentially unused imports (simple heuristic).



## Function: find_script_candidates

**Description**: Find scripts that might be one-off or obsolete.



## Function: main



## Usage Examples

### Function Usage

```python
# Using get_file_stats
result = get_file_stats()
```

```python
# Using find_large_files
result = find_large_files(min_size_kb)
```

```python
# Using find_duplicate_filenames
result = find_duplicate_filenames()
```



---
**Generated**: 2026-03-26T09:39:02.767877
**Type**: api_reference
**Quality**: comprehensive
