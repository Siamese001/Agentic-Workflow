# API Documentation: ssot

**Target Audience**: developers, api_users

# ssot API Documentation

**File**: `ssot.py`
**Classes**: 0
**Functions**: 22


## Functions

- **is_layer_root** -> bool
- **is_allowed_subfolder** -> bool
- **validate_no_nested_lcd** -> dict[str, Any] | None
- **get_canonical_test_path** -> Path
- **get_validated_project_root** -> Path
- **validate_path_within_project** -> bool
- **safe_path_join** -> Path
- **get_sovereign_territories** -> Mapping[str, Any]
- **get_core_subfolder_map** -> Mapping[str, Sequence[str]]
- **get_subfolder_metadata** -> Mapping[str, Mapping[str, Any]]
- **get_apps_rg_subfolder_map** -> Mapping[str, Sequence[str]]
- **get_apps_lic_subfolder_map** -> Mapping[str, Sequence[str]]
- **get_apps_shared_subfolder_map** -> Mapping[str, Sequence[str]]
- **get_apps_eval_subfolder_map** -> Mapping[str, Sequence[str]]
- **get_apps_exec_subfolder_map** -> Mapping[str, Sequence[str]]
- **get_apps_research_subfolder_map** -> Mapping[str, Sequence[str]]
- **get_apps_rfp_subfolder_map** -> Mapping[str, Sequence[str]]
- **safe_prefixed_filename** -> str
- **validate_no_duplicate_prefix** -> tuple[bool, str]
- **is_path_allowed** -> bool
- **is_l4_approved** -> bool
- **validate_flat_directory** -> dict[str, Any] | None


## Function: is_layer_root

**Parameters**: name
**Returns**: bool
**Description**: Return True if *name* is a canonical L0–L6 layer root.



## Function: is_allowed_subfolder

**Parameters**: layer, subfolder
**Returns**: bool
**Description**: Return True if *subfolder* is a required LCD subfolder under *layer*.



## Function: validate_no_nested_lcd

**Parameters**: path_parts
**Returns**: dict[str, Any] | None
**Description**: Detect leaf domains that illegally sprout LCD subtrees.

    Args:
        path_parts: tuple/list of path components (e.g. Path.parts).

    Returns:
        None if compliant, or a violation dict with:
        - domain: the leaf domain that is sprouting
        - illegal_subfolder: the LCD subfolder it created
        - message: human-readable explanation
    



## Function: get_canonical_test_path

**Parameters**: source_path, repo_root
**Returns**: Path
**Description**: Return the canonical test file path for a given source file.

    LocationHealerAgent and TestGeneratorAgent MUST call this function instead
    of constructing test paths ad-hoc.  The mapping is read from
    TEST_CANONICAL_LOCATION_MAP so there is a single SSOT.

    Examples
    --------
    source: agentic_core/L5_safety/foo.py  →  tests/unit/agentic_core/L5_safety/test_foo.py
    source: apps_rg/engines/bar.py         →  tests/unit/apps_rg/engines/test_bar.py
    source: tools/mirror_tests.py          →  tests/unit_min_deps/test_mirror_tests.py
    



## Function: get_validated_project_root

**Returns**: Path
**Description**: Get the validated project root by searching upward from this file.



## Function: validate_path_within_project

**Parameters**: path, project_root
**Returns**: bool
**Description**: Validate that a path is within the project root.



## Function: safe_path_join

**Parameters**: project_root
**Returns**: Path
**Description**: Safely join path parts and validate result is within project root.



## Function: get_sovereign_territories

**Returns**: Mapping[str, Any]
**Description**: Return territory definitions (DEPRECATED: use get_all_territories() instead).



## Function: get_core_subfolder_map

**Returns**: Mapping[str, Sequence[str]]
**Description**: Return CORE_SUBFOLDER_MAP from derived module.



## Function: get_subfolder_metadata

