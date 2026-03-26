# API Documentation: drift_detection_healer

**Target Audience**: developers, api_users

# drift_detection_healer API Documentation

**File**: `drift_detection_healer.py`
**Classes**: 0
**Functions**: 1


## Functions

- **heal_guardian_drift_detection** -> HealCheckResult


## Function: heal_guardian_drift_detection

**Parameters**: check
**Returns**: HealCheckResult
**Description**: Heal guardian_drift_detection with dry-run or apply mode.

    Args:
        check: Full check dict from guardian aggregate.
        repo_root: Root of the repo/sandbox to mutate (required if apply=True).
        apply: If True, perform safe filesystem mutations inside repo_root.

    Dry-run mode (apply=False):
        Returns SKIPPED with planned actions in changes_made.

    Apply mode (apply=True):
        - Empty forbidden root folders: removed.
        - Non-empty forbidden root folders: NOT removed (PARTIAL).
        - Archived files at root: deleted.
        - Duplicate folders: NEVER touched (PARTIAL if present).
        Returns HEALED if all items resolved, PARTIAL if any remain.
    



## Usage Examples

### Function Usage

```python
# Using heal_guardian_drift_detection
result = heal_guardian_drift_detection(check)
```



---
**Generated**: 2026-03-26T09:39:03.796005
**Type**: api_reference
**Quality**: comprehensive
