# API Documentation: token_enforcement_types

**Target Audience**: developers, api_users

# token_enforcement_types API Documentation

**File**: `token_enforcement_types.py`
**Classes**: 5
**Functions**: 12

## Classes

- **TokenEnforcementOutcome** (inherits from Enum)
- **TokenEnforcementArtifact**
- **TokenBudgetExceeded** (inherits from Exception)
- **TokenBudgetContext**
- **TokenBudgetStore**

## Functions

- **get_token_budget_store** -> TokenBudgetStore
- **set_token_budget_store** -> None
- **estimate_prompt_tokens** -> int
- **build_token_enforcement_artifact** -> TokenEnforcementArtifact
- **__post_init__** -> None
- **__init__** -> None
- **__post_init__** -> None
- **__init__** -> None
- **get_or_init** -> TokenBudgetContext
- **consume** -> int
- **reset** -> None
- **clear_all** -> None


## Class: TokenEnforcementOutcome

**Description**: Outcome of token budget enforcement at the LLM boundary.

**Inherits from**: Enum



## Class: TokenEnforcementArtifact

**Description**: §Wave1.8 — Emitted exactly once per LLM call attempt (PASS or FAIL).

    Hard enforcement artifact recording token budget state before/after
    model invocation. No silent swallowing — every path emits.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: TokenBudgetExceeded

**Description**: §Wave1.8 — Raised when token budget is exceeded (pre-call or post-call).

    Fail-closed: model invocation is prevented (pre-call) or flagged (post-call).
    Carries the enforcement artifact for upstream handling.
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, trace_id, required, remaining, phase, artifact
**Returns**: None



## Class: TokenBudgetContext

**Description**: §Wave1.8 — Per-trace token budget accounting.

    NOT frozen — remaining_budget is mutated on each LLM call.
    Thread-safe mutation happens in TokenBudgetStore.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: TokenBudgetStore

**Description**: §Wave1.8 — Thread-safe, trace-id-keyed token budget store.

    No global mutable counter without trace binding.
    Deterministic reset on new trace.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### get_or_init
**Parameters**: self, trace_id, initial_budget
**Returns**: TokenBudgetContext
**Description**: Get existing budget for trace_id, or create new one.

#### consume
**Parameters**: self, trace_id, tokens_used
**Returns**: int
**Description**: Subtract tokens from budget. Returns new remaining budget (may be negative).

#### reset
**Parameters**: self, trace_id
**Returns**: None
**Description**: Remove budget for a trace_id.

#### clear_all
**Parameters**: self
**Returns**: None
**Description**: Clear all budgets (for testing).



## Function: get_token_budget_store

**Returns**: TokenBudgetStore
**Description**: Get or create the global TokenBudgetStore.



## Function: set_token_budget_store

**Parameters**: store
**Returns**: None
**Description**: Replace the global store (for testing).



## Function: estimate_prompt_tokens

**Parameters**: prompt
**Returns**: int
**Description**: Estimate prompt token count. ~4 chars per token is a conservative heuristic.

    This is a minimal estimator. Real implementations should use tiktoken
    or provider-specific tokenizers.
    



## Function: build_token_enforcement_artifact

**Parameters**: trace_id, model, prompt_tokens, completion_tokens, remaining_budget, hard_limit, outcome
**Returns**: TokenEnforcementArtifact
**Description**: Factory for TokenEnforcementArtifact with deterministic fields.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, trace_id, required, remaining, phase, artifact
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: get_or_init

**Parameters**: self, trace_id, initial_budget
**Returns**: TokenBudgetContext
**Description**: Get existing budget for trace_id, or create new one.



## Function: consume

**Parameters**: self, trace_id, tokens_used
**Returns**: int
**Description**: Subtract tokens from budget. Returns new remaining budget (may be negative).



## Function: reset

**Parameters**: self, trace_id
**Returns**: None
**Description**: Remove budget for a trace_id.



## Function: clear_all

**Parameters**: self
**Returns**: None
**Description**: Clear all budgets (for testing).



## Usage Examples

### Class Usage

```python
# Using TokenEnforcementOutcome
tokenenforcementoutcome = TokenEnforcementOutcome()
```

```python
# Using TokenEnforcementArtifact
tokenenforcementartifact = TokenEnforcementArtifact()
```

```python
# Using TokenBudgetExceeded
tokenbudgetexceeded = TokenBudgetExceeded()
```

### Function Usage

```python
# Using get_token_budget_store
result = get_token_budget_store()
```

```python
# Using set_token_budget_store
result = set_token_budget_store(store)
```

```python
# Using estimate_prompt_tokens
result = estimate_prompt_tokens(prompt)
```



---
**Generated**: 2026-03-26T09:39:04.010560
**Type**: api_reference
**Quality**: comprehensive
