# API Documentation: file_classification_healer

**Target Audience**: developers, api_users

# file_classification_healer API Documentation

**File**: `file_classification_healer.py`
**Classes**: 0
**Functions**: 1


## Functions

- **heal_file_classification** -> HealCheckResult


## Function: heal_file_classification

**Parameters**: check
**Returns**: HealCheckResult
**Description**: Heal file classification violations via FileClassificationAgent.heal_repository().

    Uses cached scan results from the check dict to avoid re-scanning.

    Args:
        check: Check dict from FileClassificationValidatorAgent.to_check_dict().
        repo_root: Absolute path to repository root (required for apply mode).
        apply: When False returns dry-run summary; when True performs healing.

    Returns:
        HealCheckResult with status HEALED / PARTIAL / SKIPPED / FAILED.
    



## Usage Examples

### Function Usage

```python
# Using heal_file_classification
result = heal_file_classification(check)
```



---
**Generated**: 2026-03-26T09:39:03.805177
**Type**: api_reference
**Quality**: comprehensive
