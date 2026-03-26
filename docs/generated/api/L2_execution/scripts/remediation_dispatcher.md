# API Documentation: remediation_dispatcher

**Target Audience**: developers, api_users

# remediation_dispatcher API Documentation

**File**: `remediation_dispatcher.py`
**Classes**: 5
**Functions**: 19

## Classes

- **EscalationDecisionReason** (inherits from Enum)
- **CanonicalEscalationPayload**
- **EscalationContext**
- **ApprovalGatingError** (inherits from Exception)
- **MutationGuardError** (inherits from Exception)

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **_get_approval_types**
- **mutation_allowed** -> bool
- **validate_phase_names** -> None
- **approvals_satisfy_phase** -> bool
- **classify_check_ids** -> tuple[set[str], set[str]]
- **extract_check_ids** -> list[str]
- **extract_checks_by_id** -> dict[str, dict]
- **extract_healable_items_from_guardian_check** -> tuple[tuple[str, dict[str, Any]], ...]
- **build_healer_worklist** -> tuple[tuple[str, dict[str, Any]], ...]
- **load_approval_bundle** -> ApprovalBundle
- **_tier_escalate** -> str
- **_invoke_healer** -> HealCheckResult
- **run_dispatcher** -> CombinedHealResult
- **main** -> int
- **to_dict** -> dict[str, Any]
- **to_canonical_string** -> str
- **from_result** -> EscalationContext


## Class: EscalationDecisionReason

**Description**: Canonical reasons for tier escalation decisions.

**Inherits from**: Enum



## Class: CanonicalEscalationPayload

**Description**: Canonical, deterministic escalation payload for audit trails.

    This payload is stable across runs for identical inputs and contains
    all essential decision metadata without transient identifiers.
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dict with sorted keys for deterministic serialization.

#### to_canonical_string
**Parameters**: self
**Returns**: str
**Description**: Return deterministic string representation for comparison.



## Class: EscalationContext

**Description**: Structured escalation payload built from a failed HealCheckResult.

    This is the SSOT for what gets passed to FailureSignal — never build
    FailureSignal directly from free-text notes.

    Attributes:
        check_id: The check_id that failed.
        healer_name: Canonical healer identity (same as check_id for now).
        retry_count: Monotonic retry counter from _invoke_healer.
        failure_type: Stable category string (from escalation_hint or default).
        blast_radius_estimate: Float in [0.0, 1.0] (from hint or default 0.5).
        summary: Short human-readable summary (from notes, truncated).
        trace_id: Deterministic SHA-256 prefix of (check_id, retry_count).
    

### Methods

#### from_result
**Parameters**: cls, check_id, result, retry_count
**Returns**: EscalationContext
**Description**: Build deterministically from a HealCheckResult with strict parsing.



## Class: ApprovalGatingError

**Description**: Raised when a phase requires approval but none was provided.

**Inherits from**: Exception



## Class: MutationGuardError

**Description**: Raised when apply mode is used without sandbox or explicit override.

**Inherits from**: Exception



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: payload, target


## Function: _get_approval_types

**Description**: Lazy load approval types to avoid upward import.



## Function: mutation_allowed

**Parameters**: repo_root, allow_override
**Returns**: bool
**Description**: Check if mutations are permitted in the given repo root.

    Mutations allowed iff:
    - repo_root contains the sandbox sentinel file, OR
    - allow_override is True (--allow-repo-mutation)
    



## Function: validate_phase_names

**Parameters**: plan
**Returns**: None
**Description**: Validate that plan phase names exactly match the expected canonical list.

    Raises ValueError if names differ in count, order, or content.
    



## Function: approvals_satisfy_phase

**Parameters**: bundle, phase_name
**Returns**: bool
**Description**: Check whether the approval bundle satisfies gating for a phase.

    Returns True iff bundle contains at least one record where:
    - record.phase_name == phase_name
    - record.decision == APPROVED
    - record.token is non-empty
    



## Function: classify_check_ids

**Parameters**: check_ids, phase_prefixes
**Returns**: tuple[set[str], set[str]]
**Description**: Classify check_ids into mapped and unmapped sets.

    A check_id is "mapped" if it startswith any prefix in any phase mapping.

    Returns (mapped, unmapped) sets.
    



## Function: extract_check_ids

**Parameters**: guardian_aggregate
**Returns**: list[str]
**Description**: Extract check_ids from a guardian aggregate result deterministically.

    Supports the canonical aggregate shape produced by run_all_guardians:
    - top-level "checks" list of dicts, each with "check_id"

    Returns sorted, deduplicated list of check_ids.
    Raises ValueError for unrecognised shapes.
    



## Function: extract_checks_by_id

**Parameters**: guardian_aggregate
**Returns**: dict[str, dict]
**Description**: Build a lookup from check_id to full check dict.

    For duplicate check_ids, the first occurrence wins.
    



## Function: extract_healable_items_from_guardian_check

