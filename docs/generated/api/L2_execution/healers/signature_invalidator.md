# API Documentation: signature_invalidator

**Target Audience**: developers, api_users

# signature_invalidator API Documentation

**File**: `signature_invalidator.py`
**Classes**: 2
**Functions**: 2

## Classes

- **StaleSignatureViolation** (inherits from Exception)
- **InvalidationResult** (inherits from NamedTuple)

## Functions

- **invalidate_signature_and_rehash** -> InvalidationResult
- **verify_no_stale_signature**


## Class: StaleSignatureViolation

**Description**: Raised when a healed plan is executed with a stale signature.

**Inherits from**: Exception



## Class: InvalidationResult

**Description**: The result of invalidating a plan's signature.

**Inherits from**: NamedTuple



## Function: invalidate_signature_and_rehash

**Parameters**: plan
**Returns**: InvalidationResult
**Description**: 
    Strips cryptographic signatures and regenerates the policy hash for a healed plan.

    This is a critical step for Guarantee #4. After a plan is modified by a
    healing agent, its original approval signature is no longer valid. This
    function ensures the old signature is removed and a new policy hash is
    generated from the modified content, forcing a full L5 re-validation.

    Args:
        plan: The healed plan that has been modified.

    Returns:
        An InvalidationResult containing the plan with its signature stripped
        and a new policy hash for re-validation.
    



## Function: verify_no_stale_signature

**Parameters**: plan
**Description**: 
    Verifies that a plan about to be executed does not contain a stale signature.

    This would be called by the execution gateway before committing a change.
    It's a final check to prevent a bypass of the re-clear loop.

    Args:
        plan: The plan to be checked.

    Raises:
        StaleSignatureViolation: If a signature is present on a healed plan that
                                 should have been invalidated.
    



## Usage Examples

### Class Usage

```python
# Using StaleSignatureViolation
stalesignatureviolation = StaleSignatureViolation()
```

```python
# Using InvalidationResult
invalidationresult = InvalidationResult()
```

### Function Usage

```python
# Using invalidate_signature_and_rehash
result = invalidate_signature_and_rehash(plan)
```

```python
# Using verify_no_stale_signature
result = verify_no_stale_signature(plan)
```



---
**Generated**: 2026-03-26T09:39:03.847801
**Type**: api_reference
**Quality**: comprehensive
