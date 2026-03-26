# API Documentation: reasoning_policy_engine

**Target Audience**: developers, api_users

# reasoning_policy_engine API Documentation

**File**: `reasoning_policy_engine.py`
**Classes**: 2
**Functions**: 12

## Classes

- **RequestStructureFeatures**
- **ReasoningPolicyEngine**

## Functions

- **_get_routing_gateway**
- **_get_proof_emitter**
- **compute_complexity_score** -> float
- **select_tier** -> ReasoningTier
- **_build_stage_budgets** -> tuple[StageTokenBudget, ...]
- **compute_policy_config_hash** -> str
- **__post_init__** -> None
- **__init__** -> None
- **policy_hash** -> str
- **compute_tier** -> ReasoningTier
- **build_profile** -> ReasoningIntensityProfile
- **compute_and_stamp** -> SignedExecutionEnvelope


## Class: RequestStructureFeatures

**Description**: Capturable structural features of an incoming request.

    ALL fields must be derivable from the request payload itself or from
    known L0/L4 state.  No embedding similarity, no C0 content analysis.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: ReasoningPolicyEngine

**Description**: L0 authoritative engine that computes and stamps ReasoningIntensityProfile.

    Usage:
        engine = ReasoningPolicyEngine(policy_config={"version": "1.0.0"})
        envelope = engine.compute_and_stamp(features, route_decision)

    Determinism guarantee:
        engine.compute_and_stamp(features_A, route_A) always returns the
        same SignedExecutionEnvelope for the same (features_A, route_A).
    

### Methods

#### __init__
**Parameters**: self, policy_config
**Returns**: None

#### policy_hash
**Parameters**: self
**Returns**: str

#### compute_tier
**Parameters**: self, features
**Returns**: ReasoningTier
**Description**: Compute reasoning tier from structural features (pure function).

#### build_profile
**Parameters**: self, features, tier
**Returns**: ReasoningIntensityProfile
**Description**: Construct a versioned, hash-bound ReasoningIntensityProfile.

#### compute_and_stamp
**Parameters**: self, features, route_decision, enforcement_constraints
**Returns**: SignedExecutionEnvelope
**Description**: Compute profile, stamp into SignedExecutionEnvelope, and return.

        This is the single authoritative L0 call site.  L3 reads the
        envelope; apps_* receive it as read-only constraints.
        



## Function: _get_routing_gateway

**Parameters**: policy_hash


## Function: _get_proof_emitter



## Function: compute_complexity_score

**Parameters**: features
**Returns**: float
**Description**: Compute a normalised complexity score in [0.0, 1.0].

    This is a PURE FUNCTION:
      - No side effects.
      - No randomness.
      - No time-based signals.
      - No adaptive decay or mutable memory.
      - Identical inputs => identical output.

    Algorithm (additive, capped):
      score = w1 * f(input_length)
            + w2 * f(tool_count)
            + w3 * f(risk_tier)
            + w4 * f(budget_pressure)
            + w5 * f(low_success_rate)

    All component functions are monotone and bounded to [0.0, 1.0].
    



## Function: select_tier

**Parameters**: complexity_score
**Returns**: ReasoningTier
**Description**: Map complexity score to a discrete ReasoningTier.

    Pure function — deterministic boundary mapping, no heuristics.
    



## Function: _build_stage_budgets

**Parameters**: stage_count, base_tokens, multiplier
**Returns**: tuple[StageTokenBudget, ...]
**Description**: Compute per-stage token budgets deterministically.



## Function: compute_policy_config_hash

**Parameters**: policy_config
**Returns**: str
**Description**: Compute deterministic SHA256 hash of a policy config dict.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, policy_config
**Returns**: None


## Function: policy_hash

**Parameters**: self
**Returns**: str


## Function: compute_tier

**Parameters**: self, features
**Returns**: ReasoningTier
**Description**: Compute reasoning tier from structural features (pure function).



## Function: build_profile

**Parameters**: self, features, tier
**Returns**: ReasoningIntensityProfile
**Description**: Construct a versioned, hash-bound ReasoningIntensityProfile.



## Function: compute_and_stamp

**Parameters**: self, features, route_decision, enforcement_constraints
**Returns**: SignedExecutionEnvelope
**Description**: Compute profile, stamp into SignedExecutionEnvelope, and return.

        This is the single authoritative L0 call site.  L3 reads the
        envelope; apps_* receive it as read-only constraints.
        



## Usage Examples

### Class Usage

```python
# Using RequestStructureFeatures
requeststructurefeatures = RequestStructureFeatures()
```

```python
# Using ReasoningPolicyEngine
reasoningpolicyengine = ReasoningPolicyEngine()
reasoningpolicyengine.policy_hash()
reasoningpolicyengine.compute_tier()
```

### Function Usage

```python
# Using _get_routing_gateway
result = _get_routing_gateway(policy_hash)
```

```python
# Using _get_proof_emitter
result = _get_proof_emitter()
```

```python
# Using compute_complexity_score
result = compute_complexity_score(features)
```



---
**Generated**: 2026-03-26T09:39:02.661112
**Type**: api_reference
**Quality**: comprehensive
