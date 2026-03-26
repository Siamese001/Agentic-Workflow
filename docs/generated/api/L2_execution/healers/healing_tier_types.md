# API Documentation: healing_tier_types

**Target Audience**: developers, api_users

# healing_tier_types API Documentation

**File**: `healing_tier_types.py`
**Classes**: 5
**Functions**: 4

## Classes

- **HealingTier** (inherits from str, Enum)
- **HealingInput**
- **HealingDecision**
- **InvocationRecord**
- **FailureSignal**

## Functions

- **__post_init__** -> None
- **__post_init__** -> None
- **__post_init__** -> None
- **to_healing_input** -> HealingInput


## Class: HealingTier

**Description**: Healing model tier selected by the centralized router.

**Inherits from**: str, Enum



## Class: HealingInput

**Description**: Structured failure context consumed by the L2.3 healing router.

    Attributes:
        failure_type: Category of the failure (e.g. 'syntax_error', 'import_cycle').
        error_signature: Deterministic hash or short string identifying the error class.
        trace_id: Correlation ID linking to the execution cycle.
        retry_count: Number of prior heal attempts for this failure.
        blast_radius_estimate: Bounded [0.0, 1.0] estimate of change scope.
        required_tools: Tools the healer needs (e.g. ['ast_rewrite', 'file_move']).
        violation_metadata_refs: Paths to violation artifacts for context.
        replay_mode: Enable deterministic replay mode (timestamp excluded).
        agent_id: Optional identifier of the agent requesting healing (execution profile enforcement).
        failure_entropy_class: Entropy classification of the failure (LOW/MEDIUM/HIGH).
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: HealingDecision

**Description**: Immutable routing decision produced by the L2.3 healing router.

    Attributes:
        heal_confidence: Deterministic score in [0.0, 1.0] driving tier selection.
        tier: Selected healing tier.
        reason_codes: Deterministic list of reasons contributing to the decision.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: InvocationRecord

**Description**: Immutable record with replay-deterministic fields only.

    Timestamp excluded from replay surface for mathematical determinism.
    Provider configuration and historical data versioning included.

    Attributes:
        tier: Selected healing tier
        model_id: Model identifier used
        agent_name: Agent that made the request
        trace_id: Correlation ID for the request
        heal_confidence: Confidence score for the decision
        method_called: Method name that was invoked
        provider_config_hash: Hash of provider configuration for replay
        historical_data_hash: Hash of historical data version for replay
        replay_key: Mathematical replay key (timestamp excluded)
    



## Class: FailureSignal

**Description**: Structured signal emitted by NO_TIERING agents on failure.

    L2.3 consumes this to perform healing tier routing on behalf of the agent.
    The agent itself MUST NOT select a healing model.

    Attributes:
        source_agent: Name of the agent emitting the signal.
        failure_type: Category of the failure.
        error_signature: Deterministic identifier for the error class.
        trace_id: Correlation ID.
        context: Arbitrary structured context for the healer.
        retry_count: Number of prior attempts.
        blast_radius_estimate: Bounded [0.0, 1.0].
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_healing_input
**Parameters**: self, required_tools, violation_metadata_refs
**Returns**: HealingInput
**Description**: Convert FailureSignal to HealingInput for L2.3 router consumption.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_healing_input

**Parameters**: self, required_tools, violation_metadata_refs
**Returns**: HealingInput
**Description**: Convert FailureSignal to HealingInput for L2.3 router consumption.



## Usage Examples

### Class Usage

```python
# Using HealingTier
healingtier = HealingTier()
```

```python
# Using HealingInput
healinginput = HealingInput()
```

```python
# Using HealingDecision
healingdecision = HealingDecision()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:03.825818
**Type**: api_reference
**Quality**: comprehensive
