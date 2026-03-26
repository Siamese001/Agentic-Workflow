# API Documentation: collision_resolver

**Target Audience**: developers, api_users

# collision_resolver API Documentation

**File**: `collision_resolver.py`
**Classes**: 1
**Functions**: 6

## Classes

- **CollisionResolver**

## Functions

- **__init__**
- **_get_target_name** -> str | None
- **find_collisions**
- **report**
- **interactive_resolve**
- **get_python_files**


## Class: CollisionResolver

### Methods

#### __init__
**Parameters**: self, root

#### _get_target_name
**Parameters**: self, path
**Returns**: str | None
**Description**: Determine what name this file SHOULD have based on AST analysis.

#### find_collisions
**Parameters**: self
**Description**: Find files that want the same target name within the same directory.

#### report
**Parameters**: self
**Description**: Generate a detailed collision report.

#### interactive_resolve
**Parameters**: self
**Description**: Interactive mode for resolving collisions one by one.



## Function: __init__

**Parameters**: self, root


## Function: _get_target_name

**Parameters**: self, path
**Returns**: str | None
**Description**: Determine what name this file SHOULD have based on AST analysis.



## Function: find_collisions

**Parameters**: self
**Description**: Find files that want the same target name within the same directory.



## Function: report

**Parameters**: self
**Description**: Generate a detailed collision report.



## Function: interactive_resolve

**Parameters**: self
**Description**: Interactive mode for resolving collisions one by one.



## Function: get_python_files

**Parameters**: root
**Description**: Fallback implementation when ssot_discovery_validator is unavailable.



## Usage Examples

### Class Usage

```python
# Using CollisionResolver
collisionresolver = CollisionResolver()
collisionresolver.find_collisions()
collisionresolver.report()
```

### Function Usage

```python
# Using __init__
result = __init__(root)
```

```python
# Using _get_target_name
result = _get_target_name(path)
```

```python
# Using find_collisions
result = find_collisions()
```



---
**Generated**: 2026-03-26T09:39:02.811762
**Type**: api_reference
**Quality**: comprehensive
