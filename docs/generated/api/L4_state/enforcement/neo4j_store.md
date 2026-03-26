# API Documentation: neo4j_store

**Target Audience**: developers, api_users

# neo4j_store API Documentation

**File**: `neo4j_store.py`
**Classes**: 1
**Functions**: 7

## Classes

- **Neo4jGraphStore**

## Functions

- **__init__** -> None
- **close** -> None
- **run** -> list[Any]
- **upsert_entity** -> None
- **upsert_relation** -> None
- **update_relation_invalidity** -> None
- **query_factual_temporal** -> list[Any]


## Class: Neo4jGraphStore

**Description**: 
    L4 State: Neo4j-backed graph store for entities, temporal relations, and queries.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### close
**Parameters**: self
**Returns**: None
**Description**: TODO: Add docstring.

#### run
**Parameters**: self, cypher, params
**Returns**: list[Any]
**Description**: TODO: Add docstring.

#### upsert_entity
**Parameters**: self, entity_id, etype, name, metadata
**Returns**: None
**Description**: 
        MERGE an Entity node with basic fields + arbitrary metadata.
        

#### upsert_relation
**Parameters**: self, rel_id, subject_id, predicate, object_id, valid_at, invalid_at, attrs
**Returns**: None
**Description**: 
        MERGE a RELATION edge between two Entity nodes with temporal validity.
        

#### update_relation_invalidity
**Parameters**: self, rel_id, invalid_at, invalidated_by
**Returns**: None
**Description**: 
        Update invalidation fields for a RELATION (used by InvalidationAgent).
        

#### query_factual_temporal
**Parameters**: self, entity_name, predicate, start, end
**Returns**: list[Any]
**Description**: 
        Query temporal facts: subject -[RELATION]-> object filtered on time interval.
        



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: close

**Parameters**: self
**Returns**: None
**Description**: TODO: Add docstring.



## Function: run

**Parameters**: self, cypher, params
**Returns**: list[Any]
**Description**: TODO: Add docstring.



## Function: upsert_entity

**Parameters**: self, entity_id, etype, name, metadata
**Returns**: None
**Description**: 
        MERGE an Entity node with basic fields + arbitrary metadata.
        



## Function: upsert_relation

**Parameters**: self, rel_id, subject_id, predicate, object_id, valid_at, invalid_at, attrs
**Returns**: None
**Description**: 
        MERGE a RELATION edge between two Entity nodes with temporal validity.
        



## Function: update_relation_invalidity

**Parameters**: self, rel_id, invalid_at, invalidated_by
**Returns**: None
**Description**: 
        Update invalidation fields for a RELATION (used by InvalidationAgent).
        



## Function: query_factual_temporal

**Parameters**: self, entity_name, predicate, start, end
**Returns**: list[Any]
**Description**: 
        Query temporal facts: subject -[RELATION]-> object filtered on time interval.
        



## Usage Examples

### Class Usage

```python
# Using Neo4jGraphStore
neo4jgraphstore = Neo4jGraphStore()
neo4jgraphstore.close()
neo4jgraphstore.run()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using close
result = close()
```

```python
# Using run
result = run(cypher, params)
```



---
**Generated**: 2026-03-26T09:39:04.510239
**Type**: api_reference
**Quality**: comprehensive
