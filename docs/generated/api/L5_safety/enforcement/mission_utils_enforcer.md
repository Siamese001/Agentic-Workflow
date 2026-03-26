# API Documentation: mission_utils_enforcer

**Target Audience**: developers, api_users

# mission_utils_enforcer API Documentation

**File**: `mission_utils_enforcer.py`
**Classes**: 0
**Functions**: 7


## Functions

- **dynamic_import** -> Any | None
- **get_layer_rank** -> int
- **get_legal_l2_for_l1** -> list[str]
- **get_placement_guidance** -> str
- **get_best_target_l1** -> str
- **_calculate_subfolder_confidence_for_agent** -> float
- **get_best_target_l2** -> str


## Function: dynamic_import

**Parameters**: module_path, class_name
**Returns**: Any | None
**Description**: 
    Dynamically import classes to avoid gravity violations.

    Args:
        module_path: Dotted module path (e.g., 'agentic_core.L5_safety.enforcement.SafetyGuardrail')
        class_name: Name of the class to import

    Returns:
        The imported class, or None if import fails
    



## Function: get_layer_rank

**Parameters**: path_str
**Returns**: int
**Description**: 
    Get the authority rank of a layer based on its position in the SSOT registry.
    Lower index = higher authority.

    Args:
        path_str: File path string to check

    Returns:
        Layer rank (0-based index), or -1 if not found
    



## Function: get_legal_l2_for_l1

**Parameters**: root, l1_name
**Returns**: list[str]
**Description**: 
    Pull valid L2 folders directly from imported SSOT maps.

    Args:
        root: Root territory name (agentic_core, apps_rg, apps_lic, apps_shared)
        l1_name: L1 folder name

    Returns:
        List of approved L2 subfolder names
    



## Function: get_placement_guidance

**Parameters**: content_preview
**Returns**: str
**Description**: 
    Heuristically determine the best L1 placement for code based on content signals.

    Args:
        content_preview: First ~500 chars of file content

    Returns:
        Suggested L1 path (e.g., 'agentic_core/L1_cognition')
    



## Function: get_best_target_l1

**Parameters**: folder_name, approved_l1
**Returns**: str
**Description**: 
    Heuristically determine the best approved L1 folder for a non-approved folder.

    Args:
        folder_name: Name of the folder to relocate
        approved_l1: Set of approved L1 folder names

    Returns:
        Best matching approved L1 folder name
    



## Function: _calculate_subfolder_confidence_for_agent

**Parameters**: l1_name, item_name
**Returns**: float
**Description**: Return placement confidence for an *Agent.py file into l1_name.

    Returns:
        < 0.5 — caller must NOT auto-relocate; archive instead.
        1.0   — source layer; relocation is acceptable.
    



## Function: get_best_target_l2

**Parameters**: l1_name, item_name
**Returns**: str
**Description**: 
    Heuristically determine the best approved L2 folder within an L1.

    Args:
        l1_name: L1 folder name
        item_name: Name of file/folder to place

    Returns:
        Best matching L2 folder name, or ``"__ARCHIVE__"`` sentinel when the
        placement confidence for an *Agent.py file is below 0.5.  Callers must
        check for this sentinel and route to safe_archive() instead of moving.
    



## Usage Examples

### Function Usage

```python
# Using dynamic_import
result = dynamic_import(module_path, class_name)
```

```python
# Using get_layer_rank
result = get_layer_rank(path_str)
```

```python
# Using get_legal_l2_for_l1
result = get_legal_l2_for_l1(root, l1_name)
```



---
**Generated**: 2026-03-26T09:39:04.871279
**Type**: api_reference
**Quality**: comprehensive
