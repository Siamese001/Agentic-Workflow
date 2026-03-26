# API Documentation: architecture_governor_healer

**Target Audience**: developers, api_users

# architecture_governor_healer API Documentation

**File**: `architecture_governor_healer.py`
**Classes**: 0
**Functions**: 1


## Functions

- **heal_architecture_governance** -> HealCheckResult


## Function: heal_architecture_governance

**Parameters**: check
**Returns**: HealCheckResult
**Description**: Heal architectural governance violations via ArchitectureGovernorAgent.

    Args:
        check: Check dict from ArchitectureGovernorValidatorAgent.to_check_dict().
        repo_root: Absolute path to repository root (required for apply mode).
        apply: When False returns dry-run summary; when True performs healing.

    Returns:
        HealCheckResult with status HEALED / PARTIAL / SKIPPED / FAILED.
    



## Usage Examples

### Function Usage

```python
# Using heal_architecture_governance
result = heal_architecture_governance(check)
```



---
**Generated**: 2026-03-26T09:39:03.788085
**Type**: api_reference
**Quality**: comprehensive
