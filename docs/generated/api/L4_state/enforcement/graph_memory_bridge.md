# API Documentation: graph_memory_bridge

**Target Audience**: developers, api_users

# graph_memory_bridge API Documentation

**File**: `graph_memory_bridge.py`
**Classes**: 3
**Functions**: 20

## Classes

- **EntityDefinition**
- **RelationDefinition**
- **GraphMemoryBridge**

## Functions

- **__init__**
- **__enter__**
- **__exit__**
- **cleanup** -> None
- **validate_state_isolation** -> dict[str, Any]
- **create_isolated** -> GraphMemoryBridge
- **_init_mcp** -> None
- **_call_mcp_create_entities** -> Any
- **_call_mcp_create_relations** -> Any
- **_call_mcp_add_observations** -> Any
- **_call_mcp_search_nodes** -> Any
- **set_mcp_functions** -> None
- **is_available** -> bool
- **_safe_call** -> Any | None
- **create_agent_entity** -> bool
- **create_mastered_task_relation** -> bool
- **create_relation** -> bool
- **add_observation** -> bool
- **search_entities** -> list[dict[str, Any]]
- **get_statistics** -> dict[str, Any]


## Class: EntityDefinition

**Description**: Definition for creating an entity in the Knowledge Graph.



## Class: RelationDefinition

**Description**: Definition for creating a relation in the Knowledge Graph.



## Class: GraphMemoryBridge

**Description**: 
    [PHASE 21] Bridge to Memory MCP Knowledge Graph.

    Provides a high-level interface for:
    1. Entity creation (agents register themselves on init)
    2. Relation creation (MASTERED_TASK when memory promoted)
    3. Observation storage (synthesized truths)
    4. Graph queries (search for related entities)

    Resilient Mode: If MCP is unavailable, logs warning but doesn't crash.
    All operations are thread-safe.

    Usage:
        bridge = GraphMemoryBridge()
        bridge.create_agent_entity("GovernorAgent")
        bridge.create_mastered_task_relation("GovernorAgent", "task_hash_123")

    For testing with isolation:
        with GraphMemoryBridge() as bridge:
            bridge.create_agent_entity("TestAgent")
            # Automatically cleaned up when exiting context
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize the Graph Memory Bridge with isolated state.

#### __enter__
**Parameters**: self
**Description**: Context manager entry - return self for use in 'with' statement.

#### __exit__
**Parameters**: self, exc_type, exc_val, exc_tb
**Description**: Context manager exit - automatically cleanup when leaving context.

#### cleanup
**Parameters**: self
**Returns**: None
**Description**: Explicit cleanup method for test isolation.

        Resets all instance state to ensure clean test isolation.
        Can be called multiple times safely.
        

#### validate_state_isolation
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Validate that state is properly isolated.

        Returns:
            Dictionary with isolation validation results.
        

#### create_isolated
**Parameters**: cls
**Returns**: GraphMemoryBridge
**Description**: Create a completely isolated instance for testing.

        Returns:
            New GraphMemoryBridge instance with guaranteed isolation.
        

#### _init_mcp
**Parameters**: self
**Returns**: None
**Description**: 
        Detect live Memory MCP availability.

        Attempts to import the mcp11 module exposed by the Windsurf Memory MCP
        server.  Falls back to in-process ADGMCPClient stub when unavailable
        (CI / offline environments).
        

#### _call_mcp_create_entities
**Parameters**: self, entities
**Returns**: Any
**Description**: Call mcp11_create_entities; falls back to injected fn, SQLite store, or in-memory stub.

#### _call_mcp_create_relations
**Parameters**: self, relations
**Returns**: Any
**Description**: Call mcp11_create_relations; falls back to injected fn, SQLite store, or None.

#### _call_mcp_add_observations
**Parameters**: self, observations
**Returns**: Any
**Description**: Call mcp11_add_observations; falls back to injected fn, SQLite store, or None.

#### _call_mcp_search_nodes
**Parameters**: self, query
**Returns**: Any
**Description**: Call mcp11_search_nodes; falls back to injected fn, SQLite store, or empty list.

