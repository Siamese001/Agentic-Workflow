# API Documentation: vm_status_types

**Target Audience**: developers, api_users

# vm_status_types API Documentation

**File**: `vm_status_types.py`
**Classes**: 4
**Functions**: 4

## Classes

- **VmStatus** (inherits from Enum)
- **VmProvider** (inherits from Enum)
- **VmConfig**
- **VmInstance**

## Functions

- **to_dict** -> dict[str, Any]
- **is_running** -> bool
- **is_expired** -> bool
- **to_dict** -> dict[str, Any]


## Class: VmStatus

**Description**: VM operational status.

**Inherits from**: Enum



## Class: VmProvider

**Description**: VM Provider types.

**Inherits from**: Enum



## Class: VmConfig

**Description**: configuration for micro-VM.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: VmInstance

**Description**: Running VM instance.

### Methods

#### is_running
**Parameters**: self
**Returns**: bool
**Description**: Check if VM is running.

        Returns:
            True if running
        

#### is_expired
**Parameters**: self, current_time
**Returns**: bool
**Description**: Check if VM has exceeded timeout.

        Args:
            current_time: Current timestamp

        Returns:
            True if expired
        

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: is_running

**Parameters**: self
**Returns**: bool
**Description**: Check if VM is running.

        Returns:
            True if running
        



## Function: is_expired

**Parameters**: self, current_time
**Returns**: bool
**Description**: Check if VM has exceeded timeout.

        Args:
            current_time: Current timestamp

        Returns:
            True if expired
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Usage Examples

### Class Usage

```python
# Using VmStatus
vmstatus = VmStatus()
```

```python
# Using VmProvider
vmprovider = VmProvider()
```

```python
# Using VmConfig
vmconfig = VmConfig()
vmconfig.to_dict()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using is_running
result = is_running()
```

```python
# Using is_expired
result = is_expired(current_time)
```



---
**Generated**: 2026-03-26T09:39:04.044403
**Type**: api_reference
**Quality**: comprehensive
