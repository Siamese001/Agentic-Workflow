# API Documentation: governance_types

**Target Audience**: developers, api_users

# governance_types API Documentation

**File**: `governance_types.py`
**Classes**: 11
**Functions**: 4

## Classes

- **RouteDecisionRef**
- **PolicySnapshot**
- **EvidencePack**
- **ExceptionScope** (inherits from Enum)
- **PolicyExceptionArtifact**
- **ProposalStatus** (inherits from Enum)
- **HILOutcome** (inherits from Enum)
- **HILReviewOutcome**
- **ChangeAction** (inherits from Enum)
- **ProposedPolicyChange**
- **PolicyUpdateProposal**

## Functions

- **__post_init__** -> None
- **__post_init__** -> None
- **is_expired** -> bool
- **__post_init__** -> None


## Class: RouteDecisionRef

**Description**: §Wave2.2 — Essential subset of a RouteDecisionArtifact for cross-layer linking.



## Class: PolicySnapshot

**Description**: §Wave2.2 — Policy state at the time of escalation.



## Class: EvidencePack

**Description**: §3.4 — Structured evidence for human escalation.

    Generated when a routing decision reaches HUMAN_REVIEW.
    Contains the full action trace, policy evaluations, risk score,
    budget breach data, and an immutable boundary snapshot hash.

    Wave 2.2 extension: evidence_id, timestamp_utc, escalation_reason,
    route_decision_ref, guardian_results, policy_snapshot_data, ssot_hash,
    attachments — all optional (defaults) to preserve backward compat.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: ExceptionScope

**Description**: Valid scopes for a policy exception.

**Inherits from**: Enum



## Class: PolicyExceptionArtifact

**Description**: §3.7 — Policy exception issued by a human to override a Block decision.

    Valid only for the current semantic clock tick. The nonce ensures
    single-use and prevents replay attacks.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### is_expired
**Parameters**: self, now_tick
**Returns**: bool
**Description**: REQ-245: return True if this exception has expired per semantic clock.

        If ttl_ticks == 0 the exception has no TTL and never expires.
        Expired when now_tick > semantic_clock_tick + ttl_ticks.
        



## Class: ProposalStatus

**Description**: Status of a policy update proposal.

**Inherits from**: Enum



## Class: HILOutcome

**Description**: §Wave2.3 — Human-in-the-Loop decision outcomes.

**Inherits from**: Enum



## Class: HILReviewOutcome

**Description**: §P4.W9 — REQ-085/086: HIL review record with reviewer signature.

    Carries the reviewer identity and cryptographic signature for audit.
    MODIFY_DIFF decision requires L5 re-clearance (requires_l5_reclear=True).
    



## Class: ChangeAction

**Description**: §Wave2.3 — Actions that can be proposed for a policy change.

**Inherits from**: Enum



## Class: ProposedPolicyChange

**Description**: §Wave2.3 — A single proposed change to a policy rule or configuration.



## Class: PolicyUpdateProposal

**Description**: §3.5 — Bidirectional feedback from human override back to policy layer.

    Emitted when a human override occurs, proposing a policy diff
    that the Policy Update Mechanism (L0/L5) should evaluate.

    Wave 2.3 extension: proposal_id, timestamp_utc, evidence_pack_id,
    hil_outcome, proposed_changes, rationale, proposer, confidence —
    all optional (defaults) to preserve backward compat.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: is_expired

**Parameters**: self, now_tick
**Returns**: bool
**Description**: REQ-245: return True if this exception has expired per semantic clock.

        If ttl_ticks == 0 the exception has no TTL and never expires.
        Expired when now_tick > semantic_clock_tick + ttl_ticks.
        



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using RouteDecisionRef
routedecisionref = RouteDecisionRef()
```

```python
# Using PolicySnapshot
policysnapshot = PolicySnapshot()
```

```python
# Using EvidencePack
evidencepack = EvidencePack()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using is_expired
result = is_expired(now_tick)
```



---
**Generated**: 2026-03-26T09:39:03.441590
**Type**: api_reference
**Quality**: comprehensive
