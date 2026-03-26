# API Documentation: reasoning_intensity_types

**Target Audience**: developers, api_users

# reasoning_intensity_types API Documentation

**File**: `reasoning_intensity_types.py`
**Classes**: 6
**Functions**: 8

## Classes

- **ReasoningTier** (inherits from str, Enum)
- **StageTokenBudget**
- **ReasoningIntensityProfile**
- **SignedExecutionEnvelope**
- **ReasoningConstraintViolation**
- **ReasoningEnforcementTelemetry**

## Functions

- **_compute_profile_hash** -> str
- **_compute_envelope_hash** -> str
- **build_profile_hash** -> str
- **build_envelope_hash** -> str
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None


## Class: ReasoningTier

**Description**: Discrete reasoning intensity tiers. No fractional values allowed.

**Inherits from**: str, Enum



## Class: StageTokenBudget

**Description**: Per-HOP-stage token budget constraint stamped by L0.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: ReasoningIntensityProfile

**Description**: Sealed reasoning intensity profile stamped by L0 ReasoningPolicyEngine.

    All fields are required. profile_hash is computed over the canonical
    serialization of all policy parameters and must be included in:
      - execution trace
      - replay key
      - L3 enforcement log

    L3 may only REDUCE (enforce ceilings). No upward mutation is permitted.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: SignedExecutionEnvelope

**Description**: First-class sealed execution contract combining route decision and reasoning profile.

    L0 stamps this; L3 reads it; apps_* receive it as read-only constraints.
    The envelope_hash covers both route_decision and reasoning_profile to
    prevent partial substitution attacks.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: ReasoningConstraintViolation

**Description**: Emitted by L3 ReasoningIntensityEnforcer on policy ceiling breach.

    This is a deterministic failure artifact — not a soft warning.
    The violating stage MUST be halted immediately.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: ReasoningEnforcementTelemetry

**Description**: Non-authoritative telemetry emitted by L3 after stage execution.

    CRITICAL: This data MUST NOT influence the current run.
    It may only be used by L0 for FUTURE calibration, and only after
    windowed aggregation and versioning (no direct feedback loops).
    



## Function: _compute_profile_hash

**Parameters**: version, policy_hash, tier, max_branches, max_depth, enable_reflection, token_budget_per_stage, allowed_modes
**Returns**: str
**Description**: Compute SHA256 over deterministic canonical serialization of profile parameters.



## Function: _compute_envelope_hash

**Parameters**: route_decision_trace_id, profile_hash, policy_hash
**Returns**: str
**Description**: Compute SHA256 over envelope binding fields.



## Function: build_profile_hash

**Parameters**: version, policy_hash, tier, max_branches, max_depth, enable_reflection, token_budget_per_stage, allowed_modes
**Returns**: str
**Description**: Compute the profile_hash for use before constructing ReasoningIntensityProfile.



## Function: build_envelope_hash

**Parameters**: route_decision_trace_id, profile_hash, policy_hash
**Returns**: str
**Description**: Compute the envelope_hash for use before constructing SignedExecutionEnvelope.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using ReasoningTier
reasoningtier = ReasoningTier()
```

```python
# Using StageTokenBudget
stagetokenbudget = StageTokenBudget()
```

```python
# Using ReasoningIntensityProfile
reasoningintensityprofile = ReasoningIntensityProfile()
```

### Function Usage

```python
# Using _compute_profile_hash
result = _compute_profile_hash(version, policy_hash)
```

```python
# Using _compute_envelope_hash
result = _compute_envelope_hash(route_decision_trace_id, profile_hash)
```

```python
# Using build_profile_hash
result = build_profile_hash(version, policy_hash)
```



---
**Generated**: 2026-03-26T09:39:03.463590
**Type**: api_reference
**Quality**: comprehensive
