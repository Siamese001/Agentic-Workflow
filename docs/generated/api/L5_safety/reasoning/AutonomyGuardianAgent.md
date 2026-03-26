# API Documentation: AutonomyGuardianAgent

**Target Audience**: developers, api_users

# AutonomyGuardianAgent API Documentation

**File**: `AutonomyGuardianAgent.py`
**Classes**: 1
**Functions**: 13

## Classes

- **AutonomyGuardianAgent** (inherits from SovereignBaseAgent)

## Functions

- **_get_DashboardDataGenerator**
- **get_autonomy_guardian** -> AutonomyGuardianAgent
- **__init__** -> None
- **heal** -> dict[str, Any]
- **validate_agent_autonomy** -> list[str]
- **run** -> list[tuple[Path, str]]
- **_check_forbidden_runner_scripts** -> None
- **_check_agent_autonomy_violations** -> None
- **heal_repository** -> dict[str, int]
- **generate_compliance_report** -> None
- **_save_modular_markdown_report** -> None
- **_generate_dashboard_v2_with_rows** -> None
- **heal_repository** -> dict[str, Any]


## Class: AutonomyGuardianAgent

**Description**: 
    Sovereign guardian for agent autonomy enforcement.

    Responsibilities:
    1. Validate agents have Autonomous Repair Capability (heal_repository via SovereignBaseAgent).
    2. Detect and purge forbidden external runner scripts.
    3. Delegate high-complexity reporting to L6 observability engine.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None
**Description**: Initialize the instance.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for AutonomyGuardianAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        

#### validate_agent_autonomy
**Parameters**: self, agent_file
**Returns**: list[str]
**Description**: Delegate autonomy validation to deterministic Guardian test.

#### run
**Parameters**: self
**Returns**: list[tuple[Path, str]]
**Description**: Scan repository for autonomy and script violations.

#### _check_forbidden_runner_scripts
**Parameters**: self, violations
**Returns**: None
**Description**: Check for forbidden runner scripts.

#### _check_agent_autonomy_violations
**Parameters**: self, violations
**Returns**: None
**Description**: Check for agent autonomy violations.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Meta-healing: Purge forbidden scripts and report missing methods.

#### generate_compliance_report
**Parameters**: self, markdown, context
**Returns**: None
**Description**: Sovereign Orchestrator: Delegates processing to L6 Modular Engine.

#### _save_modular_markdown_report
**Parameters**: self, today, total_row, dashboard_rows
**Returns**: None
**Description**: Passive Markdown renderer consuming pre-computed L6 rows.

#### _generate_dashboard_v2_with_rows
**Parameters**: self, today, dashboard_rows, total_row
**Returns**: None
**Description**: L6 Interactive Dashboard generation consuming pre-computed unified rows.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing with Cognitive Performance tracking.

        Searches Pinecone for existing healing patterns before applying fixes,
        enabling pattern reuse and accelerated healing convergence.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, execute healing actions
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Internal recursion tracking

        Returns:
            Dict with healing summary: {"violations": int, "healed": int, "errors": int, "renamed": int}
        



## Function: _get_DashboardDataGenerator

**Description**: Lazy load DashboardDataGenerator to avoid upward import.



## Function: get_autonomy_guardian

**Parameters**: project_root
**Returns**: AutonomyGuardianAgent
**Description**: Factory function to create AutonomyGuardianAgent instance.



## Function: __init__

**Parameters**: self, project_root
**Returns**: None
**Description**: Initialize the instance.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for AutonomyGuardianAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        



## Function: validate_agent_autonomy

**Parameters**: self, agent_file
**Returns**: list[str]
**Description**: Delegate autonomy validation to deterministic Guardian test.



## Function: run

**Parameters**: self
**Returns**: list[tuple[Path, str]]
**Description**: Scan repository for autonomy and script violations.



## Function: _check_forbidden_runner_scripts

**Parameters**: self, violations
**Returns**: None
**Description**: Check for forbidden runner scripts.



## Function: _check_agent_autonomy_violations

**Parameters**: self, violations
**Returns**: None
**Description**: Check for agent autonomy violations.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Meta-healing: Purge forbidden scripts and report missing methods.



## Function: generate_compliance_report

**Parameters**: self, markdown, context
**Returns**: None
**Description**: Sovereign Orchestrator: Delegates processing to L6 Modular Engine.



## Function: _save_modular_markdown_report

**Parameters**: self, today, total_row, dashboard_rows
**Returns**: None
**Description**: Passive Markdown renderer consuming pre-computed L6 rows.



## Function: _generate_dashboard_v2_with_rows

**Parameters**: self, today, dashboard_rows, total_row
**Returns**: None
**Description**: L6 Interactive Dashboard generation consuming pre-computed unified rows.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing with Cognitive Performance tracking.

        Searches Pinecone for existing healing patterns before applying fixes,
        enabling pattern reuse and accelerated healing convergence.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, execute healing actions
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Internal recursion tracking

        Returns:
            Dict with healing summary: {"violations": int, "healed": int, "errors": int, "renamed": int}
        



## Usage Examples

### Class Usage

```python
# Using AutonomyGuardianAgent
autonomyguardianagent = AutonomyGuardianAgent()
autonomyguardianagent.heal()
autonomyguardianagent.validate_agent_autonomy()
```

### Function Usage

```python
# Using _get_DashboardDataGenerator
result = _get_DashboardDataGenerator()
```

```python
# Using get_autonomy_guardian
result = get_autonomy_guardian(project_root)
```

```python
# Using __init__
result = __init__(project_root)
```



---
**Generated**: 2026-03-26T09:39:05.051061
**Type**: api_reference
**Quality**: comprehensive
