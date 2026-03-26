# API Documentation: location_path_util

**Target Audience**: developers, api_users

# location_path_util API Documentation

**File**: `location_path_util.py`
**Classes**: 0
**Functions**: 2


## Functions

- **is_path_compliant** -> bool
- **get_location_agent** -> LocationHealerAgent


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
    



## Function: get_location_agent

**Parameters**: project_root
**Returns**: LocationHealerAgent
**Description**: Get or create LocationHealerAgent singleton.

    Backward-compatible redirect: callers that previously used
    ``get_location_agent()`` from LocationAgent.py now get a
    LocationHealerAgent instance instead.
    



## Usage Examples

### Function Usage

```python
# Using is_path_compliant
result = is_path_compliant(file_path, project_root)
```

```python
# Using get_location_agent
result = get_location_agent(project_root)
```



---
**Generated**: 2026-03-26T09:39:05.666160
**Type**: api_reference
**Quality**: comprehensive
