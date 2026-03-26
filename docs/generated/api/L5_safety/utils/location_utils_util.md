# API Documentation: location_utils_util

**Target Audience**: developers, api_users

# location_utils_util API Documentation

**File**: `location_utils_util.py`
**Classes**: 0
**Functions**: 4


## Functions

- **normalize_location_path** -> str
- **get_agent_files** -> list[str]
- **compute_module_path** -> str
- **is_path_compliant** -> bool


## Function: normalize_location_path

**Parameters**: path
**Returns**: str
**Description**: 
    Standardizes path formatting for comparison.

    Args:
        path: Path string to normalize

    Returns:
        Normalized path with forward slashes
    



## Function: get_agent_files

**Parameters**: root_dir
**Returns**: list[str]
**Description**: 
    Discovers all .py files within the agentic_core structure.

    Args:
        root_dir: Root directory to search

    Returns:
        List of Python file paths
    



## Function: compute_module_path

**Parameters**: file_path, project_root
**Returns**: str
**Description**: 
    Compute Python module path from file path.

    Args:
        file_path: Path to Python file
        project_root: Optional project root (auto-detected if None)

    Returns:
        Module path string (e.g., 'agentic_core.L5_safety.reasoning.LocationAgent')
    



## Function: is_path_compliant

**Parameters**: file_path, project_root
**Returns**: bool
**Description**: 
    L5 Sovereign Structural SSOT - Hard-enforcement of path validity.

    This is the Supreme Court for structural compliance. All L3 and L2 agents
    that need to validate file paths MUST call this function instead of
    implementing their own path validation logic.

    Enforces:
    1. Path must be within project root
    2. Root folder must be in SOVEREIGN_TERRITORIES (whitelist)
    3. Depth must not exceed MAX_ALLOWED_DEPTH per root
    4. No forbidden root folders (legacy_*, old_*)
    5. No numbered folder prefixes (^\d+_)

    Args:
        file_path: Path to validate (str or Path)
        project_root: Optional project root (auto-detected if None)

    Returns:
        True if path is structurally compliant, False otherwise

    Example:
        >>> is_path_compliant('agentic_core/L5_safety/validators/LocationAgent.py')
        True
        >>> is_path_compliant('legacy_code/old_agent.py')
        False
        >>> is_path_compliant('agentic_core/L1/L2/L3/L4/L5/deep.py')  # Too deep
        False
    



## Usage Examples

### Function Usage

```python
# Using normalize_location_path
result = normalize_location_path(path)
```

```python
# Using get_agent_files
result = get_agent_files(root_dir)
```

```python
# Using compute_module_path
result = compute_module_path(file_path, project_root)
```



---
**Generated**: 2026-03-26T09:39:05.668818
**Type**: api_reference
**Quality**: comprehensive
