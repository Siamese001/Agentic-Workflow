# API Documentation: NervousSystemAgent

**Target Audience**: developers, api_users

# NervousSystemAgent API Documentation

**File**: `NervousSystemAgent.py`
**Classes**: 1
**Functions**: 19

## Classes

- **NervousSystemAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__** -> None
- **_get_CoverageAgent**
- **_handle_bias_update** -> None
- **_decay_biases** -> None
- **force_exerciser_fallback** -> str | None
- **_run_self_tests** -> bool
- **_iteration** -> Any
- **_iteration** -> Any
- **_v15_build_operation_manifest** -> SurgicalManifest | None
- **get_state** -> dict[str, Any]
- **_extract_actions** -> list[ActionRequest]
- **validate_architecture** -> dict[str, Any]
- **post_phase_validation** -> dict[str, Any]
- **cleanup_violations** -> list[dict[str, Any]]
- **run_with_cleanup** -> dict[str, Any]
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **_noop_heal**
- **_state_hash**


## Class: NervousSystemAgent

**Description**: Core orchestrator that coordinates cognitive and action planes.

    Implements the 5-step agentic cycle:
    1. MISSION - Define the goal
    2. SCENE - Gather context
    3. THINK - Plan next actions (Brain)
    4. ACT - Execute actions (Hands)
    5. OBSERVE - Interpret results and update state

    Enforces strict architectural boundaries:
    - Only orchestrator can call both planes
    - Cognitive plane cannot trigger actions
    - Action plane cannot make plans
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, cognitive_plane, action_plane, config
**Returns**: None
**Description**: Initialize nervous system.

        Args:
            cognitive_plane: The brain (planning/reasoning)
            action_plane: The hands (tool execution)
            config: Orchestrator configuration
        

#### _get_CoverageAgent
**Description**: Lazy loader for CoverageAgent (upward L3->L6 seam).

#### _handle_bias_update
**Parameters**: self, event_data
**Returns**: None
**Description**: Process CoverageAgent bias events — multi-layer queue.

#### _decay_biases
**Parameters**: self
**Returns**: None
**Description**: Decrement and cleanup expired biases with dynamic decay based on health.

#### force_exerciser_fallback
**Parameters**: self, task
**Returns**: str | None
**Description**: If no candidates in target layer, direct to exerciser.

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L3 compliance.

#### _iteration
**Parameters**: self
**Returns**: Any
**Description**: Iteration.

#### _iteration
**Parameters**: self, value
**Returns**: Any
**Description**: Iteration.

#### _v15_build_operation_manifest
**Parameters**: self, operation, target_layer
**Returns**: SurgicalManifest | None
**Description**: §8.1a — Construct SurgicalManifest for orchestrator-level operation.

#### get_state
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current orchestrator state.

        Returns:
            Current state snapshot
        

#### _extract_actions
**Parameters**: self, think_result
**Returns**: list[ActionRequest]
**Description**: Extract action requests from planning result.

        Args:
            think_result: Result from think phase

        Returns:
            List of action requests
        

#### validate_architecture
**Parameters**: self, file_paths
**Returns**: dict[str, Any]
**Description**: 
        Validate architecture compliance.

        Args:
            file_paths: Specific files to validate

        Returns:
            Validation report
        

#### post_phase_validation
**Parameters**: self, phase_name, affected_paths, dry_run
**Returns**: dict[str, Any]
**Description**: 
        GOLD STANDARD: Post-phase validation using domain-specific agents.
        Validates location, hierarchy, and import compliance after phase completion.

        Args:
            phase_name: Name of the completed phase
            affected_paths: List of file paths affected by the phase
            dry_run: If True, only preview without applying fixes

        Returns:
            Dict with validation results from all integrated agents
        

#### cleanup_violations
**Parameters**: self, violations, dry_run, max_actions
**Returns**: list[dict[str, Any]]
**Description**: 
        GOLD STANDARD: Cleanup violations using integrated domain agents.
        Prioritizes healing based on violation severity and type.

        Args:
            violations: List of PhaseViolation objects
            dry_run: If True, only preview actions
            max_actions: Maximum cleanup actions per run

        Returns:
            List of action dicts with results and batch summary
        

