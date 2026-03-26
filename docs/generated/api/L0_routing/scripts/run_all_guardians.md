# API Documentation: run_all_guardians

**Target Audience**: developers, api_users

# run_all_guardians API Documentation

**File**: `run_all_guardians.py`
**Classes**: 0
**Functions**: 4


## Functions

- **_run_single_guardian** -> GuardianResult
- **run_all_guardians** -> GuardianResult
- **main** -> int
- **render_meta_learning_change_package** -> str


## Function: _run_single_guardian

**Parameters**: spec, repo_root, artifact_dir, timestamp, correlation_id
**Returns**: GuardianResult
**Description**: Import and execute a single guardian, returning its result.



## Function: run_all_guardians

**Parameters**: repo_root, write_artifacts_dir, timestamp, correlation_id, include_disabled
**Returns**: GuardianResult
**Description**: 
    Execute all registered guardians in deterministic order and aggregate.

    Args:
        include_disabled: If True, run ALL guardians (including disabled_by_default).
                          Default False = enabled-only.

    Returns a combined GuardianResult with:
    - guardian_id = "combined"
    - Global status promotion (ERROR > FAIL > PASS)
    - Per-guardian check entries
    - Combined metrics
    - Artifact references
    



## Function: main

**Returns**: int


## Function: render_meta_learning_change_package

**Parameters**: package
**Returns**: str
**Description**: Render a MetaLearningChangePackageArtifact as a deterministic string.

    This is a **pure function**: it does NOT call apply_meta_learning_proposal(),
    does NOT mutate any config, and does NOT write any files.

    Parameters
    ----------
    package : MetaLearningChangePackageArtifact
        The change package to render.
    as_json : bool
        If True, return canonical JSON string of package.to_dict().
        If False, return a stable, minimal single-line summary.

    Returns
    -------
    str
        Deterministic string representation.
    



## Usage Examples

### Function Usage

```python
# Using _run_single_guardian
result = _run_single_guardian(spec, repo_root)
```

```python
# Using run_all_guardians
result = run_all_guardians(repo_root, write_artifacts_dir)
```

```python
# Using main
result = main()
```



---
**Generated**: 2026-03-26T09:39:03.194492
**Type**: api_reference
**Quality**: comprehensive
