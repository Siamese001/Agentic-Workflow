# API Documentation: escalation_context

**Target Audience**: developers, api_users

# escalation_context API Documentation

**File**: `escalation_context.py`
**Classes**: 2
**Functions**: 4

## Classes

- **MonotonicityViolation** (inherits from RuntimeError)
- **EscalationContext**

## Functions

- **__post_init__** -> None
- **initial** -> EscalationContext
- **from_result** -> EscalationContext
- **is_exhausted** -> bool


## Class: MonotonicityViolation

**Description**: Raised when retry_count decreases between successive escalation contexts.

**Inherits from**: RuntimeError



## Class: EscalationContext

**Description**: Immutable snapshot of escalation state for one healing cycle step.

    Fields
    ------
    trace_id : str
        Identifier for the parent execution trace.
    retry_count : int
        Number of healing attempts so far (monotonically non-decreasing).
    healing_tier : str
        Current healing tier name (e.g. "tier_1", "tier_2").
    previous_retry_count : int
        retry_count of the immediately prior context (0 for the first).
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### initial
**Parameters**: cls, trace_id, healing_tier
**Returns**: EscalationContext
**Description**: Create the first EscalationContext for a trace (retry_count=0).

#### from_result
**Parameters**: cls, previous, new_healing_tier
**Returns**: EscalationContext
**Description**: Create the next context after one healing attempt.

        Increments retry_count by 1 and enforces monotonicity.

        Args:
            previous: The EscalationContext from the prior step.
            new_healing_tier: Updated tier, defaults to previous tier.

        Raises:
            MonotonicityViolation: if new retry_count < previous retry_count
                (should never happen via this factory, but guards against
                 injection of a tampered *previous*).
        

#### is_exhausted
**Parameters**: self
**Returns**: bool
**Description**: True when retry_count has reached the hard limit (5).



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: initial

**Parameters**: cls, trace_id, healing_tier
**Returns**: EscalationContext
**Description**: Create the first EscalationContext for a trace (retry_count=0).



## Function: from_result

**Parameters**: cls, previous, new_healing_tier
**Returns**: EscalationContext
**Description**: Create the next context after one healing attempt.

        Increments retry_count by 1 and enforces monotonicity.

        Args:
            previous: The EscalationContext from the prior step.
            new_healing_tier: Updated tier, defaults to previous tier.

        Raises:
            MonotonicityViolation: if new retry_count < previous retry_count
                (should never happen via this factory, but guards against
                 injection of a tampered *previous*).
        



## Function: is_exhausted

**Parameters**: self
**Returns**: bool
**Description**: True when retry_count has reached the hard limit (5).



## Usage Examples

### Class Usage

```python
# Using MonotonicityViolation
monotonicityviolation = MonotonicityViolation()
```

```python
# Using EscalationContext
escalationcontext = EscalationContext()
escalationcontext.initial()
escalationcontext.from_result()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using initial
result = initial(cls, trace_id)
```

```python
# Using from_result
result = from_result(cls, previous)
```



---
**Generated**: 2026-03-26T09:39:03.799011
**Type**: api_reference
**Quality**: comprehensive
