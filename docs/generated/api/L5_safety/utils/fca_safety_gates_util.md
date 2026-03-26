# API Documentation: fca_safety_gates_util

**Target Audience**: developers, api_users

# fca_safety_gates_util API Documentation

**File**: `fca_safety_gates_util.py`
**Classes**: 4
**Functions**: 15

## Classes

- **PlannedAction**
- **SafetyGateResult**
- **NestedLCDPolicy**
- **WaveConfig**

## Functions

- **check_rename_collisions** -> list[dict[str, Any]]
- **build_import_graph** -> dict[str, int]
- **_increment_import** -> None
- **check_init_reexports** -> int
- **check_import_impact** -> list[dict[str, Any]]
- **check_mass_action** -> dict[str, Any] | None
- **detect_agent_lineage** -> str
- **_extract_base_names** -> list[str]
- **check_observability_violation** -> dict[str, Any] | None
- **_is_observability_import** -> bool
- **check_nested_lcd_with_policy** -> dict[str, Any] | None
- **build_execution_plan** -> dict[str, Any]
- **filter_actions_for_wave** -> list[PlannedAction]
- **run_all_safety_gates** -> SafetyGateResult
- **_norm** -> str


## Class: PlannedAction

**Description**: A single proposed rename/move action.



## Class: SafetyGateResult

**Description**: Aggregate result of all safety gate checks.



## Class: NestedLCDPolicy

**Description**: Policy configuration for nested LCD subtree detection.



## Class: WaveConfig

**Description**: Configuration for a single execution wave.



## Function: check_rename_collisions

**Parameters**: rename_map, existing_files, case_sensitive
**Returns**: list[dict[str, Any]]
**Description**: 
    Detect rename collisions in a proposed rename map.

    Args:
        rename_map: {src_path -> proposed_dst_path} (relative paths, forward slashes)
        existing_files: set of all existing file paths (relative, forward slashes)
        case_sensitive: if False, detect casing-only conflicts (Windows/macOS default)

    Returns:
        List of collision dicts, each with:
            - type: "DST_COLLISION" | "DST_EXISTS" | "CASING_CONFLICT"
            - src: source path(s) involved
            - dst: destination path
            - message: human-readable description
    



## Function: build_import_graph

**Parameters**: python_files, project_root
**Returns**: dict[str, int]
**Description**: 
    Build approximate import count per module via AST.

    Returns:
        {relative_module_path -> count_of_files_that_import_it}
    



## Function: _increment_import

**Parameters**: mod, module_to_relpath, import_counts
**Returns**: None
**Description**: Increment import count for a module if it's in our project.



## Function: check_init_reexports

**Parameters**: path
**Returns**: int
**Description**: 
    Count how many __init__.py files re-export symbols from this module.

    Each re-export adds +10 to impact score per the spec.
    Returns the bonus impact score.
    



## Function: check_import_impact

**Parameters**: rename_map, import_counts, python_files, project_root, max_import_impact
**Returns**: list[dict[str, Any]]
**Description**: 
    Gate renames/moves that affect high-import-count modules.

    Args:
        rename_map: {src_relative -> dst_relative}
        import_counts: {relative_path -> import_count} from build_import_graph
        python_files: list of all python files for init re-export scanning
        project_root: repo root
        max_import_impact: threshold above which actions are blocked

    Returns:
        List of blocked items with impact details.
    



## Function: check_mass_action

**Parameters**: planned_actions_total, max_actions, force, wave_id
**Returns**: dict[str, Any] | None
**Description**: 
    Block execution if too many actions are planned.

    Args:
        planned_actions_total: total number of actions to execute
        max_actions: threshold (default 50)
        force: explicit override flag
        wave_id: required identifier when force=True

    Returns:
        None if OK, or a blocking dict with reason.
    



## Function: detect_agent_lineage

**Parameters**: path
**Returns**: str
**Description**: 
    AST-based agent detection via class inheritance analysis.

    Returns:
        "AGENT" — confirmed agent (inherits from known base)
        "ORCHESTRATOR" — confirmed orchestrator
        "EXECUTOR" — confirmed executor
        "AGENT_DETECTION_UNCERTAIN" — has Agent-like name but no confirmed lineage
        "NOT_AGENT" — no agent indicators found
    



## Function: _extract_base_names

**Parameters**: class_node
**Returns**: list[str]
**Description**: Extract base class names from a ClassDef node.



## Function: check_observability_violation

**Parameters**: path, parts
**Returns**: dict[str, Any] | None
**Description**: 
    Detect OBSERVABILITY_OUTSIDE_L6 using import evidence, not just keywords.

    Rules:
        - Only flag if file imports known observability packages/modules
          OR lives under known observability infra folders.
        - L0 maintenance scripts referencing dashboards are ALLOWED (allowlisted).
        - Keyword-only matches produce a WARNING, not a VIOLATION.

    Returns:
        None if compliant, or violation dict.
    



## Function: _is_observability_import

**Parameters**: mod
**Returns**: bool
**Description**: Check if a module name is a known observability package.



## Function: check_nested_lcd_with_policy

**Parameters**: parts, validate_fn, policy
**Returns**: dict[str, Any] | None
**Description**: 
    Wrapper around validate_no_nested_lcd that applies policy.

    When strict=False (default), findings become warnings and are NOT executable.
    When strict=True, findings are violations and are executable.
    



## Function: build_execution_plan

**Parameters**: actions
**Returns**: dict[str, Any]
**Description**: 
    Produce a machine-readable, stable-ordered execution plan.

    Returns:
        {
            "planned_actions": [...],  # sorted by (action_type, src)
            "summary": {"action_type -> count", "blocked_reason -> count"},
            "total": int,
            "blocked": int,
            "executable": int,
        }
    



## Function: filter_actions_for_wave

**Parameters**: actions, wave_config
**Returns**: list[PlannedAction]
**Description**: 
    Filter and limit actions for a specific execution wave.

    Only actions matching allow_action_types are included.
    Stops at max_actions_per_wave.
    Blocked actions are excluded.
    



## Function: run_all_safety_gates

**Parameters**: rename_map, existing_files, python_files, project_root, case_sensitive, max_import_impact, max_actions, force, wave_id, import_counts
**Returns**: SafetyGateResult
**Description**: 
    Run all safety gates on a proposed rename/move plan.

    Returns a SafetyGateResult with all blocked items and summary.
    



## Function: _norm

**Parameters**: p
**Returns**: str


## Usage Examples

### Class Usage

```python
# Using PlannedAction
plannedaction = PlannedAction()
```

```python
# Using SafetyGateResult
safetygateresult = SafetyGateResult()
```

```python
# Using NestedLCDPolicy
nestedlcdpolicy = NestedLCDPolicy()
```

### Function Usage

```python
# Using check_rename_collisions
result = check_rename_collisions(rename_map, existing_files)
```

```python
# Using build_import_graph
result = build_import_graph(python_files, project_root)
```

```python
# Using _increment_import
result = _increment_import(mod, module_to_relpath)
```



---
**Generated**: 2026-03-26T09:39:05.640687
**Type**: api_reference
**Quality**: comprehensive
