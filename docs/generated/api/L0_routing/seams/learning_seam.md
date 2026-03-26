# API Documentation: learning_seam

**Target Audience**: developers, api_users

# learning_seam API Documentation

**File**: `learning_seam.py`
**Classes**: 2
**Functions**: 4

## Classes

- **LearningArtifactIntent**
- **LearningPersistenceService** (inherits from Protocol)

## Functions

- **_intent_canonical_bytes** -> bytes
- **create** -> LearningArtifactIntent
- **verify** -> bool
- **persist_learning_intent** -> bool


## Class: LearningArtifactIntent

**Description**: Immutable intent object emitted by agents for L2 persistence.

    Fields are frozen at construction.  ``intent_hash`` is the
    sha-256 of the canonical serialisation of all other fields and
    MUST be computed before the intent leaves the emitting layer.

    L2 verifies ``intent_hash`` on receipt before persisting.
    

### Methods

#### create
**Returns**: LearningArtifactIntent
**Description**: Construct an intent with a pre-computed hash.

        This is the ONLY approved construction path.  Direct
        ``__init__`` is allowed but callers are responsible for
        providing a correct ``intent_hash``.
        

#### verify
**Parameters**: self
**Returns**: bool
**Description**: Re-derive hash and compare — used by L2 on receipt.



## Class: LearningPersistenceService

**Description**: Protocol that L2 implements to persist learning intents.

    No layer other than L2 may implement durable writes.
    

**Inherits from**: Protocol

### Methods

#### persist_learning_intent
**Parameters**: self, intent
**Returns**: bool
**Description**: Persist a verified learning intent.

        Returns True on success, False on rejection.
        Implementations MUST call ``intent.verify()`` before
        writing.
        



## Function: _intent_canonical_bytes

**Parameters**: agent_id, execution_id, outcome, metrics, context_hash
**Returns**: bytes
**Description**: Produce deterministic canonical bytes for intent hash.

    Delegates to the shared canonical serializer.
    



## Function: create

**Returns**: LearningArtifactIntent
**Description**: Construct an intent with a pre-computed hash.

        This is the ONLY approved construction path.  Direct
        ``__init__`` is allowed but callers are responsible for
        providing a correct ``intent_hash``.
        



## Function: verify

**Parameters**: self
**Returns**: bool
**Description**: Re-derive hash and compare — used by L2 on receipt.



## Function: persist_learning_intent

**Parameters**: self, intent
**Returns**: bool
**Description**: Persist a verified learning intent.

        Returns True on success, False on rejection.
        Implementations MUST call ``intent.verify()`` before
        writing.
        



## Usage Examples

### Class Usage

```python
# Using LearningArtifactIntent
learningartifactintent = LearningArtifactIntent()
learningartifactintent.create()
learningartifactintent.verify()
```

```python
# Using LearningPersistenceService
learningpersistenceservice = LearningPersistenceService()
learningpersistenceservice.persist_learning_intent()
```

### Function Usage

```python
# Using _intent_canonical_bytes
result = _intent_canonical_bytes(agent_id, execution_id)
```

```python
# Using create
result = create()
```

```python
# Using verify
result = verify()
```



---
**Generated**: 2026-03-26T09:39:03.399362
**Type**: api_reference
**Quality**: comprehensive
