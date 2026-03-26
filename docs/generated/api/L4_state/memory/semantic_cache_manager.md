# API Documentation: semantic_cache_manager

**Target Audience**: developers, api_users

# semantic_cache_manager API Documentation

**File**: `semantic_cache_manager.py`
**Classes**: 3
**Functions**: 18

## Classes

- **CriticalInfrastructureError** (inherits from Exception)
- **PII_Sanitizer**
- **SemanticCacheManager**

## Functions

- **sanitize** -> str
- **is_safe** -> bool
- **detect_pii** -> dict[str, list[str]]
- **get_instance** -> SemanticCacheManager
- **_create_instance** -> SemanticCacheManager
- **reset_instance** -> None
- **__init__**
- **_initialize** -> None
- **_init_redis** -> Exception | None
- **_init_vector_store** -> None
- **_compute_hash** -> str
- **_get_embedding** -> list[float] | None
- **recall** -> dict[str, Any] | None
- **_should_sample_trace** -> bool
- **learn** -> None
- **update_feedback_score** -> bool
- **get_stats** -> dict[str, Any]
- **get_statistics** -> dict[str, Any]


## Class: CriticalInfrastructureError

**Description**: Raised when Hive Mind infrastructure is unavailable in STRICT mode.

**Inherits from**: Exception



## Class: PII_Sanitizer

**Description**: 
    [PHASE 21] Production-Grade PII Sanitizer for content sanitization before embedding.

    Detects and redacts:
    - Email addresses
    - IPv4 and IPv6 addresses
    - API keys (OpenAI sk-*, Anthropic sk-ant-*, generic patterns)
    - AWS access keys
    - Credit card numbers (basic pattern)
    - Phone numbers (US format)
    - SSN patterns

    All detected PII is replaced with [REDACTED_<TYPE>] placeholders.
    

### Methods

#### sanitize
**Parameters**: cls, content
**Returns**: str
**Description**: 
        Sanitize content by redacting all detected PII.

        Args:
            content: Raw content string

        Returns:
            Sanitized content with PII replaced by [REDACTED_<TYPE>] placeholders
        

#### is_safe
**Parameters**: cls, content
**Returns**: bool
**Description**: 
        Check if content contains any detectable PII.

        Args:
            content: Content to check

        Returns:
            True if no PII detected, False otherwise
        

#### detect_pii
**Parameters**: cls, content
**Returns**: dict[str, list[str]]
**Description**: 
        Detect and return all PII found in content.

        Args:
            content: Content to scan

        Returns:
            Dictionary mapping PII type to list of matches found
        



## Class: SemanticCacheManager

**Description**: 
    Singleton Semantic cache Manager - The Hive Mind.

    Provides dual-layer caching for collective agent intelligence:
    - Layer 1 (Redis): O(1) exact content hash matching (Working Memory - 24h TTL)
    - Layer 2 (InMemoryVectorStore): Semantic similarity matching (Long-Term DNA - promoted memories)

    Phase 20: Enforces singleton pattern with thread-safe initialization.
    Phase 20+: Configurable compliance, PII sanitization, trace sampling, memory lifecycle.

    Uses FAISS-backed InMemoryVectorStore for Layer 2 semantic search.

    configuration:
        HIVE_MIND_STRICT_MODE: "true" raises on failure, "false" degrades gracefully
        HIVE_MIND_TRACE_SAMPLING_RATE: 0.0 to 1.0 - controls trace capture rate
        HIVE_MIND_PROMOTION_THRESHOLD: 0.0 to 1.0 - minimum feedback score for promotion

    Usage:
        cache = SemanticCacheManager.get_instance()
        result = cache.recall(context, namespace)
    

### Methods

#### get_instance
**Parameters**: cls, api_key
**Returns**: SemanticCacheManager
**Description**: 
        Get the singleton instance of SemanticCacheManager.

        Thread-safe singleton pattern ensures only one Hive Mind exists.

        Args:
            api_key: Optional API key for embedding generation

        Returns:
            The singleton SemanticCacheManager instance

        Raises:
            CriticalInfrastructureError: If STRICT_MODE and infrastructure unavailable
        

