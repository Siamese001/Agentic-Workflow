# API Documentation: human_review_queue_enforcer

**Target Audience**: developers, api_users

# human_review_queue_enforcer API Documentation

**File**: `human_review_queue_enforcer.py`
**Classes**: 6
**Functions**: 18

## Classes

- **ReviewStatus** (inherits from Enum)
- **ProposedDiff**
- **SimulatedOutcome**
- **ContextBundle**
- **ReviewRequest**
- **HumanReviewQueue**

## Functions

- **to_unified_diff** -> str
- **to_dict** -> dict[str, Any]
- **is_expired** -> bool
- **to_dict** -> dict[str, Any]
- **__init__**
- **submit_for_review** -> ReviewRequest
- **approve** -> tuple[ReviewRequest, HumanDecisionArtifact]
- **reject** -> tuple[ReviewRequest, HumanDecisionArtifact]
- **modify_diff** -> HumanDecisionArtifact
- **escalate** -> ReviewRequest
- **get_pending_requests** -> list[dict[str, Any]]
- **get_request_status** -> ReviewStatus | None
- **register_callback** -> None
- **_evict_oldest** -> None
- **_process_expired** -> None
- **_trigger_callback** -> None
- **_emit_policy_update_proposal** -> None
- **get_queue_stats** -> dict[str, Any]


## Class: ReviewStatus

**Description**: Status of a review request.

**Inherits from**: Enum



## Class: ProposedDiff

**Description**: Proposed code change for review.

### Methods

#### to_unified_diff
**Parameters**: self
**Returns**: str
**Description**: Generate unified diff format.



## Class: SimulatedOutcome

**Description**: Simulated outcome of applying the proposed fix.



## Class: ContextBundle

**Description**: Rich context bundle for human review.

    Contains all information needed for informed human decision:
    - Detection signal details
    - Proposed diff
    - AI rationale
    - Simulated outcome
    - Risk assessment
    - Historical similar cases
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: ReviewRequest

**Description**: Human review request with full context.

### Methods

#### is_expired
**Parameters**: self
**Returns**: bool
**Description**: Check if request has timed out.

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: HumanReviewQueue

**Description**: Approval queue for high-risk fixes requiring human review.

    Implements the HUMAN REVIEW GATE from target state architecture.
    Thread-safe queue management with escalation support.

    Features:
    - Rich context bundles for informed decisions
    - Escalation workflow
    - Timeout handling
    - Callback support for async workflows
    

### Methods

#### __init__
**Parameters**: self, config

#### submit_for_review
**Parameters**: self, context_bundle, timeout_seconds
**Returns**: ReviewRequest
**Description**: Submit a change for human review.

        Args:
            context_bundle: Full context for review decision
            timeout_seconds: Custom timeout for this request

        Returns:
            ReviewRequest tracking the submission
        

#### approve
**Parameters**: self, request_id, reviewer_id, notes, secret, original_plan_hash, policy_hash
**Returns**: tuple[ReviewRequest, HumanDecisionArtifact]
**Description**: Approve a pending review request.

        Returns (ReviewRequest, signed HumanDecisionArtifact).
        

#### reject
**Parameters**: self, request_id, reviewer_id, notes, secret, original_plan_hash, policy_hash
**Returns**: tuple[ReviewRequest, HumanDecisionArtifact]
**Description**: Reject a pending review request.

        Returns (ReviewRequest, signed HumanDecisionArtifact).
        

#### modify_diff
**Parameters**: self, request_id, reviewer_id, structured_patch_schema, original_plan_hash, secret
**Returns**: HumanDecisionArtifact
**Description**: Record a MODIFY_DIFF decision.

        Returns a HumanDecisionArtifact bound to original_plan_hash.
        The artifact's l5_reclear_required flag will be True.
        

#### escalate
**Parameters**: self, request_id, reason
**Returns**: ReviewRequest
**Description**: Escalate request to next level in escalation chain.

#### get_pending_requests
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get all pending review requests.