**Parameters**: check
**Returns**: tuple[tuple[str, dict[str, Any]], ...]
**Description**: Extract healable (sub_check_id, evidence_dict) pairs from a roll-up check.

    Supported evidence shapes (defensive):
    1. evidence.checks is list[dict] with "check_id" and optional "evidence" keys.
    2. evidence.violations is dict keyed by sub_check_id -> list/obj.
    3. Otherwise returns empty tuple.

    Returns tuple sorted by sub_check_id.
    



## Function: build_healer_worklist

**Parameters**: aggregate_checks
**Returns**: tuple[tuple[str, dict[str, Any]], ...]
**Description**: Build a deduplicated, sorted worklist of (check_id, check_dict) pairs.

    For each roll-up check:
    - If roll-up check_id itself exists in HEALER_REGISTRY, include it.
    - Also include extracted sub-items where sub_check_id exists in HEALER_REGISTRY.
    Deduplicate by check_id (roll-up form wins over sub-check form).
    Stable sort final tuple by check_id.
    



## Function: load_approval_bundle

**Parameters**: path
**Returns**: ApprovalBundle
**Description**: Load and return an ApprovalBundle from a JSON file.



## Function: _tier_escalate

**Parameters**: check_id, result
**Returns**: str
**Description**: Escalate a FAILED heal result to the confidence-tier LLM system.

    Guards:
      1. result.status must be FAILED (explicit check)
      2. result.needs_llm_escalation must be True (healer opt-in)
      3. (check_id, healer_name) must be in HEALER_ESCALATION_ALLOWLIST
      4. registered healer identity must match expected healer_name

    Builds a FailureSignal from EscalationContext (never from raw notes),
    calls dispatch_healing, and returns a deterministic audit note string.

    Args:
        check_id: The check_id that failed healing.
        result: The FAILED HealCheckResult from the healer.
        retry_count: Monotonic retry counter (drives tier selection).
        invoker: Injectable provider invoker (default: DefaultHealingProviderInvoker).

    Returns:
        A deterministic audit note string, or a skip note if guards block.
    



## Function: _invoke_healer

**Parameters**: check_id, check_dict
**Returns**: HealCheckResult
**Description**: Invoke a registered healer safely, converting errors to FAILED results.

    Passes repo_root and apply as keyword arguments to healers that accept them.
    Returns the healer's HealCheckResult on success, or a FAILED result
    containing the exception class name on error.

    When a healer returns FAILED AND sets needs_llm_escalation=True AND its
    check_id is in HEALER_ESCALATION_ALLOWLIST, escalates to the confidence-tier
    LLM system via _tier_escalate, appending the audit note to result.notes.

    Re-entrancy: retry_count must be incremented by the caller on each retry.
    _tier_escalate is side-effect bounded (no writes, no recursion).
    



## Function: run_dispatcher

**Parameters**: guardian_result_path, write_artifacts_dir, created_utc, plan_name, approval_bundle_path
**Returns**: CombinedHealResult
**Description**: Execute the dispatcher interpreting LEGACY_MIRROR_PLAN PhaseSpec.

    1. Validates PhaseSpec name integrity.
    2. Enforces mutation guard if apply mode requested.
    3. Loads the guardian aggregate and extracts check_ids.
    4. Loads optional ApprovalBundle (needed before phase iteration for gating).
    5. Classifies check_ids as mapped or unmapped via phase prefix mapping.
    6. Iterates phases in order, enforcing approval gating.
    7. Produces a CombinedHealResult.
    8. Validates and writes the result to the output directory.

    Returns the CombinedHealResult.
    Raises ApprovalGatingError if a phase requires approval and none is provided.
    Raises MutationGuardError if apply without sandbox or override.
    



## Function: main

**Returns**: int


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dict with sorted keys for deterministic serialization.



## Function: to_canonical_string

**Parameters**: self
**Returns**: str
**Description**: Return deterministic string representation for comparison.



## Function: from_result

**Parameters**: cls, check_id, result, retry_count
**Returns**: EscalationContext
**Description**: Build deterministically from a HealCheckResult with strict parsing.



## Usage Examples

### Class Usage

```python
# Using EscalationDecisionReason
escalationdecisionreason = EscalationDecisionReason()
```

```python
# Using CanonicalEscalationPayload
canonicalescalationpayload = CanonicalEscalationPayload()
canonicalescalationpayload.to_dict()
canonicalescalationpayload.to_canonical_string()
```

```python
# Using EscalationContext
escalationcontext = EscalationContext()
escalationcontext.from_result()
```

### Function Usage

```python
# Using _invoke_authorize_and_execute
result = _invoke_authorize_and_execute(execution_context, target_callable)
```

```python
# Using _make_execution_context
result = _make_execution_context(payload, target)
```

```python
# Using _get_approval_types
result = _get_approval_types()
```



---
**Generated**: 2026-03-26T09:39:03.897386
**Type**: api_reference
**Quality**: comprehensive
