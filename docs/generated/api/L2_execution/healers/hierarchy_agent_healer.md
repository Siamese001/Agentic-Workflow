# API Documentation: hierarchy_agent_healer

**Target Audience**: developers, api_users

# hierarchy_agent_healer API Documentation

**File**: `hierarchy_agent_healer.py`
**Classes**: 0
**Functions**: 1


## Functions

- **heal_hierarchy_violations** -> HealCheckResult


## Function: heal_hierarchy_violations

**Parameters**: check
**Returns**: HealCheckResult
**Description**: Heal hierarchy violations via HierarchyAgent with healing_enabled=True.

    Args:
        check: Check dict from HierarchyValidatorAgent.to_check_dict().
        repo_root: Absolute path to repository root (required for apply mode).
        apply: When False returns dry-run summary; when True performs healing.

    Returns:
        HealCheckResult with status HEALED / PARTIAL / SKIPPED / FAILED.
    



## Usage Examples

### Function Usage

```python
# Using heal_hierarchy_violations
result = heal_hierarchy_violations(check)
```



---
**Generated**: 2026-03-26T09:39:03.827829
**Type**: api_reference
**Quality**: comprehensive
