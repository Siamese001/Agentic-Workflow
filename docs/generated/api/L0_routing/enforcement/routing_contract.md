# API Documentation: routing_contract

**Target Audience**: developers, api_users

# routing_contract API Documentation

**File**: `routing_contract.py`
**Classes**: 8
**Functions**: 19

## Classes

- **UngovernnedRouteError** (inherits from RuntimeError)
- **StaleRoutingContractError** (inherits from RuntimeError)
- **RoutingContractValidationError** (inherits from ValueError)
- **RoutingContext**
- **RoutingContract**
- **RoutingProposal**
- **ProposalCommitter**
- **_ContractRegistry**

## Functions

- **_emit_references_policy_hash** -> None
- **emit_replay_key** -> None
- **emit_determinism_digest** -> None
- **_emit_records_execution_trace** -> None
- **commit_proposal** -> None
- **_get_contract_registry** -> _ContractRegistry
- **reset_contract_registry** -> None
- **create_and_commit_routing_contract** -> RoutingContract
- **execute_route** -> Any
- **validate** -> None
- **is_policy_current** -> bool
- **is_expired** -> bool
- **require_valid** -> None
- **__init__** -> None
- **record** -> None
- **store** -> None
- **get** -> RoutingContract | None
- **all_contracts** -> list[RoutingContract]
- **all_proposals** -> list[RoutingProposal]


## Class: UngovernnedRouteError

**Description**: Raised when a route is executed without a committed RoutingContract.

**Inherits from**: RuntimeError



## Class: StaleRoutingContractError

**Description**: Raised when a RoutingContract is reused after a policy change.

**Inherits from**: RuntimeError



## Class: RoutingContractValidationError

**Description**: Raised when a RoutingContract cannot be created due to missing fields.

**Inherits from**: ValueError



## Class: RoutingContext

**Description**: All inputs required to create a governed RoutingContract.

    Fields:
        run_id:          Active run identifier.
        router_id:       Identity of the router component emitting this decision.
        request_hash:    SHA-256[:32] of the raw routing request payload.
        candidate_routes: Ordered list of candidate route identifiers.
        chosen_route:    The selected route identifier.
        policy_hash:     Hash of the active routing policy.
        policy_version:  Version string of the active routing policy.
        metadata:        Optional freeform metadata.
    

### Methods

#### validate
**Parameters**: self
**Returns**: None
**Description**: Raise RoutingContractValidationError on missing required fields.



## Class: RoutingContract

**Description**: Immutable governance artifact for a single routing decision.

    Created exclusively by create_and_commit_routing_contract().
    All fields are set at creation time and cannot be mutated.

    Any downstream component consuming a route MUST receive a RoutingContract,
    not raw route output.
    

### Methods

#### is_policy_current
**Parameters**: self, current_policy_hash
**Returns**: bool
**Description**: Return False if policy changed since contract issuance.

#### is_expired
**Parameters**: self, current_tick
**Returns**: bool
**Description**: Return True if the contract has exceeded its expiry window.

#### require_valid
**Parameters**: self, current_policy_hash, current_tick
**Returns**: None
**Description**: Raise StaleRoutingContractError if contract is stale or expired.



## Class: RoutingProposal

**Description**: Internal binding artifact linking RoutingContract to governance ledger.

    The presence of this class and commit_proposal() ensures the ADG scanner
    emits proposal_commits_routing edges for this module.
    



## Class: ProposalCommitter

**Description**: ADG-scanner-visible committer class.

    Presence ensures proposal_commits_routing edge is emitted.
    



## Class: _ContractRegistry

**Description**: Thread-safe in-memory store for committed RoutingContracts.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### record
**Parameters**: self, proposal
**Returns**: None

#### store
**Parameters**: self, contract
**Returns**: None

#### get
**Parameters**: self, routing_contract_id
**Returns**: RoutingContract | None

#### all_contracts
**Parameters**: self
**Returns**: list[RoutingContract]

#### all_proposals
**Parameters**: self
**Returns**: list[RoutingProposal]



