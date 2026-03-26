# API Documentation: L5SafetyExerciserAgent

**Target Audience**: developers, api_users

# L5SafetyExerciserAgent API Documentation

**File**: `L5SafetyExerciserAgent.py`
**Classes**: 1
**Functions**: 20

## Classes

- **L5SafetyExerciserAgent** (inherits from SovereignBaseAgent)

## Functions

- **_get_layer_entry**
- **_get_hierarchy_agent** -> Any
- **_get_naming_agent** -> Any
- **_get_import_agent** -> Any
- **_get_RedTeamAgent** -> Any
- **_get_healer_agent** -> Any
- **log_event** -> Any
- **__init__** -> None
- **act** -> str
- **_exercise_naming_validation** -> str
- **_exercise_hierarchy_check** -> str
- **_exercise_gravity_check** -> str
- **_exercise_healing_probe** -> str
- **_exercise_red_team_probe** -> str
- **_exercise_guardrail_limits** -> str
- **heal_repository** -> dict
- **_run_self_tests** -> dict
- **heal** -> dict[str, Any]
- **layer_entry**
- **wrapper**


## Class: L5SafetyExerciserAgent

**Description**: 
    Sub-atomic responsibility: Safely exercise L5 safety primitives via no-op/dry-run checks.
    Triggered by CoverageAgent synthetic tasks — directly boosts L5 metrics.
    Dispatch table keeps CC low (linear, no nesting).
    All operations isolated (temp files, in-memory) — zero persistent side effects.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the instance.

#### act
**Parameters**: self
**Returns**: str
**Description**: Primary entrypoint — called by orchestrator on synthetic task.

#### _exercise_naming_validation
**Parameters**: self
**Returns**: str
**Description**: Probe naming laws on synthetic filenames.

#### _exercise_hierarchy_check
**Parameters**: self
**Returns**: str
**Description**: Dry-run hierarchy validation (in-memory).

#### _exercise_gravity_check
**Parameters**: self
**Returns**: str
**Description**: Probe gravity on synthetic import code.

#### _exercise_healing_probe
**Parameters**: self
**Returns**: str
**Description**: Trigger healer on dummy violation.

#### _exercise_red_team_probe
**Parameters**: self
**Returns**: str
**Description**: Light red team fuzz (prompt injection simulation).

#### _exercise_guardrail_limits
**Parameters**: self
**Returns**: str
**Description**: Cycle rate limit / mutation guard (in-memory counter).

#### heal_repository
**Parameters**: self, dry_run
**Returns**: dict
**Description**: Repository healing with parent chain invocation.

#### _run_self_tests
**Parameters**: self
**Returns**: dict
**Description**: Run internal self-tests.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by L5SafetyExerciserAgent.

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



## Function: _get_hierarchy_agent

**Returns**: Any
**Description**: Get hierarchy agent.



## Function: _get_naming_agent

**Returns**: Any
**Description**: Get naming agent.



## Function: _get_import_agent

**Returns**: Any
**Description**: Get import healer (Phase 5 Migration: ImportAgent -> CodeHealerAgent).



## Function: _get_RedTeamAgent

**Returns**: Any
**Description**: Get red team agent.



## Function: _get_healer_agent

**Returns**: Any
**Description**: Get healer agent.



## Function: log_event

**Parameters**: event_type, payload
**Returns**: Any
**Description**: Log event with fallback to print.



## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the instance.



## Function: act

**Parameters**: self
**Returns**: str
**Description**: Primary entrypoint — called by orchestrator on synthetic task.



## Function: _exercise_naming_validation

**Parameters**: self
**Returns**: str
**Description**: Probe naming laws on synthetic filenames.



## Function: _exercise_hierarchy_check

**Parameters**: self
**Returns**: str
**Description**: Dry-run hierarchy validation (in-memory).



## Function: _exercise_gravity_check

**Parameters**: self
**Returns**: str
**Description**: Probe gravity on synthetic import code.



## Function: _exercise_healing_probe

**Parameters**: self
**Returns**: str
**Description**: Trigger healer on dummy violation.



## Function: _exercise_red_team_probe

**Parameters**: self
**Returns**: str
**Description**: Light red team fuzz (prompt injection simulation).



## Function: _exercise_guardrail_limits

**Parameters**: self
**Returns**: str
**Description**: Cycle rate limit / mutation guard (in-memory counter).



## Function: heal_repository

**Parameters**: self, dry_run
**Returns**: dict
**Description**: Repository healing with parent chain invocation.



## Function: _run_self_tests

**Parameters**: self
**Returns**: dict
**Description**: Run internal self-tests.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by L5SafetyExerciserAgent.

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



## Function: wrapper

**Parameters**: f


## Usage Examples

### Class Usage

```python
# Using L5SafetyExerciserAgent
l5safetyexerciseragent = L5SafetyExerciserAgent()
l5safetyexerciseragent.act()
l5safetyexerciseragent.heal_repository()
```

### Function Usage

```python
# Using _get_layer_entry
result = _get_layer_entry()
```

```python
# Using _get_hierarchy_agent
result = _get_hierarchy_agent()
```

```python
# Using _get_naming_agent
result = _get_naming_agent()
```



---
**Generated**: 2026-03-26T09:39:05.288367
**Type**: api_reference
**Quality**: comprehensive
