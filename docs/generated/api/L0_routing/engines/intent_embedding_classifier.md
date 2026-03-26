# API Documentation: intent_embedding_classifier

**Target Audience**: developers, api_users

# intent_embedding_classifier API Documentation

**File**: `intent_embedding_classifier.py`
**Classes**: 2
**Functions**: 11

## Classes

- **_PrototypeEntry**
- **IntentEmbeddingClassifier**

## Functions

- **_l2_normalize** -> list[float]
- **_average_vectors** -> list[float] | None
- **__init__** -> None
- **_get_embedder** -> Any | None
- **_embed_texts** -> list[list[float]] | None
- **encode_prototype** -> bool
- **has_prototype** -> bool
- **prototype_count** -> int
- **classify** -> tuple[str, float] | None
- **update_prototype** -> bool
- **get_prototype_hash** -> str | None


## Class: _PrototypeEntry

**Description**: In-memory prototype record for one routing target.



## Class: IntentEmbeddingClassifier

**Description**: Cosine-similarity intent classifier backed by a LocalFAISSStore index.

    Usage::

        classifier = IntentEmbeddingClassifier(store_base_path=Path("..."))
        classifier.encode_prototype("resume_writer", ["resume", "cv", "career"])
        classifier.encode_prototype("code_reviewer", ["code", "review", "python"])
        target_name, confidence = classifier.classify("Please review my Python code")

    When embedding is unavailable (kill-switch / FAISS not installed), all
    methods return safe defaults without raising.

    Args:
        store_base_path: Directory passed to LocalFAISSStore for index storage.
        embedder:        Optional pre-built embedding callable
                         ``(texts: list[str]) -> list[list[float]]``.
                         When None, the classifier attempts to build one from
                         ``EmbeddingServiceFactory``.
        cosine_cutoff:   Minimum cosine score to return a non-None result
                         (default 0.0 — always returns best match).
    

### Methods

#### __init__
**Parameters**: self, store_base_path, embedder, cosine_cutoff
**Returns**: None

#### _get_embedder
**Parameters**: self
**Returns**: Any | None

#### _embed_texts
**Parameters**: self, texts
**Returns**: list[list[float]] | None
**Description**: Embed a list of texts, returning None if embedding is disabled.

#### encode_prototype
**Parameters**: self, target_name, texts
**Returns**: bool
**Description**: Encode and store a prototype vector for a routing target.

        Args:
            target_name: Name of the routing target (must match RouteTarget.name).
            texts:       List of representative texts (keywords + description).

        Returns:
            True if prototype was stored, False if embedding unavailable.
        

#### has_prototype
**Parameters**: self, target_name
**Returns**: bool
**Description**: Return True if a prototype exists for this target.

#### prototype_count
**Parameters**: self
**Returns**: int
**Description**: Return number of registered prototypes.

#### classify
**Parameters**: self, user_input
**Returns**: tuple[str, float] | None
**Description**: Classify user_input against registered prototypes.

        Args:
            user_input: Raw user or task input string.

        Returns:
            ``(target_name, confidence)`` tuple where confidence is cosine
            similarity in ``[0.0, 1.0]``, or ``None`` if:
            - No prototypes registered.
            - Embedding unavailable.
            - No match above ``cosine_cutoff``.
        

#### update_prototype
**Parameters**: self, target_name, texts
**Returns**: bool
**Description**: Re-encode prototype for target_name with new exemplar texts.

        Called by the MetaLearningBus when a ROUTING_MISCLASSIFICATION
        OptimizationCommit is applied.

        Returns:
            True if update succeeded, False otherwise.
        

#### get_prototype_hash
**Parameters**: self, target_name
**Returns**: str | None
**Description**: Return the content hash of a stored prototype, or None.



## Function: _l2_normalize

**Parameters**: vec
**Returns**: list[float]


## Function: _average_vectors

**Parameters**: vecs
**Returns**: list[float] | None
**Description**: Return component-wise average of a non-empty list of equal-length vectors.



## Function: __init__

**Parameters**: self, store_base_path, embedder, cosine_cutoff
**Returns**: None


## Function: _get_embedder

**Parameters**: self
**Returns**: Any | None


## Function: _embed_texts

**Parameters**: self, texts
**Returns**: list[list[float]] | None
**Description**: Embed a list of texts, returning None if embedding is disabled.



## Function: encode_prototype

**Parameters**: self, target_name, texts
**Returns**: bool
**Description**: Encode and store a prototype vector for a routing target.

        Args:
            target_name: Name of the routing target (must match RouteTarget.name).
            texts:       List of representative texts (keywords + description).

        Returns:
            True if prototype was stored, False if embedding unavailable.
        



## Function: has_prototype

**Parameters**: self, target_name
**Returns**: bool
**Description**: Return True if a prototype exists for this target.



## Function: prototype_count

**Parameters**: self
**Returns**: int
**Description**: Return number of registered prototypes.



## Function: classify

**Parameters**: self, user_input
**Returns**: tuple[str, float] | None
**Description**: Classify user_input against registered prototypes.

        Args:
            user_input: Raw user or task input string.

        Returns:
            ``(target_name, confidence)`` tuple where confidence is cosine
            similarity in ``[0.0, 1.0]``, or ``None`` if:
            - No prototypes registered.
            - Embedding unavailable.
            - No match above ``cosine_cutoff``.
        



## Function: update_prototype

**Parameters**: self, target_name, texts
**Returns**: bool
**Description**: Re-encode prototype for target_name with new exemplar texts.

        Called by the MetaLearningBus when a ROUTING_MISCLASSIFICATION
        OptimizationCommit is applied.

        Returns:
            True if update succeeded, False otherwise.
        



## Function: get_prototype_hash

**Parameters**: self, target_name
**Returns**: str | None
**Description**: Return the content hash of a stored prototype, or None.



## Usage Examples

### Class Usage

```python
# Using _PrototypeEntry
_prototypeentry = _PrototypeEntry()
```

```python
# Using IntentEmbeddingClassifier
intentembeddingclassifier = IntentEmbeddingClassifier()
intentembeddingclassifier.encode_prototype()
intentembeddingclassifier.has_prototype()
```

### Function Usage

```python
# Using _l2_normalize
result = _l2_normalize(vec)
```

```python
# Using _average_vectors
result = _average_vectors(vecs)
```

```python
# Using __init__
result = __init__(store_base_path, embedder)
```



---
**Generated**: 2026-03-26T09:39:02.659608
**Type**: api_reference
**Quality**: comprehensive
