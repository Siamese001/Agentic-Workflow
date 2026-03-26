# API Documentation: static_dispatch_registry

**Target Audience**: developers, api_users

# static_dispatch_registry API Documentation

**File**: `static_dispatch_registry.py`
**Classes**: 2
**Functions**: 11

## Classes

- **UnregisteredDispatchError** (inherits from LookupError)
- **StaticDispatchRegistry**

## Functions

- **get_guardian_registry** -> StaticDispatchRegistry
- **__init__** -> None
- **register** -> None
- **register_many** -> None
- **dispatch** -> ModuleType
- **dispatch_attr** -> Any
- **dispatch_callable** -> Callable[..., Any]
- **is_registered** -> bool
- **registered_keys** -> list[str]
- **__len__** -> int
- **__contains__** -> bool


## Class: UnregisteredDispatchError

**Description**: Raised when dispatch is requested for an unregistered symbol.

**Inherits from**: LookupError



## Class: StaticDispatchRegistry

**Description**: Controlled dispatch surface replacing dynamic __import__ usage.

    Example::

        registry = StaticDispatchRegistry()
        registry.register("guardian.hygiene", "agentic_core.L0_routing.scripts.run_guardian_hygiene")
        registry.register("guardian.c0", "agentic_core.L0_routing.scripts.run_guardian_c0_sovereignty")

        # Later — no __import__ needed:
        mod = registry.dispatch("guardian.hygiene")
        mod.main()

    The registry is fail-closed: dispatching an unregistered key raises
    ``UnregisteredDispatchError`` rather than falling through to dynamic import.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### register
**Parameters**: self, key, module_path
**Returns**: None
**Description**: Register *module_path* under *key*.

        Args:
            key: Logical dispatch key (e.g. ``"guardian.hygiene"``).
            module_path: Fully-qualified Python module path (e.g.
                ``"agentic_core.L0_routing.scripts.run_guardian_hygiene"``).
        

#### register_many
**Parameters**: self, mapping
**Returns**: None
**Description**: Register multiple ``{key: module_path}`` pairs at once.

#### dispatch
**Parameters**: self, key
**Returns**: ModuleType
**Description**: Return the module registered under *key*.

        Lazily imports the module on first call; returns the cached module
        on subsequent calls.

        Raises:
            UnregisteredDispatchError: if *key* has not been registered.
            ImportError: if the registered module cannot be imported.
        

#### dispatch_attr
**Parameters**: self, key, attr
**Returns**: Any
**Description**: Return *attr* from the module registered under *key*.

        Raises:
            UnregisteredDispatchError: if *key* not registered.
            AttributeError: if *attr* not found on the module.
        

#### dispatch_callable
**Parameters**: self, key, attr
**Returns**: Callable[..., Any]
**Description**: Return a callable *attr* from the module registered under *key*.

        Raises:
            TypeError: if the resolved attribute is not callable.
        

#### is_registered
**Parameters**: self, key
**Returns**: bool
**Description**: Return True if *key* has been registered.

#### registered_keys
**Parameters**: self
**Returns**: list[str]
**Description**: Return sorted list of all registered keys.

#### __len__
**Parameters**: self
**Returns**: int

#### __contains__
**Parameters**: self, key
**Returns**: bool



## Function: get_guardian_registry

**Returns**: StaticDispatchRegistry
**Description**: Return the singleton guardian registry, creating and pre-populating it on first call.



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: register

**Parameters**: self, key, module_path
**Returns**: None
**Description**: Register *module_path* under *key*.

        Args:
            key: Logical dispatch key (e.g. ``"guardian.hygiene"``).
            module_path: Fully-qualified Python module path (e.g.
                ``"agentic_core.L0_routing.scripts.run_guardian_hygiene"``).
        



## Function: register_many

**Parameters**: self, mapping
**Returns**: None
**Description**: Register multiple ``{key: module_path}`` pairs at once.



## Function: dispatch

**Parameters**: self, key
**Returns**: ModuleType
**Description**: Return the module registered under *key*.

        Lazily imports the module on first call; returns the cached module
        on subsequent calls.

        Raises:
            UnregisteredDispatchError: if *key* has not been registered.
            ImportError: if the registered module cannot be imported.
        



## Function: dispatch_attr

**Parameters**: self, key, attr
**Returns**: Any
**Description**: Return *attr* from the module registered under *key*.

        Raises:
            UnregisteredDispatchError: if *key* not registered.
            AttributeError: if *attr* not found on the module.
        



## Function: dispatch_callable

**Parameters**: self, key, attr
**Returns**: Callable[..., Any]
**Description**: Return a callable *attr* from the module registered under *key*.

        Raises:
            TypeError: if the resolved attribute is not callable.
        



## Function: is_registered

**Parameters**: self, key
**Returns**: bool
**Description**: Return True if *key* has been registered.



## Function: registered_keys

**Parameters**: self
**Returns**: list[str]
**Description**: Return sorted list of all registered keys.



## Function: __len__

**Parameters**: self
**Returns**: int


## Function: __contains__

**Parameters**: self, key
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using UnregisteredDispatchError
unregistereddispatcherror = UnregisteredDispatchError()
```

```python
# Using StaticDispatchRegistry
staticdispatchregistry = StaticDispatchRegistry()
staticdispatchregistry.register()
staticdispatchregistry.register_many()
```

### Function Usage

```python
# Using get_guardian_registry
result = get_guardian_registry()
```

```python
# Using __init__
result = __init__()
```

```python
# Using register
result = register(key, module_path)
```



---
**Generated**: 2026-03-26T09:39:03.738147
**Type**: api_reference
**Quality**: comprehensive
