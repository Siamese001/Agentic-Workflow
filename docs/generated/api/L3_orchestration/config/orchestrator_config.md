# API Documentation: orchestrator_config

**Target Audience**: developers, api_users

# orchestrator_config API Documentation

**File**: `orchestrator_config.py`
**Classes**: 3
**Functions**: 3

## Classes

- **OrchestratorConfig**
- **CognitiveConfig**
- **ActionConfig**

## Functions

- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]


## Class: OrchestratorConfig

**Description**: configuration for the orchestrator (Nervous System).

    Attributes:
        mission_id: Unique identifier for the mission
        max_iterations: Maximum Think-Act-Observe iterations
        max_phases: Maximum number of phases to execute
        enable_tri_brain: Whether to enable tri-brain routing
        enable_reflection: Whether to run reflection phase
        enable_state_persistence: Whether to persist state between runs
        timeout_seconds: Overall execution timeout
        retry_on_failure: Whether to retry failed actions
        max_retries: Maximum retry attempts
        parallel_actions: Whether to execute actions in parallel
        metadata: Additional configuration metadata
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary representation.



## Class: CognitiveConfig

**Description**: configuration for the cognitive plane.
    Attributes:
        model: LLM model to use for reasoning
        temperature: Sampling temperature
        max_tokens: Maximum tokens for generation
        enable_cot: Enable chain-of-thought reasoning
        enable_self_critique: Enable self-critique loop
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary representation.



## Class: ActionConfig

**Description**: configuration for the action plane.

    Attributes:
        sandbox_enabled: Whether to run actions in sandbox
        timeout_per_action: Timeout per action in seconds
        max_concurrent: Maximum concurrent actions
        enable_fallback: Enable fallback providers
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary representation.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary representation.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary representation.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary representation.



## Usage Examples

### Class Usage

```python
# Using OrchestratorConfig
orchestratorconfig = OrchestratorConfig()
orchestratorconfig.to_dict()
```

```python
# Using CognitiveConfig
cognitiveconfig = CognitiveConfig()
cognitiveconfig.to_dict()
```

```python
# Using ActionConfig
actionconfig = ActionConfig()
actionconfig.to_dict()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:04.087848
**Type**: api_reference
**Quality**: comprehensive