#### set_mcp_functions
**Parameters**: self, create_entities, create_relations, add_observations, search_nodes
**Returns**: None
**Description**: 
        Inject MCP tool functions (for testing or custom implementations).

        Args:
            create_entities: Function matching mcp7_create_entities signature
            create_relations: Function matching mcp7_create_relations signature
            add_observations: Function matching mcp7_add_observations signature
            search_nodes: Function matching mcp7_search_nodes signature
        

#### is_available
**Parameters**: self
**Returns**: bool
**Description**: Check if the Graph Memory Bridge is available.

#### _safe_call
**Parameters**: self, operation, fn
**Returns**: Any | None
**Description**: 
        Safely execute an MCP operation with error handling.

        Args:
            operation: Name of the operation for logging
            fn: The function to call
            *args, **kwargs: Arguments to pass to the function

        Returns:
            Result of the operation or None if failed/unavailable
        

#### create_agent_entity
**Parameters**: self, agent_name, agent_type, observations
**Returns**: bool
**Description**: 
        Create an agent entity in the Knowledge Graph.

        Called automatically when an agent with MetaLearningMixin is instantiated.
        Idempotent: Will not create duplicate entities.

        Args:
            agent_name: Name of the agent (typically class name)
            agent_type: Type of entity (default: "Agent")
            observations: Initial observations about the agent

        Returns:
            True if created (or already exists), False if failed
        

#### create_mastered_task_relation
**Parameters**: self, agent_name, task_description, feedback_score
**Returns**: bool
**Description**: 
        Create a MASTERED_TASK relation when memory is promoted to Long-Term DNA.

        This is called when a memory's feedback_score >= 0.8 (promotion threshold).

        Args:
            agent_name: Name of the agent that mastered the task
            task_description: Description of the task (will be hashed)
            feedback_score: The feedback score that triggered promotion

        Returns:
            True if relation created, False if failed
        

#### create_relation
**Parameters**: self, from_entity, to_entity, relation_type
**Returns**: bool
**Description**: 
        Create a generic relation between two entities.

        Args:
            from_entity: Source entity name
            to_entity: Target entity name
            relation_type: Type of relation

        Returns:
            True if created, False if failed
        

#### add_observation
**Parameters**: self, entity_name, observation
**Returns**: bool
**Description**: 
        Add an observation to an existing entity.

        Enforces 4KB limit on observation size to prevent graph bloat.

        Args:
            entity_name: Name of the entity
            observation: The observation to add

        Returns:
            True if added, False if failed
        

#### search_entities
**Parameters**: self, query
**Returns**: list[dict[str, Any]]
**Description**: 
        Search for entities in the Knowledge Graph.

        Args:
            query: Search query string

        Returns:
            List of matching entities (empty if failed or unavailable)
        

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get bridge statistics.



## Function: __init__

**Parameters**: self
**Description**: Initialize the Graph Memory Bridge with isolated state.



## Function: __enter__

**Parameters**: self
**Description**: Context manager entry - return self for use in 'with' statement.



## Function: __exit__

**Parameters**: self, exc_type, exc_val, exc_tb
**Description**: Context manager exit - automatically cleanup when leaving context.



## Function: cleanup

**Parameters**: self
**Returns**: None
**Description**: Explicit cleanup method for test isolation.

        Resets all instance state to ensure clean test isolation.
        Can be called multiple times safely.
        



## Function: validate_state_isolation

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Validate that state is properly isolated.

        Returns:
            Dictionary with isolation validation results.
        



## Function: create_isolated

**Parameters**: cls
**Returns**: GraphMemoryBridge
**Description**: Create a completely isolated instance for testing.

        Returns:
            New GraphMemoryBridge instance with guaranteed isolation.
        



## Function: _init_mcp

**Parameters**: self
**Returns**: None
**Description**: 
        Detect live Memory MCP availability.

        Attempts to import the mcp11 module exposed by the Windsurf Memory MCP
        server.  Falls back to in-process ADGMCPClient stub when unavailable
        (CI / offline environments).
        



## Function: _call_mcp_create_entities

