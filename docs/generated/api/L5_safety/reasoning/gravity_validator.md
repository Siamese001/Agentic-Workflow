# API Documentation: gravity_validator

**Target Audience**: developers, api_users

# gravity_validator API Documentation

**File**: `gravity_validator.py`
**Classes**: 1
**Functions**: 10

## Classes

- **GravityValidatorAgent**

## Functions

- **_get_apps_roots** -> frozenset[str]
- **__init__** -> None
- **scan** -> list[Any]
- **to_check_dict** -> dict[str, Any]
- **run** -> dict[str, Any]
- **_in_sovereign_scope** -> bool
- **_not_excluded** -> bool
- **_has_known_layers** -> bool
- **_parse_cached** -> _ast.Module | None
- **_is_module_level_import** -> bool


## Class: GravityValidatorAgent

**Description**: L5 Certify-only validator for layer gravity violations.

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None

#### scan
**Parameters**: self
**Returns**: list[Any]
**Description**: Run StructuralValidatorAgent and return filtered gravity violations.

        Returns:
            List of violation objects in the sovereign scope.
        

#### to_check_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return structured check dict for _invoke_healer dispatch.

#### run
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Alias for to_check_dict for orchestrator compatibility.



## Function: _get_apps_roots

**Returns**: frozenset[str]
**Description**: Derive apps_* roots from PROJECT_ROOT_WHITELIST — zero hardcoded folder names.



## Function: __init__

**Parameters**: self, project_root
**Returns**: None


## Function: scan

**Parameters**: self
**Returns**: list[Any]
**Description**: Run StructuralValidatorAgent and return filtered gravity violations.

        Returns:
            List of violation objects in the sovereign scope.
        



## Function: to_check_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return structured check dict for _invoke_healer dispatch.



## Function: run

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Alias for to_check_dict for orchestrator compatibility.



## Function: _in_sovereign_scope

**Parameters**: v
**Returns**: bool


## Function: _not_excluded

**Parameters**: v
**Returns**: bool


## Function: _has_known_layers

**Parameters**: v
**Returns**: bool
**Description**: Exclude violations where both layers are unknown — unactionable noise.



## Function: _parse_cached

**Parameters**: fp_str
**Returns**: _ast.Module | None


## Function: _is_module_level_import

**Parameters**: v
**Returns**: bool
**Description**: Return True only if the violation's import is at module scope (not inside a function/class).



## Usage Examples

### Class Usage

```python
# Using GravityValidatorAgent
gravityvalidatoragent = GravityValidatorAgent()
gravityvalidatoragent.scan()
gravityvalidatoragent.to_check_dict()
```

### Function Usage

```python
# Using _get_apps_roots
result = _get_apps_roots()
```

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using scan
result = scan()
```



---
**Generated**: 2026-03-26T09:39:05.246080
**Type**: api_reference
**Quality**: comprehensive
