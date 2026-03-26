# API Documentation: run_guardian_architecture_governance

**Target Audience**: developers, api_users

# run_guardian_architecture_governance API Documentation

**File**: `run_guardian_architecture_governance.py`
**Classes**: 0
**Functions**: 7


## Functions

- **_get_layer_from_path** -> str | None
- **_extract_target_layer** -> str | None
- **_collect_python_files** -> list[Path]
- **scan_import_compliance** -> list[dict]
- **scan_layer_gravity** -> list[dict]
- **run_architecture_governance_guardian** -> GuardianResult
- **main** -> int


## Function: _get_layer_from_path

**Parameters**: file_path
**Returns**: str | None
**Description**: Extract layer (L0-L6) from file path parts.



## Function: _extract_target_layer

**Parameters**: node
**Returns**: str | None
**Description**: Extract target layer from an import AST node.



## Function: _collect_python_files

**Parameters**: repo_root
**Returns**: list[Path]
**Description**: Return sorted Python files under agentic_core/ for import scanning.



## Function: scan_import_compliance

**Parameters**: repo_root, files
**Returns**: list[dict]
**Description**: Detect illegal upward dependencies (lower layer importing higher layer).

    Reproduces ``gravity_validator._check_import_violations()`` detection
    using pure AST parsing.

    Returns sorted list of violation dicts with keys:
    path, source_layer, target_layer, import_line, line_number.
    



## Function: scan_layer_gravity

**Parameters**: repo_root, files
**Returns**: list[dict]
**Description**: Detect agents physically located in the wrong layer.

    Reproduces ``gravity_validator._check_gravity_violations()`` detection
    using the SSOT scanner. An agent's assigned layer (from its class or
    naming convention) must match its physical location layer.

    Returns sorted list of violation dicts with keys:
    path, agent_name, actual_layer, assigned_layer.
    



## Function: run_architecture_governance_guardian

**Parameters**: repo_root, write_artifacts_dir, timestamp
**Returns**: GuardianResult
**Description**: Execute architecture governance guardian.

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
# Using _get_layer_from_path
result = _get_layer_from_path(file_path)
```

```python
# Using _extract_target_layer
result = _extract_target_layer(node)
```

```python
# Using _collect_python_files
result = _collect_python_files(repo_root)
```



---
**Generated**: 2026-03-26T09:39:03.199102
**Type**: api_reference
**Quality**: comprehensive
