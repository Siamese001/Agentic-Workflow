# API Documentation: import_guard

**Target Audience**: developers, api_users

# import_guard API Documentation

**File**: `import_guard.py`
**Classes**: 2
**Functions**: 6

## Classes

- **DynamicImportDeniedError** (inherits from Exception)
- **ImportGuard**

## Functions

- **get_import_guard** -> ImportGuard
- **set_import_guard_mode** -> None
- **__init__** -> None
- **check** -> dict[str, Any]
- **get_import_log** -> list[dict[str, Any]]
- **clear_log** -> None


## Class: DynamicImportDeniedError

**Description**: Raised when a dynamic import is denied by guardrail.

**Inherits from**: Exception



## Class: ImportGuard

**Description**: 
    Guardrail for dynamic import operations.

    Enforces allowlist/denylist policy and logging before
    allowing importlib or __import__ operations.
    

### Methods

#### __init__
**Parameters**: self, mode
**Returns**: None
**Description**: 
        Initialize ImportGuard.

        Args:
            mode: "warn" (log violations) or "enforce" (block violations)
        

#### check
**Parameters**: self, operation, module_name, metadata
**Returns**: dict[str, Any]
**Description**: 
        Pre-import guardrail check for dynamic import operations.

        Args:
            operation: Operation being performed ("import_module", "__import__", etc.)
            module_name: Module being imported (if available)
            metadata: Additional context

        Returns:
            dict with verdict and details

        Raises:
            DynamicImportDeniedError: If import is denied in enforce mode
        

#### get_import_log
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get full import log.

#### clear_log
**Parameters**: self
**Returns**: None
**Description**: Clear import log.



## Function: get_import_guard

**Returns**: ImportGuard
**Description**: Get global ImportGuard instance.



## Function: set_import_guard_mode

**Parameters**: mode
**Returns**: None
**Description**: Set global ImportGuard mode ("warn" or "enforce").



## Function: __init__

**Parameters**: self, mode
**Returns**: None
**Description**: 
        Initialize ImportGuard.

        Args:
            mode: "warn" (log violations) or "enforce" (block violations)
        



## Function: check

**Parameters**: self, operation, module_name, metadata
**Returns**: dict[str, Any]
**Description**: 
        Pre-import guardrail check for dynamic import operations.

        Args:
            operation: Operation being performed ("import_module", "__import__", etc.)
            module_name: Module being imported (if available)
            metadata: Additional context

        Returns:
            dict with verdict and details

        Raises:
            DynamicImportDeniedError: If import is denied in enforce mode
        



## Function: get_import_log

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get full import log.



## Function: clear_log

**Parameters**: self
**Returns**: None
**Description**: Clear import log.



## Usage Examples

### Class Usage

```python
# Using DynamicImportDeniedError
dynamicimportdeniederror = DynamicImportDeniedError()
```

```python
# Using ImportGuard
importguard = ImportGuard()
importguard.check()
importguard.get_import_log()
```

### Function Usage

```python
# Using get_import_guard
result = get_import_guard()
```

```python
# Using set_import_guard_mode
result = set_import_guard_mode(mode)
```

```python
# Using __init__
result = __init__(mode)
```



---
**Generated**: 2026-03-26T09:39:04.855340
**Type**: api_reference
**Quality**: comprehensive
