# API Documentation: guardian_heal_orchestrator

**Target Audience**: developers, api_users

# guardian_heal_orchestrator API Documentation

**File**: `guardian_heal_orchestrator.py`
**Classes**: 0
**Functions**: 4


## Functions

- **_run_guardians** -> dict
- **_run_dispatcher** -> dict
- **run_pipeline** -> dict
- **main** -> int


## Function: _run_guardians

**Parameters**: repo_root, timestamp, correlation_id, write_artifacts_dir
**Returns**: dict
**Description**: Run all enabled guardians and return aggregate result as dict.



## Function: _run_dispatcher

**Parameters**: guardian_aggregate, write_artifacts_dir, created_utc
**Returns**: dict
**Description**: Run the remediation dispatcher on guardian aggregate.

    Writes aggregate to a temp file for dispatcher consumption, then
    invokes the dispatcher and returns the CombinedHealResult as dict.
    



## Function: run_pipeline

**Parameters**: mode, repo_root, write_artifacts_dir, timestamp, correlation_id, allow_repo_mutation
**Returns**: dict
**Description**: Execute the L0 pipeline in the specified mode.

    Args:
        mode: One of "scan", "dry-run", "apply".
        repo_root: Project root (defaults to SSOT get_validated_project_root).
        write_artifacts_dir: Repo-relative dir for artifacts.
        timestamp: Injectable ISO-8601 timestamp.
        correlation_id: Trace correlation ID.
        allow_repo_mutation: Allow apply mode on non-sandbox repos.

    Returns:
        Pipeline result dict with keys: mode, guardian_result, heal_result (if applicable).
    



## Function: main

**Returns**: int


## Usage Examples

### Function Usage

```python
# Using _run_guardians
result = _run_guardians(repo_root, timestamp)
```

```python
# Using _run_dispatcher
result = _run_dispatcher(guardian_aggregate, write_artifacts_dir)
```

```python
# Using run_pipeline
result = run_pipeline(mode, repo_root)
```



---
**Generated**: 2026-03-26T09:39:04.352560
**Type**: api_reference
**Quality**: comprehensive
