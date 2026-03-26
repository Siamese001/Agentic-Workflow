# API Documentation: _verify

**Target Audience**: developers, api_users

# _verify API Documentation

**File**: `_verify.py`
**Classes**: 0
**Functions**: 9


## Functions

- **_allowlist_hash** -> str
- **_assert_frozen** -> str | None
- **_print_phantom_diff** -> None
- **_canonical_repo_path** -> str
- **_is_repo_relative_normalized** -> bool
- **_collect_scan_files** -> tuple[list[str], list[str]]
- **_path_under_scan_roots** -> bool
- **main** -> int
- **dfs** -> None


## Function: _allowlist_hash

**Returns**: str
**Description**: Deterministic SHA-256 of the canonical allowlist.



## Function: _assert_frozen

**Parameters**: obj, path
**Returns**: str | None
**Description**: Recursively verify deep immutability.

    Returns None if fully frozen, or a string describing the first
    mutable structure found (with its path).
    



## Function: _print_phantom_diff

**Parameters**: current, saved
**Returns**: None
**Description**: Print deterministic diff between current and saved phantom sets.



## Function: _canonical_repo_path

**Parameters**: path
**Returns**: str
**Description**: Normalize a path to canonical repo-relative form.

    - Converts backslashes to forward slashes
    - Collapses '.' segments
    - Rejects '..' segments (raises ValueError)
    - Rejects absolute paths (raises ValueError)
    - Returns normalized forward-slash path
    



## Function: _is_repo_relative_normalized

**Parameters**: path
**Returns**: bool
**Description**: Check path is repo-relative, forward-slash only, no '..' segments.

    Baseline entries must already be in canonical form — backslashes are rejected.
    



## Function: _collect_scan_files

**Parameters**: root
**Returns**: tuple[list[str], list[str]]
**Description**: Collect all files under SCAN_ROOTS with SCAN_EXTENSIONS, excluding SCAN_EXCLUDES.

    Returns (files, missing_roots) where missing_roots lists any SCAN_ROOT
    that does not exist as a directory.
    



## Function: _path_under_scan_roots

**Parameters**: path
**Returns**: bool
**Description**: Check that a repo-relative path starts with one of SCAN_ROOTS.



## Function: main

**Returns**: int


## Function: dfs

**Parameters**: u
**Returns**: None


## Usage Examples

### Function Usage

```python
# Using _allowlist_hash
result = _allowlist_hash()
```

```python
# Using _assert_frozen
result = _assert_frozen(obj, path)
```

```python
# Using _print_phantom_diff
result = _print_phantom_diff(current, saved)
```



---
**Generated**: 2026-03-26T09:39:05.977665
**Type**: api_reference
**Quality**: comprehensive
