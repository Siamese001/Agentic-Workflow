# API Documentation: extract_agent_duplicates_util

**Target Audience**: developers, api_users

# extract_agent_duplicates_util API Documentation

**File**: `extract_agent_duplicates_util.py`
**Classes**: 0
**Functions**: 2


## Functions

- **is_agent_file** -> bool
- **infer_rationale** -> str


## Function: is_agent_file

**Parameters**: path
**Returns**: bool
**Description**: Check if path is an actual agent file (not test).

    [REFACTORED 2026-02-08] Aligned with classification kernel naming rules.
    For full AST-based classification, use:
        from agentic_core.L5_safety.core_kernel.classification_kernel import is_agent_file
    



## Function: infer_rationale

**Parameters**: canonical, dup_path, action
**Returns**: str
**Description**: Infer rationale based on path patterns.



## Usage Examples

### Function Usage

```python
# Using is_agent_file
result = is_agent_file(path)
```

```python
# Using infer_rationale
result = infer_rationale(canonical, dup_path)
```



---
**Generated**: 2026-03-26T09:39:03.095256
**Type**: api_reference
**Quality**: comprehensive
