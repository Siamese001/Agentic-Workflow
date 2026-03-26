# API Documentation: gravity_leak_healer

**Target Audience**: developers, api_users

# gravity_leak_healer API Documentation

**File**: `gravity_leak_healer.py`
**Classes**: 0
**Functions**: 1


## Functions

- **heal_gravity_violations** -> HealCheckResult


## Function: heal_gravity_violations

**Parameters**: check
**Returns**: HealCheckResult
**Description**: Heal layer gravity violations via GravityLeakRepairAgent.heal_violations().

    Consumes pre-computed violations from the check dict (produced by
    GravityValidatorAgent.to_check_dict()), so no duplicate scan occurs.

    Args:
        check: Check dict from GravityValidatorAgent.to_check_dict().
        repo_root: Absolute path to repository root (required for apply mode).
        apply: When False returns dry-run summary; when True performs healing.

    Returns:
        HealCheckResult with status HEALED / PARTIAL / SKIPPED / FAILED.
    



## Usage Examples

### Function Usage

```python
# Using heal_gravity_violations
result = heal_gravity_violations(check)
```



---
**Generated**: 2026-03-26T09:39:03.807756
**Type**: api_reference
**Quality**: comprehensive
