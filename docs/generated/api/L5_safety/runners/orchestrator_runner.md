# API Documentation: orchestrator_runner

**Target Audience**: developers, api_users

# orchestrator_runner API Documentation

**File**: `orchestrator_runner.py`
**Classes**: 0
**Functions**: 3


## Functions

- **get_project_root** -> Path
- **run_orchestrator_mission** -> dict
- **main** -> int


## Function: get_project_root

**Returns**: Path
**Description**: Get project root from this file's location.



## Function: run_orchestrator_mission

**Parameters**: project_root, targets, execute
**Returns**: dict
**Description**: Run orchestrator mission with agent roster.



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
# Using run_orchestrator_mission
result = run_orchestrator_mission(project_root, targets)
```

```python
# Using main
result = main()
```



---
**Generated**: 2026-03-26T09:39:05.461990
**Type**: api_reference
**Quality**: comprehensive
