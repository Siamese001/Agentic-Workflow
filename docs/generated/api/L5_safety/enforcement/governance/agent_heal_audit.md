# API Documentation: agent_heal_audit

**Target Audience**: developers, api_users

# agent_heal_audit API Documentation

**File**: `agent_heal_audit.py`
**Classes**: 1
**Functions**: 12

## Classes

- **AgentHealAuditScanner**

## Functions

- **main**
- **_get_escalation_scenarios_static** -> list[dict[str, Any]]
- **_get_repo_heal_coverage_static** -> dict[str, int]
- **_get_repo_heal_outcomes_static** -> dict[str, Any]
- **_get_telemetry_schema_summary** -> dict[str, Any]
- **_get_telemetry_aggregates_static** -> dict[str, Any]
- **_get_budget_caps_summary** -> dict[str, Any]
- **generate_markdown_report** -> str
- **__init__**
- **_is_runtime_agent** -> tuple[bool, str]
- **scan_agent_file** -> list[dict[str, Any]]
- **scan_repository** -> dict[str, Any]


## Class: AgentHealAuditScanner

**Description**: AST-based scanner for agent healing capabilities.

### Methods

#### __init__
**Parameters**: self, repo_root
**Description**: Initialize scanner with repository root.

#### _is_runtime_agent
**Parameters**: self, class_name, base_names, file_path
**Returns**: tuple[bool, str]
**Description**: Deterministically classify if a class is a runtime agent.

        Returns:
            (is_runtime, reason)
        

#### scan_agent_file
**Parameters**: self, file_path
**Returns**: list[dict[str, Any]]
**Description**: Scan a single Python file for Agent classes and their healing methods.

#### scan_repository
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Scan entire repository for Agent classes.



## Function: main

**Description**: Main CLI entry point.



## Function: _get_escalation_scenarios_static

**Returns**: list[dict[str, Any]]
**Description**: Return pre-computed escalation scenarios (stdlib only, no imports).

    These are deterministic results from decide_heal_escalation for fixed inputs.
    Pre-computed to avoid runtime imports in AST-only audit module.
    



## Function: _get_repo_heal_coverage_static

**Parameters**: runtime_agents
**Returns**: dict[str, int]
**Description**: Compute repo-heal coverage from runtime agents (static analysis).

    Categorizes agents by their heal_repository implementation status.
    



## Function: _get_repo_heal_outcomes_static

**Returns**: dict[str, Any]
**Description**: Get simulated repo-heal outcomes on a fixed synthetic tree.

    Uses pre-computed values for determinism (no actual file system scan).
    No network calls.
    



## Function: _get_telemetry_schema_summary

**Returns**: dict[str, Any]
**Description**: Get telemetry schema summary for Phase 5 report.

    Returns schema fields and determinism rules (no timestamps).
    



## Function: _get_telemetry_aggregates_static

**Returns**: dict[str, Any]
**Description**: Get telemetry aggregates from synthetic artifacts (fixed set).

    Uses pre-computed values for determinism (no filesystem nondeterminism).
    



## Function: _get_budget_caps_summary

**Returns**: dict[str, Any]
**Description**: Get budget caps summary for Phase 5 report.



## Function: generate_markdown_report

**Parameters**: audit_data
**Returns**: str
**Description**: Generate deterministic markdown report from audit data.



## Function: __init__

**Parameters**: self, repo_root
**Description**: Initialize scanner with repository root.



## Function: _is_runtime_agent

**Parameters**: self, class_name, base_names, file_path
**Returns**: tuple[bool, str]
**Description**: Deterministically classify if a class is a runtime agent.

        Returns:
            (is_runtime, reason)
        



## Function: scan_agent_file

**Parameters**: self, file_path
**Returns**: list[dict[str, Any]]
**Description**: Scan a single Python file for Agent classes and their healing methods.



## Function: scan_repository

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Scan entire repository for Agent classes.



## Usage Examples

### Class Usage

```python
# Using AgentHealAuditScanner
agenthealauditscanner = AgentHealAuditScanner()
agenthealauditscanner.scan_agent_file()
agenthealauditscanner.scan_repository()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using _get_escalation_scenarios_static
result = _get_escalation_scenarios_static()
```

```python
# Using _get_repo_heal_coverage_static
result = _get_repo_heal_coverage_static(runtime_agents)
```



---
**Generated**: 2026-03-26T09:39:05.990616
**Type**: api_reference
**Quality**: comprehensive