#### get_request_status
**Parameters**: self, request_id
**Returns**: ReviewStatus | None
**Description**: Get status of a specific request.

#### register_callback
**Parameters**: self, request_id, callback
**Returns**: None
**Description**: Register callback for when request is resolved.

#### _evict_oldest
**Parameters**: self
**Returns**: None
**Description**: Evict oldest pending request.

#### _process_expired
**Parameters**: self
**Returns**: None
**Description**: Process expired requests.

#### _trigger_callback
**Parameters**: self, request_id, action
**Returns**: None
**Description**: Trigger registered callback.

#### _emit_policy_update_proposal
**Parameters**: self, request, outcome
**Returns**: None
**Description**: §Wave2.3 — Build and emit PolicyUpdateProposal after HIL finalization.

#### get_queue_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get queue statistics for observability.



## Function: to_unified_diff

**Parameters**: self
**Returns**: str
**Description**: Generate unified diff format.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: is_expired

**Parameters**: self
**Returns**: bool
**Description**: Check if request has timed out.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: __init__

**Parameters**: self, config


## Function: submit_for_review

**Parameters**: self, context_bundle, timeout_seconds
**Returns**: ReviewRequest
**Description**: Submit a change for human review.

        Args:
            context_bundle: Full context for review decision
            timeout_seconds: Custom timeout for this request

        Returns:
            ReviewRequest tracking the submission
        



## Function: approve

**Parameters**: self, request_id, reviewer_id, notes, secret, original_plan_hash, policy_hash
**Returns**: tuple[ReviewRequest, HumanDecisionArtifact]
**Description**: Approve a pending review request.

        Returns (ReviewRequest, signed HumanDecisionArtifact).
        



## Function: reject

**Parameters**: self, request_id, reviewer_id, notes, secret, original_plan_hash, policy_hash
**Returns**: tuple[ReviewRequest, HumanDecisionArtifact]
**Description**: Reject a pending review request.

        Returns (ReviewRequest, signed HumanDecisionArtifact).
        



## Function: modify_diff

**Parameters**: self, request_id, reviewer_id, structured_patch_schema, original_plan_hash, secret
**Returns**: HumanDecisionArtifact
**Description**: Record a MODIFY_DIFF decision.

        Returns a HumanDecisionArtifact bound to original_plan_hash.
        The artifact's l5_reclear_required flag will be True.
        



## Function: escalate

**Parameters**: self, request_id, reason
**Returns**: ReviewRequest
**Description**: Escalate request to next level in escalation chain.



## Function: get_pending_requests

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get all pending review requests.



## Function: get_request_status

**Parameters**: self, request_id
**Returns**: ReviewStatus | None
**Description**: Get status of a specific request.



## Function: register_callback

**Parameters**: self, request_id, callback
**Returns**: None
**Description**: Register callback for when request is resolved.



## Function: _evict_oldest

**Parameters**: self
**Returns**: None
**Description**: Evict oldest pending request.



## Function: _process_expired

**Parameters**: self
**Returns**: None
**Description**: Process expired requests.



## Function: _trigger_callback

**Parameters**: self, request_id, action
**Returns**: None
**Description**: Trigger registered callback.



## Function: _emit_policy_update_proposal

**Parameters**: self, request, outcome
**Returns**: None
**Description**: §Wave2.3 — Build and emit PolicyUpdateProposal after HIL finalization.



## Function: get_queue_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get queue statistics for observability.



## Usage Examples

### Class Usage

```python
# Using ReviewStatus
reviewstatus = ReviewStatus()
```

```python
# Using ProposedDiff
proposeddiff = ProposedDiff()
proposeddiff.to_unified_diff()
```

```python
# Using SimulatedOutcome
simulatedoutcome = SimulatedOutcome()
```

### Function Usage

```python
# Using to_unified_diff
result = to_unified_diff()
```

```python
# Using to_dict
result = to_dict()
```

```python
# Using is_expired
result = is_expired()
```



---
**Generated**: 2026-03-26T09:39:04.850633
**Type**: api_reference
**Quality**: comprehensive
