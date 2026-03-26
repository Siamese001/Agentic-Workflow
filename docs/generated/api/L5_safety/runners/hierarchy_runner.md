# API Documentation: hierarchy_runner

**Target Audience**: developers, api_users

# hierarchy_runner API Documentation

**File**: `hierarchy_runner.py`
**Classes**: 0
**Functions**: 5


## Functions

- **get_project_root** -> Path
- **run_hierarchy_dry_run** -> dict
- **run_heal_violations** -> dict
- **verify_mro** -> dict
- **main** -> int


## Function: get_project_root

**Returns**: Path
**Description**: Get project root from this file's location.



## Function: run_hierarchy_dry_run

**Parameters**: project_root
**Returns**: dict
**Description**: Run HierarchyAgent in dry-run mode.



## Function: run_heal_violations

**Parameters**: project_root
**Returns**: dict
**Description**: Run HierarchyAgent to heal violations in dry-run mode.



## Function: verify_mro

**Returns**: dict
**Description**: Verify HierarchyAgent MRO structure.



## Function: main

**Returns**: int
**Description**: CLI entry point for subprocess invocation.



## Usage Examples

### Function Usage

```python
# Using get_project_root
result = get_project_root()
```

```python
# Using run_hierarchy_dry_run
result = run_hierarchy_dry_run(project_root)
```

```python
# Using run_heal_violations
result = run_heal_violations(project_root)
```



---
**Generated**: 2026-03-26T09:39:05.460423
**Type**: api_reference
**Quality**: comprehensive
