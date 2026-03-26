# API Documentation: ephemeral_vm_types

**Target Audience**: developers, api_users

# ephemeral_vm_types API Documentation

**File**: `ephemeral_vm_types.py`
**Classes**: 4
**Functions**: 7

## Classes

- **IsolationLevel** (inherits from Enum)
- **IsolationConfig**
- **ExecutionResult**
- **EphemeralVm**

## Functions

- **create_ephemeral_vm** -> EphemeralVM
- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **__init__**
- **_create_vm_config** -> tuple
- **_handle_timeout** -> ExecutionResult
- **_handle_execution_error** -> ExecutionResult


## Class: IsolationLevel

**Description**: Isolation levels for VM.

**Inherits from**: Enum



## Class: IsolationConfig

**Description**: configuration for VM isolation.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: ExecutionResult

**Description**: Result from code execution in VM.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: EphemeralVm

**Description**: Ephemeral VM for secure code execution.

    Features:
    - Automatic creation and teardown
    - Strict isolation
    - Resource limits
    - Timeout enforcement
    - Network isolation
    

### Methods

#### __init__
**Parameters**: self, vm_manager, IsolationConfig, enable_logging
**Description**: Initialize ephemeral VM.

        Args:
            vm_manager: Firecracker manager
            IsolationConfig: Isolation configuration
            enable_logging: Enable logging
        

#### _create_vm_config
**Parameters**: self, timeout
**Returns**: tuple
**Description**: Create VM configuration.

#### _handle_timeout
**Parameters**: self, vm_id, timeout, start_time
**Returns**: ExecutionResult
**Description**: Handle execution timeout.

#### _handle_execution_error
**Parameters**: self, vm_id, error, start_time
**Returns**: ExecutionResult
**Description**: Handle execution error.



## Function: create_ephemeral_vm

**Parameters**: vm_manager, IsolationConfig
**Returns**: EphemeralVM
**Description**: Factory function to create ephemeral VM.

    Args:
        vm_manager: Optional VM manager
        IsolationConfig: Optional isolation config

    Returns:
        EphemeralVM instance
    



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: __init__

**Parameters**: self, vm_manager, IsolationConfig, enable_logging
**Description**: Initialize ephemeral VM.

        Args:
            vm_manager: Firecracker manager
            IsolationConfig: Isolation configuration
            enable_logging: Enable logging
        



## Function: _create_vm_config

**Parameters**: self, timeout
**Returns**: tuple
**Description**: Create VM configuration.



## Function: _handle_timeout

**Parameters**: self, vm_id, timeout, start_time
**Returns**: ExecutionResult
**Description**: Handle execution timeout.



## Function: _handle_execution_error

**Parameters**: self, vm_id, error, start_time
**Returns**: ExecutionResult
**Description**: Handle execution error.



## Usage Examples

### Class Usage

```python
# Using IsolationLevel
isolationlevel = IsolationLevel()
```

```python
# Using IsolationConfig
isolationconfig = IsolationConfig()
isolationconfig.to_dict()
```

```python
# Using ExecutionResult
executionresult = ExecutionResult()
executionresult.to_dict()
```

### Function Usage

```python
# Using create_ephemeral_vm
result = create_ephemeral_vm(vm_manager, IsolationConfig)
```

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:03.954524
**Type**: api_reference
**Quality**: comprehensive
