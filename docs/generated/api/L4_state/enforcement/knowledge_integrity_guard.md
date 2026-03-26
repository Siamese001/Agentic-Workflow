# API Documentation: knowledge_integrity_guard

**Target Audience**: developers, api_users

# knowledge_integrity_guard API Documentation

**File**: `knowledge_integrity_guard.py`
**Classes**: 3
**Functions**: 6

## Classes

- **KnowledgeIntegrityViolation** (inherits from Exception)
- **KnowledgeNode**
- **KnowledgeIntegrityGuard**

## Functions

- **__post_init__**
- **_canonical_bytes** -> bytes
- **__init__**
- **mutate** -> KnowledgeNode
- **verify_chain** -> bool
- **create_compaction_snapshot** -> dict[str, Any]


## Class: KnowledgeIntegrityViolation

**Description**: Raised when a knowledge mutation breaks the hash chain integrity.

**Inherits from**: Exception



## Class: KnowledgeNode

**Description**: Represents a versioned node in the knowledge base.

### Methods

#### __post_init__
**Parameters**: self

#### _canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Computes the canonical byte representation for signing.



## Class: KnowledgeIntegrityGuard

**Description**: 
    Enforces hash chain integrity for the knowledge base.

    This guard enforces Guarantee #9 by ensuring every mutation is part of an
    unbroken, verifiable hash chain anchored to a genesis hash. It supports
    compaction through signed checkpoints to maintain integrity over time.
    

### Methods

#### __init__
**Parameters**: self, genesis_hash

#### mutate
**Parameters**: self, node_id, content
**Returns**: KnowledgeNode
**Description**: 
        Applies a mutation, creating a new node in the hash chain.

        Args:
            node_id: The identifier of the node to mutate.
            content: The new content for the node.

        Returns:
            The newly created, signed KnowledgeNode.
        

#### verify_chain
**Parameters**: self
**Returns**: bool
**Description**: 
        Verifies the integrity of the entire hash chain from HEAD to genesis.

        Raises:
            KnowledgeIntegrityViolation: If the chain is broken.
        

#### create_compaction_snapshot
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Creates a signed checkpoint snapshot for long-term compaction.

        This allows old parts of the chain to be pruned without losing the
        overall integrity guarantee.
        



## Function: __post_init__

**Parameters**: self


## Function: _canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: Computes the canonical byte representation for signing.



## Function: __init__

**Parameters**: self, genesis_hash


## Function: mutate

**Parameters**: self, node_id, content
**Returns**: KnowledgeNode
**Description**: 
        Applies a mutation, creating a new node in the hash chain.

        Args:
            node_id: The identifier of the node to mutate.
            content: The new content for the node.

        Returns:
            The newly created, signed KnowledgeNode.
        



## Function: verify_chain

**Parameters**: self
**Returns**: bool
**Description**: 
        Verifies the integrity of the entire hash chain from HEAD to genesis.

        Raises:
            KnowledgeIntegrityViolation: If the chain is broken.
        



## Function: create_compaction_snapshot

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Creates a signed checkpoint snapshot for long-term compaction.

        This allows old parts of the chain to be pruned without losing the
        overall integrity guarantee.
        



## Usage Examples

### Class Usage

```python
# Using KnowledgeIntegrityViolation
knowledgeintegrityviolation = KnowledgeIntegrityViolation()
```

```python
# Using KnowledgeNode
knowledgenode = KnowledgeNode()
```

```python
# Using KnowledgeIntegrityGuard
knowledgeintegrityguard = KnowledgeIntegrityGuard()
knowledgeintegrityguard.mutate()
knowledgeintegrityguard.verify_chain()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _canonical_bytes
result = _canonical_bytes()
```

```python
# Using __init__
result = __init__(genesis_hash)
```



---
**Generated**: 2026-03-26T09:39:04.502201
**Type**: api_reference
**Quality**: comprehensive