#### run_with_cleanup
**Parameters**: self, files, dry_run
**Returns**: dict[str, Any]
**Description**: 
        GOLD STANDARD: Full orchestration with autonomous cleanup.
        Runs all phases, validates, and cleans up violations.

        Args:
            files: Optional list of files to process
            dry_run: If True, only preview cleanup actions

        Returns:
            Dict with comprehensive execution and cleanup summaries
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 orchestration agent - operational only.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by NervousSystemAgent.

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
        



## Function: __init__

**Parameters**: self, cognitive_plane, action_plane, config
**Returns**: None
**Description**: Initialize nervous system.

        Args:
            cognitive_plane: The brain (planning/reasoning)
            action_plane: The hands (tool execution)
            config: Orchestrator configuration
        



## Function: _get_CoverageAgent

**Description**: Lazy loader for CoverageAgent (upward L3->L6 seam).



## Function: _handle_bias_update

**Parameters**: self, event_data
**Returns**: None
**Description**: Process CoverageAgent bias events — multi-layer queue.



## Function: _decay_biases

**Parameters**: self
**Returns**: None
**Description**: Decrement and cleanup expired biases with dynamic decay based on health.



## Function: force_exerciser_fallback

**Parameters**: self, task
**Returns**: str | None
**Description**: If no candidates in target layer, direct to exerciser.



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L3 compliance.



## Function: _iteration

**Parameters**: self
**Returns**: Any
**Description**: Iteration.



## Function: _iteration

**Parameters**: self, value
**Returns**: Any
**Description**: Iteration.



## Function: _v15_build_operation_manifest

**Parameters**: self, operation, target_layer
**Returns**: SurgicalManifest | None
**Description**: §8.1a — Construct SurgicalManifest for orchestrator-level operation.



## Function: get_state

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current orchestrator state.

        Returns:
            Current state snapshot
        



## Function: _extract_actions

**Parameters**: self, think_result
**Returns**: list[ActionRequest]
**Description**: Extract action requests from planning result.

        Args:
            think_result: Result from think phase

        Returns:
            List of action requests
        



## Function: validate_architecture

**Parameters**: self, file_paths
**Returns**: dict[str, Any]
**Description**: 
        Validate architecture compliance.

        Args:
            file_paths: Specific files to validate

        Returns:
            Validation report
        



## Function: post_phase_validation

**Parameters**: self, phase_name, affected_paths, dry_run
**Returns**: dict[str, Any]
**Description**: 
        GOLD STANDARD: Post-phase validation using domain-specific agents.
        Validates location, hierarchy, and import compliance after phase completion.

        Args:
            phase_name: Name of the completed phase
            affected_paths: List of file paths affected by the phase
            dry_run: If True, only preview without applying fixes

        Returns:
            Dict with validation results from all integrated agents
        



## Function: cleanup_violations

**Parameters**: self, violations, dry_run, max_actions
**Returns**: list[dict[str, Any]]
**Description**: 
        GOLD STANDARD: Cleanup violations using integrated domain agents.
        Prioritizes healing based on violation severity and type.

        Args:
            violations: List of PhaseViolation objects
            dry_run: If True, only preview actions
            max_actions: Maximum cleanup actions per run

        Returns:
            List of action dicts with results and batch summary
        



## Function: run_with_cleanup

**Parameters**: self, files, dry_run
**Returns**: dict[str, Any]
**Description**: 
        GOLD STANDARD: Full orchestration with autonomous cleanup.
        Runs all phases, validates, and cleans up violations.

        Args:
            files: Optional list of files to process
            dry_run: If True, only preview cleanup actions

        Returns:
            Dict with comprehensive execution and cleanup summaries
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L3 orchestration agent - operational only.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by NervousSystemAgent.

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
        



## Function: _noop_heal

**Parameters**: m


## Function: _state_hash



## Usage Examples

### Class Usage

```python
# Using NervousSystemAgent
nervoussystemagent = NervousSystemAgent()
nervoussystemagent.force_exerciser_fallback()
nervoussystemagent.get_state()
```

### Function Usage

```python
# Using __init__
result = __init__(cognitive_plane, action_plane)
```

```python
# Using _get_CoverageAgent
result = _get_CoverageAgent()
```

```python
# Using _handle_bias_update
result = _handle_bias_update(event_data)
```



---
**Generated**: 2026-03-26T09:39:04.295417
**Type**: api_reference
**Quality**: comprehensive
