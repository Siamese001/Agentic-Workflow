# API Documentation: classification_compliance_healer

**Target Audience**: developers, api_users

# classification_compliance_healer API Documentation

**File**: `classification_compliance_healer.py`
**Classes**: 0
**Functions**: 2


## Functions

- **heal_naming_compliance** -> HealCheckResult
- **heal_territory_compliance** -> HealCheckResult


## Function: heal_naming_compliance

**Parameters**: check
**Returns**: HealCheckResult
**Description**: Heal naming_compliance violations (compound suffix conflicts).

    Naming violations require human review — automated renames risk breaking
    imports across the codebase. This healer always reports planned actions
    but never applies renames automatically.

    Dry-run: SKIPPED with planned actions.
    Apply: SKIPPED (renames require human review).
    



## Function: heal_territory_compliance

**Parameters**: check
**Returns**: HealCheckResult
**Description**: Heal territory_compliance violations (misplaced files).

    Dry-run: SKIPPED with planned move actions.
    Apply: Move files to their canonical folder per FILETYPE_TO_FOLDER mapping.
    



## Usage Examples

### Function Usage

```python
# Using heal_naming_compliance
result = heal_naming_compliance(check)
```

```python
# Using heal_territory_compliance
result = heal_territory_compliance(check)
```



---
**Generated**: 2026-03-26T09:39:03.794474
**Type**: api_reference
**Quality**: comprehensive
