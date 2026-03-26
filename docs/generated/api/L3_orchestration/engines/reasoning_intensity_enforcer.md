# API Documentation: reasoning_intensity_enforcer

**Target Audience**: developers, api_users

# reasoning_intensity_enforcer API Documentation

**File**: `reasoning_intensity_enforcer.py`
**Classes**: 5
**Functions**: 13

## Classes

- **ReasoningBudgetExceeded** (inherits from Exception)
- **ReasoningModeViolation** (inherits from Exception)
- **InvalidEnvelopeError** (inherits from Exception)
- **StageExecutionMetrics**
- **ReasoningIntensityEnforcer**

## Functions

- **__init__** -> None
- **__init__** -> None
- **__init__** -> None
- **profile_hash** -> str
- **profile** -> ReasoningIntensityProfile
- **validate_envelope** -> None
- **enforce_pre_stage** -> None
- **enforce_post_stage** -> None
- **drain_telemetry** -> list[ReasoningEnforcementTelemetry]
- **get_enforcement_summary** -> dict[str, Any]
- **_check_ceiling** -> None
- **_get_stage_budget** -> int | None
- **_buffer_telemetry** -> None


## Class: ReasoningBudgetExceeded

**Description**: Raised when a HOP stage exceeds a ceiling set in the reasoning profile.

    This is a HARD STOP — no retry, no silent fallback, no mode downgrade.
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, violation
**Returns**: None



## Class: ReasoningModeViolation

**Description**: Raised when a stage requests a reasoning mode not permitted by L0 profile.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, stage_id, requested_mode, profile_hash
**Returns**: None



## Class: InvalidEnvelopeError

**Description**: Raised when the SignedExecutionEnvelope is missing or hash-invalid.

**Inherits from**: Exception



## Class: StageExecutionMetrics

**Description**: Metrics reported by a HOP stage after execution.

    Must be provided by the stage handler for enforcement validation.
    All values must be non-negative integers or booleans.
    



## Class: ReasoningIntensityEnforcer

**Description**: L3 operational enforcer of the L0-stamped ReasoningIntensityProfile.

    Usage:
        enforcer = ReasoningIntensityEnforcer(envelope)
        enforcer.validate_envelope()                    # call once at start
        enforcer.enforce_pre_stage(stage_id=3)          # before each stage
        enforcer.enforce_post_stage(metrics)            # after each stage
        telemetry = enforcer.drain_telemetry()          # at end of run

    The telemetry returned by drain_telemetry() is NON-AUTHORITATIVE and
    must not be fed back into the current run's policy decisions.
    

### Methods

#### __init__
**Parameters**: self, envelope, trace_id
**Returns**: None

#### profile_hash
**Parameters**: self
**Returns**: str

#### profile
**Parameters**: self
**Returns**: ReasoningIntensityProfile

#### validate_envelope
**Parameters**: self
**Returns**: None
**Description**: Verify envelope integrity before any stage executes.

        Recomputes envelope_hash and profile_hash; raises InvalidEnvelopeError
        on any mismatch. Must be called exactly once before enforce_pre_stage.
        

#### enforce_pre_stage
**Parameters**: self, stage_id, requested_mode
**Returns**: None
**Description**: Check that stage is permitted to proceed.

        Verifies:
          - Envelope has been validated.
          - requested_mode (if provided) is in allowed_modes.
        Raises ReasoningModeViolation on failure (HARD STOP).
        

#### enforce_post_stage
**Parameters**: self, metrics
**Returns**: None
**Description**: Enforce profile ceilings after a stage reports its execution metrics.

        Checks (in order):
          1. branch ceiling
          2. depth ceiling
          3. per-stage token budget
          4. reflection flag
          5. mode membership

        On ANY violation: record, then raise ReasoningBudgetExceeded.
        No silent truncation, no fallback, no mode downgrade.

        L3 may never INCREASE any ceiling — only enforce the stamped limit.
        

