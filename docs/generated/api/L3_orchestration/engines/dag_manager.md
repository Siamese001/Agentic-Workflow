# API Documentation: dag_manager

**Target Audience**: developers, api_users

# dag_manager API Documentation

**File**: `dag_manager.py`
**Classes**: 4
**Functions**: 11

## Classes

- **DAGManager** (inherits from HealerMixin, MCPHardenedMixin, L3SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin)
- **HealerMixin**
- **MCPHardenedMixin**
- **L3SubatomicTestingMixin**

## Functions

- **__init__** -> None
- **register_function** -> None
- **add_node** -> None
- **request_mutation** -> MutationResult
- **create_mutation_request** -> DAGMutation
- **get_next_node** -> SubatomicHop | None
- **pause_node** -> bool
- **resume_node** -> bool
- **get_graph_stats** -> Dict[str, Any]
- **visualize_graph** -> Dict[str, Any]
- **heal_repository** -> Dict[str, int]


## Class: DAGManager

**Description**: Manages the dynamic DAG with mutation capabilities.

    HARDENED: Redis caching + Pinecone vector support for DAG structure caching.
    

**Inherits from**: HealerMixin, MCPHardenedMixin, L3SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize the DAG Manager.

        Args:
            config: Optional configuration
        

#### register_function
**Parameters**: self, name, function
**Returns**: None
**Description**: Register a hop function that can be spawned.

        Args:
            name: Function name
            function: The function to register
        

#### add_node
**Parameters**: self, hop, predecessors
**Returns**: None
**Description**: Add a node to the DAG.

        Args:
            hop: The SubatomicHop to add
            predecessors: Optional list of predecessor node IDs
        

#### request_mutation
**Parameters**: self, mutation
**Returns**: MutationResult
**Description**: Request a mutation to the DAG.

        Args:
            mutation: The mutation to request

        Returns:
            Result of the mutation
        

#### create_mutation_request
**Parameters**: self, action, target_hop_id, hop_function, reason, requester_hop_id
**Returns**: DAGMutation
**Description**: Create a mutation request.

        Args:
            action: Type of mutation
            target_hop_id: Target node ID
            hop_function: Function name for new node
            reason: Reason for mutation
            requester_hop_id: ID of requesting node
            **kwargs: Additional hop spec parameters

        Returns:
            DAGMutation object
        

#### get_next_node
**Parameters**: self
**Returns**: SubatomicHop | None
**Description**: Get the next node to execute.

        Returns:
            Next SubatomicHop or None if queue is empty
        

#### pause_node
**Parameters**: self, hop_id
**Returns**: bool
**Description**: Pause a node's execution.

        Args:
            hop_id: Node ID to pause

        Returns:
            True if paused successfully
        

#### resume_node
**Parameters**: self, hop_id
**Returns**: bool
**Description**: Resume a paused node.

        Args:
            hop_id: Node ID to resume

        Returns:
            True if resumed successfully
        

#### get_graph_stats
**Parameters**: self
**Returns**: Dict[str, Any]
**Description**: Get graph statistics.

#### visualize_graph
**Parameters**: self
**Returns**: Dict[str, Any]
**Description**: Get graph data for visualization.

        Returns:
            Dictionary with nodes and edges
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: Dict[str, int]
**Description**: L3 orchestration agent - operational only.



## Class: HealerMixin

**Description**: Stub.



## Class: MCPHardenedMixin

**Description**: Stub.



## Class: L3SubatomicTestingMixin



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize the DAG Manager.

        Args:
            config: Optional configuration
        



## Function: register_function

**Parameters**: self, name, function
**Returns**: None
**Description**: Register a hop function that can be spawned.

        Args:
            name: Function name
            function: The function to register
        



## Function: add_node

**Parameters**: self, hop, predecessors
**Returns**: None
**Description**: Add a node to the DAG.

        Args:
            hop: The SubatomicHop to add
            predecessors: Optional list of predecessor node IDs
        



## Function: request_mutation

**Parameters**: self, mutation
**Returns**: MutationResult
**Description**: Request a mutation to the DAG.

        Args:
            mutation: The mutation to request

        Returns:
            Result of the mutation
        



## Function: create_mutation_request

**Parameters**: self, action, target_hop_id, hop_function, reason, requester_hop_id
**Returns**: DAGMutation
**Description**: Create a mutation request.

        Args:
            action: Type of mutation
            target_hop_id: Target node ID
            hop_function: Function name for new node
            reason: Reason for mutation
            requester_hop_id: ID of requesting node
            **kwargs: Additional hop spec parameters

        Returns:
            DAGMutation object
        



## Function: get_next_node

**Parameters**: self
**Returns**: SubatomicHop | None
**Description**: Get the next node to execute.

        Returns:
            Next SubatomicHop or None if queue is empty
        



## Function: pause_node

**Parameters**: self, hop_id
**Returns**: bool
**Description**: Pause a node's execution.

        Args:
            hop_id: Node ID to pause

        Returns:
            True if paused successfully
        



## Function: resume_node

**Parameters**: self, hop_id
**Returns**: bool
**Description**: Resume a paused node.

        Args:
            hop_id: Node ID to resume

        Returns:
            True if resumed successfully
        



## Function: get_graph_stats

**Parameters**: self
**Returns**: Dict[str, Any]
**Description**: Get graph statistics.



## Function: visualize_graph

**Parameters**: self
**Returns**: Dict[str, Any]
**Description**: Get graph data for visualization.

        Returns:
            Dictionary with nodes and edges
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: Dict[str, int]
**Description**: L3 orchestration agent - operational only.



## Usage Examples

### Class Usage

```python
# Using DAGManager
dagmanager = DAGManager()
dagmanager.register_function()
dagmanager.add_node()
```

```python
# Using HealerMixin
healermixin = HealerMixin()
```

```python
# Using MCPHardenedMixin
mcphardenedmixin = MCPHardenedMixin()
```

### Function Usage

```python
# Using __init__
result = __init__(config)
```

```python
# Using register_function
result = register_function(name, function)
```

```python
# Using add_node
result = add_node(hop, predecessors)
```



---
**Generated**: 2026-03-26T09:39:04.154135
**Type**: api_reference
**Quality**: comprehensive