**Parameters**: self, entities
**Returns**: Any
**Description**: Call mcp11_create_entities; falls back to injected fn, SQLite store, or in-memory stub.



## Function: _call_mcp_create_relations

**Parameters**: self, relations
**Returns**: Any
**Description**: Call mcp11_create_relations; falls back to injected fn, SQLite store, or None.



## Function: _call_mcp_add_observations

**Parameters**: self, observations
**Returns**: Any
**Description**: Call mcp11_add_observations; falls back to injected fn, SQLite store, or None.



## Function: _call_mcp_search_nodes

**Parameters**: self, query
**Returns**: Any
**Description**: Call mcp11_search_nodes; falls back to injected fn, SQLite store, or empty list.



## Function: set_mcp_functions

**Parameters**: self, create_entities, create_relations, add_observations, search_nodes
**Returns**: None
**Description**: 
        Inject MCP tool functions (for testing or custom implementations).

        Args:
            create_entities: Function matching mcp7_create_entities signature
            create_relations: Function matching mcp7_create_relations signature
            add_observations: Function matching mcp7_add_observations signature
            search_nodes: Function matching mcp7_search_nodes signature
        



## Function: is_available

**Parameters**: self
**Returns**: bool
**Description**: Check if the Graph Memory Bridge is available.



## Function: _safe_call

**Parameters**: self, operation, fn
**Returns**: Any | None
**Description**: 
        Safely execute an MCP operation with error handling.

        Args:
            operation: Name of the operation for logging
            fn: The function to call
            *args, **kwargs: Arguments to pass to the function

        Returns:
            Result of the operation or None if failed/unavailable
        



## Function: create_agent_entity

**Parameters**: self, agent_name, agent_type, observations
**Returns**: bool
**Description**: 
        Create an agent entity in the Knowledge Graph.

        Called automatically when an agent with MetaLearningMixin is instantiated.
        Idempotent: Will not create duplicate entities.

        Args:
            agent_name: Name of the agent (typically class name)
            agent_type: Type of entity (default: "Agent")
            observations: Initial observations about the agent

        Returns:
            True if created (or already exists), False if failed
        



## Function: create_mastered_task_relation

**Parameters**: self, agent_name, task_description, feedback_score
**Returns**: bool
**Description**: 
        Create a MASTERED_TASK relation when memory is promoted to Long-Term DNA.

        This is called when a memory's feedback_score >= 0.8 (promotion threshold).

        Args:
            agent_name: Name of the agent that mastered the task
            task_description: Description of the task (will be hashed)
            feedback_score: The feedback score that triggered promotion

        Returns:
            True if relation created, False if failed
        



## Function: create_relation

**Parameters**: self, from_entity, to_entity, relation_type
**Returns**: bool
**Description**: 
        Create a generic relation between two entities.

        Args:
            from_entity: Source entity name
            to_entity: Target entity name
            relation_type: Type of relation

        Returns:
            True if created, False if failed
        



## Function: add_observation

**Parameters**: self, entity_name, observation
**Returns**: bool
**Description**: 
        Add an observation to an existing entity.

        Enforces 4KB limit on observation size to prevent graph bloat.

        Args:
            entity_name: Name of the entity
            observation: The observation to add

        Returns:
            True if added, False if failed
        



## Function: search_entities

**Parameters**: self, query
**Returns**: list[dict[str, Any]]
**Description**: 
        Search for entities in the Knowledge Graph.

        Args:
            query: Search query string

        Returns:
            List of matching entities (empty if failed or unavailable)
        



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get bridge statistics.



## Usage Examples

### Class Usage

```python
# Using EntityDefinition
entitydefinition = EntityDefinition()
```

```python
# Using RelationDefinition
relationdefinition = RelationDefinition()
```

```python
# Using GraphMemoryBridge
graphmemorybridge = GraphMemoryBridge()
graphmemorybridge.cleanup()
graphmemorybridge.validate_state_isolation()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using __enter__
result = __enter__()
```

```python
# Using __exit__
result = __exit__(exc_type, exc_val)
```



---
**Generated**: 2026-03-26T09:39:04.499179
**Type**: api_reference
**Quality**: comprehensive
