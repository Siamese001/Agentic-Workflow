# API Documentation: preventative_sandbox

**Target Audience**: developers, api_users

# preventative_sandbox API Documentation

**File**: `preventative_sandbox.py`
**Classes**: 3
**Functions**: 10

## Classes

- **SandboxViolationError** (inherits from RuntimeError)
- **_PatchTarget**
- **PreventativeSandbox**

## Functions

- **_resolve_module** -> Any
- **__init__** -> None
- **register_target** -> None
- **is_active** -> bool
- **_all_targets** -> list[_PatchTarget]
- **_make_guard** -> Callable[..., Any]
- **_patch_all** -> None
- **_restore_all** -> None
- **activated**
- **_guard** -> Any


## Class: SandboxViolationError

**Description**: Raised when a write-capable function is called in sandbox.

**Inherits from**: RuntimeError

### Methods

#### __init__
**Parameters**: self, function_name
**Returns**: None



## Class: _PatchTarget

**Description**: Describes one function to patch.



## Class: PreventativeSandbox

**Description**: Scoped sandbox that blocks write-capable functions.

    Usage::

        sandbox = PreventativeSandbox()
        with sandbox.activated():
            # all write vectors raise SandboxViolationError
            ...
        # originals restored

    Must live in L2 — not in agent constructors, L6, or global.
    

### Methods

#### register_target
**Parameters**: self, module_path, attr_name, category
**Returns**: None
**Description**: Register an additional write vector to patch.

#### is_active
**Parameters**: self
**Returns**: bool

#### _all_targets
**Parameters**: self
**Returns**: list[_PatchTarget]

#### _make_guard
**Parameters**: self, target
**Returns**: Callable[..., Any]
**Description**: Create a guard function that raises on call.

#### _patch_all
**Parameters**: self
**Returns**: None
**Description**: Replace all write vectors with guards.

#### _restore_all
**Parameters**: self
**Returns**: None
**Description**: Restore all original functions.

#### activated
**Parameters**: self
**Description**: Context manager for scoped sandbox activation.

        Guarantees restoration even on exception.
        



## Function: _resolve_module

**Parameters**: module_path
**Returns**: Any
**Description**: Import and return the module object.



## Function: __init__

**Parameters**: self, function_name
**Returns**: None


## Function: register_target

**Parameters**: self, module_path, attr_name, category
**Returns**: None
**Description**: Register an additional write vector to patch.



## Function: is_active

**Parameters**: self
**Returns**: bool


## Function: _all_targets

**Parameters**: self
**Returns**: list[_PatchTarget]


## Function: _make_guard

**Parameters**: self, target
**Returns**: Callable[..., Any]
**Description**: Create a guard function that raises on call.



## Function: _patch_all

**Parameters**: self
**Returns**: None
**Description**: Replace all write vectors with guards.



## Function: _restore_all

**Parameters**: self
**Returns**: None
**Description**: Restore all original functions.



## Function: activated

**Parameters**: self
**Description**: Context manager for scoped sandbox activation.

        Guarantees restoration even on exception.
        



## Function: _guard

**Returns**: Any


## Usage Examples

### Class Usage

```python
# Using SandboxViolationError
sandboxviolationerror = SandboxViolationError()
```

```python
# Using _PatchTarget
_patchtarget = _PatchTarget()
```

```python
# Using PreventativeSandbox
preventativesandbox = PreventativeSandbox()
preventativesandbox.register_target()
preventativesandbox.is_active()
```

### Function Usage

```python
# Using _resolve_module
result = _resolve_module(module_path)
```

```python
# Using __init__
result = __init__(function_name)
```

```python
# Using register_target
result = register_target(module_path, attr_name)
```



---
**Generated**: 2026-03-26T09:39:03.718560
**Type**: api_reference
**Quality**: comprehensive
