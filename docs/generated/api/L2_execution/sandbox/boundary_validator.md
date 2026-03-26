# API Documentation: boundary_validator

**Target Audience**: developers, api_users

# boundary_validator API Documentation

**File**: `boundary_validator.py`
**Classes**: 0
**Functions**: 4


## Functions

- **_snapshot_hash** -> str
- **compute_boundary_diff** -> dict[str, Any]
- **_diff_hash** -> str
- **verify_mutation_replay_integrity** -> None


## Function: _snapshot_hash

**Parameters**: snapshot
**Returns**: str


## Function: compute_boundary_diff

**Parameters**: snapshot_pre, snapshot_post
**Returns**: dict[str, Any]
**Description**: Compute a deterministic diff between two boundary snapshots.

    Returns a dict mapping changed keys to (pre_value, post_value) tuples.
    Only top-level key changes are tracked for simplicity.
    



## Function: _diff_hash

**Parameters**: diff
**Returns**: str


## Function: verify_mutation_replay_integrity

**Parameters**: snapshot_pre, snapshot_post, uwg_state_diff
**Returns**: None
**Description**: Verify that the observed boundary diff matches the UWG-recorded state_diff.

    Raises MutationReplayIntegrityViolation on mismatch.

    Wire into _run_heal_pipeline() Phase 3 validation.
    



## Usage Examples

### Function Usage

```python
# Using _snapshot_hash
result = _snapshot_hash(snapshot)
```

```python
# Using compute_boundary_diff
result = compute_boundary_diff(snapshot_pre, snapshot_post)
```

```python
# Using _diff_hash
result = _diff_hash(diff)
```



---
**Generated**: 2026-03-26T09:39:03.890773
**Type**: api_reference
**Quality**: comprehensive
