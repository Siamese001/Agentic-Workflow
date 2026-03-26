# API Documentation: heal_llm_seam_types

**Target Audience**: developers, api_users

# heal_llm_seam_types API Documentation

**File**: `heal_llm_seam_types.py`
**Classes**: 9
**Functions**: 22

## Classes

- **HealSeamBypassError** (inherits from Exception)
- **HealLlmRequest**
- **PolicyDecisionRecord**
- **HealBudgetExceededError** (inherits from Exception)
- **HealBudgetCaps**
- **HealTelemetryRecord**
- **RepoHealOperation**
- **RepoHealPlan**
- **RepoHealResult**

## Functions

- **set_heal_seam_capability** -> contextvars.Token[bool]
- **reset_heal_seam_capability** -> None
- **assert_heal_seam_capability** -> None
- **guarded_heal_llm_call** -> str | None
- **set_heal_budget_caps** -> contextvars.Token[HealBudgetCaps | None]
- **reset_heal_budget_counters** -> None
- **increment_escalation_count** -> None
- **get_budget_counters** -> dict[str, int]
- **emit_heal_telemetry** -> Path
- **_is_path_allowed** -> bool
- **_is_extension_allowed** -> bool
- **build_repo_heal_plan** -> RepoHealPlan
- **apply_repo_heal_plan** -> RepoHealResult
- **to_dict** -> dict[str, Any]
- **input_hash** -> str
- **from_env** -> HealBudgetCaps
- **to_dict** -> dict[str, Any]
- **telemetry_hash** -> str
- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **plan_hash** -> str
- **to_dict** -> dict[str, Any]


## Class: HealSeamBypassError

**Description**: Raised when LLM escalation is attempted outside canonical seam.

**Inherits from**: Exception



## Class: HealLlmRequest

**Description**: Typed request payload for heal LLM calls.

    Attributes:
        prompt: The prompt text to send to the LLM.
        model_id: Optional model identifier; None means use the default model.
        metadata: Arbitrary metadata for observability/instrumentation.
    



## Class: PolicyDecisionRecord

**Description**: Deterministic policy decision record (no timestamps/UUIDs).

    Emitted per heal run for observability.
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to JSON-serializable dict.

#### input_hash
**Parameters**: self
**Returns**: str
**Description**: Compute deterministic hash of inputs for stable filenames.



## Class: HealBudgetExceededError

**Description**: Raised when heal escalation budget is exceeded.

**Inherits from**: Exception



## Class: HealBudgetCaps

**Description**: Budget caps for heal escalation (defaults from env vars).

### Methods

#### from_env
**Parameters**: cls, enable_llm
**Returns**: HealBudgetCaps
**Description**: Load budget caps from environment variables with sensible defaults.



## Class: HealTelemetryRecord

**Description**: Deterministic telemetry record for heal runs (no timestamps/UUIDs).

    Emitted per heal / heal_repository run for observability.
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to JSON-serializable dict.

#### telemetry_hash
**Parameters**: self
**Returns**: str
**Description**: Compute deterministic hash of telemetry record for filenames.



## Class: RepoHealOperation

**Description**: A single deterministic heal operation in a repo-heal plan.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to JSON-serializable dict.



## Class: RepoHealPlan

**Description**: Deterministic plan for repo-wide healing.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to JSON-serializable dict.

#### plan_hash
**Parameters**: self
**Returns**: str
**Description**: Compute deterministic hash of the plan for stable comparison.



## Class: RepoHealResult

**Description**: Result of applying a repo-heal plan.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to JSON-serializable dict.



## Function: set_heal_seam_capability

**Parameters**: enabled
**Returns**: contextvars.Token[bool]
**Description**: Set the heal seam capability token. Only callable from standard_heal.



## Function: reset_heal_seam_capability

**Parameters**: token
**Returns**: None
**Description**: Reset the heal seam capability token.



## Function: assert_heal_seam_capability

