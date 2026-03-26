# API Documentation: execution_guardrail_chokepoint

**Target Audience**: developers, api_users

# execution_guardrail_chokepoint API Documentation

**File**: `execution_guardrail_chokepoint.py`
**Classes**: 5
**Functions**: 11

## Classes

- **GuardrailDenied** (inherits from PermissionError)
- **MissingCapabilityToken** (inherits from PermissionError)
- **MissingPolicyHash** (inherits from PermissionError)
- **HumanReviewRequired** (inherits from PermissionError)
- **ExecutionBypassAttempt** (inherits from RuntimeError)

## Functions

- **_emit_applies_guardrail** -> None
- **_emit_validated_by_safety_plane** -> None
- **_emit_references_policy_hash** -> None
- **_emit_execution_terminates_at_uwg** -> None
- **_emit_reenters_safety** -> None
- **_emit_requires_human_review** -> None
- **_emit_records_execution_trace** -> None
- **_emit_signs_execution_trace** -> None
- **_evaluate_guardrail** -> GuardrailOutcome
- **_make_decision_hash** -> str
- **authorize_and_execute** -> tuple[Any, ExecutionContext]


## Class: GuardrailDenied

**Description**: Execution denied by guardrail. ADG edge: reenters_safety

**Inherits from**: PermissionError



## Class: MissingCapabilityToken

**Description**: No capability token provided. Fail-closed.

**Inherits from**: PermissionError



## Class: MissingPolicyHash

**Description**: No policy hash bound to execution context. Fail-closed.

**Inherits from**: PermissionError



## Class: HumanReviewRequired

**Description**: HUMAN_GATED action attempted without human approval.
    ADG edge: requires_human_review
    

**Inherits from**: PermissionError



## Class: ExecutionBypassAttempt

**Description**: Direct execution outside authorize_and_execute() detected.

**Inherits from**: RuntimeError



## Function: _emit_applies_guardrail

**Parameters**: ctx, outcome
**Returns**: None
**Description**: ADG edge: applies_guardrail



## Function: _emit_validated_by_safety_plane

**Parameters**: ctx
**Returns**: None
**Description**: ADG edge: validated_by_safety_plane



## Function: _emit_references_policy_hash

**Parameters**: ctx
**Returns**: None
**Description**: ADG edge: references_policy_hash



## Function: _emit_execution_terminates_at_uwg

**Parameters**: ctx
**Returns**: None
**Description**: ADG edge: execution_terminates_at_uwg



## Function: _emit_reenters_safety

**Parameters**: ctx, reason
**Returns**: None
**Description**: ADG edge: reenters_safety



## Function: _emit_requires_human_review

**Parameters**: ctx
**Returns**: None
**Description**: ADG edge: requires_human_review



## Function: _emit_records_execution_trace

**Parameters**: ctx
**Returns**: None
**Description**: ADG edge: records_execution_trace



## Function: _emit_signs_execution_trace

**Parameters**: ctx, output_hash
**Returns**: None
**Description**: ADG edge: signs_execution_trace



## Function: _evaluate_guardrail

**Parameters**: ctx, target_name
**Returns**: GuardrailOutcome
**Description**: Evaluate guardrail for execution context.

    Returns GuardrailOutcome. Only ALLOW may proceed.
    Calls _emit_validated_by_safety_plane when safety plane is available.
    



## Function: _make_decision_hash

**Parameters**: ctx, outcome
**Returns**: str


## Function: authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload
**Returns**: tuple[Any, ExecutionContext]
**Description**: Mandatory L2 execution chokepoint — P0/L2 enforcement.

    Args:
        execution_context:      Validated run-scoped ExecutionContext.
        target_callable:        The callable to execute (only on ALLOW).
        capability_token:       Token proving authority (must match ctx.capability_token).
        payload:                Execution payload passed to target_callable.
        target_name:            Human-readable target identifier for guardrail.
        human_approved:         Must be True for HUMAN_GATED actions.
        safety_plane_available: If False, guardrail returns ERROR (fail-closed).
        uwg_callable:           If provided, MUTATION actions route through this.

    Returns:
        (output, bound_context) — execution result and context with decision bound.

    Raises:
        MissingCapabilityToken:  token missing or mismatched.
        MissingPolicyHash:       no policy hash on context.
        HumanReviewRequired:     HUMAN_GATED without human_approved.
        GuardrailDenied:         guardrail returned DENY/ERROR/TIMEOUT/UNKNOWN.
        ValueError:              invalid execution_context.
    



## Usage Examples

### Class Usage

```python
# Using GuardrailDenied
guardraildenied = GuardrailDenied()
```

```python
# Using MissingCapabilityToken
missingcapabilitytoken = MissingCapabilityToken()
```

```python
# Using MissingPolicyHash
missingpolicyhash = MissingPolicyHash()
```

### Function Usage

```python
# Using _emit_applies_guardrail
result = _emit_applies_guardrail(ctx, outcome)
```

```python
# Using _emit_validated_by_safety_plane
result = _emit_validated_by_safety_plane(ctx)
```

```python
# Using _emit_references_policy_hash
result = _emit_references_policy_hash(ctx)
```



---
**Generated**: 2026-03-26T09:39:03.694852
**Type**: api_reference
**Quality**: comprehensive
