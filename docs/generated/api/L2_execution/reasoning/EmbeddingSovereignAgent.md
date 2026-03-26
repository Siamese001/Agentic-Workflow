# API Documentation: EmbeddingSovereignAgent

**Target Audience**: developers, api_users

# EmbeddingSovereignAgent API Documentation

**File**: `EmbeddingSovereignAgent.py`
**Classes**: 3
**Functions**: 14

## Classes

- **EmbeddingSovereignAgent** (inherits from RedisCacheMixin, SovereignBaseAgent)
- **SubatomicTestingMixin**
- **RedisCacheMixin**

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **get_embedding_gateway** -> EmbeddingSovereignAgent
- **__post_init__** -> None
- **__new__**
- **reset_instance**
- **config**
- **EXPECTED_DIMENSIONS** -> dict[str, int]
- **_audit** -> None
- **_content_hash** -> str
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **cache_get**
- **cache_set**


## Class: EmbeddingSovereignAgent

**Description**: 
    Unified Embedding Gateway with Redis caching.

    [PHASE 4 MIGRATION] Absorbed from:
    - gemini_embedder.py
    - core_embedder.py
    - PineconeSovereignAgent.get_embedding()

    [PHASE 8] NOT an agent - utility singleton to avoid circular imports.
    

**Inherits from**: RedisCacheMixin, SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the EmbeddingSovereignAgent.

#### __new__
**Parameters**: cls
**Description**: Singleton constructor.

#### reset_instance
**Parameters**: cls
**Description**: [TESTING ONLY] Reset the singleton instance.

#### config
**Parameters**: self
**Description**: [PHASE 6] Access centralized config.

#### EXPECTED_DIMENSIONS
**Parameters**: self
**Returns**: dict[str, int]
**Description**: [PHASE 6] Dynamic dimensions from config.

#### _audit
**Parameters**: self, provider, success, cached, latency_ms
**Returns**: None
**Description**: 
        [PHASE 4] Record embedding operation.
        Includes FIFO rotation to prevent memory leaks.
        

#### _content_hash
**Parameters**: self, content
**Returns**: str
**Description**: Generate deterministic hash for caching.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        L2 Execution Agent - Embedding Gateway Healing.

        WIRED CAPABILITIES:
        - Validates embedding provider configurations
        - Checks Redis cache connectivity
        - Verifies API key availability
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by EmbeddingSovereignAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Class: SubatomicTestingMixin



## Class: RedisCacheMixin

### Methods

#### cache_get
**Parameters**: self, key

#### cache_set
**Parameters**: self, key, value, ttl



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: payload, target


## Function: get_embedding_gateway

**Returns**: EmbeddingSovereignAgent
**Description**: Get or create the global embedding gateway.



## Function: __post_init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the EmbeddingSovereignAgent.



## Function: __new__

**Parameters**: cls
**Description**: Singleton constructor.



## Function: reset_instance

**Parameters**: cls
**Description**: [TESTING ONLY] Reset the singleton instance.



## Function: config

**Parameters**: self
**Description**: [PHASE 6] Access centralized config.



## Function: EXPECTED_DIMENSIONS

**Parameters**: self
**Returns**: dict[str, int]
**Description**: [PHASE 6] Dynamic dimensions from config.



## Function: _audit

**Parameters**: self, provider, success, cached, latency_ms
**Returns**: None
**Description**: 
        [PHASE 4] Record embedding operation.
        Includes FIFO rotation to prevent memory leaks.
        



## Function: _content_hash

**Parameters**: self, content
**Returns**: str
**Description**: Generate deterministic hash for caching.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        L2 Execution Agent - Embedding Gateway Healing.

        WIRED CAPABILITIES:
        - Validates embedding provider configurations
        - Checks Redis cache connectivity
        - Verifies API key availability
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by EmbeddingSovereignAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Function: cache_get

**Parameters**: self, key


## Function: cache_set

**Parameters**: self, key, value, ttl


## Usage Examples

### Class Usage

```python
# Using EmbeddingSovereignAgent
embeddingsovereignagent = EmbeddingSovereignAgent()
embeddingsovereignagent.reset_instance()
embeddingsovereignagent.config()
```

```python
# Using SubatomicTestingMixin
subatomictestingmixin = SubatomicTestingMixin()
```

```python
# Using RedisCacheMixin
rediscachemixin = RedisCacheMixin()
rediscachemixin.cache_get()
rediscachemixin.cache_set()
```

### Function Usage

```python
# Using _invoke_authorize_and_execute
result = _invoke_authorize_and_execute(execution_context, target_callable)
```

```python
# Using _make_execution_context
result = _make_execution_context(payload, target)
```

```python
# Using get_embedding_gateway
result = get_embedding_gateway()
```



---
**Generated**: 2026-03-26T09:39:03.866785
**Type**: api_reference
**Quality**: comprehensive
