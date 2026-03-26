# API Documentation: SecurityManagerAgent

**Target Audience**: developers, api_users

# SecurityManagerAgent API Documentation

**File**: `SecurityManagerAgent.py`
**Classes**: 7
**Functions**: 16

## Classes

- **PermissionLevel** (inherits from Enum)
- **SecurityAction** (inherits from Enum)
- **SecurityAuditEntry**
- **AgentPermission**
- **secure_config**
- **secure_checkpoint**
- **SecurityManagerAgent** (inherits from SovereignBaseAgent)

## Functions

- **create_legacy_permission_manager** -> SecurityManagerAgent
- **create_legacy_checkpoint_manager** -> SecurityManagerAgent
- **create_legacy_config_manager** -> SecurityManagerAgent
- **heal_repository** -> dict[str, Any]
- **__init__**
- **_audit** -> None
- **_check_permission** -> bool
- **grant_permission** -> bool
- **revoke_permission** -> bool
- **get_permission_level** -> PermissionLevel
- **set_config** -> bool
- **get_config** -> Any | None
- **create_checkpoint** -> secure_checkpoint | None
- **restore_checkpoint** -> dict[str, Any] | None
- **get_audit_log** -> list[SecurityAuditEntry]
- **heal** -> dict


## Class: PermissionLevel

**Description**: Permission levels for security access.

**Inherits from**: Enum



## Class: SecurityAction

**Description**: Types of security actions.

**Inherits from**: Enum



## Class: SecurityAuditEntry

**Description**: Audit log entry for security operations.



## Class: AgentPermission

**Description**: Permission record for an agent.



## Class: secure_config

**Description**: Secure configuration entry.



## Class: secure_checkpoint

**Description**: Secure checkpoint record.



## Class: SecurityManagerAgent

**Description**: 
    Vaulted security manager with permission-based access control.

    Consolidates:
    - AgentPermissionManagerAgent (permissions)
    - SecureCheckpointManagerAgent (checkpoints)
    - SecureConfigManagerAgent (configuration)

    Usage:
        manager = SecurityManagerAgent()

        # Grant permission
        manager.grant_permission("agent_1", PermissionLevel.SECURE_READER, "admin")

        # Access config (requires permission)
        value = manager.get_config("api_key", agent_id="agent_1")

        # Create secure checkpoint
        checkpoint = manager.create_checkpoint("agent_1", data={"state": "active"})
    

**Inherits from**: SovereignBaseAgent

### Methods

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        

#### __init__
**Parameters**: self, vault_path

#### _audit
**Parameters**: self, agent_id, action, resource, success, details
**Returns**: None
**Description**: Log a security audit entry.

#### _check_permission
**Parameters**: self, agent_id, required_level, resource
**Returns**: bool
**Description**: Check if agent has required permission level.

#### grant_permission
**Parameters**: self, agent_id, level, granted_by, expires_at, allowed_resources
**Returns**: bool
**Description**: Grant permission to an agent.

#### revoke_permission
**Parameters**: self, agent_id, revoked_by
**Returns**: bool
**Description**: Revoke permission from an agent.

#### get_permission_level
**Parameters**: self, agent_id
**Returns**: PermissionLevel
**Description**: Get permission level for an agent.

#### set_config
**Parameters**: self, key, value, agent_id, required_level, encrypted
**Returns**: bool
**Description**: Set a secure configuration value.

#### get_config
**Parameters**: self, key, agent_id
**Returns**: Any | None
**Description**: Get a secure configuration value.

#### create_checkpoint
**Parameters**: self, agent_id, data, encrypted
**Returns**: secure_checkpoint | None
**Description**: Create a secure checkpoint.

#### restore_checkpoint
**Parameters**: self, checkpoint_id, agent_id
**Returns**: dict[str, Any] | None
**Description**: Restore from a secure checkpoint.

#### get_audit_log
**Parameters**: self, agent_id, action, limit
**Returns**: list[SecurityAuditEntry]
**Description**: Get audit log entries.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal security management violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (permission, config, checkpoint)
                - agent_id: Agent that caused the violation
                - action: Security action that failed

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: create_legacy_permission_manager

**Returns**: SecurityManagerAgent
**Description**: Create a security manager for permission management.



## Function: create_legacy_checkpoint_manager

**Returns**: SecurityManagerAgent
**Description**: Create a security manager for checkpoint operations.



## Function: create_legacy_config_manager

**Returns**: SecurityManagerAgent
**Description**: Create a security manager for configuration access.



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        



## Function: __init__

**Parameters**: self, vault_path


## Function: _audit

**Parameters**: self, agent_id, action, resource, success, details
**Returns**: None
**Description**: Log a security audit entry.



## Function: _check_permission

**Parameters**: self, agent_id, required_level, resource
**Returns**: bool
**Description**: Check if agent has required permission level.



## Function: grant_permission

**Parameters**: self, agent_id, level, granted_by, expires_at, allowed_resources
**Returns**: bool
**Description**: Grant permission to an agent.



## Function: revoke_permission

**Parameters**: self, agent_id, revoked_by
**Returns**: bool
**Description**: Revoke permission from an agent.



## Function: get_permission_level

**Parameters**: self, agent_id
**Returns**: PermissionLevel
**Description**: Get permission level for an agent.



## Function: set_config

**Parameters**: self, key, value, agent_id, required_level, encrypted
**Returns**: bool
**Description**: Set a secure configuration value.



## Function: get_config

**Parameters**: self, key, agent_id
**Returns**: Any | None
**Description**: Get a secure configuration value.



## Function: create_checkpoint

**Parameters**: self, agent_id, data, encrypted
**Returns**: secure_checkpoint | None
**Description**: Create a secure checkpoint.



## Function: restore_checkpoint

**Parameters**: self, checkpoint_id, agent_id
**Returns**: dict[str, Any] | None
**Description**: Restore from a secure checkpoint.



## Function: get_audit_log

**Parameters**: self, agent_id, action, limit
**Returns**: list[SecurityAuditEntry]
**Description**: Get audit log entries.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal security management violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (permission, config, checkpoint)
                - agent_id: Agent that caused the violation
                - action: Security action that failed

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using PermissionLevel
permissionlevel = PermissionLevel()
```

```python
# Using SecurityAction
securityaction = SecurityAction()
```

```python
# Using SecurityAuditEntry
securityauditentry = SecurityAuditEntry()
```

### Function Usage

```python
# Using create_legacy_permission_manager
result = create_legacy_permission_manager()
```

```python
# Using create_legacy_checkpoint_manager
result = create_legacy_checkpoint_manager()
```

```python
# Using create_legacy_config_manager
result = create_legacy_config_manager()
```



---
**Generated**: 2026-03-26T09:39:05.396054
**Type**: api_reference
**Quality**: comprehensive
