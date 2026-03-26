# API Documentation: execution_context

**Target Audience**: developers, api_users

# execution_context API Documentation

**File**: `execution_context.py`
**Classes**: 3
**Functions**: 10

## Classes

- **ActionClass** (inherits from str, Enum)
- **GuardrailOutcome** (inherits from str, Enum)
- **ExecutionContext**

## Functions

- **is_irreversible** -> bool
- **requires_uwg** -> bool
- **requires_human_review** -> bool
- **requires_network_policy** -> bool
- **may_proceed** -> bool
- **is_abnormal** -> bool
- **__post_init__** -> None
- **create** -> ExecutionContext
- **with_guardrail_decision** -> ExecutionContext
- **to_dict** -> dict[str, Any]


## Class: ActionClass

**Description**: Execution target action classification.

    Every execution target must be classified before execution.
    Higher-risk classes require stricter routing.
    

**Inherits from**: str, Enum

### Methods

#### is_irreversible
**Parameters**: self
**Returns**: bool

#### requires_uwg
**Parameters**: self
**Returns**: bool

#### requires_human_review
**Parameters**: self
**Returns**: bool

#### requires_network_policy
**Parameters**: self
**Returns**: bool



## Class: GuardrailOutcome

**Description**: Fail-closed guardrail outcome set.

    Only ALLOW may proceed to execution.
    All other outcomes MUST terminate execution.
    

**Inherits from**: str, Enum

### Methods

#### may_proceed
**Parameters**: self
**Returns**: bool

#### is_abnormal
**Parameters**: self
**Returns**: bool



## Class: ExecutionContext

**Description**: Immutable run-scoped execution context.

    All 9 required fields MUST be non-empty at creation time.
    No execution may proceed without an explicit instance.

    Fields:
        execution_request_id   — unique per execution attempt
        run_id                 — agent run linkage
        capability_token       — token proving authority to act
        policy_hash            — active policy state hash
        guardrail_decision_id  — ID of guardrail decision (filled post-evaluation)
        guardrail_decision_hash — hash of guardrail decision (filled post-evaluation)
        execution_input_hash   — hash of execution payload
        execution_target_hash  — hash of execution target identifier
        trace_id               — routing/execution trace linkage
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### create
**Parameters**: cls
**Returns**: ExecutionContext
**Description**: Factory with deterministic hashing.

#### with_guardrail_decision
**Parameters**: self, decision_id, decision_hash
**Returns**: ExecutionContext
**Description**: Return copy with guardrail decision bound.

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Function: is_irreversible

**Parameters**: self
**Returns**: bool


## Function: requires_uwg

**Parameters**: self
**Returns**: bool


## Function: requires_human_review

**Parameters**: self
**Returns**: bool


## Function: requires_network_policy

**Parameters**: self
**Returns**: bool


## Function: may_proceed

**Parameters**: self
**Returns**: bool


## Function: is_abnormal

**Parameters**: self
**Returns**: bool


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: create

**Parameters**: cls
**Returns**: ExecutionContext
**Description**: Factory with deterministic hashing.



## Function: with_guardrail_decision

**Parameters**: self, decision_id, decision_hash
**Returns**: ExecutionContext
**Description**: Return copy with guardrail decision bound.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Usage Examples

### Class Usage

```python
# Using ActionClass
actionclass = ActionClass()
actionclass.is_irreversible()
actionclass.requires_uwg()
```

```python
# Using GuardrailOutcome
guardrailoutcome = GuardrailOutcome()
guardrailoutcome.may_proceed()
guardrailoutcome.is_abnormal()
```

```python
# Using ExecutionContext
executioncontext = ExecutionContext()
executioncontext.create()
executioncontext.with_guardrail_decision()
```

### Function Usage

```python
# Using is_irreversible
result = is_irreversible()
```

```python
# Using requires_uwg
result = requires_uwg()
```

```python
# Using requires_human_review
result = requires_human_review()
```



---
**Generated**: 2026-03-26T09:39:03.646256
**Type**: api_reference
**Quality**: comprehensive
