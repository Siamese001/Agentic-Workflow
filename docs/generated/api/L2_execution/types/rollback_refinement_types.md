# API Documentation: rollback_refinement_types

**Target Audience**: developers, api_users

# rollback_refinement_types API Documentation

**File**: `rollback_refinement_types.py`
**Classes**: 4
**Functions**: 8

## Classes

- **RollbackStrategyId**
- **RollbackOutcomeStats**
- **RollbackRefinementRequest**
- **RollbackRefinementDecision**

## Functions

- **canonical_bytes** -> bytes
- **content_hash** -> str
- **canonical_bytes** -> bytes
- **content_hash** -> str
- **canonical_bytes** -> bytes
- **content_hash** -> str
- **canonical_bytes** -> bytes
- **content_hash** -> str


## Class: RollbackStrategyId

**Description**: Identifier for a rollback strategy.

### Methods

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Canonical byte representation for hashing.

#### content_hash
**Parameters**: self
**Returns**: str
**Description**: SHA256 hex hash of canonical representation.



## Class: RollbackOutcomeStats

**Description**: Statistics for rollback strategy outcomes.

### Methods

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Canonical byte representation for hashing.

#### content_hash
**Parameters**: self
**Returns**: str
**Description**: SHA256 hex hash of canonical representation.



## Class: RollbackRefinementRequest

**Description**: Request to refine rollback strategy selection.

### Methods

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Canonical byte representation for hashing.

#### content_hash
**Parameters**: self
**Returns**: str
**Description**: SHA256 hex hash of canonical representation.



## Class: RollbackRefinementDecision

**Description**: Decision on rollback strategy with deterministic ranking.

### Methods

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Canonical byte representation for hashing.

#### content_hash
**Parameters**: self
**Returns**: str
**Description**: SHA256 hex hash of canonical representation.



## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: Canonical byte representation for hashing.



## Function: content_hash

**Parameters**: self
**Returns**: str
**Description**: SHA256 hex hash of canonical representation.



## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: Canonical byte representation for hashing.



## Function: content_hash

**Parameters**: self
**Returns**: str
**Description**: SHA256 hex hash of canonical representation.



## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: Canonical byte representation for hashing.



## Function: content_hash

**Parameters**: self
**Returns**: str
**Description**: SHA256 hex hash of canonical representation.



## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: Canonical byte representation for hashing.



## Function: content_hash

**Parameters**: self
**Returns**: str
**Description**: SHA256 hex hash of canonical representation.



## Usage Examples

### Class Usage

```python
# Using RollbackStrategyId
rollbackstrategyid = RollbackStrategyId()
rollbackstrategyid.canonical_bytes()
rollbackstrategyid.content_hash()
```

```python
# Using RollbackOutcomeStats
rollbackoutcomestats = RollbackOutcomeStats()
rollbackoutcomestats.canonical_bytes()
rollbackoutcomestats.content_hash()
```

```python
# Using RollbackRefinementRequest
rollbackrefinementrequest = RollbackRefinementRequest()
rollbackrefinementrequest.canonical_bytes()
rollbackrefinementrequest.content_hash()
```

### Function Usage

```python
# Using canonical_bytes
result = canonical_bytes()
```

```python
# Using content_hash
result = content_hash()
```

```python
# Using canonical_bytes
result = canonical_bytes()
```



---
**Generated**: 2026-03-26T09:39:04.000920
**Type**: api_reference
**Quality**: comprehensive
