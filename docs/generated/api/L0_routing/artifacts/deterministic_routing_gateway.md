# API Documentation: deterministic_routing_gateway

**Target Audience**: developers, api_users

# deterministic_routing_gateway API Documentation

**File**: `deterministic_routing_gateway.py`
**Classes**: 2
**Functions**: 10

## Classes

- **RoutingArtifact**
- **DeterministicRoutingGateway**

## Functions

- **_compute_replay_key** -> str
- **_compute_determinism_digest** -> str
- **get_routing_gateway** -> DeterministicRoutingGateway
- **reset_routing_gateway** -> None
- **as_route_decision** -> RouteDecisionArtifact
- **__init__** -> None
- **stamp_decision** -> RoutingArtifact
- **verify_replay** -> bool
- **ledger** -> list[RoutingArtifact]
- **clear_ledger** -> None


## Class: RoutingArtifact

**Description**: Deterministic routing artifact emitted at each L0 routing decision.

    Carries the replay key and determinism digest so that every routing
    decision can be reproduced exactly and audited post-hoc.
    

### Methods

#### as_route_decision
**Parameters**: self, risk_score, budget_est
**Returns**: RouteDecisionArtifact
**Description**: Convert to the canonical RouteDecisionArtifact for downstream consumers.



## Class: DeterministicRoutingGateway

**Description**: Single gateway for all L0 routing decisions.

    Every routing decision must pass through ``stamp_decision`` before
    being dispatched. This ensures that:
    - A replay key is emitted (``emits_replay_key`` ADG edge).
    - A determinism digest is emitted (``emits_determinism_digest`` ADG edge).
    - The artifact is recorded in the ledger for later replay.

    Usage::

        gw = DeterministicRoutingGateway(policy_hash="abc123")
        artifact = gw.stamp_decision("standard_validation")
        # dispatch using artifact.route_path
    

### Methods

#### __init__
**Parameters**: self, policy_hash
**Returns**: None

#### stamp_decision
**Parameters**: self, route_path, metadata
**Returns**: RoutingArtifact
**Description**: Stamp a routing decision with a replay key and determinism digest.

        Returns a :class:`RoutingArtifact` that must be forwarded with the
        request so downstream layers can verify routing provenance.
        

#### verify_replay
**Parameters**: self, artifact
**Returns**: bool
**Description**: Verify a routing artifact can be deterministically replayed.

        Returns True if the replay key can be reconstructed from the
        artifact's own fields (i.e., it was not tampered with).
        

#### ledger
**Parameters**: self
**Returns**: list[RoutingArtifact]
**Description**: Return a copy of all stamped routing artifacts.

#### clear_ledger
**Parameters**: self
**Returns**: None
**Description**: Clear the ledger (for testing).



## Function: _compute_replay_key

**Parameters**: route_path, policy_hash, trace_id
**Returns**: str
**Description**: Compute a deterministic replay key from routing inputs.



## Function: _compute_determinism_digest

**Parameters**: replay_key, timestamp
**Returns**: str
**Description**: Compute a determinism digest binding the replay key to an execution moment.



## Function: get_routing_gateway

**Parameters**: policy_hash
**Returns**: DeterministicRoutingGateway
**Description**: Return the process-level deterministic routing gateway.



## Function: reset_routing_gateway

**Returns**: None
**Description**: Reset the global routing gateway (for testing).



## Function: as_route_decision

**Parameters**: self, risk_score, budget_est
**Returns**: RouteDecisionArtifact
**Description**: Convert to the canonical RouteDecisionArtifact for downstream consumers.



## Function: __init__

**Parameters**: self, policy_hash
**Returns**: None


## Function: stamp_decision

**Parameters**: self, route_path, metadata
**Returns**: RoutingArtifact
**Description**: Stamp a routing decision with a replay key and determinism digest.

        Returns a :class:`RoutingArtifact` that must be forwarded with the
        request so downstream layers can verify routing provenance.
        



## Function: verify_replay

**Parameters**: self, artifact
**Returns**: bool
**Description**: Verify a routing artifact can be deterministically replayed.

        Returns True if the replay key can be reconstructed from the
        artifact's own fields (i.e., it was not tampered with).
        



## Function: ledger

**Parameters**: self
**Returns**: list[RoutingArtifact]
**Description**: Return a copy of all stamped routing artifacts.



## Function: clear_ledger

**Parameters**: self
**Returns**: None
**Description**: Clear the ledger (for testing).



## Usage Examples

### Class Usage

```python
# Using RoutingArtifact
routingartifact = RoutingArtifact()
routingartifact.as_route_decision()
```

```python
# Using DeterministicRoutingGateway
deterministicroutinggateway = DeterministicRoutingGateway()
deterministicroutinggateway.stamp_decision()
deterministicroutinggateway.verify_replay()
```

### Function Usage

```python
# Using _compute_replay_key
result = _compute_replay_key(route_path, policy_hash)
```

```python
# Using _compute_determinism_digest
result = _compute_determinism_digest(replay_key, timestamp)
```

```python
# Using get_routing_gateway
result = get_routing_gateway(policy_hash)
```



---
**Generated**: 2026-03-26T09:39:02.570263
**Type**: api_reference
**Quality**: comprehensive
