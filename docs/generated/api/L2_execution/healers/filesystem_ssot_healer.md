# API Documentation: filesystem_ssot_healer

**Target Audience**: developers, api_users

# filesystem_ssot_healer API Documentation

**File**: `filesystem_ssot_healer.py`
**Classes**: 0
**Functions**: 1


## Functions

- **heal_filesystem_ssot_drift** -> HealCheckResult


## Function: heal_filesystem_ssot_drift

**Parameters**: check
**Returns**: HealCheckResult
**Description**: Heal root-level SSOT drift by archiving forbidden root folders.

    Args:
        check: Check dict from FilesystemSSOTValidatorAgent.to_check_dict().
        repo_root: Absolute path to repository root (required for apply mode).
        apply: When False returns dry-run summary; when True archives folders.

    Returns:
        HealCheckResult with status HEALED / PARTIAL / SKIPPED / FAILED.
    



## Usage Examples

### Function Usage

```python
# Using heal_filesystem_ssot_drift
result = heal_filesystem_ssot_drift(check)
```



---
**Generated**: 2026-03-26T09:39:03.803603
**Type**: api_reference
**Quality**: comprehensive
