# API Documentation: run_guardian_c0_sovereignty

**Target Audience**: developers, api_users

# run_guardian_c0_sovereignty API Documentation

**File**: `run_guardian_c0_sovereignty.py`
**Classes**: 0
**Functions**: 5


## Functions

- **_collect_files** -> list[Path]
- **_node_contains_embedding_attr** -> bool
- **scan_embedding_control_flow** -> dict[str, list[dict]]
- **run_c0_sovereignty_guardian** -> GuardianResult
- **_main** -> int


## Function: _collect_files

**Parameters**: repo_root
**Returns**: list[Path]


## Function: _node_contains_embedding_attr

**Parameters**: node
**Returns**: bool
**Description**: Return True if the expression subtree references an embedding attribute.



## Function: scan_embedding_control_flow

**Parameters**: repo_root, files
**Returns**: dict[str, list[dict]]
**Description**: 
    Detect embedding results used in control-flow (routing/tier) or threshold assignment.

    Returns dict keyed by check_id → sorted violation list.
    



## Function: run_c0_sovereignty_guardian

**Parameters**: repo_root, write_artifacts_dir, timestamp, correlation_id
**Returns**: GuardianResult


## Function: _main

**Parameters**: argv
**Returns**: int


## Usage Examples

### Function Usage

```python
# Using _collect_files
result = _collect_files(repo_root)
```

```python
# Using _node_contains_embedding_attr
result = _node_contains_embedding_attr(node)
```

```python
# Using scan_embedding_control_flow
result = scan_embedding_control_flow(repo_root, files)
```



---
**Generated**: 2026-03-26T09:39:03.202121
**Type**: api_reference
**Quality**: comprehensive
