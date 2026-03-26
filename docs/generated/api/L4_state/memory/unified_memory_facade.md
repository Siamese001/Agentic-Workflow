# API Documentation: unified_memory_facade

**Target Audience**: developers, api_users

# unified_memory_facade API Documentation

**File**: `unified_memory_facade.py`
**Classes**: 4
**Functions**: 19

## Classes

- **MemoryBackend** (inherits from Protocol)
- **RetrievalCandidate**
- **FacadeStats**
- **UnifiedMemoryFacade**

## Functions

- **get_memory_facade** -> UnifiedMemoryFacade
- **reset_memory_facade** -> None
- **read** -> Any | None
- **write** -> None
- **delete** -> None
- **is_high_confidence** -> bool
- **__init__** -> None
- **register_backend** -> None
- **retrieve_via** -> RetrievalCandidate
- **gated_retrieve** -> RetrievalCandidate | None
- **store** -> None
- **delete** -> None
- **store_embedding** -> None
- **get_embedding** -> Any | None
- **registered_backends** -> list[str]
- **stats** -> FacadeStats
- **read** -> Any | None
- **write** -> None
- **delete** -> None


## Class: MemoryBackend

**Description**: Protocol that all L4 memory backends must satisfy to plug into the facade.

**Inherits from**: Protocol

### Methods

#### read
**Parameters**: self, key
**Returns**: Any | None
**Description**: Ellipsis

#### write
**Parameters**: self, key, value
**Returns**: None
**Description**: Ellipsis

#### delete
**Parameters**: self, key
**Returns**: None
**Description**: Ellipsis



## Class: RetrievalCandidate

**Description**: Single result returned by the unified facade retrieve path.

### Methods

#### is_high_confidence
**Parameters**: self
**Returns**: bool



## Class: FacadeStats



## Class: UnifiedMemoryFacade

**Description**: Single interface over all L4 memory backends.

    Callers interact only with the facade; it dispatches to the
    appropriate backend based on key namespace or explicit routing.

    Backends are registered by name::

        facade = UnifiedMemoryFacade()
        facade.register_backend("semantic", semantic_cache_manager)
        facade.register_backend("blackboard", blackboard_store)
        facade.register_backend("case_library", case_library)

    Then all reads route through ``retrieve_via``::

        result = facade.retrieve_via("semantic", "campaign_context")
        if not result.is_high_confidence:
            raise LowConfidenceError(result)
        use(result.value)

    And all writes route through ``store``::

        facade.store("blackboard", "run_context", value)
    

### Methods

#### __init__
**Parameters**: self, confidence_threshold
**Returns**: None

#### register_backend
**Parameters**: self, name, backend
**Returns**: None
**Description**: Register a memory backend under ``name``.

#### retrieve_via
**Parameters**: self, backend_name, key, confidence
**Returns**: RetrievalCandidate
**Description**: Retrieve a value via a named backend.

        Emits ``retrieves_via`` + ``pulls_context`` ADG edges.
        

#### gated_retrieve
**Parameters**: self, backend_name, key, confidence
**Returns**: RetrievalCandidate | None
**Description**: Retrieve gated by confidence threshold.

        Emits ``gated_by_confidence`` ADG edge. Returns None if confidence
        is below the threshold.
        

#### store
**Parameters**: self, backend_name, key, value
**Returns**: None
**Description**: Write a value to a named backend.

        All L4 writes must route through this method.
        Emits writes_through ADG edge (P1/L4 write-through discipline).
        

#### delete
**Parameters**: self, backend_name, key
**Returns**: None
**Description**: Delete a value from a named backend.

#### store_embedding
**Parameters**: self, key, embedding
**Returns**: None
**Description**: Store an embedding for a given key.

        Emits ``stores_embedding`` + ``embeds_into`` ADG edges.
        

#### get_embedding
**Parameters**: self, key
**Returns**: Any | None
**Description**: Retrieve a stored embedding.

#### registered_backends
**Parameters**: self
**Returns**: list[str]
**Description**: Return all registered backend names.

