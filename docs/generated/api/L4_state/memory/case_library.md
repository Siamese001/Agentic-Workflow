# API Documentation: case_library

**Target Audience**: developers, api_users

# case_library API Documentation

**File**: `case_library.py`
**Classes**: 1
**Functions**: 17

## Classes

- **CaseLibrary**

## Functions

- **_get_case_memory_types**
- **_entity_name** -> str
- **_policy_entity_name** -> str
- **_trace_entity_name** -> str
- **_plan_entity_name** -> str
- **_truncate** -> str
- **__init__** -> None
- **store** -> bool
- **search** -> list[dict[str, Any]]
- **search_by_policy** -> list[dict[str, Any]]
- **search_by_trace** -> list[dict[str, Any]]
- **search_by_adg_node** -> list[dict[str, Any]]
- **_build_observations** -> list[str]
- **_link_bundle** -> None
- **_link_adg_nodes** -> None
- **_link_type_specific** -> None
- **get_stats** -> dict[str, Any]


## Class: CaseLibrary

**Description**: ADG-keyed Memory MCP durable case-law archive.

    All five bundle types are stored as structured entities in the Memory MCP
    knowledge graph.  The library builds:

    * One entity per bundle (keyed by ``ADG::Case::<type>::<hash_prefix>``).
    * Observations: artifact_type, trace_id, policy_hash, outcome label,
      replay status, ADG node names, and a compact canonical summary.
    * Relations: ``sourced_from_adg_node``, ``governed_by_policy``,
      ``lineage_of``, and bundle-type-specific relations.

    Usage
    -----
    .. code-block:: python

        lib = CaseLibrary()
        lib.store(case_record)
        results = lib.search("healer timeout failure CASE_RECORD")
    

### Methods

#### __init__
**Parameters**: self, bridge
**Returns**: None

#### store
**Parameters**: self, bundle
**Returns**: bool
**Description**: Store a case bundle as a Memory MCP entity with ADG-keyed relations.

        Returns True if the entity was written (or already existed), False on error.
        

#### search
**Parameters**: self, query
**Returns**: list[dict[str, Any]]
**Description**: Search the case library by free-text query.

        Returns a list of raw MCP graph node dicts.  Empty list on miss or error.
        

#### search_by_policy
**Parameters**: self, policy_hash
**Returns**: list[dict[str, Any]]
**Description**: Find all bundles governed by a specific policy hash.

#### search_by_trace
**Parameters**: self, trace_id
**Returns**: list[dict[str, Any]]
**Description**: Find all bundles linked to a specific execution trace.

#### search_by_adg_node
**Parameters**: self, adg_entity_name
**Returns**: list[dict[str, Any]]
**Description**: Find all bundles sourced from a specific ADG component node.

#### _build_observations
**Parameters**: self, bundle, stable_hash
**Returns**: list[str]
**Description**: Build the observation list stored on the Memory MCP entity.

#### _link_bundle
**Parameters**: self, bundle, entity_name, stable_hash
**Returns**: None
**Description**: Create all ADG-keyed relations for a bundle entity.

#### _link_adg_nodes
**Parameters**: self, bundle, entity_name
**Returns**: None
**Description**: Create ``sourced_from_adg_node`` relations for each ADG node ref.

#### _link_type_specific
**Parameters**: self, bundle, entity_name
**Returns**: None
**Description**: Create bundle-type-specific relations.

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return bridge stats for observability.



## Function: _get_case_memory_types



## Function: _entity_name

**Parameters**: artifact_type, stable_hash
**Returns**: str
**Description**: Build a canonical ADG entity name for a case bundle.

    Schema: ``ADG::Case::<ARTIFACT_TYPE>::<first_16_hex_chars>``
    



## Function: _policy_entity_name

**Parameters**: policy_hash
**Returns**: str


## Function: _trace_entity_name

**Parameters**: trace_id
**Returns**: str


## Function: _plan_entity_name

**Parameters**: plan_hash
**Returns**: str


## Function: _truncate

**Parameters**: s, limit
**Returns**: str


## Function: __init__

**Parameters**: self, bridge
**Returns**: None


## Function: store

**Parameters**: self, bundle
**Returns**: bool
**Description**: Store a case bundle as a Memory MCP entity with ADG-keyed relations.

        Returns True if the entity was written (or already existed), False on error.
        



## Function: search

**Parameters**: self, query
**Returns**: list[dict[str, Any]]
**Description**: Search the case library by free-text query.

        Returns a list of raw MCP graph node dicts.  Empty list on miss or error.
        



## Function: search_by_policy

**Parameters**: self, policy_hash
**Returns**: list[dict[str, Any]]
**Description**: Find all bundles governed by a specific policy hash.



## Function: search_by_trace

**Parameters**: self, trace_id
**Returns**: list[dict[str, Any]]
**Description**: Find all bundles linked to a specific execution trace.



## Function: search_by_adg_node

**Parameters**: self, adg_entity_name
**Returns**: list[dict[str, Any]]
**Description**: Find all bundles sourced from a specific ADG component node.



## Function: _build_observations

**Parameters**: self, bundle, stable_hash
**Returns**: list[str]
**Description**: Build the observation list stored on the Memory MCP entity.



## Function: _link_bundle

**Parameters**: self, bundle, entity_name, stable_hash
**Returns**: None
**Description**: Create all ADG-keyed relations for a bundle entity.



## Function: _link_adg_nodes

**Parameters**: self, bundle, entity_name
**Returns**: None
**Description**: Create ``sourced_from_adg_node`` relations for each ADG node ref.



## Function: _link_type_specific

**Parameters**: self, bundle, entity_name
**Returns**: None
**Description**: Create bundle-type-specific relations.



## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return bridge stats for observability.



## Usage Examples

### Class Usage

```python
# Using CaseLibrary
caselibrary = CaseLibrary()
caselibrary.store()
caselibrary.search()
```

### Function Usage

```python
# Using _get_case_memory_types
result = _get_case_memory_types()
```

```python
# Using _entity_name
result = _entity_name(artifact_type, stable_hash)
```

```python
# Using _policy_entity_name
result = _policy_entity_name(policy_hash)
```



---
**Generated**: 2026-03-26T09:39:04.569361
**Type**: api_reference
**Quality**: comprehensive
