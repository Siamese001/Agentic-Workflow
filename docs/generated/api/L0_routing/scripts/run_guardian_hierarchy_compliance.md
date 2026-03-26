# API Documentation: run_guardian_hierarchy_compliance

**Target Audience**: developers, api_users

# run_guardian_hierarchy_compliance API Documentation

**File**: `run_guardian_hierarchy_compliance.py`
**Classes**: 0
**Functions**: 5


## Functions

- **_get_l3_subfolders** -> list[str]
- **scan_missing_structure** -> list[dict]
- **scan_subfolder_compliance** -> list[dict]
- **run_hierarchy_compliance_guardian** -> GuardianResult
- **main** -> int


## Function: _get_l3_subfolders

**Parameters**: layer_def
**Returns**: list[str]
**Description**: Extract L3 subfolder names from a layer definition in SOVEREIGN_TERRITORIES.

    The nested structure is: agentic_core -> subfolders -> L2_layer -> subfolders -> {L3...}
    Works with both dict and MappingProxyType (deep-frozen).
    



## Function: scan_missing_structure

**Parameters**: repo_root
**Returns**: list[dict]
**Description**: Detect missing L2 layer and L3 sub-territory directories.

    Reproduces ``HierarchyAgent.create_missing_structure()`` detection logic
    without creating anything.

    Returns sorted list of violation dicts with keys:
    level, path, parent_layer (for L3 violations).
    



## Function: scan_subfolder_compliance

**Parameters**: repo_root
**Returns**: list[dict]
**Description**: Detect non-approved subfolders within agentic_core layers.

    Reproduces ``HierarchyAgent._relocate_l3_territory_files()`` detection:
    any subfolder under an L2 layer that is not in the SOVEREIGN_TERRITORIES
    blueprint is a compliance violation.

    Returns sorted list of violation dicts with keys:
    path, parent_layer, folder_name.
    



## Function: run_hierarchy_compliance_guardian

**Parameters**: repo_root, write_artifacts_dir, timestamp
**Returns**: GuardianResult
**Description**: Execute hierarchy compliance guardian.

    Args:
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir to write result JSON.
        timestamp: Injectable timestamp for determinism.

    Returns:
        GuardianResult conforming to guardian_contract.py schema.
    



## Function: main

**Returns**: int


## Usage Examples

### Function Usage

```python
# Using _get_l3_subfolders
result = _get_l3_subfolders(layer_def)
```

```python
# Using scan_missing_structure
result = scan_missing_structure(repo_root)
```

```python
# Using scan_subfolder_compliance
result = scan_subfolder_compliance(repo_root)
```



---
**Generated**: 2026-03-26T09:39:03.227592
**Type**: api_reference
**Quality**: comprehensive