#### drain_telemetry
**Parameters**: self
**Returns**: list[ReasoningEnforcementTelemetry]
**Description**: Return buffered non-authoritative telemetry and clear the buffer.

        CRITICAL: This data must NOT be fed back into the current run's
        policy decisions. It is for FUTURE L0 calibration only, and only
        after windowed aggregation and versioning.
        

#### get_enforcement_summary
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return a summary suitable for inclusion in the execution trace.

#### _check_ceiling
**Parameters**: self, stage_id, kind, limit, observed
**Returns**: None
**Description**: Fail-closed ceiling check. Raises ReasoningBudgetExceeded on breach.

#### _get_stage_budget
**Parameters**: self, stage_id
**Returns**: int | None
**Description**: Look up token budget for a stage from the profile.

#### _buffer_telemetry
**Parameters**: self, metrics, compliant
**Returns**: None



## Function: __init__

**Parameters**: self, violation
**Returns**: None


## Function: __init__

**Parameters**: self, stage_id, requested_mode, profile_hash
**Returns**: None


## Function: __init__

**Parameters**: self, envelope, trace_id
**Returns**: None


## Function: profile_hash

**Parameters**: self
**Returns**: str


## Function: profile

**Parameters**: self
**Returns**: ReasoningIntensityProfile


## Function: validate_envelope

**Parameters**: self
**Returns**: None
**Description**: Verify envelope integrity before any stage executes.

        Recomputes envelope_hash and profile_hash; raises InvalidEnvelopeError
        on any mismatch. Must be called exactly once before enforce_pre_stage.
        



## Function: enforce_pre_stage

**Parameters**: self, stage_id, requested_mode
**Returns**: None
**Description**: Check that stage is permitted to proceed.

        Verifies:
          - Envelope has been validated.
          - requested_mode (if provided) is in allowed_modes.
        Raises ReasoningModeViolation on failure (HARD STOP).
        



## Function: enforce_post_stage

**Parameters**: self, metrics
**Returns**: None
**Description**: Enforce profile ceilings after a stage reports its execution metrics.

        Checks (in order):
          1. branch ceiling
          2. depth ceiling
          3. per-stage token budget
          4. reflection flag
          5. mode membership

        On ANY violation: record, then raise ReasoningBudgetExceeded.
        No silent truncation, no fallback, no mode downgrade.

        L3 may never INCREASE any ceiling — only enforce the stamped limit.
        



## Function: drain_telemetry

**Parameters**: self
**Returns**: list[ReasoningEnforcementTelemetry]
**Description**: Return buffered non-authoritative telemetry and clear the buffer.

        CRITICAL: This data must NOT be fed back into the current run's
        policy decisions. It is for FUTURE L0 calibration only, and only
        after windowed aggregation and versioning.
        



## Function: get_enforcement_summary

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return a summary suitable for inclusion in the execution trace.



## Function: _check_ceiling

**Parameters**: self, stage_id, kind, limit, observed
**Returns**: None
**Description**: Fail-closed ceiling check. Raises ReasoningBudgetExceeded on breach.



## Function: _get_stage_budget

**Parameters**: self, stage_id
**Returns**: int | None
**Description**: Look up token budget for a stage from the profile.



## Function: _buffer_telemetry

**Parameters**: self, metrics, compliant
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using ReasoningBudgetExceeded
reasoningbudgetexceeded = ReasoningBudgetExceeded()
```

```python
# Using ReasoningModeViolation
reasoningmodeviolation = ReasoningModeViolation()
```

```python
# Using InvalidEnvelopeError
invalidenvelopeerror = InvalidEnvelopeError()
```

### Function Usage

```python
# Using __init__
result = __init__(violation)
```

```python
# Using __init__
result = __init__(stage_id, requested_mode)
```

```python
# Using __init__
result = __init__(envelope, trace_id)
```



---
**Generated**: 2026-03-26T09:39:04.197308
**Type**: api_reference
**Quality**: comprehensive
