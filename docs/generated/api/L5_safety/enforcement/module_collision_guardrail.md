# API Documentation: module_collision_guardrail

**Target Audience**: developers, api_users

# module_collision_guardrail API Documentation

**File**: `module_collision_guardrail.py`
**Classes**: 0
**Functions**: 12


## Functions

- **compute_logical_import_path** -> str
- **should_exclude** -> bool
- **scan_directory** -> dict[str, list[Path]]
- **is_allowed_shim_pair** -> bool
- **detect_collisions** -> dict[str, list[tuple[str, list[Path]]]]
- **format_violations** -> str
- **load_baseline** -> dict
- **save_baseline** -> None
- **check_against_baseline** -> list[str]
- **get_repo_root** -> Path
- **discover_roots** -> dict[str, Path]
- **main**


## Function: compute_logical_import_path

**Parameters**: file_path, root
**Returns**: str
**Description**: Compute logical import path for a Python file.



## Function: should_exclude

**Parameters**: path
**Returns**: bool
**Description**: Check if path should be excluded from scanning.



## Function: scan_directory

**Parameters**: root, repo_root
**Returns**: dict[str, list[Path]]
**Description**: Scan directory for Python files and map logical paths to physical files.



## Function: is_allowed_shim_pair

**Parameters**: files
**Returns**: bool
**Description**: Check if duplicate files form an allowed canonical+shim pair.



## Function: detect_collisions

**Parameters**: scans
**Returns**: dict[str, list[tuple[str, list[Path]]]]
**Description**: Detect various types of module collisions.



## Function: format_violations

**Parameters**: violations
**Returns**: str
**Description**: Format violations for output with deterministic sorting.



## Function: load_baseline

**Returns**: dict
**Description**: Load the baseline file containing allowed collisions.



## Function: save_baseline

**Parameters**: collisions
**Returns**: None
**Description**: Save current collisions to baseline file (deterministic format).



## Function: check_against_baseline

**Parameters**: collisions, baseline
**Returns**: list[str]
**Description**: Check if collisions exceed baseline. Returns list of violations.



## Function: get_repo_root

**Returns**: Path
**Description**: Determine repository root via git or fallback to .git search.



## Function: discover_roots

**Parameters**: repo_root
**Returns**: dict[str, Path]
**Description**: Discover roots to scan with deterministic ordering.



## Function: main

**Description**: Main entry point.



## Usage Examples

### Function Usage

```python
# Using compute_logical_import_path
result = compute_logical_import_path(file_path, root)
```

```python
# Using should_exclude
result = should_exclude(path)
```

```python
# Using scan_directory
result = scan_directory(root, repo_root)
```



---
**Generated**: 2026-03-26T09:39:04.880767
**Type**: api_reference
**Quality**: comprehensive
