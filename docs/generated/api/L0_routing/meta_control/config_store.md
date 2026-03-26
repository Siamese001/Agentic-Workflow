# API Documentation: config_store

**Target Audience**: developers, api_users

# config_store API Documentation

**File**: `config_store.py`
**Classes**: 0
**Functions**: 17


## Functions

- **_capture_start_of_run_state** -> dict[str, Any]
- **_clear_start_of_run_cache** -> None
- **_get_MetaLearningChangePackageArtifact**
- **_component_dir** -> Path
- **_current_path** -> Path
- **_versions_dir** -> Path
- **_version_path** -> Path
- **_atomic_write_json** -> None
- **_validate_inputs** -> None
- **load_current** -> dict[str, Any]
- **_scan_latest_version** -> int
- **write_next_version** -> ConfigSnapshotArtifact
- **apply_change_package_readonly** -> ConfigDeltaArtifact
- **get_active_version** -> int
- **read_active_payload** -> dict[str, Any]
- **read_version_payload** -> dict[str, Any]
- **activate_version** -> None


## Function: _capture_start_of_run_state

**Parameters**: store_root, app_id, component
**Returns**: dict[str, Any]
**Description**: Capture the active state at the start of a run for time-shifted consumption.

    This is called once per component per run to establish what L0 should read
    during this run, regardless of any writes that happen during the run.
    



## Function: _clear_start_of_run_cache

**Returns**: None
**Description**: Clear the start-of-run cache (for testing only).



## Function: _get_MetaLearningChangePackageArtifact



## Function: _component_dir

**Parameters**: store_root, app_id, component
**Returns**: Path


## Function: _current_path

**Parameters**: store_root, app_id, component
**Returns**: Path


## Function: _versions_dir

**Parameters**: store_root, app_id, component
**Returns**: Path


## Function: _version_path

**Parameters**: store_root, app_id, component, version
**Returns**: Path


## Function: _atomic_write_json

**Parameters**: path, data
**Returns**: None
**Description**: Atomically write *data* as canonical JSON to *path*.



## Function: _validate_inputs

**Parameters**: app_id, component
**Returns**: None


## Function: load_current

**Parameters**: store_root, app_id, component
**Returns**: dict[str, Any]
**Description**: Load the current active config payload. Returns {} if missing.



## Function: _scan_latest_version

**Parameters**: store_root, app_id, component
**Returns**: int
**Description**: Scan versions/ directory; return highest version (0 if none).



## Function: write_next_version

**Parameters**: store_root, app_id, component, payload, semantic_clock
**Returns**: ConfigSnapshotArtifact
**Description**: Write a new versioned snapshot and update current.json.



## Function: apply_change_package_readonly

**Parameters**: store_root, change_package, semantic_clock
**Returns**: ConfigDeltaArtifact
**Description**: Compute a config delta WITHOUT writing to disk (read-only).



## Function: get_active_version

**Parameters**: store_root, app_id, component
**Returns**: int
**Description**: Get the currently activated version for a component.

    Returns the version number from current.json or 0 if no active version.
    This represents the version that was activated at the start of the run.

    Args:
        store_root: Root path of the config store.
        app_id: Application identifier.
        component: Component name.

    Returns:
        Active version number (0 if none).
    



## Function: read_active_payload

**Parameters**: store_root, app_id, component
**Returns**: dict[str, Any]
**Description**: Read the payload of the currently activated version.

    This is the time-shifted read: it reads what was activated at the
    start of the run, not anything written during this run.

    Args:
        store_root: Root path of the config store.
        app_id: Application identifier.
        component: Component name.

    Returns:
        Payload dictionary (empty if no active version).
    



## Function: read_version_payload

**Parameters**: store_root, app_id, component, version
**Returns**: dict[str, Any]
**Description**: Read the payload of a specific version.

    Args:
        store_root: Root path of the config store.
        app_id: Application identifier.
        component: Component name.
        version: Specific version to read.

    Returns:
        Payload dictionary for the specified version.

    Raises:
        ValueError: If the version does not exist.
    



## Function: activate_version

**Parameters**: store_root, app_id, component, version
**Returns**: None
**Description**: Activate a specific version by updating current.json.

    This is the only way to change what L0 reads on the next run.
    The activation pointer is updated atomically.

    Args:
        store_root: Root path of the config store.
        app_id: Application identifier.
        component: Component name.
        version: Version to activate.

    Raises:
        ValueError: If the version does not exist.
    



## Usage Examples

### Function Usage

```python
# Using _capture_start_of_run_state
result = _capture_start_of_run_state(store_root, app_id)
```

```python
# Using _clear_start_of_run_cache
result = _clear_start_of_run_cache()
```

```python
# Using _get_MetaLearningChangePackageArtifact
result = _get_MetaLearningChangePackageArtifact()
```



---
**Generated**: 2026-03-26T09:39:02.676795
**Type**: api_reference
**Quality**: comprehensive
