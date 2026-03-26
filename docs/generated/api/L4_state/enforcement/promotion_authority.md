# API Documentation: promotion_authority

**Target Audience**: developers, api_users

# promotion_authority API Documentation

**File**: `promotion_authority.py`
**Classes**: 2
**Functions**: 9

## Classes

- **PromotionPointerUpdate**
- **PromotionAuthority**

## Functions

- **get_promotion_authority** -> PromotionAuthority
- **update_pointer_via_gateway** -> PromotionPointerUpdate
- **validate_pointer_update_integrity** -> bool
- **__init__**
- **set_write_gateway**
- **update_pointer_via_gateway** -> PromotionPointerUpdate
- **_get_current_pointer** -> str
- **get_update_history** -> PromotionPointerUpdate | None
- **validate_pointer_update_integrity** -> bool


## Class: PromotionPointerUpdate

**Description**: Immutable record of a promotion pointer update.



## Class: PromotionAuthority

**Description**: Manages promotion pointer updates through gateway with capability tokens.

### Methods

#### __init__
**Parameters**: self

#### set_write_gateway
**Parameters**: self, gateway
**Description**: Set the write gateway for pointer updates.

#### update_pointer_via_gateway
**Parameters**: self, new_pointer, capability_token
**Returns**: PromotionPointerUpdate
**Description**: Update pointer via gateway with capability token validation.

#### _get_current_pointer
**Parameters**: self, namespace
**Returns**: str
**Description**: Get current pointer for namespace.

#### get_update_history
**Parameters**: self, namespace
**Returns**: PromotionPointerUpdate | None
**Description**: Get update history for namespace.

#### validate_pointer_update_integrity
**Parameters**: self, namespace, expected_hash
**Returns**: bool
**Description**: Validate pointer update integrity.



## Function: get_promotion_authority

**Returns**: PromotionAuthority
**Description**: Get the singleton promotion authority instance.



## Function: update_pointer_via_gateway

**Parameters**: new_pointer, capability_token
**Returns**: PromotionPointerUpdate
**Description**: Update pointer via gateway with capability token validation.



## Function: validate_pointer_update_integrity

**Parameters**: namespace, expected_hash
**Returns**: bool
**Description**: Validate pointer update integrity.



## Function: __init__

**Parameters**: self


## Function: set_write_gateway

**Parameters**: self, gateway
**Description**: Set the write gateway for pointer updates.



## Function: update_pointer_via_gateway

**Parameters**: self, new_pointer, capability_token
**Returns**: PromotionPointerUpdate
**Description**: Update pointer via gateway with capability token validation.



## Function: _get_current_pointer

**Parameters**: self, namespace
**Returns**: str
**Description**: Get current pointer for namespace.



## Function: get_update_history

**Parameters**: self, namespace
**Returns**: PromotionPointerUpdate | None
**Description**: Get update history for namespace.



## Function: validate_pointer_update_integrity

**Parameters**: self, namespace, expected_hash
**Returns**: bool
**Description**: Validate pointer update integrity.



## Usage Examples

### Class Usage

```python
# Using PromotionPointerUpdate
promotionpointerupdate = PromotionPointerUpdate()
```

```python
# Using PromotionAuthority
promotionauthority = PromotionAuthority()
promotionauthority.set_write_gateway()
promotionauthority.update_pointer_via_gateway()
```

### Function Usage

```python
# Using get_promotion_authority
result = get_promotion_authority()
```

```python
# Using update_pointer_via_gateway
result = update_pointer_via_gateway(new_pointer, capability_token)
```

```python
# Using validate_pointer_update_integrity
result = validate_pointer_update_integrity(namespace, expected_hash)
```



---
**Generated**: 2026-03-26T09:39:04.514985
**Type**: api_reference
**Quality**: comprehensive
