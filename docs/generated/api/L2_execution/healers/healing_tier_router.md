# API Documentation: healing_tier_router

**Target Audience**: developers, api_users

# healing_tier_router API Documentation

**File**: `healing_tier_router.py`
**Classes**: 1
**Functions**: 7

## Classes

- **SovereigntyViolation** (inherits from Exception)

## Functions

- **get_historical_success_rate** -> float
- **set_historical_success_rate** -> None
- **clear_historical_success_rates** -> None
- **compute_heal_confidence** -> tuple[float, tuple[str, ...]]
- **route_healing_tier** -> HealingDecision
- **route_by_confidence** -> HealingDecision
- **_compute_replay_key** -> str


## Class: SovereigntyViolation

**Description**: Raised when structural sovereignty constraints are violated.

**Inherits from**: Exception



## Function: get_historical_success_rate

**Parameters**: error_signature
**Returns**: float
**Description**: Get historical success rate, preferring live meta-learning prior.

    If a MetaPriorProvider is supplied and returns a non-neutral value it
    is used directly (Phase 1 live store path).  Otherwise falls back to
    the compile-time frozen HISTORICAL_SUCCESS_RATES for determinism.

    Args:
        error_signature: Error signature to look up
        meta_prior_provider: Optional live store seam (injected from Phase 1)

    Returns:
        Success-rate prior in [0.0, 1.0]
    



## Function: set_historical_success_rate

**Parameters**: error_signature, rate
**Returns**: None
**Description**: Override historical success rate for a specific error_signature.

    Used by tests to control scoring behavior.  The override lives in a
    module-level mutable dict and is cleared by clear_historical_success_rates.
    



## Function: clear_historical_success_rates

**Returns**: None
**Description**: Clear all test-time overrides, restoring compile-time frozen defaults.



## Function: compute_heal_confidence

**Parameters**: healing_input
**Returns**: tuple[float, tuple[str, ...]]
**Description**: Mathematically deterministic confidence calculation - zero external dependencies.

    Fixed precision arithmetic, no environment access, versioned historical data.

    Args:
        healing_input: Structured failure context
        meta_prior_provider: Optional live meta-prior provider

    Returns:
        Tuple of (confidence score in [0.0, 1.0], reason_codes tuple)
    



## Function: route_healing_tier

**Parameters**: healing_input, config
**Returns**: HealingDecision
**Description**: Mathematically deterministic tier router - absolute choke point.

    This is the SINGLE CHOKE POINT for all healing model selection.
    No environment access, no external data loading, fixed precision math.

    Args:
        healing_input: Structured failure context
        config: Optional HealingTierConfig; uses canonical X/Y constants if None
        meta_prior_provider: Optional live meta-prior provider

    Returns:
        Immutable HealingDecision with mathematical determinism guarantees
    



## Function: route_by_confidence

**Parameters**: confidence, retry_count, failure_type, error_signature, blast_radius_estimate, agent_id, config
**Returns**: HealingDecision
**Description**: Bridge: convert raw confidence float into a canonical HealingDecision.

    Wraps route_healing_tier() so legacy callers that hold only a confidence
    float (e.g. SovereignDecisionEngine, decorators_util) can delegate to the
    single choke-point without constructing a HealingInput themselves.

    Args:
        confidence: Pre-computed confidence score in [0.0, 1.0].
        retry_count: Number of prior heal attempts.
        failure_type: Canonical failure type string (maps to FAILURE_CLASS_PRIORS).
        error_signature: Error signature for historical look-up.
        blast_radius_estimate: Normalised blast radius [0.0, 1.0].
        agent_id: Optional agent identifier for allowlist check.
        config: Optional HealingTierConfig; uses canonical X/Y defaults if None.
        meta_prior_provider: Optional live meta-prior provider.

    Returns:
        Immutable HealingDecision with tier and reason_codes.
    



## Function: _compute_replay_key

**Parameters**: healing_input, decision
**Returns**: str
**Description**: Compute mathematical replay key - timestamp excluded for determinism.

    Args:
        healing_input: Input context
        decision: Routing decision

    Returns:
        Deterministic hash for replay verification
    



## Usage Examples

### Class Usage

```python
# Using SovereigntyViolation
sovereigntyviolation = SovereigntyViolation()
```

### Function Usage

```python
# Using get_historical_success_rate
result = get_historical_success_rate(error_signature)
```

```python
# Using set_historical_success_rate
result = set_historical_success_rate(error_signature, rate)
```

```python
# Using clear_historical_success_rates
result = clear_historical_success_rates()
```



---
**Generated**: 2026-03-26T09:39:03.823315
**Type**: api_reference
**Quality**: comprehensive
