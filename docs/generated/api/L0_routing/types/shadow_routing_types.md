# API Documentation: shadow_routing_types

**Target Audience**: developers, api_users

# shadow_routing_types API Documentation

**File**: `shadow_routing_types.py`
**Classes**: 3
**Functions**: 4

## Classes

- **ShadowRoutingRationale** (inherits from str, Enum)
- **ShadowRoutingDecision**
- **ShadowRoutingTelemetry**

## Functions

- **_get_canonical_json**
- **compute_canonical_fingerprint** -> str
- **to_canonical_json** -> str
- **to_canonical_json** -> str


## Class: ShadowRoutingRationale

**Description**: Shadow routing rationale - independent of live routing rationale.

**Inherits from**: str, Enum



## Class: ShadowRoutingDecision

**Description**: Non-invasive shadow routing decision with drift detection.

    This artifact is produced after the actual routing decision is made
    and cannot affect the live route. It serves as a side-channel for
    detecting routing drift and providing shadow suggestions.
    

### Methods

#### compute_canonical_fingerprint
**Parameters**: self, features
**Returns**: str
**Description**: Compute deterministic 64-hex fingerprint from routing features.

        Args:
            features: Dictionary of routing features used for classification

        Returns:
            64-character lowercase hex SHA256 digest
        

#### to_canonical_json
**Parameters**: self
**Returns**: str
**Description**: Convert to canonical JSON for hashing/storage.

        Returns:
            Canonical JSON string representation
        



## Class: ShadowRoutingTelemetry

**Description**: Telemetry artifact for shadow routing observations.

    Emitted to L6 observability bus and optionally stored in L4.
    

### Methods

#### to_canonical_json
**Parameters**: self
**Returns**: str
**Description**: Convert to canonical JSON for storage/transmission.



## Function: _get_canonical_json



## Function: compute_canonical_fingerprint

**Parameters**: self, features
**Returns**: str
**Description**: Compute deterministic 64-hex fingerprint from routing features.

        Args:
            features: Dictionary of routing features used for classification

        Returns:
            64-character lowercase hex SHA256 digest
        



## Function: to_canonical_json

**Parameters**: self
**Returns**: str
**Description**: Convert to canonical JSON for hashing/storage.

        Returns:
            Canonical JSON string representation
        



## Function: to_canonical_json

**Parameters**: self
**Returns**: str
**Description**: Convert to canonical JSON for storage/transmission.



## Usage Examples

### Class Usage

```python
# Using ShadowRoutingRationale
shadowroutingrationale = ShadowRoutingRationale()
```

```python
# Using ShadowRoutingDecision
shadowroutingdecision = ShadowRoutingDecision()
shadowroutingdecision.compute_canonical_fingerprint()
shadowroutingdecision.to_canonical_json()
```

```python
# Using ShadowRoutingTelemetry
shadowroutingtelemetry = ShadowRoutingTelemetry()
shadowroutingtelemetry.to_canonical_json()
```

### Function Usage

```python
# Using _get_canonical_json
result = _get_canonical_json()
```

```python
# Using compute_canonical_fingerprint
result = compute_canonical_fingerprint(features)
```

```python
# Using to_canonical_json
result = to_canonical_json()
```



---
**Generated**: 2026-03-26T09:39:03.477775
**Type**: api_reference
**Quality**: comprehensive
