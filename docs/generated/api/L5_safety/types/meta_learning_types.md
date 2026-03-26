# API Documentation: meta_learning_types

**Target Audience**: developers, api_users

# meta_learning_types API Documentation

**File**: `meta_learning_types.py`
**Classes**: 3
**Functions**: 8

## Classes

- **LearningContext**
- **LearningResult**
- **MetaLearningProtocol** (inherits from ABC)

## Functions

- **__post_init__** -> None
- **to_cache_key** -> str
- **__post_init__** -> None
- **recall_or_execute** -> LearningResult
- **learn_experience** -> bool
- **invalidate_cache** -> int
- **get_cache_stats** -> dict[str, Any]
- **is_available** -> bool


## Class: LearningContext

**Description**: Context for meta-learning operations.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_cache_key
**Parameters**: self
**Returns**: str
**Description**: Generate cache key from context.



## Class: LearningResult

**Description**: Result of meta-learning operation.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: MetaLearningProtocol

**Description**: Protocol for meta-learning implementations.

    Implementations must provide recall-or-execute pattern:
    1. Check cache for previous successful execution
    2. If found and confident, return cached result
    3. If not found, execute and cache successful results
    

**Inherits from**: ABC

### Methods

#### recall_or_execute
**Parameters**: self, context, execution_fn
**Returns**: LearningResult
**Description**: Recall from cache or execute and learn.

        Args:
            context: Learning context with cache key info
            execution_fn: Function to execute if cache miss

        Returns:
            LearningResult with result and cache status
        

#### learn_experience
**Parameters**: self, context, result, success
**Returns**: bool
**Description**: Store learning experience for future recall.

        Args:
            context: Learning context
            result: Result to cache
            success: Whether execution was successful

        Returns:
            True if learning was stored successfully
        

#### invalidate_cache
**Parameters**: self, context_key, agent_name
**Returns**: int
**Description**: Invalidate cached learnings.

        Args:
            context_key: Specific key to invalidate (None for all)
            agent_name: Invalidate all for specific agent

        Returns:
            Number of entries invalidated
        

#### get_cache_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get cache statistics.

#### is_available
**Parameters**: self
**Returns**: bool
**Description**: Check if meta-learning system is available.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_cache_key

**Parameters**: self
**Returns**: str
**Description**: Generate cache key from context.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: recall_or_execute

**Parameters**: self, context, execution_fn
**Returns**: LearningResult
**Description**: Recall from cache or execute and learn.

        Args:
            context: Learning context with cache key info
            execution_fn: Function to execute if cache miss

        Returns:
            LearningResult with result and cache status
        



## Function: learn_experience

**Parameters**: self, context, result, success
**Returns**: bool
**Description**: Store learning experience for future recall.

        Args:
            context: Learning context
            result: Result to cache
            success: Whether execution was successful

        Returns:
            True if learning was stored successfully
        



## Function: invalidate_cache

**Parameters**: self, context_key, agent_name
**Returns**: int
**Description**: Invalidate cached learnings.

        Args:
            context_key: Specific key to invalidate (None for all)
            agent_name: Invalidate all for specific agent

        Returns:
            Number of entries invalidated
        



## Function: get_cache_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get cache statistics.



## Function: is_available

**Parameters**: self
**Returns**: bool
**Description**: Check if meta-learning system is available.



## Usage Examples

### Class Usage

```python
# Using LearningContext
learningcontext = LearningContext()
learningcontext.to_cache_key()
```

```python
# Using LearningResult
learningresult = LearningResult()
```

```python
# Using MetaLearningProtocol
metalearningprotocol = MetaLearningProtocol()
metalearningprotocol.recall_or_execute()
metalearningprotocol.learn_experience()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using to_cache_key
result = to_cache_key()
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:05.537910
**Type**: api_reference
**Quality**: comprehensive
