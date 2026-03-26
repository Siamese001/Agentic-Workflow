# API Documentation: subprocess_runner_util

**Target Audience**: developers, api_users

# subprocess_runner_util API Documentation

**File**: `subprocess_runner_util.py`
**Classes**: 0
**Functions**: 5


## Functions

- **invoke_arch_governor** -> dict[str, Any]
- **invoke_orchestrator_mission** -> dict[str, Any]
- **invoke_agent_roster_validation** -> dict[str, Any]
- **invoke_hierarchy_agent** -> dict[str, Any]
- **invoke_code_validator** -> dict[str, Any]


## Function: invoke_arch_governor

**Parameters**: action, project_root, targets, auto_approve
**Returns**: dict[str, Any]
**Description**: 
    Invoke ArchitectureGovernorAgent via subprocess.

    Args:
        action: One of 'verify', 'capture_baseline', 'audit'
        project_root: Project root path (auto-detected if None)
        targets: Target territories for audit action
        auto_approve: Auto-approve mode

    Returns:
        Dict with 'success' key and action-specific results
    



## Function: invoke_orchestrator_mission

**Parameters**: project_root, targets, execute
**Returns**: dict[str, Any]
**Description**: 
    Invoke orchestrator mission via subprocess.

    Args:
        project_root: Project root path (auto-detected if None)
        targets: Target territories
        execute: Execute mode (vs dry-run)

    Returns:
        Dict with 'success' key and mission results
    



## Function: invoke_agent_roster_validation

**Returns**: dict[str, Any]
**Description**: 
    Invoke agent roster validation via subprocess.

    Returns:
        Dict with 'success', 'agents_validated', and 'integrity_errors' keys
    



## Function: invoke_hierarchy_agent

**Parameters**: action, project_root
**Returns**: dict[str, Any]
**Description**: 
    Invoke HierarchyAgent via subprocess.

    Args:
        action: One of 'dry_run', 'heal_violations', 'verify_mro'
        project_root: Project root path (auto-detected if None)

    Returns:
        Dict with 'success' key and action-specific results
    



## Function: invoke_code_validator

**Parameters**: action, project_root, directory
**Returns**: dict[str, Any]
**Description**: 
    Invoke CodeValidatorAgent via subprocess.

    Args:
        action: One of 'validate', 'validate_directory'
        project_root: Project root path (auto-detected if None)
        directory: Directory to validate (required for validate_directory)

    Returns:
        Dict with 'success' key and action-specific results
    



## Usage Examples

### Function Usage

```python
# Using invoke_arch_governor
result = invoke_arch_governor(action, project_root)
```

```python
# Using invoke_orchestrator_mission
result = invoke_orchestrator_mission(project_root, targets)
```

```python
# Using invoke_agent_roster_validation
result = invoke_agent_roster_validation()
```



---
**Generated**: 2026-03-26T09:39:03.558188
**Type**: api_reference
**Quality**: comprehensive
