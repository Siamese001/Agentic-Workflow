# API Documentation: governance_contracts

**Target Audience**: developers, api_users

# governance_contracts API Documentation

**File**: `governance_contracts.py`
**Classes**: 3
**Functions**: 9

## Classes

- **EvidencePackError** (inherits from Exception)
- **PolicyExceptionError** (inherits from Exception)
- **PolicyUpdateError** (inherits from Exception)

## Functions

- **_make_proposal_id** -> str
- **build_evidence_pack** -> EvidencePack
- **validate_evidence_pack** -> EvidencePack
- **build_hil_evidence_pack** -> EvidencePack
- **emit_policy_exception** -> PolicyExceptionArtifact
- **validate_policy_exception_tick** -> bool
- **propose_policy_update** -> PolicyUpdateProposal
- **validate_proposal** -> PolicyUpdateProposal
- **build_hil_policy_proposal** -> PolicyUpdateProposal


## Class: EvidencePackError

**Description**: Raised when EvidencePack construction fails (fail-closed).

**Inherits from**: Exception



## Class: PolicyExceptionError

**Description**: Raised when PolicyExceptionArtifact construction or validation fails.

**Inherits from**: Exception



## Class: PolicyUpdateError

**Description**: Raised when PolicyUpdateProposal construction or validation fails.

**Inherits from**: Exception



## Function: _make_proposal_id

**Parameters**: trace_id
**Returns**: str
**Description**: REQ-111: deterministic ID derived from trace_id; no uuid4.



## Function: build_evidence_pack

**Parameters**: trace_id, action_trace, policy_evals, risk_score, budget_breach_data, boundary_snapshot_hash
**Returns**: EvidencePack
**Description**: §3.4 — Build a structured EvidencePack for human escalation.

    Fail-closed: any invalid field raises EvidencePackError.
    



## Function: validate_evidence_pack

**Parameters**: pack
**Returns**: EvidencePack
**Description**: §3.4 — Validate that an object is a well-formed EvidencePack.



## Function: build_hil_evidence_pack

**Parameters**: trace_id, escalation_reason, route_decision_ref, policy_snapshot_data, risk_score, action_trace, policy_evals, guardian_results, ssot_hash, attachments, semantic_clock
**Returns**: EvidencePack
**Description**: §Wave2.2 — Build a full EvidencePack for HIL escalation.

    Fail-closed: any invalid field raises EvidencePackError.
    



## Function: emit_policy_exception

**Parameters**: trace_id, exception_scope, semantic_clock_tick, issuer_signature, nonce
**Returns**: PolicyExceptionArtifact
**Description**: §3.7 — Emit a PolicyExceptionArtifact for a policy challenge.

    Generates a cryptographic nonce if not provided.
    Fail-closed: any invalid field raises PolicyExceptionError.
    



## Function: validate_policy_exception_tick

**Parameters**: artifact, current_tick
**Returns**: bool
**Description**: §3.7 — Validate that a policy exception is valid for the current tick.

    An exception is valid ONLY for the semantic clock tick it was issued at.
    Returns True if valid, raises PolicyExceptionError if expired.
    



## Function: propose_policy_update

**Parameters**: trace_id, override_id, proposed_policy_diff, originating_agent, semantic_clock_tick
**Returns**: PolicyUpdateProposal
**Description**: §3.5 — Emit a PolicyUpdateProposal for bidirectional feedback.

    Emitted when a human override occurs, proposing a policy change
    back to the Policy Update Mechanism.
    Fail-closed: any invalid field raises PolicyUpdateError.
    



## Function: validate_proposal

**Parameters**: proposal
**Returns**: PolicyUpdateProposal
**Description**: §3.5 — Validate that an object is a well-formed PolicyUpdateProposal.



## Function: build_hil_policy_proposal

**Parameters**: trace_id, evidence_pack_id, hil_outcome, reviewer_id, review_notes, request_id, file_scope, confidence, semantic_clock
**Returns**: PolicyUpdateProposal
**Description**: §Wave2.3 — Build a PolicyUpdateProposal from HIL review outcome.

    Uses a deterministic mapping table from HILOutcome to ProposedPolicyChange
    entries. If no structured reason exists, proposed_changes is empty but
    rationale must explain why.

    Fail-closed: any invalid field raises PolicyUpdateError.
    



## Usage Examples

### Class Usage

```python
# Using EvidencePackError
evidencepackerror = EvidencePackError()
```

```python
# Using PolicyExceptionError
policyexceptionerror = PolicyExceptionError()
```

```python
# Using PolicyUpdateError
policyupdateerror = PolicyUpdateError()
```

### Function Usage

```python
# Using _make_proposal_id
result = _make_proposal_id(trace_id)
```

```python
# Using build_evidence_pack
result = build_evidence_pack(trace_id, action_trace)
```

```python
# Using validate_evidence_pack
result = validate_evidence_pack(pack)
```



---
**Generated**: 2026-03-26T09:39:02.620229
**Type**: api_reference
**Quality**: comprehensive
