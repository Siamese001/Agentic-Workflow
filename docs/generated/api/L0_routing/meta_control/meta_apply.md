# API Documentation: meta_apply

**Target Audience**: developers, api_users

# meta_apply API Documentation

**File**: `meta_apply.py`
**Classes**: 0
**Functions**: 13


## Functions

- **_get_apply_attempt_types**
- **_get_meta_learning_types**
- **_get_rollout_types**
- **_get_CapabilityTokenArtifact**
- **_check_routing_thresholds_blast** -> str | None
- **_check_tool_policies_blast** -> str | None
- **_check_prompt_templates_blast** -> str | None
- **_check_blast_radius** -> str | None
- **_config_path** -> Path
- **_rollback_path** -> Path
- **_atomic_write_json** -> None
- **apply_meta_learning_rollout** -> MetaLearningApplyAttemptArtifact
- **_reject** -> MetaLearningApplyAttemptArtifact


## Function: _get_apply_attempt_types



## Function: _get_meta_learning_types



## Function: _get_rollout_types



## Function: _get_CapabilityTokenArtifact

**Description**: Lazy load CapabilityTokenArtifact to avoid upward import.



## Function: _check_routing_thresholds_blast

**Parameters**: change_spec
**Returns**: str | None
**Description**: Validate routing_thresholds change_spec against blast-radius limits.

    Returns reject_reason string or None if valid.
    



## Function: _check_tool_policies_blast

**Parameters**: change_spec
**Returns**: str | None
**Description**: Validate tool_policies change_spec against blast-radius limits.

    Returns reject_reason string or None if valid.
    



## Function: _check_prompt_templates_blast

**Parameters**: change_spec
**Returns**: str | None
**Description**: Validate prompt_templates change_spec against blast-radius limits.

    Returns reject_reason string or None if valid.
    



## Function: _check_blast_radius

**Parameters**: target_component, change_spec
**Returns**: str | None
**Description**: Dispatch blast-radius check to component-specific validator.



## Function: _config_path

**Parameters**: base_dir, target_component
**Returns**: Path
**Description**: Deterministic config file path for a target component.



## Function: _rollback_path

**Parameters**: base_dir, target_component
**Returns**: Path
**Description**: Deterministic rollback snapshot path for a target component.



## Function: _atomic_write_json

**Parameters**: path, data
**Returns**: None
**Description**: Atomic JSON write: write to tmp then rename.



## Function: apply_meta_learning_rollout

**Returns**: MetaLearningApplyAttemptArtifact
**Description**: Explicit, guarded runtime apply for meta-learning changes.

    Parameters
    ----------
    change_package : MetaLearningChangePackageArtifact
        The approved change package to apply.
    rollout_plan : MetaLearningRolloutPlanArtifact
        The rollout plan governing this apply.
    capability_token : CapabilityTokenArtifact | None
        Required capability token with FS:WRITE permission.
    apply_mode : "DRY_RUN" | "APPLY"
        DRY_RUN validates gates only; APPLY writes config.
    policy_config_hash : str | None
        Expected policy config hash; must match all artifacts.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    base_dir : Path | None
        Base directory for versioned config state. Required for APPLY mode.

    Returns
    -------
    MetaLearningApplyAttemptArtifact
        Audit record of the apply attempt.
    



## Function: _reject

**Parameters**: reason
**Returns**: MetaLearningApplyAttemptArtifact


## Usage Examples

### Function Usage

```python
# Using _get_apply_attempt_types
result = _get_apply_attempt_types()
```

```python
# Using _get_meta_learning_types
result = _get_meta_learning_types()
```

```python
# Using _get_rollout_types
result = _get_rollout_types()
```



---
**Generated**: 2026-03-26T09:39:02.683918
**Type**: api_reference
**Quality**: comprehensive
