# API Documentation: boot_sequence

**Target Audience**: developers, api_users

# boot_sequence API Documentation

**File**: `boot_sequence.py`
**Classes**: 1
**Functions**: 3

## Classes

- **BootSequence**

## Functions

- **main**
- **__init__**
- **execute_boot** -> dict[str, Any]


## Class: BootSequence

**Description**: 
    Orchestrates the secure boot process of the Agentic Workflow system.
    

### Methods

#### __init__
**Parameters**: self, strict_mode

#### execute_boot
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Executes the complete boot sequence with cryptographic handshake.

        Returns:
            Dict containing boot status, metrics, and any violations
        



## Function: main

**Description**: Entry point for the boot sequence.



## Function: __init__

**Parameters**: self, strict_mode


## Function: execute_boot

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Executes the complete boot sequence with cryptographic handshake.

        Returns:
            Dict containing boot status, metrics, and any violations
        



## Usage Examples

### Class Usage

```python
# Using BootSequence
bootsequence = BootSequence()
bootsequence.execute_boot()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using __init__
result = __init__(strict_mode)
```

```python
# Using execute_boot
result = execute_boot()
```



---
**Generated**: 2026-03-26T09:39:02.599312
**Type**: api_reference
**Quality**: comprehensive
