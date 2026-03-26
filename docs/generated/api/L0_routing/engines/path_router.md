# API Documentation: path_router

**Target Audience**: developers, api_users

# path_router API Documentation

**File**: `path_router.py`
**Classes**: 2
**Functions**: 3

## Classes

- **Path** (inherits from Enum)
- **PathRouter**

## Functions

- **_get_routing_gateway**
- **_get_proof_emitter**
- **select_path** -> Path


## Class: Path

**Description**: Deterministic path enumeration for L0 routing.

**Inherits from**: Enum



## Class: PathRouter

**Description**: 
    Deterministic path router for governed payloads.

    Implements strict Path A/B/C/D dispatch semantics with zero business logic.
    

### Methods

#### select_path
**Parameters**: self, payload
**Returns**: Path
**Description**: 
        Select routing path based on payload characteristics.

        Deterministic logic:
        - If payload.check_ids empty → Path.A
        - If payload.sanitized is True → Path.B
        - If len(payload.check_ids) == 1 → Path.C
        - Else → Path.D

        Args:
            payload: GovernedPayload to route

        Returns:
            Selected Path enum value
        



## Function: _get_routing_gateway



## Function: _get_proof_emitter



## Function: select_path

**Parameters**: self, payload
**Returns**: Path
**Description**: 
        Select routing path based on payload characteristics.

        Deterministic logic:
        - If payload.check_ids empty → Path.A
        - If payload.sanitized is True → Path.B
        - If len(payload.check_ids) == 1 → Path.C
        - Else → Path.D

        Args:
            payload: GovernedPayload to route

        Returns:
            Selected Path enum value
        



## Usage Examples

### Class Usage

```python
# Using Path
path = Path()
```

```python
# Using PathRouter
pathrouter = PathRouter()
pathrouter.select_path()
```

### Function Usage

```python
# Using _get_routing_gateway
result = _get_routing_gateway()
```

```python
# Using _get_proof_emitter
result = _get_proof_emitter()
```

```python
# Using select_path
result = select_path(payload)
```



---
**Generated**: 2026-03-26T09:39:02.661112
**Type**: api_reference
**Quality**: comprehensive
