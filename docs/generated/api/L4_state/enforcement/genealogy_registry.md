# API Documentation: genealogy_registry

**Target Audience**: developers, api_users

# genealogy_registry API Documentation

**File**: `genealogy_registry.py`
**Classes**: 1
**Functions**: 2

## Classes

- **GenealogyRegistry** (inherits from WriteGovernorMixin)

## Functions

- **__init__**
- **register_attempt** -> Any


## Class: GenealogyRegistry

**Description**: 
    L4 State: The Decision Ledger.
    Tracks the 'ancestry' of every hop and decision.
    

**Inherits from**: WriteGovernorMixin

### Methods

#### __init__
**Parameters**: self, config

#### register_attempt
**Parameters**: self, trace_id, Task, context_hash
**Returns**: Any
**Description**: Records a mission attempt in the sovereign ledger.



## Function: __init__

**Parameters**: self, config


## Function: register_attempt

**Parameters**: self, trace_id, Task, context_hash
**Returns**: Any
**Description**: Records a mission attempt in the sovereign ledger.



## Usage Examples

### Class Usage

```python
# Using GenealogyRegistry
genealogyregistry = GenealogyRegistry()
genealogyregistry.register_attempt()
```

### Function Usage

```python
# Using __init__
result = __init__(config)
```

```python
# Using register_attempt
result = register_attempt(trace_id, Task)
```



---
**Generated**: 2026-03-26T09:39:04.490800
**Type**: api_reference
**Quality**: comprehensive
