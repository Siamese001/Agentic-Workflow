# API Documentation: DAGMutatorAgent

**Target Audience**: developers, api_users

# DAGMutatorAgent API Documentation

**File**: `DAGMutatorAgent.py`
**Classes**: 8
**Functions**: 18

## Classes

- **GraphTransaction**
- **MutationAction** (inherits from Enum)
- **HopSpec** (inherits from BaseModel)
- **DAGMutation** (inherits from BaseModel)
- **MutationResult** (inherits from BaseModel)
- **DAGConfig** (inherits from BaseModel)
- **DAGMutatorAgent** (inherits from SovereignBaseAgent)
- **Config**

## Functions

- **__init__** -> None
- **__enter__**
- **__exit__**
- **_validate_transaction_graph**
- **_validate_depth_ordering**
- **validate_hop_spec**
- **__init__** -> None
- **apply_mutation** -> MutationResult
- **_validate_mutation** -> None
- **_spawn_predecessor** -> MutationResult
- **_spawn_successor** -> MutationResult
- **_skip_successor** -> MutationResult
- **_replace_node** -> MutationResult
- **_update_depths** -> None
- **_store_mutation_result** -> None
- **get_mutation_history** -> list[MutationResult]
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]


## Class: GraphTransaction

**Description**: Context manager for atomic graph mutations.

    Implements copy-on-write semantics to ensure the graph is never
    left in a corrupted state if a mutation fails partway through.
    

### Methods

#### __init__
**Parameters**: self, manager
**Returns**: None
**Description**: Initialize the transaction.

        Args:
            manager: The DynamicDAGManager instance
        

#### __enter__
**Parameters**: self
**Description**: Enter transaction - create a copy of the graph.

        Returns:
            The transaction graph (copy of original)
        

#### __exit__
**Parameters**: self, exc_type, exc_val, exc_tb
**Description**: Exit transaction - commit or rollback.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred

        Returns:
            False to propagate exceptions, True to suppress
        

#### _validate_transaction_graph
**Parameters**: self
**Description**: Validate that the transaction graph is still a valid DAG.

        Raises:
            ValueError: If validation fails
        

#### _validate_depth_ordering
**Parameters**: self
**Description**: Validate that depth values are consistent with graph structure.



## Class: MutationAction

**Description**: Types of DAG mutations.

**Inherits from**: Enum



## Class: HopSpec

**Description**: Specification for creating a new hop.

**Inherits from**: BaseModel



## Class: DAGMutation

**Description**: A mutation request for the DAG.

**Inherits from**: BaseModel

### Methods

#### validate_hop_spec
**Parameters**: cls, v, values



## Class: MutationResult

**Description**: Result of applying a mutation.

**Inherits from**: BaseModel



## Class: DAGConfig

**Description**: configuration for DAG management.

**Inherits from**: BaseModel



## Class: DAGMutatorAgent

**Description**: Handles the actual graph mutations.

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize the DAGMutatorAgent.

        Args:
            config: DAG configuration
        

#### apply_mutation
**Parameters**: self, graph, mutation
**Returns**: MutationResult
**Description**: Apply a mutation to the graph with transactional safety.

        Args:
            graph: The NetworkX directed graph
            mutation: The mutation to apply

        Returns:
            MutationResult with details
        

#### _validate_mutation
**Parameters**: self, graph, mutation
**Returns**: None
**Description**: Validate that a mutation is safe to apply.

#### _spawn_predecessor
**Parameters**: self, graph, mutation
**Returns**: MutationResult
**Description**: Spawn a new predecessor node.

#### _spawn_successor
**Parameters**: self, graph, mutation
**Returns**: MutationResult
**Description**: Spawn a new successor node.

#### _skip_successor
**Parameters**: self, graph, mutation
**Returns**: MutationResult
**Description**: Skip a successor node by bridging the gap.

#### _replace_node
**Parameters**: self, graph, mutation
**Returns**: MutationResult
**Description**: Replace a node with a new one.

#### _update_depths
**Parameters**: self, graph
**Returns**: None
**Description**: Update depth annotations for all nodes.

#### _store_mutation_result
**Parameters**: self, result
**Returns**: None
**Description**: Store mutation result in history.

#### get_mutation_history
**Parameters**: self, limit
**Returns**: list[MutationResult]
**Description**: Get mutation history.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        DAG Mutation Healing - Validates graph mutation logic integrity.

        WIRED CAPABILITIES:
        - _validate_mutation(): Self-diagnostic on graph mutation rules.
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by DAGMutatorAgent.

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
        



## Class: Config



## Function: __init__

**Parameters**: self, manager
**Returns**: None
**Description**: Initialize the transaction.

        Args:
            manager: The DynamicDAGManager instance
        



## Function: __enter__

**Parameters**: self
**Description**: Enter transaction - create a copy of the graph.

        Returns:
            The transaction graph (copy of original)
        



## Function: __exit__

**Parameters**: self, exc_type, exc_val, exc_tb
**Description**: Exit transaction - commit or rollback.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred

        Returns:
            False to propagate exceptions, True to suppress
        



## Function: _validate_transaction_graph

**Parameters**: self
**Description**: Validate that the transaction graph is still a valid DAG.

        Raises:
            ValueError: If validation fails
        



## Function: _validate_depth_ordering

**Parameters**: self
**Description**: Validate that depth values are consistent with graph structure.



## Function: validate_hop_spec

**Parameters**: cls, v, values


## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize the DAGMutatorAgent.

        Args:
            config: DAG configuration
        



## Function: apply_mutation

**Parameters**: self, graph, mutation
**Returns**: MutationResult
**Description**: Apply a mutation to the graph with transactional safety.

        Args:
            graph: The NetworkX directed graph
            mutation: The mutation to apply

        Returns:
            MutationResult with details
        



## Function: _validate_mutation

**Parameters**: self, graph, mutation
**Returns**: None
**Description**: Validate that a mutation is safe to apply.



## Function: _spawn_predecessor

**Parameters**: self, graph, mutation
**Returns**: MutationResult
**Description**: Spawn a new predecessor node.



## Function: _spawn_successor

**Parameters**: self, graph, mutation
**Returns**: MutationResult
**Description**: Spawn a new successor node.



## Function: _skip_successor

**Parameters**: self, graph, mutation
**Returns**: MutationResult
**Description**: Skip a successor node by bridging the gap.



## Function: _replace_node

**Parameters**: self, graph, mutation
**Returns**: MutationResult
**Description**: Replace a node with a new one.



## Function: _update_depths

**Parameters**: self, graph
**Returns**: None
**Description**: Update depth annotations for all nodes.



## Function: _store_mutation_result

**Parameters**: self, result
**Returns**: None
**Description**: Store mutation result in history.



## Function: get_mutation_history

**Parameters**: self, limit
**Returns**: list[MutationResult]
**Description**: Get mutation history.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        DAG Mutation Healing - Validates graph mutation logic integrity.

        WIRED CAPABILITIES:
        - _validate_mutation(): Self-diagnostic on graph mutation rules.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by DAGMutatorAgent.

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
        



## Usage Examples

### Class Usage

```python
# Using GraphTransaction
graphtransaction = GraphTransaction()
```

```python
# Using MutationAction
mutationaction = MutationAction()
```

```python
# Using HopSpec
hopspec = HopSpec()
```

### Function Usage

```python
# Using __init__
result = __init__(manager)
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
**Generated**: 2026-03-26T09:39:04.268868
**Type**: api_reference
**Quality**: comprehensive
