# API Documentation: policy_action_contract

**Target Audience**: developers, api_users

# policy_action_contract API Documentation

**File**: `policy_action_contract.py`
**Classes**: 4
**Functions**: 15

## Classes

- **PolicyOutcome** (inherits from str, Enum)
- **ActionClass** (inherits from str, Enum)
- **PolicyDecisionArtifact**
- **PolicyEnforcementError** (inherits from PermissionError)

## Functions

- **_record_artifact** -> None
- **get_decision_artifacts** -> list[PolicyDecisionArtifact]
- **_get_trace_id** -> str
- **_resolve_policy_hash** -> str
- **_run_safety_plane** -> PolicyOutcome
- **_apply_guardrail_check** -> PolicyOutcome
- **_escalate_to_hitl** -> PolicyDecisionArtifact
- **enforce_policy_before_action** -> PolicyDecisionArtifact
- **proceeds** -> bool
- **needs_hitl** -> bool
- **requires_safety_plane** -> bool
- **requires_human_review** -> bool
- **is_valid** -> bool
- **build** -> PolicyDecisionArtifact
- **__init__** -> None


## Class: PolicyOutcome

**Description**: Allowed policy outcomes. Only ALLOW proceeds automatically.

**Inherits from**: str, Enum

### Methods

#### proceeds
**Parameters**: self
**Returns**: bool
**Description**: True only for ALLOW — all other outcomes are fail-closed.

#### needs_hitl
**Parameters**: self
**Returns**: bool



## Class: ActionClass

**Description**: Minimum policy-binding action classes (§5).

**Inherits from**: str, Enum

### Methods

#### requires_safety_plane
**Parameters**: self
**Returns**: bool
**Description**: High-risk classes that must bind to safety plane (§7).

#### requires_human_review
**Parameters**: self
**Returns**: bool



## Class: PolicyDecisionArtifact

**Description**: Immutable enforcement record attached to every governed action (§1).

    All 9 required fields must be non-empty for the artifact to be valid.
    

### Methods

#### is_valid
**Parameters**: self
**Returns**: bool
**Description**: Returns True only if all 9 required fields are populated.

#### build
**Parameters**: cls, policy_hash, policy_version, action_class, decision_outcome, reason, trace_id, actor_id, run_id
**Returns**: PolicyDecisionArtifact



## Class: PolicyEnforcementError

**Description**: Raised when a policy enforcement decision blocks an action.

**Inherits from**: PermissionError

### Methods

#### __init__
**Parameters**: self, artifact, reason
**Returns**: None



## Function: _record_artifact

**Parameters**: artifact
**Returns**: None


## Function: get_decision_artifacts

**Returns**: list[PolicyDecisionArtifact]
**Description**: Return all recorded decision artifacts (for auditing).



## Function: _get_trace_id

**Returns**: str


## Function: _resolve_policy_hash

**Parameters**: policy_hash, actor_id
**Returns**: str
**Description**: Resolve active policy_hash — emits references_policy_hash ADG edge.



## Function: _run_safety_plane

**Parameters**: action_class, action_name, policy_hash, actor_id, trace_id, metadata
**Returns**: PolicyOutcome
**Description**: Query safety plane for high-risk actions — emits validated_by_safety_plane.

    Uses ``authorize_and_execute`` symbol which the ADG scanner maps to
    both ``validated_by_safety_plane`` and ``applies_guardrail``.
    



## Function: _apply_guardrail_check

**Parameters**: action_class, action_name, policy_hash, actor_id, trace_id
**Returns**: PolicyOutcome
**Description**: Apply guardrail check — emits applies_guardrail ADG edge via GuardrailGate.



## Function: _escalate_to_hitl

**Parameters**: artifact, action_name
**Returns**: PolicyDecisionArtifact
**Description**: Route to HITL gate — emits requires_human_review + escalates_to_human.



## Function: enforce_policy_before_action

**Parameters**: action_name, action_class, actor_id, run_id, policy_hash, policy_version, metadata
**Returns**: PolicyDecisionArtifact
**Description**: Mandatory policy enforcement wrapper (§3).

    Steps:
    1. Resolve active policy hash (→ references_policy_hash)
    2. Classify action type (already provided via ActionClass)
    3. Apply guardrail check (→ applies_guardrail via GuardrailGate)
    4. Query safety plane if required class (→ validated_by_safety_plane via authorize_and_execute)
    5. Produce ALLOW / DENY / REQUIRE_HUMAN_REVIEW decision
    6. Attach decision to trace
    7. Block action if decision not ALLOW (→ raise PolicyEnforcementError)

    Hard rule (§4): ERROR / TIMEOUT / UNKNOWN → block (fail-closed).
    Hard rule (§1): artifact must have all 9 fields.

    Returns PolicyDecisionArtifact with decision_outcome=ALLOW when action may proceed.
    Raises PolicyEnforcementError otherwise.
    



## Function: proceeds

**Parameters**: self
**Returns**: bool
**Description**: True only for ALLOW — all other outcomes are fail-closed.



## Function: needs_hitl

**Parameters**: self
**Returns**: bool


## Function: requires_safety_plane

**Parameters**: self
**Returns**: bool
**Description**: High-risk classes that must bind to safety plane (§7).



## Function: requires_human_review

**Parameters**: self
**Returns**: bool


## Function: is_valid

**Parameters**: self
**Returns**: bool
**Description**: Returns True only if all 9 required fields are populated.



## Function: build

**Parameters**: cls, policy_hash, policy_version, action_class, decision_outcome, reason, trace_id, actor_id, run_id
**Returns**: PolicyDecisionArtifact


## Function: __init__

**Parameters**: self, artifact, reason
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using PolicyOutcome
policyoutcome = PolicyOutcome()
policyoutcome.proceeds()
policyoutcome.needs_hitl()
```

```python
# Using ActionClass
actionclass = ActionClass()
actionclass.requires_safety_plane()
actionclass.requires_human_review()
```

```python
# Using PolicyDecisionArtifact
policydecisionartifact = PolicyDecisionArtifact()
policydecisionartifact.is_valid()
policydecisionartifact.build()
```

### Function Usage

```python
# Using _record_artifact
result = _record_artifact(artifact)
```

```python
# Using get_decision_artifacts
result = get_decision_artifacts()
```

```python
# Using _get_trace_id
result = _get_trace_id()
```



---
**Generated**: 2026-03-26T09:39:04.896291
**Type**: api_reference
**Quality**: comprehensive
