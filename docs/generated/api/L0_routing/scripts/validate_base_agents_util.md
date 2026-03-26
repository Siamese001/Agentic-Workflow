# API Documentation: validate_base_agents_util

**Target Audience**: developers, api_users

# validate_base_agents_util API Documentation

**File**: `validate_base_agents_util.py`
**Classes**: 0
**Functions**: 4


## Functions

- **find_base_agents** -> dict[str, list[dict]]
- **validate_base_agents** -> tuple[bool, list[str]]
- **suggest_fixes** -> list[str]
- **main**


## Function: find_base_agents

**Returns**: dict[str, list[dict]]
**Description**: Find all base agents grouped by layer.



## Function: validate_base_agents

**Returns**: tuple[bool, list[str]]
**Description**: Validate base agent uniqueness per layer.



## Function: suggest_fixes

**Returns**: list[str]
**Description**: Suggest fixes for base agent violations.



## Function: main

**Description**: Main entry point.



## Usage Examples

### Function Usage

```python
# Using find_base_agents
result = find_base_agents()
```

```python
# Using validate_base_agents
result = validate_base_agents()
```

```python
# Using suggest_fixes
result = suggest_fixes()
```



---
**Generated**: 2026-03-26T09:39:03.281805
**Type**: api_reference
**Quality**: comprehensive
