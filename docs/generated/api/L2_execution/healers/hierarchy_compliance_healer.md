# API Documentation: hierarchy_compliance_healer

**Target Audience**: developers, api_users

# hierarchy_compliance_healer API Documentation

**File**: `hierarchy_compliance_healer.py`
**Classes**: 0
**Functions**: 2


## Functions

- **heal_missing_structure** -> HealCheckResult
- **heal_subfolder_compliance** -> HealCheckResult


## Function: heal_missing_structure

**Parameters**: check
**Returns**: HealCheckResult
**Description**: Heal missing_structure violations (missing L2/L3 directories).

    Dry-run: SKIPPED with planned mkdir actions.
    Apply: Create missing directories.
    



## Function: heal_subfolder_compliance

**Parameters**: check
**Returns**: HealCheckResult
**Description**: Heal subfolder_compliance violations (non-approved subfolders).

    Non-approved subfolder remediation is risky (files need relocation,
    imports need updating). This healer reports planned actions but never
    removes or relocates folders automatically.

    Dry-run: SKIPPED with planned actions.
    Apply: SKIPPED (folder relocation requires human review).
    



## Usage Examples

### Function Usage

```python
# Using heal_missing_structure
result = heal_missing_structure(check)
```

```python
# Using heal_subfolder_compliance
result = heal_subfolder_compliance(check)
```



---
**Generated**: 2026-03-26T09:39:03.830652
**Type**: api_reference
**Quality**: comprehensive