**Returns**: Mapping[str, Mapping[str, Any]]
**Description**: Return SUBFOLDER_METADATA from derived module.



## Function: get_apps_rg_subfolder_map

**Returns**: Mapping[str, Sequence[str]]
**Description**: Return APPS_RG_SUBFOLDER_MAP from derived module.



## Function: get_apps_lic_subfolder_map

**Returns**: Mapping[str, Sequence[str]]
**Description**: Return APPS_LIC_SUBFOLDER_MAP from derived module.



## Function: get_apps_shared_subfolder_map

**Returns**: Mapping[str, Sequence[str]]
**Description**: Return APPS_SHARED_SUBFOLDER_MAP from derived module.



## Function: get_apps_eval_subfolder_map

**Returns**: Mapping[str, Sequence[str]]
**Description**: Return APPS_EVAL_SUBFOLDER_MAP from derived module.



## Function: get_apps_exec_subfolder_map

**Returns**: Mapping[str, Sequence[str]]
**Description**: Return APPS_EXEC_SUBFOLDER_MAP from derived module.



## Function: get_apps_research_subfolder_map

**Returns**: Mapping[str, Sequence[str]]
**Description**: Return APPS_RESEARCH_SUBFOLDER_MAP from derived module.



## Function: get_apps_rfp_subfolder_map

**Returns**: Mapping[str, Sequence[str]]
**Description**: Return APPS_RFP_SUBFOLDER_MAP from derived module.



## Function: safe_prefixed_filename

**Parameters**: prefix, filename
**Returns**: str
**Description**: 
    SSOT safeguard: Generate a prefixed filename WITHOUT duplicate prefixes.

    Prevents name sprawl like:
        healing_strategies.py -> healing_healing_strategies.py (BAD)

    Instead produces:
        healing_strategies.py -> healing_strategies.py (already has prefix)
        strategies.py -> healing_strategies.py (prefix added)

    Args:
        prefix: The prefix to add (e.g., 'healing', 'auditors')
        filename: The original filename

    Returns:
        Filename with prefix added only if not already present
    



## Function: validate_no_duplicate_prefix

**Parameters**: filename
**Returns**: tuple[bool, str]
**Description**: 
    SSOT safeguard: Detect if a filename has duplicate prefixes.

    Examples of violations:
        healing_healing_strategies.py -> True, "Duplicate prefix: healing_"
        auditors_auditors_report.py -> True, "Duplicate prefix: auditors_"

    Returns:
        (has_violation, message)
    



## Function: is_path_allowed

**Parameters**: rel_path
**Returns**: bool
**Description**: 
    [ULTRA-HARDENED] Determines if a path conforms to SOVEREIGN_TERRITORIES.
    Enforces path normalization, cross-domain deportation, and depth precision.
    



## Function: is_l4_approved

**Parameters**: path
**Returns**: bool
**Description**: 
    [HARDENED] Helper to verify L4 specializations.
    Safely navigates both List-based (Apps) and Dict-based (Core) subfolders.
    ONLY approves exactly depth 4 folder structures (excluding filename).
    



## Function: validate_flat_directory

**Parameters**: path_parts
**Returns**: dict[str, Any] | None
**Description**: Detect files nested inside directories that must be flat (no subfolders).

    Args:
        path_parts: tuple/list of path components (e.g. Path.parts).

    Returns:
        None if compliant, or a violation dict with:
        - domain: the flat directory that was violated
        - illegal_child: the subdirectory found inside it
        - message: human-readable explanation
    



## Usage Examples

### Function Usage

```python
# Using is_layer_root
result = is_layer_root(name)
```

```python
# Using is_allowed_subfolder
result = is_allowed_subfolder(layer, subfolder)
```

```python
# Using validate_no_nested_lcd
result = validate_no_nested_lcd(path_parts)
```



---
**Generated**: 2026-03-26T09:39:05.941661
**Type**: api_reference
**Quality**: comprehensive
