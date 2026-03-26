# API Documentation: sovereign_base_model_types

**Target Audience**: developers, api_users

# sovereign_base_model_types API Documentation

**File**: `sovereign_base_model_types.py`
**Classes**: 2
**Functions**: 1

## Classes

- **SovereignBaseModel** (inherits from BaseModel)
- **Territory** (inherits from SovereignBaseModel)

## Functions

- **validate_invariants** -> SovereignBaseModel


## Class: SovereignBaseModel

**Description**: 
    Base model for all Sovereign entities.
    Enforces strict type checking and immutability (frozen) to ensure
    data integrity across agent handoffs and state transitions.
    

**Inherits from**: BaseModel

### Methods

#### validate_invariants
**Parameters**: self
**Returns**: SovereignBaseModel
**Description**: Cross-field validation hook for shared invariants.



## Class: Territory

**Description**: 
    Represents a logical or physical boundary within the system.
    Used for mapping organizational depth and canonical paths.
    

**Inherits from**: SovereignBaseModel



## Function: validate_invariants

**Parameters**: self
**Returns**: SovereignBaseModel
**Description**: Cross-field validation hook for shared invariants.



## Usage Examples

### Class Usage

```python
# Using SovereignBaseModel
sovereignbasemodel = SovereignBaseModel()
sovereignbasemodel.validate_invariants()
```

```python
# Using Territory
territory = Territory()
```

### Function Usage

```python
# Using validate_invariants
result = validate_invariants()
```



---
**Generated**: 2026-03-26T09:39:05.573322
**Type**: api_reference
**Quality**: comprehensive