**Returns**: None
**Description**: Assert that the heal seam capability is enabled.

    Raises:
        HealSeamBypassError: If called outside the canonical standard_heal seam.
    



## Function: guarded_heal_llm_call

**Parameters**: request
**Returns**: str | None
**Description**: Guarded LLM call that enforces canonical seam access.

    Returns:
        LLM response string, or None if no caller is configured.

    Raises:
        HealSeamBypassError: If called outside standard_heal context.
    



## Function: set_heal_budget_caps

**Parameters**: caps
**Returns**: contextvars.Token[HealBudgetCaps | None]
**Description**: Set budget caps for current heal run.



## Function: reset_heal_budget_counters

**Returns**: None
**Description**: Reset budget counters to zero.



## Function: increment_escalation_count

**Parameters**: tier
**Returns**: None
**Description**: Increment escalation count and check budget.

    Raises:
        HealBudgetExceededError: If budget cap is exceeded.
    



## Function: get_budget_counters

**Returns**: dict[str, int]
**Description**: Get current budget counter values.



## Function: emit_heal_telemetry

**Parameters**: record, artifacts_root
**Returns**: Path
**Description**: Emit a deterministic telemetry artifact.

    Args:
        record: The telemetry record to emit.
        artifacts_root: Root path for artifacts (default: artifacts/consolidation/heal_telemetry)

    Returns:
        Path to the emitted artifact.

    Raises:
        ValueError: If file exists with different content.
    



## Function: _is_path_allowed

**Parameters**: path_parts
**Returns**: bool
**Description**: Check if path is allowed based on denylist.



## Function: _is_extension_allowed

**Parameters**: filename
**Returns**: bool
**Description**: Check if file extension is in allowlist.



## Function: build_repo_heal_plan

**Parameters**: repo_root
**Returns**: RepoHealPlan
**Description**: Build a deterministic repo-heal plan.

    Scans the repository and creates a sorted list of operations.
    Pure function - no side effects, no network calls.

    Args:
        repo_root: Absolute path to repository root.

    Returns:
        RepoHealPlan with deterministic, sorted operations.
    



## Function: apply_repo_heal_plan

**Parameters**: plan, dry_run
**Returns**: RepoHealResult
**Description**: Apply a repo-heal plan deterministically.

    Pure function for dry_run=True. No network calls.

    Args:
        plan: The heal plan to apply.
        dry_run: If True, simulate operations without changes.

    Returns:
        RepoHealResult with operation counts.
    



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to JSON-serializable dict.



## Function: input_hash

**Parameters**: self
**Returns**: str
**Description**: Compute deterministic hash of inputs for stable filenames.



## Function: from_env

**Parameters**: cls, enable_llm
**Returns**: HealBudgetCaps
**Description**: Load budget caps from environment variables with sensible defaults.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to JSON-serializable dict.



## Function: telemetry_hash

**Parameters**: self
**Returns**: str
**Description**: Compute deterministic hash of telemetry record for filenames.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to JSON-serializable dict.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to JSON-serializable dict.



## Function: plan_hash

**Parameters**: self
**Returns**: str
**Description**: Compute deterministic hash of the plan for stable comparison.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to JSON-serializable dict.



## Usage Examples

### Class Usage

```python
# Using HealSeamBypassError
healseambypasserror = HealSeamBypassError()
```

```python
# Using HealLlmRequest
healllmrequest = HealLlmRequest()
```

```python
# Using PolicyDecisionRecord
policydecisionrecord = PolicyDecisionRecord()
policydecisionrecord.to_dict()
policydecisionrecord.input_hash()
```

### Function Usage

```python
# Using set_heal_seam_capability
result = set_heal_seam_capability(enabled)
```

```python
# Using reset_heal_seam_capability
result = reset_heal_seam_capability(token)
```

```python
# Using assert_heal_seam_capability
result = assert_heal_seam_capability()
```



---
**Generated**: 2026-03-26T09:39:05.516151
**Type**: api_reference
**Quality**: comprehensive
