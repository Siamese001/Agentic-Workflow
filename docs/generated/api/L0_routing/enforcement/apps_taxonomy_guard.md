# API Documentation: apps_taxonomy_guard

**Target Audience**: developers, api_users

# apps_taxonomy_guard API Documentation

**File**: `apps_taxonomy_guard.py`
**Classes**: 1
**Functions**: 6

## Classes

- **AppsTaxonomyGuard**

## Functions

- **scan** -> tuple[str, ...]
- **_scan_apps_directory** -> list[str]
- **_scan_file** -> list[str]
- **_check_import_node** -> list[str]
- **_check_import_from_node** -> list[str]
- **_is_allowed_import** -> bool


## Class: AppsTaxonomyGuard

**Description**: 
    Guard that enforces apps_* taxonomy rules via AST parsing.

    Uses read-only AST parsing (no imports/execution) to detect
    prohibited imports from apps_* to agentic_core.
    

### Methods

#### scan
**Parameters**: self
**Returns**: tuple[str, ...]
**Description**: 
        Scan apps_* packages for prohibited agentic_core imports.

        Args:
            repo_root: Repository root path

        Returns:
            Deterministic sorted tuple of violation strings: "path:lineno import ..."
        

#### _scan_apps_directory
**Parameters**: self, apps_dir, repo_root
**Returns**: list[str]
**Description**: Scan a single apps_* directory for violations.

#### _scan_file
**Parameters**: self, file_path, repo_root
**Returns**: list[str]
**Description**: Scan a single Python file for prohibited imports.

#### _check_import_node
**Parameters**: self, node, file_path, repo_root
**Returns**: list[str]
**Description**: Check import node for prohibited agentic_core imports.

#### _check_import_from_node
**Parameters**: self, node, file_path, repo_root
**Returns**: list[str]
**Description**: Check import-from node for prohibited agentic_core imports.

#### _is_allowed_import
**Parameters**: self, import_path
**Returns**: bool
**Description**: Check if import path is in the allowlist.



## Function: scan

**Parameters**: self
**Returns**: tuple[str, ...]
**Description**: 
        Scan apps_* packages for prohibited agentic_core imports.

        Args:
            repo_root: Repository root path

        Returns:
            Deterministic sorted tuple of violation strings: "path:lineno import ..."
        



## Function: _scan_apps_directory

**Parameters**: self, apps_dir, repo_root
**Returns**: list[str]
**Description**: Scan a single apps_* directory for violations.



## Function: _scan_file

**Parameters**: self, file_path, repo_root
**Returns**: list[str]
**Description**: Scan a single Python file for prohibited imports.



## Function: _check_import_node

**Parameters**: self, node, file_path, repo_root
**Returns**: list[str]
**Description**: Check import node for prohibited agentic_core imports.



## Function: _check_import_from_node

**Parameters**: self, node, file_path, repo_root
**Returns**: list[str]
**Description**: Check import-from node for prohibited agentic_core imports.



## Function: _is_allowed_import

**Parameters**: self, import_path
**Returns**: bool
**Description**: Check if import path is in the allowlist.



## Usage Examples

### Class Usage

```python
# Using AppsTaxonomyGuard
appstaxonomyguard = AppsTaxonomyGuard()
appstaxonomyguard.scan()
```

### Function Usage

```python
# Using scan
result = scan()
```

```python
# Using _scan_apps_directory
result = _scan_apps_directory(apps_dir, repo_root)
```

```python
# Using _scan_file
result = _scan_file(file_path, repo_root)
```



---
**Generated**: 2026-03-26T09:39:02.597799
**Type**: api_reference
**Quality**: comprehensive
