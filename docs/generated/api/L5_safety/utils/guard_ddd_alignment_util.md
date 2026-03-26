# API Documentation: guard_ddd_alignment_util

**Target Audience**: developers, api_users

# guard_ddd_alignment_util API Documentation

**File**: `guard_ddd_alignment_util.py`
**Classes**: 0
**Functions**: 2


## Functions

- **get_ddd_violations_detailed** -> list[dict]
- **validate_ddd_alignment** -> tuple[float, list[str]]


## Function: get_ddd_violations_detailed

**Parameters**: root_path
**Returns**: list[dict]
**Description**: 
    [NEW] Detailed DDD Violation detector — structured output for L0 healing/forensics.

    Returns:
        List of dicts with keys: file, line, type, description, Severity
    



## Function: validate_ddd_alignment

**Parameters**: root_path
**Returns**: tuple[float, list[str]]
**Description**: 
    Existing Auditor-compatible validator — simple score + string issues.
    Used directly by Sovereign Auditor v3.1.
    



## Usage Examples

### Function Usage

```python
# Using get_ddd_violations_detailed
result = get_ddd_violations_detailed(root_path)
```

```python
# Using validate_ddd_alignment
result = validate_ddd_alignment(root_path)
```



---
**Generated**: 2026-03-26T09:39:05.658802
**Type**: api_reference
**Quality**: comprehensive
