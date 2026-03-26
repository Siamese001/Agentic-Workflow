# API Documentation: fix_inherited_invocation_util

**Target Audience**: developers, api_users

# fix_inherited_invocation_util API Documentation

**File**: `fix_inherited_invocation_util.py`
**Classes**: 0
**Functions**: 5


## Functions

- **load_inherited_agents** -> list[dict]
- **find_class_end** -> tuple[int, int]
- **has_heal_repository** -> bool
- **add_heal_repository** -> bool
- **main**


## Function: load_inherited_agents

**Returns**: list[dict]
**Description**: Load agents with invocation='Inherited' status.



## Function: find_class_end

**Parameters**: source, class_name
**Returns**: tuple[int, int]
**Description**: Find the end of a class definition to insert method before it.



## Function: has_heal_repository

**Parameters**: source, class_name
**Returns**: bool
**Description**: Check if class already has heal_repository method.



## Function: add_heal_repository

**Parameters**: file_path, class_name
**Returns**: bool
**Description**: Add heal_repository method to a class.



## Function: main



## Usage Examples

### Function Usage

```python
# Using load_inherited_agents
result = load_inherited_agents()
```

```python
# Using find_class_end
result = find_class_end(source, class_name)
```

```python
# Using has_heal_repository
result = has_heal_repository(source, class_name)
```



---
**Generated**: 2026-03-26T09:39:05.644209
**Type**: api_reference
**Quality**: comprehensive
