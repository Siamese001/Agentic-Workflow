# API Documentation: _ssot_meta_learning

**Target Audience**: developers, api_users

# _ssot_meta_learning API Documentation

**File**: `_ssot_meta_learning.py`
**Classes**: 0
**Functions**: 1


## Functions

- **_fire_meta_learning_intake** -> None


## Function: _fire_meta_learning_intake

**Parameters**: state_mgr, now_utc, repo_root
**Returns**: None
**Description**: Wire HealingOutcomeIntakeAdapter and MetaLearningPipeline after each run.

    Both imports are guarded — if archived modules are not yet restored (pre-Wave 0B)
    this is a safe no-op. After Wave 0B restoration the full pipeline activates.
    



## Usage Examples

### Function Usage

```python
# Using _fire_meta_learning_intake
result = _fire_meta_learning_intake(state_mgr, now_utc)
```



---
**Generated**: 2026-03-26T09:39:03.321144
**Type**: api_reference
**Quality**: comprehensive
