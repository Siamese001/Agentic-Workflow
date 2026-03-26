# API Documentation: meta_apply_ops

**Target Audience**: developers, api_users

# meta_apply_ops API Documentation

**File**: `meta_apply_ops.py`
**Classes**: 0
**Functions**: 13


## Functions

- **_get_apply_attempt_types**
- **_get_rollout_types**
- **_check_no_schema_changes** -> bool
- **_check_policy_hash_unchanged** -> bool
- **_check_guardian_determinism_empty_diff** -> bool
- **evaluate_invariants** -> tuple[bool, str | None]
- **rollback_meta_learning_rollout** -> MetaLearningRollbackArtifact
- **apply_with_invariants** -> MetaLearningApplyAttemptArtifact
- **_rate_limit_path** -> Path
- **check_rate_limit** -> tuple[bool, int | None]
- **record_apply_timestamp** -> None
- **_canary_state_path** -> Path
- **record_canary_state** -> dict[str, Any]


## Function: _get_apply_attempt_types



## Function: _get_rollout_types



## Function: _check_no_schema_changes

**Parameters**: base_dir, target_component, policy_config_hash
**Returns**: bool
**Description**: Assert no changes outside the target config file path.

    Checks that only config.json and rollback.json exist in the component dir.
    



## Function: _check_policy_hash_unchanged

**Parameters**: base_dir, target_component, policy_config_hash
**Returns**: bool
**Description**: Assert policy_config_hash matches the one stored in config metadata.

    In this wave, we validate structurally: the hash parameter is non-None
    iff the caller expects policy pinning. Always passes if hash is None
    (unpinned mode).
    



## Function: _check_guardian_determinism_empty_diff

**Parameters**: base_dir, target_component, policy_config_hash
**Returns**: bool
**Description**: Simulated guardian determinism check.

    In production this would compare two guardian JSON runs.
    In this wave it is a structural placeholder that always passes
    unless a test injects a failing comparator.
    



## Function: evaluate_invariants

**Parameters**: invariant_names, base_dir, target_component, policy_config_hash
**Returns**: tuple[bool, str | None]
**Description**: Evaluate named invariants from the registry.

    Returns (all_pass, first_failure_name).
    Unknown invariant names are treated as failures (fail-closed).
    



## Function: rollback_meta_learning_rollout

**Returns**: MetaLearningRollbackArtifact
**Description**: Restore prior config from rollback snapshot and emit rollback artifact.

    Parameters
    ----------
    rollout_plan : MetaLearningRolloutPlanArtifact
        The rollout plan being rolled back.
    reason : str
        One of ROLLBACK_REASONS.
    target_component : str
        Target component name (from change_package).
    base_dir : Path
        Base directory for versioned config state.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    policy_config_hash : str | None
        Policy config hash for the rollback artifact.

    Returns
    -------
    MetaLearningRollbackArtifact
    



## Function: apply_with_invariants

**Returns**: MetaLearningApplyAttemptArtifact
**Description**: Write candidate config, evaluate invariants, rollback on failure.

    This function is called AFTER all gates pass in apply_meta_learning_rollout.
    It performs the actual write, evaluates invariants, and rolls back if any fail.

    Parameters
    ----------
    change_package_trace_id : str
        Trace ID of the change package being applied.
    rollout_plan : MetaLearningRolloutPlanArtifact
        The rollout plan (contains invariant names).
    change_spec : dict
        The change to write.
    target_component : str
        Target component name.
    base_dir : Path
        Base directory for versioned config state.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    policy_config_hash : str | None
        Policy config hash.

    Returns
    -------
    MetaLearningApplyAttemptArtifact
    



## Function: _rate_limit_path

**Parameters**: base_dir, target_component
**Returns**: Path
**Description**: Path to rate-limit state file.



## Function: check_rate_limit

**Parameters**: base_dir, app_id, target_component, now_epoch_s
**Returns**: tuple[bool, int | None]
**Description**: Check if an apply is allowed under the rate limit.

    Returns (allowed, last_apply_epoch_s).
    Only 1 APPLY per (app_id, target_component) per hour.
    



## Function: record_apply_timestamp

**Parameters**: base_dir, app_id, target_component, now_epoch_s
**Returns**: None
**Description**: Record an apply timestamp for rate limiting.



## Function: _canary_state_path

**Parameters**: base_dir, target_component
**Returns**: Path
**Description**: Path to canary state file.



## Function: record_canary_state

**Returns**: dict[str, Any]
**Description**: Record canary rollout state for governance tracking.

    Only records plan state — no per-user routing.

    Returns the canary state dict.
    



## Usage Examples

### Function Usage

```python
# Using _get_apply_attempt_types
result = _get_apply_attempt_types()
```

```python
# Using _get_rollout_types
result = _get_rollout_types()
```

```python
# Using _check_no_schema_changes
result = _check_no_schema_changes(base_dir, target_component)
```



---
**Generated**: 2026-03-26T09:39:02.687925
**Type**: api_reference
**Quality**: comprehensive
