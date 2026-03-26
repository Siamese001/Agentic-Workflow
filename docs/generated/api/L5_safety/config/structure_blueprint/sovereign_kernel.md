# API Documentation: sovereign_kernel

**Target Audience**: developers, api_users

# sovereign_kernel API Documentation

**File**: `sovereign_kernel.py`
**Classes**: 0
**Functions**: 3


## Functions

- **is_kernel_component** -> bool
- **is_modular_extension** -> bool
- **validate_boundary** -> tuple[bool, str]


## Function: is_kernel_component

**Parameters**: module_path
**Returns**: bool
**Description**: Check if a given module path is part of the sovereign kernel.



## Function: is_modular_extension

**Parameters**: module_path
**Returns**: bool
**Description**: Check if a given module path is a modular extension.



## Function: validate_boundary

**Parameters**: module_path
**Returns**: tuple[bool, str]
**Description**: Validate that a module respects kernel/extension boundary.

    Returns:
        (is_valid, reason) tuple
    



## Usage Examples

### Function Usage

```python
# Using is_kernel_component
result = is_kernel_component(module_path)
```

```python
# Using is_modular_extension
result = is_modular_extension(module_path)
```

```python
# Using validate_boundary
result = validate_boundary(module_path)
```



---
**Generated**: 2026-03-26T09:39:05.935414
**Type**: api_reference
**Quality**: comprehensive
