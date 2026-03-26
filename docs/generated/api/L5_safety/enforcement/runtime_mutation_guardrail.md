# API Documentation: runtime_mutation_guardrail

**Target Audience**: developers, api_users

# runtime_mutation_guardrail API Documentation

**File**: `runtime_mutation_guardrail.py`
**Classes**: 1
**Functions**: 4

## Classes

- **_GuardedSysModules** (inherits from dict)

## Functions

- **_guarded_reload** -> ModuleType
- **_guarded_setattr** -> None
- **install_guards** -> None
- **__setitem__** -> None


## Class: _GuardedSysModules

**Description**: REQ-417: wraps sys.modules to block replacement of already-loaded core modules.

    Allows:
      - Adding new module keys (initial import).
      - Replacing non-core-prefix keys.
    Blocks:
      - Replacing an EXISTING core-prefix key (e.g. monkey-patching a live module).
    

**Inherits from**: dict

### Methods

#### __setitem__
**Parameters**: self, key, value
**Returns**: None



## Function: _guarded_reload

**Parameters**: module
**Returns**: ModuleType
**Description**: REQ-417: block importlib.reload for core-layer modules.



## Function: _guarded_setattr

**Parameters**: obj, name, value
**Returns**: None
**Description**: REQ-417: reference guard for runtime attribute mutation on core instances.

    Not installed globally (would break too many stdlib primitives). Use as a
    test-double or call directly to validate core-object mutation semantics.
    



## Function: install_guards

**Returns**: None
**Description**: Install runtime mutation guards. Idempotent — safe to call at process start.



## Function: __setitem__

**Parameters**: self, key, value
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using _GuardedSysModules
_guardedsysmodules = _GuardedSysModules()
```

### Function Usage

```python
# Using _guarded_reload
result = _guarded_reload(module)
```

```python
# Using _guarded_setattr
result = _guarded_setattr(obj, name)
```

```python
# Using install_guards
result = install_guards()
```



---
**Generated**: 2026-03-26T09:39:04.918850
**Type**: api_reference
**Quality**: comprehensive