#### _create_instance
**Parameters**: cls, api_key
**Returns**: SemanticCacheManager
**Description**: Internal factory method for creating the singleton.

#### reset_instance
**Parameters**: cls
**Returns**: None
**Description**: Reset the singleton instance (for testing only).

#### __init__
**Parameters**: self, api_key
**Description**: 
        Initialize is blocked for direct instantiation.
        Use get_instance() instead.
        

#### _initialize
**Parameters**: self, api_key
**Returns**: None
**Description**: 
        Internal initialization method with configurable compliance.

        Args:
            api_key: Optional API key for embedding generation

        Raises:
            CriticalInfrastructureError: If STRICT_MODE and infrastructure unavailable
        

#### _init_redis
**Parameters**: self
**Returns**: Exception | None
**Description**: 
        Initialize Redis connection with retry logic.

        Returns:
            Exception if connection failed, None if successful
        

#### _init_vector_store
**Parameters**: self
**Returns**: None
**Description**: Initialize in-memory vector store for semantic matching (BGE-m3 backend).

#### _compute_hash
**Parameters**: self, context, namespace
**Returns**: str
**Description**: Compute SHA256 hash for exact matching.

        Key includes determinism anchors (embedding model version and retrieval
        config hash) so cached results are automatically invalidated when either
        changes, preventing stale or inconsistent retrieval results.
        

#### _get_embedding
**Parameters**: self, text
**Returns**: list[float] | None
**Description**: Generate BGE-m3 embedding for semantic matching.

#### recall
**Parameters**: self, context, namespace
**Returns**: dict[str, Any] | None
**Description**: 
        Recall a result based on exact or semantic match.

        Args:
            context: The context string to query
            namespace: The namespace (typically agent class name)

        Returns:
            Cached result dict or None if not found
        

#### _should_sample_trace
**Parameters**: self, trace_id
**Returns**: bool
**Description**: 
        Determine if this trace should be sampled based on sampling rate.

        Deterministic sampling based on trace_id hash to ensure reproducibility.

        Returns:
            True if trace should be captured, False if skipped
        

#### learn
**Parameters**: self, context, namespace, result, feedback_score
**Returns**: None
**Description**: 
        Teach the Hive Mind a new result (Working Memory).

        Stores in Working Memory (Redis) with 24h TTL.
        Does NOT automatically promote to Long-Term Memory (InMemoryVectorStore).
        Use promote_to_long_term() with explicit feedback_score for DNA promotion.

        Args:
            context: The context string
            namespace: The namespace (typically agent class name)
            result: The result to store
            feedback_score: Optional feedback score (0.0 to 1.0) for promotion consideration
        

#### update_feedback_score
**Parameters**: self, context, namespace, feedback_score
**Returns**: bool
**Description**: 
        Update the feedback score for an existing memory.

        If the new score exceeds the promotion threshold, the memory
        will be automatically promoted to Long-Term DNA.

        Args:
            context: The context string
            namespace: The namespace
            feedback_score: New feedback score (0.0 to 1.0)

        Returns:
            True if updated (and possibly promoted), False if memory not found
        

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Alias for get_statistics() for test compatibility.

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get cache statistics.



## Function: sanitize

**Parameters**: cls, content
**Returns**: str
**Description**: 
        Sanitize content by redacting all detected PII.

        Args:
            content: Raw content string

        Returns:
            Sanitized content with PII replaced by [REDACTED_<TYPE>] placeholders
        



## Function: is_safe

**Parameters**: cls, content
**Returns**: bool
**Description**: 
        Check if content contains any detectable PII.

        Args:
            content: Content to check

        Returns:
            True if no PII detected, False otherwise
        



## Function: detect_pii

**Parameters**: cls, content
**Returns**: dict[str, list[str]]
**Description**: 
        Detect and return all PII found in content.

        Args:
            content: Content to scan

        Returns:
            Dictionary mapping PII type to list of matches found
        



## Function: get_instance

**Parameters**: cls, api_key
**Returns**: SemanticCacheManager
**Description**: 
        Get the singleton instance of SemanticCacheManager.

        Thread-safe singleton pattern ensures only one Hive Mind exists.

        Args:
            api_key: Optional API key for embedding generation

        Returns:
            The singleton SemanticCacheManager instance

        Raises:
            CriticalInfrastructureError: If STRICT_MODE and infrastructure unavailable
        



