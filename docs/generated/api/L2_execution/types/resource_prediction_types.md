# API Documentation: resource_prediction_types

**Target Audience**: developers, api_users

# resource_prediction_types API Documentation

**File**: `resource_prediction_types.py`
**Classes**: 3
**Functions**: 6

## Classes

- **FailureSignature**
- **ResourceEnvelope**
- **ResourcePrediction**

## Functions

- **canonical_bytes** -> bytes
- **content_hash** -> str
- **canonical_bytes** -> bytes
- **content_hash** -> str
- **canonical_bytes** -> bytes
- **content_hash** -> str


## Class: FailureSignature

**Description**: Deterministic signature of a failure for resource prediction.

### Methods

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Canonical byte representation for hashing.

#### content_hash
**Parameters**: self
**Returns**: str
**Description**: SHA256 hex hash of canonical representation.



## Class: ResourceEnvelope

**Description**: Bounded resource envelope for execution.

### Methods

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Canonical byte representation for hashing.

#### content_hash
**Parameters**: self
**Returns**: str
**Description**: SHA256 hex hash of canonical representation.



## Class: ResourcePrediction

**Description**: Deterministic resource prediction for a failure signature.

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



## Usage Examples

### Class Usage

```python
# Using FailureSignature
failuresignature = FailureSignature()
failuresignature.canonical_bytes()
failuresignature.content_hash()
```

```python
# Using ResourceEnvelope
resourceenvelope = ResourceEnvelope()
resourceenvelope.canonical_bytes()
resourceenvelope.content_hash()
```

```python
# Using ResourcePrediction
resourceprediction = ResourcePrediction()
resourceprediction.canonical_bytes()
resourceprediction.content_hash()
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
**Generated**: 2026-03-26T09:39:03.998888
**Type**: api_reference
**Quality**: comprehensive
