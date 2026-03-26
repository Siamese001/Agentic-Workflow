# API Documentation: capability_token_types

**Target Audience**: developers, api_users

# capability_token_types API Documentation

**File**: `capability_token_types.py`
**Classes**: 5
**Functions**: 21

## Classes

- **CapabilityTokenSubject**
- **CapabilityConstraints**
- **CapabilityTokenArtifact**
- **CapabilityDecisionArtifact**
- **CapabilityEnforcer**

## Functions

- **_canonical_json** -> str
- **_compute_trace_id** -> str
- **build_capability_token** -> CapabilityTokenArtifact
- **build_capability_decision** -> CapabilityDecisionArtifact
- **issue_capability_token** -> CapabilityTokenArtifact
- **__post_init__** -> None
- **to_dict** -> dict[str, str]
- **__post_init__** -> None
- **to_dict** -> dict[str, Any]
- **__post_init__** -> None
- **_payload_dict** -> dict[str, Any]
- **to_json** -> str
- **__post_init__** -> None
- **_payload_dict** -> dict[str, Any]
- **to_json** -> str
- **__init__** -> None
- **token** -> CapabilityTokenArtifact
- **call_count** -> int
- **decisions** -> list[CapabilityDecisionArtifact]
- **check** -> CapabilityDecisionArtifact
- **_path_matches** -> bool


## Class: CapabilityTokenSubject

**Description**: Subject identity within a capability token.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, str]



## Class: CapabilityConstraints

**Description**: Constraints on a capability token.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: CapabilityTokenArtifact

**Description**: §A.1 — Capability token for L2 execution boundary enforcement.

    All fields are immutable. trace_id is deterministic (SHA-256 of canonical payload).
    semantic_clock is required (no wall-clock).
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### _payload_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Canonical payload for serialization (includes trace_id).

#### to_json
**Parameters**: self
**Returns**: str
**Description**: Deterministic JSON serialization.



## Class: CapabilityDecisionArtifact

**Description**: §A.2 — Decision artifact emitted at the L2 enforcement chokepoint.

    Emitted for every tool invocation (both ALLOW and DENY).
    trace_id is deterministic (SHA-256 of canonical payload excluding trace_id).
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### _payload_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Canonical payload for serialization.

#### to_json
**Parameters**: self
**Returns**: str
**Description**: Deterministic JSON serialization.



## Class: CapabilityEnforcer

**Description**: Stateful enforcer for a single CapabilityTokenArtifact.

    Tracks invocation count and validates permissions + path constraints.
    Emits a CapabilityDecisionArtifact for every check (ALLOW or DENY).
    

### Methods

#### __init__
**Parameters**: self, token
**Returns**: None

#### token
**Parameters**: self
**Returns**: CapabilityTokenArtifact

#### call_count
**Parameters**: self
**Returns**: int

#### decisions
**Parameters**: self
**Returns**: list[CapabilityDecisionArtifact]

#### check
**Parameters**: self
**Returns**: CapabilityDecisionArtifact
**Description**: Check capability and emit decision artifact.

        Args:
            tool_name: Name of the tool being invoked.
            action: Action being performed (e.g. "execute").
            requested_resource: Resource path being accessed.
            required_permission: Permission code required (from PERMISSION_CODES values).
            semantic_clock: Current semantic clock snapshot.

        Returns:
            CapabilityDecisionArtifact (ALLOW or DENY).

        Raises:
            PermissionError: If decision is DENY.
        

#### _path_matches
**Parameters**: requested, allowed
**Returns**: bool
**Description**: Check if requested resource matches any allowed path prefix.

        Uses segment-based comparison on logical resource URIs (not filesystem paths).
        



## Function: _canonical_json

**Parameters**: obj
**Returns**: str
**Description**: Deterministic JSON: sorted keys, no extra whitespace.



## Function: _compute_trace_id

