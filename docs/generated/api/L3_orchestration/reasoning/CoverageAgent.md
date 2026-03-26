# API Documentation: CoverageAgent

**Target Audience**: developers, api_users

# CoverageAgent API Documentation

**File**: `CoverageAgent.py`
**Classes**: 1
**Functions**: 17

## Classes

- **CoverageAgent** (inherits from SovereignBaseAgent)

## Functions

- **_get_layer_entry**
- **__init__** -> None
- **_handle_param_update** -> None
- **_fetch_metrics** -> dict[str, int] | None
- **_compute_proportions** -> dict[str, float]
- **_shannon_entropy** -> float
- **act** -> str
- **_apply_routing_bias** -> None
- **_inject_synthetic_exercises** -> None
- **_run_self_tests** -> dict
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **layer_entry**
- **publish_event** -> Any
- **subscribe_event** -> Any
- **enqueue** -> Any
- **wrapper**


## Class: CoverageAgent

**Description**: CoverageAgent agent for autonomous operations.

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, layers, threshold_entropy, dashboard_api_url, intervention_mode, bias_weight, bias_duration_cycles, synthetic_tasks_per_trigger, priority_boost_layers
**Returns**: None
**Description**: 
        Initialize coverage agent.

        Args:
            layers: Optional list of layer names to monitor
            threshold_entropy: Entropy threshold for triggering interventions
            dashboard_api_url: URL for dashboard metrics API
            intervention_mode: Mode of intervention (report/bias_only/full_active)
            bias_weight: Selection score multiplier for biased layers
            bias_duration_cycles: Number of cycles to sustain bias
            synthetic_tasks_per_trigger: Number of synthetic tasks per trigger
            priority_boost_layers: Ordered list of layers for forced exploration
        

#### _handle_param_update
**Parameters**: self, event_data
**Returns**: None
**Description**: Handle parameter updates from MetaCoverageOptimizerAgent.

#### _fetch_metrics
**Parameters**: self
**Returns**: dict[str, int] | None
**Description**: Pull layer activation counts from dashboard backend.

#### _compute_proportions
**Parameters**: self, counts
**Returns**: dict[str, float]
**Description**: Compute proportions.

#### _shannon_entropy
**Parameters**: self, proportions
**Returns**: float
**Description**: Shannon entropy.

#### act
**Parameters**: self
**Returns**: str
**Description**: Primary actuation method — call periodically from orchestrator/metrics coordinator.

#### _apply_routing_bias
**Parameters**: self, layer
**Returns**: None
**Description**: Publish bias event — orchestrator subscribes and applies multiplier.

#### _inject_synthetic_exercises
**Parameters**: self, layer
**Returns**: None
**Description**: Enqueue safe no-op tasks targeting layer — direct metric increment.

#### _run_self_tests
**Parameters**: self
**Returns**: dict
**Description**: Run internal self-tests.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        L3 Orchestration Agent - Coverage Agent Healing.

        WIRED CAPABILITIES:
        - Validates layer coverage metrics
        - Checks dashboard API connectivity
        - Verifies entropy threshold configuration
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by CoverageAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Function: _get_layer_entry

**Description**: Lazy load layer_entry to avoid upward import.



## Function: __init__

**Parameters**: self, layers, threshold_entropy, dashboard_api_url, intervention_mode, bias_weight, bias_duration_cycles, synthetic_tasks_per_trigger, priority_boost_layers
**Returns**: None
**Description**: 
        Initialize coverage agent.

        Args:
            layers: Optional list of layer names to monitor
            threshold_entropy: Entropy threshold for triggering interventions
            dashboard_api_url: URL for dashboard metrics API
            intervention_mode: Mode of intervention (report/bias_only/full_active)
            bias_weight: Selection score multiplier for biased layers
            bias_duration_cycles: Number of cycles to sustain bias
            synthetic_tasks_per_trigger: Number of synthetic tasks per trigger
            priority_boost_layers: Ordered list of layers for forced exploration
        



## Function: _handle_param_update

**Parameters**: self, event_data
**Returns**: None
**Description**: Handle parameter updates from MetaCoverageOptimizerAgent.



## Function: _fetch_metrics

**Parameters**: self
**Returns**: dict[str, int] | None
**Description**: Pull layer activation counts from dashboard backend.



## Function: _compute_proportions

**Parameters**: self, counts
**Returns**: dict[str, float]
**Description**: Compute proportions.



## Function: _shannon_entropy

**Parameters**: self, proportions
**Returns**: float
**Description**: Shannon entropy.



## Function: act

**Parameters**: self
**Returns**: str
**Description**: Primary actuation method — call periodically from orchestrator/metrics coordinator.



## Function: _apply_routing_bias

**Parameters**: self, layer
**Returns**: None
**Description**: Publish bias event — orchestrator subscribes and applies multiplier.



## Function: _inject_synthetic_exercises

**Parameters**: self, layer
**Returns**: None
**Description**: Enqueue safe no-op tasks targeting layer — direct metric increment.



## Function: _run_self_tests

**Parameters**: self
**Returns**: dict
**Description**: Run internal self-tests.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        L3 Orchestration Agent - Coverage Agent Healing.

        WIRED CAPABILITIES:
        - Validates layer coverage metrics
        - Checks dashboard API connectivity
        - Verifies entropy threshold configuration
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by CoverageAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Function: layer_entry

**Description**: Stub layer_entry decorator.



## Function: publish_event

**Parameters**: event_type, payload
**Returns**: Any
**Description**: Execute publish_event operation.



## Function: subscribe_event

**Parameters**: event_type, handler
**Returns**: Any
**Description**: Execute subscribe_event operation.



## Function: enqueue

**Parameters**: task_payload
**Returns**: Any
**Description**: Execute enqueue operation.



## Function: wrapper

**Parameters**: f


## Usage Examples

### Class Usage

```python
# Using CoverageAgent
coverageagent = CoverageAgent()
coverageagent.act()
coverageagent.heal_repository()
```

### Function Usage

```python
# Using _get_layer_entry
result = _get_layer_entry()
```

```python
# Using __init__
result = __init__(layers, threshold_entropy)
```

```python
# Using _handle_param_update
result = _handle_param_update(event_data)
```



---
**Generated**: 2026-03-26T09:39:04.256140
**Type**: api_reference
**Quality**: comprehensive