## Function: _create_instance

**Parameters**: cls, api_key
**Returns**: SemanticCacheManager
**Description**: Internal factory method for creating the singleton.



## Function: reset_instance

**Parameters**: cls
**Returns**: None
**Description**: Reset the singleton instance (for testing only).



## Function: __init__

**Parameters**: self, api_key
**Description**: 
        Initialize is blocked for direct instantiation.
        Use get_instance() instead.
        



## Function: _initialize

**Parameters**: self, api_key
**Returns**: None
**Description**: 
        Internal initialization method with configurable compliance.

        Args:
            api_key: Optional API key for embedding generation

        Raises:
            CriticalInfrastructureError: If STRICT_MODE and infrastructure unavailable
        



## Function: _init_redis

**Parameters**: self
**Returns**: Exception | None
**Description**: 
        Initialize Redis connection with retry logic.

        Returns:
            Exception if connection failed, None if successful
        



## Function: _init_vector_store

**Parameters**: self
**Returns**: None
**Description**: Initialize in-memory vector store for semantic matching (BGE-m3 backend).



## Function: _compute_hash

**Parameters**: self, context, namespace
**Returns**: str
**Description**: Compute SHA256 hash for exact matching.

        Key includes determinism anchors (embedding model version and retrieval
        config hash) so cached results are automatically invalidated when either
        changes, preventing stale or inconsistent retrieval results.
        



## Function: _get_embedding

**Parameters**: self, text
**Returns**: list[float] | None
**Description**: Generate BGE-m3 embedding for semantic matching.



## Function: recall

**Parameters**: self, context, namespace
**Returns**: dict[str, Any] | None
**Description**: 
        Recall a result based on exact or semantic match.

        Args:
            context: The context string to query
            namespace: The namespace (typically agent class name)

        Returns:
            Cached result dict or None if not found
        



## Function: _should_sample_trace

**Parameters**: self, trace_id
**Returns**: bool
**Description**: 
        Determine if this trace should be sampled based on sampling rate.

        Deterministic sampling based on trace_id hash to ensure reproducibility.

        Returns:
            True if trace should be captured, False if skipped
        



## Function: learn

**Parameters**: self, context, namespace, result, feedback_score
**Returns**: None
**Description**: 
        Teach the Hive Mind a new result (Working Memory).

        Stores in Working Memory (Redis) with 24h TTL.
        Does NOT automatically promote to Long-Term Memory (InMemoryVectorStore).
        Use promote_to_long_term() with explicit feedback_score for DNA promotion.

        Args:
            context: The context string
            namespace: The namespace (typically agent class name)
            result: The result to store
            feedback_score: Optional feedback score (0.0 to 1.0) for promotion consideration
        



## Function: update_feedback_score

**Parameters**: self, context, namespace, feedback_score
**Returns**: bool
**Description**: 
        Update the feedback score for an existing memory.

        If the new score exceeds the promotion threshold, the memory
        will be automatically promoted to Long-Term DNA.

        Args:
            context: The context string
            namespace: The namespace
            feedback_score: New feedback score (0.0 to 1.0)

        Returns:
            True if updated (and possibly promoted), False if memory not found
        



## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Alias for get_statistics() for test compatibility.



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get cache statistics.



## Usage Examples

### Class Usage

```python
# Using CriticalInfrastructureError
criticalinfrastructureerror = CriticalInfrastructureError()
```

```python
# Using PII_Sanitizer
pii_sanitizer = PII_Sanitizer()
pii_sanitizer.sanitize()
pii_sanitizer.is_safe()
```

```python
# Using SemanticCacheManager
semanticcachemanager = SemanticCacheManager()
semanticcachemanager.get_instance()
semanticcachemanager.reset_instance()
```

### Function Usage

```python
# Using sanitize
result = sanitize(cls, content)
```

```python
# Using is_safe
result = is_safe(cls, content)
```

```python
# Using detect_pii
result = detect_pii(cls, content)
```



---
**Generated**: 2026-03-26T09:39:04.591597
**Type**: api_reference
**Quality**: comprehensive
