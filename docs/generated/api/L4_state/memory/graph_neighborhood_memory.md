# API Documentation: graph_neighborhood_memory

**Target Audience**: developers, api_users

# graph_neighborhood_memory API Documentation

**File**: `graph_neighborhood_memory.py`
**Classes**: 2
**Functions**: 14

## Classes

- **MemoryCard**
- **GraphNeighborhoodMemory**

## Functions

- **_get_determinism_fns**
- **_truncate** -> str
- **to_dict** -> dict[str, object]
- **stable_hash** -> str
- **to_observations** -> list[str]
- **__init__** -> None
- **upsert_card** -> bool
- **record_failure** -> bool
- **record_healer_success** -> bool
- **record_policy_touchpoint** -> bool
- **search** -> list[dict[str, Any]]
- **get_card** -> MemoryCard | None
- **list_cached_entities** -> list[str]
- **get_stats** -> dict[str, Any]


## Class: MemoryCard

**Description**: In-process representation of an ADG node memory card.

    Attributes
    ----------
    adg_entity_name:
        Canonical ADG entity name (e.g. ``ADG::Module::agentic_core/L2_execution/...``).
    layer:
        Layer label (e.g. ``L0``, ``L4``, ``L_SL``).
    territory:
        Sovereign territory label (e.g. ``L4_state``, ``L5_safety``).
    relation_families:
        Set of ADG relation families observed at this node
        (e.g. ``{"routing", "healing", "guardrail"}``).
    common_failure_families:
        Set of stable failure category strings seen at this node.
    common_healers:
        Set of healer_id strings that successfully resolved issues at this node.
    policy_touchpoints:
        Set of policy_hash strings that governed decisions at this node.
    replay_sensitive:
        True if this node participates in deterministic replay paths.
    retrieval_sensitive:
        True if this node is on a RAG/retrieval path (completeness-relevant).
    timestamp_utc:
        Unix timestamp of the most recent card update (caller-supplied).
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, object]

#### stable_hash
**Parameters**: self
**Returns**: str

#### to_observations
**Parameters**: self
**Returns**: list[str]
**Description**: Build the observation list stored on the Memory MCP entity.



## Class: GraphNeighborhoodMemory

**Description**: Persists per-ADG-node memory cards in Memory MCP.

    Each call to ``upsert_card`` stores (or updates via new observations) a
    memory card entity for the given ADG node.  The in-process ``_cards`` dict
    acts as a write-through cache so repeated upserts within the same process
    avoid redundant bridge calls for unchanged cards.

    Usage
    -----
    .. code-block:: python

        mem = GraphNeighborhoodMemory()

        card = MemoryCard(
            adg_entity_name="ADG::Module::agentic_core/L2_execution/healers/base.py",
            layer="L2",
            territory="L2_execution",
            relation_families={"healing", "guardrail"},
            common_failure_families={"IMPORT_ERROR", "POLICY_VIOLATION"},
            common_healers={"AutoRepairHealer"},
            policy_touchpoints={"abc123..."},
            replay_sensitive=True,
            timestamp_utc=1700000000,
        )
        mem.upsert_card(card)

        results = mem.search("L2 healing POLICY_VIOLATION")
    

### Methods

#### __init__
**Parameters**: self, bridge
**Returns**: None

#### upsert_card
**Parameters**: self, card
**Returns**: bool
**Description**: Store or update a memory card for an ADG node.

        If a card for this entity was already stored in this process with an
        identical ``stable_hash``, the write is skipped (no-op).

        Returns True on successful write or no-op, False on bridge error.
        

#### record_failure
**Parameters**: self, adg_entity_name, failure_family, layer, timestamp_utc, territory
**Returns**: bool
**Description**: Convenience: add a failure family observation to an existing card.

        If no card exists in process yet for this entity, creates a minimal one.
        

#### record_healer_success
**Parameters**: self, adg_entity_name, healer_id, layer, timestamp_utc, territory
**Returns**: bool
**Description**: Convenience: add a successful healer observation to an existing card.

#### record_policy_touchpoint
**Parameters**: self, adg_entity_name, policy_hash, layer, timestamp_utc, territory
**Returns**: bool
**Description**: Convenience: add a policy hash touchpoint to an existing card.

#### search
**Parameters**: self, query
**Returns**: list[dict[str, Any]]
**Description**: Search the neighborhood memory by free-text query.

        Returns raw MCP graph node dicts.
        

#### get_card
**Parameters**: self, adg_entity_name
**Returns**: MemoryCard | None
**Description**: Return the in-process cached card for an entity (if any).

#### list_cached_entities
**Parameters**: self
**Returns**: list[str]
**Description**: Return list of ADG entity names with in-process cards.

#### get_stats
**Parameters**: self
**Returns**: dict[str, Any]



## Function: _get_determinism_fns



## Function: _truncate

**Parameters**: s, limit
**Returns**: str


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, object]


## Function: stable_hash

**Parameters**: self
**Returns**: str


## Function: to_observations

**Parameters**: self
**Returns**: list[str]
**Description**: Build the observation list stored on the Memory MCP entity.



## Function: __init__

**Parameters**: self, bridge
**Returns**: None


## Function: upsert_card

**Parameters**: self, card
**Returns**: bool
**Description**: Store or update a memory card for an ADG node.

        If a card for this entity was already stored in this process with an
        identical ``stable_hash``, the write is skipped (no-op).

        Returns True on successful write or no-op, False on bridge error.
        



## Function: record_failure

**Parameters**: self, adg_entity_name, failure_family, layer, timestamp_utc, territory
**Returns**: bool
**Description**: Convenience: add a failure family observation to an existing card.

        If no card exists in process yet for this entity, creates a minimal one.
        



## Function: record_healer_success

**Parameters**: self, adg_entity_name, healer_id, layer, timestamp_utc, territory
**Returns**: bool
**Description**: Convenience: add a successful healer observation to an existing card.



## Function: record_policy_touchpoint

**Parameters**: self, adg_entity_name, policy_hash, layer, timestamp_utc, territory
**Returns**: bool
**Description**: Convenience: add a policy hash touchpoint to an existing card.



## Function: search

**Parameters**: self, query
**Returns**: list[dict[str, Any]]
**Description**: Search the neighborhood memory by free-text query.

        Returns raw MCP graph node dicts.
        



## Function: get_card

**Parameters**: self, adg_entity_name
**Returns**: MemoryCard | None
**Description**: Return the in-process cached card for an entity (if any).



## Function: list_cached_entities

**Parameters**: self
**Returns**: list[str]
**Description**: Return list of ADG entity names with in-process cards.



## Function: get_stats

**Parameters**: self
**Returns**: dict[str, Any]


## Usage Examples

### Class Usage

```python
# Using MemoryCard
memorycard = MemoryCard()
memorycard.to_dict()
memorycard.stable_hash()
```

```python
# Using GraphNeighborhoodMemory
graphneighborhoodmemory = GraphNeighborhoodMemory()
graphneighborhoodmemory.upsert_card()
graphneighborhoodmemory.record_failure()
```

### Function Usage

```python
# Using _get_determinism_fns
result = _get_determinism_fns()
```

```python
# Using _truncate
result = _truncate(s, limit)
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:04.571988
**Type**: api_reference
**Quality**: comprehensive
