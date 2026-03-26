# API Documentation: permission_scope_types

**Target Audience**: developers, api_users

# permission_scope_types API Documentation

**File**: `permission_scope_types.py`
**Classes**: 4
**Functions**: 3

## Classes

- **PermissionScope** (inherits from Enum)
- **PermissionAction** (inherits from Enum)
- **Permission**
- **PermissionCheck**

## Functions

- **matches** -> bool
- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]


## Class: PermissionScope

**Description**: Permission scopes.

**Inherits from**: Enum



## Class: PermissionAction

**Description**: Permission actions.

**Inherits from**: Enum



## Class: Permission

**Description**: Individual Permission.

### Methods

#### matches
**Parameters**: self, scope, action, resource
**Returns**: bool
**Description**: Check if Permission matches request.

        Args:
            scope: Requested scope
            action: Requested action
            resource: Requested resource

        Returns:
            True if matches
        

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: PermissionCheck

**Description**: Result of Permission check.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: matches

**Parameters**: self, scope, action, resource
**Returns**: bool
**Description**: Check if Permission matches request.

        Args:
            scope: Requested scope
            action: Requested action
            resource: Requested resource

        Returns:
            True if matches
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Usage Examples

### Class Usage

```python
# Using PermissionScope
permissionscope = PermissionScope()
```

```python
# Using PermissionAction
permissionaction = PermissionAction()
```

```python
# Using Permission
permission = Permission()
permission.matches()
permission.to_dict()
```

### Function Usage

```python
# Using matches
result = matches(scope, action)
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
**Generated**: 2026-03-26T09:39:04.394660
**Type**: api_reference
**Quality**: comprehensive
