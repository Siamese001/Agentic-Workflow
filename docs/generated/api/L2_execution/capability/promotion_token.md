# API Documentation: promotion_token

**Target Audience**: developers, api_users

# promotion_token API Documentation

**File**: `promotion_token.py`
**Classes**: 3
**Functions**: 15

## Classes

- **PromotionToken**
- **PromotionTokenStore**
- **PromotionTokenIssuer**

## Functions

- **get_token_issuer** -> PromotionTokenIssuer
- **issue_promotion_token** -> PromotionToken
- **validate_scope_and_use** -> bool
- **is_expired** -> bool
- **is_valid_for_namespace** -> bool
- **__new__**
- **is_nonce_used** -> bool
- **mark_nonce_used** -> None
- **store_token** -> None
- **get_token** -> PromotionToken | None
- **revoke_token** -> bool
- **clear_all** -> None
- **__init__**
- **issue_promotion_token** -> PromotionToken
- **validate_token** -> bool


## Class: PromotionToken

**Description**: Scoped capability token for promotion operations.

### Methods

#### validate_scope_and_use
**Parameters**: self
**Returns**: bool
**Description**: Validate token scope and single-use status.

#### is_expired
**Parameters**: self, current_tick
**Returns**: bool
**Description**: Check if token is expired.

        For point windows (start == end), the token is only valid at exactly that tick.
        For range windows, a grace period applies before the start; only checks upper bound.
        

#### is_valid_for_namespace
**Parameters**: self, namespace
**Returns**: bool
**Description**: Check if token is valid for given namespace.



## Class: PromotionTokenStore

**Description**: Store for tracking used nonces and token state.

### Methods

#### __new__
**Parameters**: cls

#### is_nonce_used
**Parameters**: cls, nonce
**Returns**: bool
**Description**: Check if nonce has been used.

#### mark_nonce_used
**Parameters**: cls, nonce
**Returns**: None
**Description**: Mark nonce as used.

#### store_token
**Parameters**: cls, token
**Returns**: None
**Description**: Store active token.

#### get_token
**Parameters**: cls, token_id
**Returns**: PromotionToken | None
**Description**: Get stored token.

#### revoke_token
**Parameters**: cls, token_id
**Returns**: bool
**Description**: Revoke token.

#### clear_all
**Parameters**: cls
**Returns**: None
**Description**: Clear all stored data (for testing).



## Class: PromotionTokenIssuer

**Description**: Issues promotion tokens with proper scope and constraints.

### Methods

#### __init__
**Parameters**: self

#### issue_promotion_token
**Parameters**: self, target_namespace, semantic_clock_tick, window_size, replay_digest, guardian_signature
**Returns**: PromotionToken
**Description**: Issue a new promotion token.

#### validate_token
**Parameters**: self, token, namespace, current_tick
**Returns**: bool
**Description**: Validate token scope, time window, and single-use nonce (consuming check).

        Checks namespace, expiration, action scope, and single-use nonce.
        Consumes nonce on first successful validation.
        



## Function: get_token_issuer

**Returns**: PromotionTokenIssuer
**Description**: Get the singleton token issuer.



## Function: issue_promotion_token

**Parameters**: target_namespace, semantic_clock_tick, window_size, replay_digest, guardian_signature
**Returns**: PromotionToken
**Description**: Issue a new promotion token.



## Function: validate_scope_and_use

**Parameters**: self
**Returns**: bool
**Description**: Validate token scope and single-use status.



## Function: is_expired

**Parameters**: self, current_tick
**Returns**: bool
**Description**: Check if token is expired.

        For point windows (start == end), the token is only valid at exactly that tick.
        For range windows, a grace period applies before the start; only checks upper bound.
        



## Function: is_valid_for_namespace

**Parameters**: self, namespace
**Returns**: bool
**Description**: Check if token is valid for given namespace.



## Function: __new__

**Parameters**: cls


## Function: is_nonce_used

**Parameters**: cls, nonce
**Returns**: bool
**Description**: Check if nonce has been used.



## Function: mark_nonce_used

**Parameters**: cls, nonce
**Returns**: None
**Description**: Mark nonce as used.



## Function: store_token

**Parameters**: cls, token
**Returns**: None
**Description**: Store active token.



## Function: get_token

**Parameters**: cls, token_id
**Returns**: PromotionToken | None
**Description**: Get stored token.



## Function: revoke_token

**Parameters**: cls, token_id
**Returns**: bool
**Description**: Revoke token.



## Function: clear_all

**Parameters**: cls
**Returns**: None
**Description**: Clear all stored data (for testing).



## Function: __init__

**Parameters**: self


## Function: issue_promotion_token

**Parameters**: self, target_namespace, semantic_clock_tick, window_size, replay_digest, guardian_signature
**Returns**: PromotionToken
**Description**: Issue a new promotion token.



## Function: validate_token

**Parameters**: self, token, namespace, current_tick
**Returns**: bool
**Description**: Validate token scope, time window, and single-use nonce (consuming check).

        Checks namespace, expiration, action scope, and single-use nonce.
        Consumes nonce on first successful validation.
        



## Usage Examples

### Class Usage

```python
# Using PromotionToken
promotiontoken = PromotionToken()
promotiontoken.validate_scope_and_use()
promotiontoken.is_expired()
```

```python
# Using PromotionTokenStore
promotiontokenstore = PromotionTokenStore()
promotiontokenstore.is_nonce_used()
promotiontokenstore.mark_nonce_used()
```

```python
# Using PromotionTokenIssuer
promotiontokenissuer = PromotionTokenIssuer()
promotiontokenissuer.issue_promotion_token()
promotiontokenissuer.validate_token()
```

### Function Usage

```python
# Using get_token_issuer
result = get_token_issuer()
```

```python
# Using issue_promotion_token
result = issue_promotion_token(target_namespace, semantic_clock_tick)
```

```python
# Using validate_scope_and_use
result = validate_scope_and_use()
```



---
**Generated**: 2026-03-26T09:39:03.619256
**Type**: api_reference
**Quality**: comprehensive