#### stats
**Parameters**: self
**Returns**: FacadeStats

#### read
**Parameters**: self, key
**Returns**: Any | None
**Description**: MemoryBackend protocol compliance — reads from all backends in order.

#### write
**Parameters**: self, key, value
**Returns**: None
**Description**: MemoryBackend protocol compliance — writes to the first registered backend.

        Emits writes_through ADG edge (P1/L4 write-through discipline).
        

#### delete
**Parameters**: self, key
**Returns**: None
**Description**: MemoryBackend protocol compliance — delete from all backends.



## Function: get_memory_facade

**Parameters**: confidence_threshold
**Returns**: UnifiedMemoryFacade
**Description**: Return the process-level UnifiedMemoryFacade.



## Function: reset_memory_facade

**Returns**: None
**Description**: Reset the global facade (for testing).



## Function: read

**Parameters**: self, key
**Returns**: Any | None
**Description**: Ellipsis



## Function: write

**Parameters**: self, key, value
**Returns**: None
**Description**: Ellipsis



## Function: delete

**Parameters**: self, key
**Returns**: None
**Description**: Ellipsis



## Function: is_high_confidence

**Parameters**: self
**Returns**: bool


## Function: __init__

**Parameters**: self, confidence_threshold
**Returns**: None


## Function: register_backend

**Parameters**: self, name, backend
**Returns**: None
**Description**: Register a memory backend under ``name``.



## Function: retrieve_via

**Parameters**: self, backend_name, key, confidence
**Returns**: RetrievalCandidate
**Description**: Retrieve a value via a named backend.

        Emits ``retrieves_via`` + ``pulls_context`` ADG edges.
        



## Function: gated_retrieve

**Parameters**: self, backend_name, key, confidence
**Returns**: RetrievalCandidate | None
**Description**: Retrieve gated by confidence threshold.

        Emits ``gated_by_confidence`` ADG edge. Returns None if confidence
        is below the threshold.
        



## Function: store

**Parameters**: self, backend_name, key, value
**Returns**: None
**Description**: Write a value to a named backend.

        All L4 writes must route through this method.
        Emits writes_through ADG edge (P1/L4 write-through discipline).
        



## Function: delete

**Parameters**: self, backend_name, key
**Returns**: None
**Description**: Delete a value from a named backend.



## Function: store_embedding

**Parameters**: self, key, embedding
**Returns**: None
**Description**: Store an embedding for a given key.

        Emits ``stores_embedding`` + ``embeds_into`` ADG edges.
        



## Function: get_embedding

**Parameters**: self, key
**Returns**: Any | None
**Description**: Retrieve a stored embedding.



## Function: registered_backends

**Parameters**: self
**Returns**: list[str]
**Description**: Return all registered backend names.



## Function: stats

**Parameters**: self
**Returns**: FacadeStats


## Function: read

**Parameters**: self, key
**Returns**: Any | None
**Description**: MemoryBackend protocol compliance — reads from all backends in order.



## Function: write

**Parameters**: self, key, value
**Returns**: None
**Description**: MemoryBackend protocol compliance — writes to the first registered backend.

        Emits writes_through ADG edge (P1/L4 write-through discipline).
        



## Function: delete

**Parameters**: self, key
**Returns**: None
**Description**: MemoryBackend protocol compliance — delete from all backends.



## Usage Examples

### Class Usage

```python
# Using MemoryBackend
memorybackend = MemoryBackend()
memorybackend.read()
memorybackend.write()
```

```python
# Using RetrievalCandidate
retrievalcandidate = RetrievalCandidate()
retrievalcandidate.is_high_confidence()
```

```python
# Using FacadeStats
facadestats = FacadeStats()
```

### Function Usage

```python
# Using get_memory_facade
result = get_memory_facade(confidence_threshold)
```

```python
# Using reset_memory_facade
result = reset_memory_facade()
```

```python
# Using read
result = read(key)
```



---
**Generated**: 2026-03-26T09:39:04.602881
**Type**: api_reference
**Quality**: comprehensive
