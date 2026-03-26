# API Documentation: route_policy_governor

**Target Audience**: developers, api_users

# route_policy_governor API Documentation

**File**: `route_policy_governor.py`
**Classes**: 2
**Functions**: 8

## Classes

- **RoutingProposal**
- **RoutePolicyGovernor**

## Functions

- **get_route_policy_governor** -> RoutePolicyGovernor
- **reset_route_policy_governor** -> None
- **satisfies_policy** -> bool
- **__init__** -> None
- **_trace_id** -> str
- **_verify_boundary** -> bool
- **commit_routing** -> RoutingProposal
- **ledger** -> list[RoutingProposal]


## Class: RoutingProposal

**Description**: A routing decision committed to a governance policy hash.

    Every L0 routing dispatch must produce a RoutingProposal before
    the request is forwarded, making the policy provenance traceable.
    

### Methods

#### satisfies_policy
**Parameters**: self
**Returns**: bool
**Description**: Return True if the proposal was committed against a non-empty policy hash.



## Class: RoutePolicyGovernor

**Description**: Commits routing decisions to a governance policy before dispatch.

    Usage::

        governor = RoutePolicyGovernor(policy_hash="abc123")
        proposal = governor.commit_routing("standard_validation", metadata={})
        assert proposal.satisfies_policy()
        dispatch(proposal.routing_artifact)
    

### Methods

#### __init__
**Parameters**: self, policy_hash, gateway
**Returns**: None

#### _trace_id
**Parameters**: self
**Returns**: str

#### _verify_boundary
**Parameters**: self, route_path
**Returns**: bool
**Description**: Verify the route path is within governed boundaries.

        Emits ``verifies_boundary`` ADG edge.
        

#### commit_routing
**Parameters**: self, route_path, metadata
**Returns**: RoutingProposal
**Description**: Commit a routing decision against the governing policy hash.

        Emits ``proposal_commits_routing`` + ``references_policy_hash``
        + ``reads_governed_config`` ADG edges.
        

#### ledger
**Parameters**: self
**Returns**: list[RoutingProposal]



## Function: get_route_policy_governor

**Parameters**: policy_hash
**Returns**: RoutePolicyGovernor


## Function: reset_route_policy_governor

**Returns**: None


## Function: satisfies_policy

**Parameters**: self
**Returns**: bool
**Description**: Return True if the proposal was committed against a non-empty policy hash.



## Function: __init__

**Parameters**: self, policy_hash, gateway
**Returns**: None


## Function: _trace_id

**Parameters**: self
**Returns**: str


## Function: _verify_boundary

**Parameters**: self, route_path
**Returns**: bool
**Description**: Verify the route path is within governed boundaries.

        Emits ``verifies_boundary`` ADG edge.
        



## Function: commit_routing

**Parameters**: self, route_path, metadata
**Returns**: RoutingProposal
**Description**: Commit a routing decision against the governing policy hash.

        Emits ``proposal_commits_routing`` + ``references_policy_hash``
        + ``reads_governed_config`` ADG edges.
        



## Function: ledger

**Parameters**: self
**Returns**: list[RoutingProposal]


## Usage Examples

### Class Usage

```python
# Using RoutingProposal
routingproposal = RoutingProposal()
routingproposal.satisfies_policy()
```

```python
# Using RoutePolicyGovernor
routepolicygovernor = RoutePolicyGovernor()
routepolicygovernor.commit_routing()
routepolicygovernor.ledger()
```

### Function Usage

```python
# Using get_route_policy_governor
result = get_route_policy_governor(policy_hash)
```

```python
# Using reset_route_policy_governor
result = reset_route_policy_governor()
```

```python
# Using satisfies_policy
result = satisfies_policy()
```



---
**Generated**: 2026-03-26T09:39:02.706644
**Type**: api_reference
**Quality**: comprehensive
