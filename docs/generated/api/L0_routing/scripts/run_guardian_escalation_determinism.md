# API Documentation: run_guardian_escalation_determinism

**Target Audience**: developers, api_users

# run_guardian_escalation_determinism API Documentation

**File**: `run_guardian_escalation_determinism.py`
**Classes**: 0
**Functions**: 4


## Functions

- **_collect_files** -> list[Path]
- **scan_escalation_patterns** -> dict[str, list[dict]]
- **run_escalation_determinism_guardian** -> GuardianResult
- **_main** -> int


## Function: _collect_files

**Parameters**: repo_root
**Returns**: list[Path]


## Function: scan_escalation_patterns

**Parameters**: repo_root, files
**Returns**: dict[str, list[dict]]


## Function: run_escalation_determinism_guardian

**Parameters**: repo_root, write_artifacts_dir, timestamp, correlation_id
**Returns**: GuardianResult


## Function: _main

**Parameters**: argv
**Returns**: int


## Usage Examples

### Function Usage

```python
# Using _collect_files
result = _collect_files(repo_root)
```

```python
# Using scan_escalation_patterns
result = scan_escalation_patterns(repo_root, files)
```

```python
# Using run_escalation_determinism_guardian
result = run_escalation_determinism_guardian(repo_root, write_artifacts_dir)
```



---
**Generated**: 2026-03-26T09:39:03.221130
**Type**: api_reference
**Quality**: comprehensive
