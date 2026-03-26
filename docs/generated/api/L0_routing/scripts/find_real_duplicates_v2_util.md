# API Documentation: find_real_duplicates_v2_util

**Target Audience**: developers, api_users

# find_real_duplicates_v2_util API Documentation

**File**: `find_real_duplicates_v2_util.py`
**Classes**: 0
**Functions**: 4


## Functions

- **is_agent_file** -> bool
- **get_priority** -> int
- **infer_rationale** -> str
- **main**


## Function: is_agent_file

**Parameters**: path
**Returns**: bool
**Description**: Check if path is an actual agent file (not test).

    [REFACTORED 2026-02-08] Aligned with classification kernel naming rules.
    For full AST-based classification, use:
        from agentic_core.L5_safety.core_kernel.classification_kernel import is_agent_file
    



## Function: get_priority

**Parameters**: path, project_root
**Returns**: int
**Description**: Get location priority (lower = better/canonical).



## Function: infer_rationale

**Parameters**: canonical, duplicate, project_root
**Returns**: str
**Description**: Infer rationale based on path patterns.



## Function: main



## Usage Examples

### Function Usage

```python
# Using is_agent_file
result = is_agent_file(path)
```

```python
# Using get_priority
result = get_priority(path, project_root)
```

```python
# Using infer_rationale
result = infer_rationale(canonical, duplicate)
```



---
**Generated**: 2026-03-26T09:39:03.131032
**Type**: api_reference
**Quality**: comprehensive