**Parameters**: payload
**Returns**: str
**Description**: Deterministic trace_id = SHA-256 of canonical JSON payload (excluding trace_id).



## Function: build_capability_token

**Returns**: CapabilityTokenArtifact
**Description**: Build a CapabilityTokenArtifact with deterministic trace_id.

    Permissions and allowed_paths are sorted automatically.
    



## Function: build_capability_decision

**Returns**: CapabilityDecisionArtifact
**Description**: Build a CapabilityDecisionArtifact with deterministic trace_id.



## Function: issue_capability_token

**Returns**: CapabilityTokenArtifact
**Description**: §Wave5.0.3 — Deterministic capability token issuance helper.

    High-level convenience for upstream (L5/L3) callers to mint a
    CapabilityTokenArtifact with flat parameters.  Validates permission
    codes, constructs composite sub-objects, and delegates to
    build_capability_token for deterministic trace_id generation.

    Args:
        semantic_clock: Required SemanticClockSnapshot (ValueError if None).
        subject_kind: Subject type (e.g. "agent").
        subject_id: Subject identifier (e.g. "StructureHealerAgent").
        issued_by: Issuer identity string.
        permissions: List of permission code values (must be in
            ALL_PERMISSION_VALUES, e.g. "TOOL:READ").  Sorted automatically.
        allowed_paths: List of resource path prefixes.  Sorted automatically.
        max_tool_calls: Maximum invocations allowed under this token.
        policy_config_hash: Optional policy config hash for pinning.

    Returns:
        CapabilityTokenArtifact with deterministic trace_id.

    Raises:
        ValueError: If semantic_clock is None or any permission is unknown.
    



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, str]


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: _payload_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Canonical payload for serialization (includes trace_id).



## Function: to_json

**Parameters**: self
**Returns**: str
**Description**: Deterministic JSON serialization.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: _payload_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Canonical payload for serialization.



## Function: to_json

**Parameters**: self
**Returns**: str
**Description**: Deterministic JSON serialization.



## Function: __init__

**Parameters**: self, token
**Returns**: None


## Function: token

**Parameters**: self
**Returns**: CapabilityTokenArtifact


## Function: call_count

**Parameters**: self
**Returns**: int


## Function: decisions

**Parameters**: self
**Returns**: list[CapabilityDecisionArtifact]


## Function: check

**Parameters**: self
**Returns**: CapabilityDecisionArtifact
**Description**: Check capability and emit decision artifact.

        Args:
            tool_name: Name of the tool being invoked.
            action: Action being performed (e.g. "execute").
            requested_resource: Resource path being accessed.
            required_permission: Permission code required (from PERMISSION_CODES values).
            semantic_clock: Current semantic clock snapshot.

        Returns:
            CapabilityDecisionArtifact (ALLOW or DENY).

        Raises:
            PermissionError: If decision is DENY.
        



## Function: _path_matches

**Parameters**: requested, allowed
**Returns**: bool
**Description**: Check if requested resource matches any allowed path prefix.

        Uses segment-based comparison on logical resource URIs (not filesystem paths).
        



## Usage Examples

### Class Usage

```python
# Using CapabilityTokenSubject
capabilitytokensubject = CapabilityTokenSubject()
capabilitytokensubject.to_dict()
```

```python
# Using CapabilityConstraints
capabilityconstraints = CapabilityConstraints()
capabilityconstraints.to_dict()
```

```python
# Using CapabilityTokenArtifact
capabilitytokenartifact = CapabilityTokenArtifact()
capabilitytokenartifact.to_json()
```

### Function Usage

```python
# Using _canonical_json
result = _canonical_json(obj)
```

```python
# Using _compute_trace_id
result = _compute_trace_id(payload)
```

```python
# Using build_capability_token
result = build_capability_token()
```



---
**Generated**: 2026-03-26T09:39:03.949007
**Type**: api_reference
**Quality**: comprehensive
