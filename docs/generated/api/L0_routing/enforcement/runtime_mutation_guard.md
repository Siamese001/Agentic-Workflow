# API Documentation: runtime_mutation_guard

**Target Audience**: developers, api_users

# runtime_mutation_guard API Documentation

**File**: `runtime_mutation_guard.py`
**Classes**: 4
**Functions**: 14

## Classes

- **RuntimeMutationViolation** (inherits from Exception)
- **RuntimeMutationGuard**
- **TestUnprotected**
- **TestProtected**

## Functions

- **is_protected_module** -> bool
- **is_protected_object** -> bool
- **guard_setattr** -> None
- **guard_importlib_reload** -> types.ModuleType
- **guard_metaclass_creation** -> type
- **guard_function_replacement** -> None
- **get_mutation_guard** -> RuntimeMutationGuard
- **install_runtime_mutation_guard** -> None
- **uninstall_runtime_mutation_guard** -> None
- **test_runtime_mutation_guard** -> bool
- **__init__**
- **install** -> None
- **uninstall** -> None
- **is_installed** -> bool


## Class: RuntimeMutationViolation

**Description**: Raised when dynamic runtime mutation is attempted.

**Inherits from**: Exception



## Class: RuntimeMutationGuard

**Description**: Guards against dynamic runtime mutations in core layers.

### Methods

#### __init__
**Parameters**: self

#### install
**Parameters**: self
**Returns**: None
**Description**: Install the runtime mutation guard (REQ-417).

#### uninstall
**Parameters**: self
**Returns**: None
**Description**: Uninstall the runtime mutation guard.

#### is_installed
**Parameters**: self
**Returns**: bool
**Description**: Check if guard is installed.

        Returns:
            True if installed, False otherwise
        



## Class: TestUnprotected



## Class: TestProtected



## Function: is_protected_module

**Parameters**: module_name
**Returns**: bool
**Description**: Check if a module is protected from mutation (REQ-417).

    Args:
        module_name: Name of the module to check

    Returns:
        True if module is protected, False otherwise
    



## Function: is_protected_object

**Parameters**: obj
**Returns**: bool
**Description**: Check if an object belongs to a protected core layer.

    Args:
        obj: Object to check

    Returns:
        True if object is protected, False otherwise
    



## Function: guard_setattr

**Parameters**: obj, name, value
**Returns**: None
**Description**: Guard setattr to prevent mutation of protected objects (REQ-417).

    Args:
        obj: Object to modify
        name: Attribute name
        value: New value

    Raises:
        RuntimeMutationViolation: If attempting to modify protected object
    



## Function: guard_importlib_reload

**Parameters**: module
**Returns**: types.ModuleType
**Description**: Guard importlib.reload to prevent reloading protected modules (REQ-417).

    Args:
        module: Module to reload

    Returns:
        The reloaded module

    Raises:
        RuntimeMutationViolation: If attempting to reload protected module
    



## Function: guard_metaclass_creation

**Parameters**: name, bases, namespace
**Returns**: type
**Description**: Guard metaclass creation to prevent permission alteration (REQ-417).

    Args:
        name: Class name
        bases: Base classes
        namespace: Class namespace

    Returns:
        Created class

    Raises:
        RuntimeMutationViolation: If metaclass alters protected permissions
    



## Function: guard_function_replacement

**Parameters**: func, new_func
**Returns**: None
**Description**: Guard against replacing functions in protected modules.

    Args:
        func: Original function
        new_func: Replacement function

    Raises:
        RuntimeMutationViolation: If attempting to replace protected function
    



## Function: get_mutation_guard

**Returns**: RuntimeMutationGuard
**Description**: Get the global mutation guard instance.



## Function: install_runtime_mutation_guard

**Returns**: None
**Description**: Install the runtime mutation guard (REQ-417).



## Function: uninstall_runtime_mutation_guard

**Returns**: None
**Description**: Uninstall the runtime mutation guard.



## Function: test_runtime_mutation_guard

**Returns**: bool
**Description**: Test that runtime mutation prohibition is working.

    Returns:
        True if guard is working, False otherwise
    



## Function: __init__

**Parameters**: self


## Function: install

**Parameters**: self
**Returns**: None
**Description**: Install the runtime mutation guard (REQ-417).



## Function: uninstall

**Parameters**: self
**Returns**: None
**Description**: Uninstall the runtime mutation guard.



## Function: is_installed

**Parameters**: self
**Returns**: bool
**Description**: Check if guard is installed.

        Returns:
            True if installed, False otherwise
        



## Usage Examples

### Class Usage

```python
# Using RuntimeMutationViolation
runtimemutationviolation = RuntimeMutationViolation()
```

```python
# Using RuntimeMutationGuard
runtimemutationguard = RuntimeMutationGuard()
runtimemutationguard.install()
runtimemutationguard.uninstall()
```

```python
# Using TestUnprotected
testunprotected = TestUnprotected()
```

### Function Usage

```python
# Using is_protected_module
result = is_protected_module(module_name)
```

```python
# Using is_protected_object
result = is_protected_object(obj)
```

```python
# Using guard_setattr
result = guard_setattr(obj, name)
```



---
**Generated**: 2026-03-26T09:39:02.636003
**Type**: api_reference
**Quality**: comprehensive
