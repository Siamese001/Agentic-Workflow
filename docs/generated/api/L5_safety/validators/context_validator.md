# API Documentation: context_validator

**Target Audience**: developers, api_users

# context_validator API Documentation

**File**: `context_validator.py`
**Classes**: 3
**Functions**: 16

## Classes

- **CacheEntry**
- **HealingPattern**
- **L4ContextManager**

## Functions

- **get_context_manager** -> L4ContextManager
- **is_expired** -> bool
- **__init__**
- **get_instance** -> L4ContextManager
- **reset_instance**
- **cache_get** -> Any | None
- **cache_set**
- **cache_clear**
- **recall_healing_pattern** -> dict[str, Any] | None
- **store_healing_pattern**
- **_compute_violation_signature** -> str
- **get_file_analysis** -> dict[str, Any] | None
- **set_file_analysis**
- **get_python_files** -> list[Path]
- **invalidate_python_files_cache**
- **get_stats** -> dict[str, Any]


## Class: CacheEntry

**Description**: Represents a cached analysis result.

### Methods

#### is_expired
**Parameters**: self
**Returns**: bool
**Description**: Check if cache entry has expired.



## Class: HealingPattern

**Description**: Represents a successful healing pattern.



## Class: L4ContextManager

**Description**: 
    Centralized state management for L5 agents.

    Singleton pattern ensures all agents share the same context.
    Enables cross-agent learning and eliminates redundant state.
    

### Methods

#### __init__
**Parameters**: self, project_root

#### get_instance
**Parameters**: cls, project_root
**Returns**: L4ContextManager
**Description**: Get or create singleton instance.

#### reset_instance
**Parameters**: cls
**Description**: Reset singleton (for testing only).

#### cache_get
**Parameters**: self, key, agent
**Returns**: Any | None
**Description**: 
        Retrieve cached value.

        Args:
            key: Cache key
            agent: Agent requesting the value

        Returns:
            Cached value or None if not found/expired
        

#### cache_set
**Parameters**: self, key, value, agent, ttl
**Description**: 
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
            agent: Agent storing the value
            ttl: Time-to-live in seconds (default 1 hour)
        

#### cache_clear
**Parameters**: self, agent
**Description**: 
        Clear cache entries.

        Args:
            agent: If specified, only clear entries from this agent
        

#### recall_healing_pattern
**Parameters**: self, violation, agent
**Returns**: dict[str, Any] | None
**Description**: 
        Recall a successful healing pattern.

        Enables cross-agent learning: If GravityLeakRepairAgent successfully
        fixed a similar violation, StructuralEngineerAgent can reuse that pattern.

        Args:
            violation: Violation characteristics
            agent: Agent requesting the pattern

        Returns:
            Healing pattern metadata or None
        

#### store_healing_pattern
**Parameters**: self, violation, result, agent
**Description**: 
        Store a successful healing pattern.

        Args:
            violation: Violation that was healed
            result: Healing result
            agent: Agent that performed the healing
        

#### _compute_violation_signature
**Parameters**: self, violation
**Returns**: str
**Description**: 
        Compute a unique signature for a violation.

        Similar violations should have the same signature to enable pattern reuse.
        

#### get_file_analysis
**Parameters**: self, file_path, analysis_type
**Returns**: dict[str, Any] | None
**Description**: 
        Get cached file analysis result.

        Args:
            file_path: Path to file
            analysis_type: Type of analysis (e.g., "complexity", "gravity")

        Returns:
            Cached analysis or None
        

#### set_file_analysis
**Parameters**: self, file_path, analysis_type, result
**Description**: 
        Cache file analysis result.

        Args:
            file_path: Path to file
            analysis_type: Type of analysis
            result: Analysis result
        

#### get_python_files
**Parameters**: self, max_age
**Returns**: list[Path]
**Description**: 
        Get list of Python files in project.

        Cached for performance - all agents share the same list.

        Args:
            max_age: Maximum age of cache in seconds (default 5 minutes)

        Returns:
            List of Python file paths
        

