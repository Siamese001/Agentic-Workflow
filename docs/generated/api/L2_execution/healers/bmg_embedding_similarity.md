# API Documentation: bmg_embedding_similarity

**Target Audience**: developers, api_users

# bmg_embedding_similarity API Documentation

**File**: `bmg_embedding_similarity.py`
**Classes**: 0
**Functions**: 5


## Functions

- **_get_model** -> object
- **_is_cuda_available** -> bool
- **bmg_cosine_similarity** -> float
- **bmg_embed_text** -> list[float]
- **clear_model_cache** -> None


## Function: _get_model

**Returns**: object
**Description**: Load and cache the BGE-M3 model.  Raises ImportError if unavailable.



## Function: _is_cuda_available

**Returns**: bool
**Description**: Return True if a CUDA device is reachable without importing torch directly.



## Function: bmg_cosine_similarity

**Parameters**: unknown, candidates
**Returns**: float
**Description**: Return the maximum cosine similarity between *unknown* and *candidates*.

    Uses numpy dot-product on L2-normalised vectors (avoids direct torch import).

    Args:
        unknown: The query string (e.g. a file path or violation description).
        candidates: Non-empty list of reference strings.

    Returns:
        Float in [0.0, 1.0] — maximum cosine similarity across all candidates.

    Raises:
        ImportError: If sentence-transformers is not installed.
        ValueError: If candidates is empty.
    



## Function: bmg_embed_text

**Parameters**: text
**Returns**: list[float]
**Description**: Embed a single text string using BAAI/bge-m3.

    Returns an L2-normalised embedding vector as a plain Python list of
    floats.  Suitable for storage in ``HealingOutcomeEvent.failure_vector``
    and subsequent cosine-similarity novelty checks.

    Args:
        text: The text to embed (e.g. a normalized failure signal string).

    Returns:
        L2-normalised float list of length equal to the model's output
        dimension (~1024 for bge-m3).

    Raises:
        ImportError: If sentence-transformers is not installed.
    



## Function: clear_model_cache

**Returns**: None
**Description**: Invalidate the cached model (for tests and hot-reload).



## Usage Examples

### Function Usage

```python
# Using _get_model
result = _get_model()
```

```python
# Using _is_cuda_available
result = _is_cuda_available()
```

```python
# Using bmg_cosine_similarity
result = bmg_cosine_similarity(unknown, candidates)
```



---
**Generated**: 2026-03-26T09:39:03.790623
**Type**: api_reference
**Quality**: comprehensive
