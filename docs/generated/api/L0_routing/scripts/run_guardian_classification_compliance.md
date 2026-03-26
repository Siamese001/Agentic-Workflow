# API Documentation: run_guardian_classification_compliance

**Target Audience**: developers, api_users

# run_guardian_classification_compliance API Documentation

**File**: `run_guardian_classification_compliance.py`
**Classes**: 0
**Functions**: 5


## Functions

- **_collect_python_files** -> list[Path]
- **scan_naming_compliance** -> list[dict]
- **scan_territory_compliance** -> list[dict]
- **run_classification_compliance_guardian** -> GuardianResult
- **main** -> int


## Function: _collect_python_files

**Parameters**: repo_root
**Returns**: list[Path]
**Description**: Return sorted list of Python files in agentic_core/ and apps_*/ trees.

    Deterministic: sorted by repo-relative POSIX path, skips SKIP_PARTS.
    



## Function: scan_naming_compliance

**Parameters**: repo_root, files
**Returns**: list[dict]
**Description**: Detect compound suffix conflicts in filenames.

    Returns sorted list of violation dicts with keys:
    filename, path, conflicting_tags, pattern_matched.
    



## Function: scan_territory_compliance

**Parameters**: repo_root, files
**Returns**: list[dict]
**Description**: Detect files residing in incorrect LCD folders per classification.

    Uses the SSOT classification kernel for AST-based file classification
    and FILETYPE_TO_FOLDER for expected folder mapping.

    Only checks files that are inside a recognized LCD folder within
    agentic_core/ layers. Files in apps_* are excluded (they have
    their own territory rules in FileClassificationAgent).

    Returns sorted list of violation dicts with keys:
    filename, path, classified_as, current_folder, expected_folder.
    



## Function: run_classification_compliance_guardian

**Parameters**: repo_root, write_artifacts_dir, timestamp
**Returns**: GuardianResult
**Description**: Execute classification compliance guardian.

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
# Using _collect_python_files
result = _collect_python_files(repo_root)
```

```python
# Using scan_naming_compliance
result = scan_naming_compliance(repo_root, files)
```

```python
# Using scan_territory_compliance
result = scan_territory_compliance(repo_root, files)
```



---
**Generated**: 2026-03-26T09:39:03.208876
**Type**: api_reference
**Quality**: comprehensive