## Function: _emit_references_policy_hash

**Parameters**: routing_contract_id, policy_hash, policy_version
**Returns**: None
**Description**: ADG edge: references_policy_hash



## Function: emit_replay_key

**Parameters**: routing_contract_id, replay_key
**Returns**: None
**Description**: ADG edge: emits_replay_key



## Function: emit_determinism_digest

**Parameters**: routing_contract_id, determinism_digest
**Returns**: None
**Description**: ADG edge: emits_determinism_digest



## Function: _emit_records_execution_trace

**Parameters**: routing_contract_id, router_id, chosen_route
**Returns**: None
**Description**: ADG edge: records_execution_trace



## Function: commit_proposal

**Parameters**: proposal
**Returns**: None
**Description**: Commit a RoutingProposal to the governance ledger.

    ADG scanner detects commit_proposal -> proposal_commits_routing edge.
    



## Function: _get_contract_registry

**Returns**: _ContractRegistry


## Function: reset_contract_registry

**Returns**: None
**Description**: Reset registry — for use in tests only.



## Function: create_and_commit_routing_contract

**Parameters**: routing_context
**Returns**: RoutingContract
**Description**: Mandatory entrypoint for governed routing decisions.

    Steps (per §3 spec):
      1. Validate routing_context completeness.
      2. Hash candidate routes.
      3. Hash chosen route.
      4. Resolve policy hash and version.
      5. Generate replay key.
      6. Generate determinism digest.
      7. Attach trace id.
      8. Persist contract.
      9. Return immutable RoutingContract.

    No route may be selected outside this function.

    Args:
        routing_context: Fully populated RoutingContext.
        expiry_ticks:    Seconds until contract expires (default 3600).

    Returns:
        Immutable RoutingContract.

    Raises:
        RoutingContractValidationError: If context is incomplete.
    



## Function: execute_route

**Parameters**: contract, fn
**Returns**: Any
**Description**: Execute a routing action that requires a RoutingContract.

    Prohibited: fn(raw_route, ...) without contract.
    Required:   execute_route(contract, fn, ...)

    Raises:
        UngovernnedRouteError: If contract is not a RoutingContract instance.
    



## Function: validate

**Parameters**: self
**Returns**: None
**Description**: Raise RoutingContractValidationError on missing required fields.



## Function: is_policy_current

**Parameters**: self, current_policy_hash
**Returns**: bool
**Description**: Return False if policy changed since contract issuance.



## Function: is_expired

**Parameters**: self, current_tick
**Returns**: bool
**Description**: Return True if the contract has exceeded its expiry window.



## Function: require_valid

**Parameters**: self, current_policy_hash, current_tick
**Returns**: None
**Description**: Raise StaleRoutingContractError if contract is stale or expired.



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: record

**Parameters**: self, proposal
**Returns**: None


## Function: store

**Parameters**: self, contract
**Returns**: None


## Function: get

**Parameters**: self, routing_contract_id
**Returns**: RoutingContract | None


## Function: all_contracts

**Parameters**: self
**Returns**: list[RoutingContract]


## Function: all_proposals

**Parameters**: self
**Returns**: list[RoutingProposal]


## Usage Examples

### Class Usage

```python
# Using UngovernnedRouteError
ungovernnedrouteerror = UngovernnedRouteError()
```

```python
# Using StaleRoutingContractError
staleroutingcontracterror = StaleRoutingContractError()
```

```python
# Using RoutingContractValidationError
routingcontractvalidationerror = RoutingContractValidationError()
```

### Function Usage

```python
# Using _emit_references_policy_hash
result = _emit_references_policy_hash(routing_contract_id, policy_hash)
```

```python
# Using emit_replay_key
result = emit_replay_key(routing_contract_id, replay_key)
```

```python
# Using emit_determinism_digest
result = emit_determinism_digest(routing_contract_id, determinism_digest)
```



---
**Generated**: 2026-03-26T09:39:02.631003
**Type**: api_reference
**Quality**: comprehensive
