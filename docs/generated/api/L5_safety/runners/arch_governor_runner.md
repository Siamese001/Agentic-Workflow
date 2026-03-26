# API Documentation: arch_governor_runner

**Target Audience**: developers, api_users

# arch_governor_runner API Documentation

**File**: `arch_governor_runner.py`
**Classes**: 0
**Functions**: 5


## Functions

- **get_project_root** -> Path
- **run_ci_verification** -> dict
- **capture_golden_baseline** -> dict
- **run_audit** -> dict
- **main** -> int


## Function: get_project_root

**Returns**: Path
**Description**: Get project root from this file's location.



## Function: run_ci_verification

**Parameters**: project_root, auto_approve
**Returns**: dict
**Description**: Run CI verification and return results as dict.



## Function: capture_golden_baseline

**Parameters**: project_root
**Returns**: dict
**Description**: Capture golden baseline and return manifest path.



## Function: run_audit

**Parameters**: project_root, targets
**Returns**: dict
**Description**: Run audit with optional target territories.



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
# Using run_ci_verification
result = run_ci_verification(project_root, auto_approve)
```

```python
# Using capture_golden_baseline
result = capture_golden_baseline(project_root)
```



---
**Generated**: 2026-03-26T09:39:05.455316
**Type**: api_reference
**Quality**: comprehensive
