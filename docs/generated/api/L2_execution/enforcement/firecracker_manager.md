# API Documentation: firecracker_manager

**Target Audience**: developers, api_users

# firecracker_manager API Documentation

**File**: `firecracker_manager.py`
**Classes**: 1
**Functions**: 5

## Classes

- **FirecrackerManager**

## Functions

- **create_firecracker_manager** -> FirecrackerManager
- **__init__**
- **get_vm** -> VMInstance | None
- **list_vms** -> list[VMInstance]
- **heal_repository** -> dict[str, int]


## Class: FirecrackerManager

**Description**: Manager for Firecracker micro-VMs.

    Provides:
    - VM lifecycle management
    - Resource isolation
    - Network isolation
    - Automatic cleanup

    Simplified implementation for Phase 3.
    Production should use full Firecracker/E2B SDK.
    

### Methods

#### __init__
**Parameters**: self, Provider, enable_logging
**Description**: Initialize Firecracker manager.

        Args:
            Provider: VM Provider
            enable_logging: Enable logging
        

#### get_vm
**Parameters**: self, vm_id
**Returns**: VMInstance | None
**Description**: Get VM instance.

        Args:
            vm_id: VM identifier

        Returns:
            VMInstance or None
        

#### list_vms
**Parameters**: self, status
**Returns**: list[VMInstance]
**Description**: List all VMs.

        Args:
            status: Optional status filter

        Returns:
            List of VM instances
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L2 execution agent - operational only.



## Function: create_firecracker_manager

**Parameters**: Provider
**Returns**: FirecrackerManager
**Description**: Factory function to create Firecracker manager.

    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    Args:
        Provider: VM Provider type

    Returns:
        FirecrackerManager instance
    



## Function: __init__

**Parameters**: self, Provider, enable_logging
**Description**: Initialize Firecracker manager.

        Args:
            Provider: VM Provider
            enable_logging: Enable logging
        



## Function: get_vm

**Parameters**: self, vm_id
**Returns**: VMInstance | None
**Description**: Get VM instance.

        Args:
            vm_id: VM identifier

        Returns:
            VMInstance or None
        



## Function: list_vms

**Parameters**: self, status
**Returns**: list[VMInstance]
**Description**: List all VMs.

        Args:
            status: Optional status filter

        Returns:
            List of VM instances
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L2 execution agent - operational only.



## Usage Examples

### Class Usage

```python
# Using FirecrackerManager
firecrackermanager = FirecrackerManager()
firecrackermanager.get_vm()
firecrackermanager.list_vms()
```

### Function Usage

```python
# Using create_firecracker_manager
result = create_firecracker_manager(Provider)
```

```python
# Using __init__
result = __init__(Provider, enable_logging)
```

```python
# Using get_vm
result = get_vm(vm_id)
```



---
**Generated**: 2026-03-26T09:39:03.702399
**Type**: api_reference
**Quality**: comprehensive