#### invalidate_python_files_cache
**Parameters**: self
**Description**: Force refresh of Python files list on next access.

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get statistics about context manager usage.



## Function: get_context_manager

**Parameters**: project_root
**Returns**: L4ContextManager
**Description**: 
    Factory function for L4ContextManager.

    Args:
        project_root: Path to project root

    Returns:
        Singleton L4ContextManager instance
    



## Function: is_expired

**Parameters**: self
**Returns**: bool
**Description**: Check if cache entry has expired.



## Function: __init__

**Parameters**: self, project_root


## Function: get_instance

**Parameters**: cls, project_root
**Returns**: L4ContextManager
**Description**: Get or create singleton instance.



## Function: reset_instance

**Parameters**: cls
**Description**: Reset singleton (for testing only).



## Function: cache_get

**Parameters**: self, key, agent
**Returns**: Any | None
**Description**: 
        Retrieve cached value.

        Args:
            key: Cache key
            agent: Agent requesting the value

        Returns:
            Cached value or None if not found/expired
        



## Function: cache_set

**Parameters**: self, key, value, agent, ttl
**Description**: 
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
            agent: Agent storing the value
            ttl: Time-to-live in seconds (default 1 hour)
        



## Function: cache_clear

**Parameters**: self, agent
**Description**: 
        Clear cache entries.

        Args:
            agent: If specified, only clear entries from this agent
        



## Function: recall_healing_pattern

**Parameters**: self, violation, agent
**Returns**: dict[str, Any] | None
**Description**: 
        Recall a successful healing pattern.

        Enables cross-agent learning: If GravityLeakRepairAgent successfully
        fixed a similar violation, StructuralEngineerAgent can reuse that pattern.

        Args:
            violation: Violation characteristics
            agent: Agent requesting the pattern

        Returns:
            Healing pattern metadata or None
        



## Function: store_healing_pattern

**Parameters**: self, violation, result, agent
**Description**: 
        Store a successful healing pattern.

        Args:
            violation: Violation that was healed
            result: Healing result
            agent: Agent that performed the healing
        



## Function: _compute_violation_signature

**Parameters**: self, violation
**Returns**: str
**Description**: 
        Compute a unique signature for a violation.

        Similar violations should have the same signature to enable pattern reuse.
        



## Function: get_file_analysis

**Parameters**: self, file_path, analysis_type
**Returns**: dict[str, Any] | None
**Description**: 
        Get cached file analysis result.

        Args:
            file_path: Path to file
            analysis_type: Type of analysis (e.g., "complexity", "gravity")

        Returns:
            Cached analysis or None
        



## Function: set_file_analysis

**Parameters**: self, file_path, analysis_type, result
**Description**: 
        Cache file analysis result.

        Args:
            file_path: Path to file
            analysis_type: Type of analysis
            result: Analysis result
        



## Function: get_python_files

**Parameters**: self, max_age
**Returns**: list[Path]
**Description**: 
        Get list of Python files in project.

        Cached for performance - all agents share the same list.

        Args:
            max_age: Maximum age of cache in seconds (default 5 minutes)

        Returns:
            List of Python file paths
        



## Function: invalidate_python_files_cache

**Parameters**: self
**Description**: Force refresh of Python files list on next access.



## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get statistics about context manager usage.



## Usage Examples

### Class Usage

```python
# Using CacheEntry
cacheentry = CacheEntry()
cacheentry.is_expired()
```

```python
# Using HealingPattern
healingpattern = HealingPattern()
```

```python
# Using L4ContextManager
l4contextmanager = L4ContextManager()
l4contextmanager.get_instance()
l4contextmanager.reset_instance()
```

### Function Usage

```python
# Using get_context_manager
result = get_context_manager(project_root)
```

```python
# Using is_expired
result = is_expired()
```

```python
# Using __init__
result = __init__(project_root)
```



---
**Generated**: 2026-03-26T09:39:05.768574
**Type**: api_reference
**Quality**: comprehensive
