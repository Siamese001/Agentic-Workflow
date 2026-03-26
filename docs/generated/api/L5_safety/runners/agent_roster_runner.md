# API Documentation: agent_roster_runner

**Target Audience**: developers, api_users

# agent_roster_runner API Documentation

**File**: `agent_roster_runner.py`
**Classes**: 0
**Functions**: 4


## Functions

- **get_project_root** -> Path
- **_get_ObservabilityProbeExecutorAgent**
- **validate_agent_roster** -> dict
- **main** -> int


## Function: get_project_root

**Returns**: Path
**Description**: Get project root from this file's location.



## Function: _get_ObservabilityProbeExecutorAgent

**Description**: Lazy loader for ObservabilityProbeExecutorAgent (upward L5->L6 seam).



## Function: validate_agent_roster

**Returns**: dict
**Description**: Validate mandatory agent roster integrity.



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
# Using _get_ObservabilityProbeExecutorAgent
result = _get_ObservabilityProbeExecutorAgent()
```

```python
# Using validate_agent_roster
result = validate_agent_roster()
```



---
**Generated**: 2026-03-26T09:39:05.452806
**Type**: api_reference
**Quality**: comprehensive
