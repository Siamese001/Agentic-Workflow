# API Documentation: SovereignActionPlaneAgent

**Target Audience**: developers, api_users

# SovereignActionPlaneAgent API Documentation

**File**: `SovereignActionPlaneAgent.py`
**Classes**: 3
**Functions**: 13

## Classes

- **SovereignToolsmith**
- **SovereignSandbox**
- **SovereignActionPlaneAgent** (inherits from SovereignBaseAgent, IActionPlane)

## Functions

- **create_sovereign_action_plane** -> IActionPlane
- **get_sovereign_action_plane** -> SovereignActionPlane
- **__init__** -> None
- **__init__** -> None
- **__init__** -> None
- **_run_self_tests** -> bool
- **get_capabilities** -> list[Any]
- **get_available_tools** -> list[str]
- **_v15_build_operation_manifest** -> SurgicalManifest | None
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **_noop_heal**
- **_state_hash**


## Class: SovereignToolsmith

**Description**: Toolsmith implementation for dynamic tool creation.

### Methods

#### __init__
**Parameters**: self, output_dir
**Returns**: None
**Description**: 
        Initialize Toolsmith.

        Args:
            output_dir: Directory for generated tools
        



## Class: SovereignSandbox

**Description**: Secure execution environment for tools.

### Methods

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize sandbox.



## Class: SovereignActionPlaneAgent

**Description**: Sovereign action plane with Toolsmith and Sandbox.

**Inherits from**: SovereignBaseAgent, IActionPlane

### Methods

#### __init__
**Parameters**: self, safety_layer, SignalLedger
**Returns**: None
**Description**: Initialize the sovereign action plane.

        Args:
            safety_layer: L5 safety layer for validation
            SignalLedger: L4 signal ledger for logging ExecutionResults
        

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L2 compliance.

#### get_capabilities
**Parameters**: self
**Returns**: list[Any]
**Description**: Get available action capabilities.

#### get_available_tools
**Parameters**: self
**Returns**: list[str]
**Description**: Get list of available tool names.

#### _v15_build_operation_manifest
**Parameters**: self, operation, target_layer
**Returns**: SurgicalManifest | None
**Description**: §8.1b — Construct SurgicalManifest for L2 action plane operation.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L2 execution agent - operational only.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by SovereignActionPlaneAgent.

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
        



## Function: create_sovereign_action_plane

**Parameters**: safety_layer, SignalLedger
**Returns**: IActionPlane
**Description**: Factory function to create sovereign action plane.

    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    Args:
        safety_layer: L5 safety layer for validation
        SignalLedger: L4 signal ledger for logging ExecutionResults

    Returns:
        SovereignActionPlane instance
    



## Function: get_sovereign_action_plane

**Returns**: SovereignActionPlane
**Description**: Factory function to get sovereign action plane instance.



## Function: __init__

**Parameters**: self, output_dir
**Returns**: None
**Description**: 
        Initialize Toolsmith.

        Args:
            output_dir: Directory for generated tools
        



## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize sandbox.



## Function: __init__

**Parameters**: self, safety_layer, SignalLedger
**Returns**: None
**Description**: Initialize the sovereign action plane.

        Args:
            safety_layer: L5 safety layer for validation
            SignalLedger: L4 signal ledger for logging ExecutionResults
        



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L2 compliance.



## Function: get_capabilities

**Parameters**: self
**Returns**: list[Any]
**Description**: Get available action capabilities.



## Function: get_available_tools

**Parameters**: self
**Returns**: list[str]
**Description**: Get list of available tool names.



## Function: _v15_build_operation_manifest

**Parameters**: self, operation, target_layer
**Returns**: SurgicalManifest | None
**Description**: §8.1b — Construct SurgicalManifest for L2 action plane operation.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L2 execution agent - operational only.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by SovereignActionPlaneAgent.

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
# Using SovereignToolsmith
sovereigntoolsmith = SovereignToolsmith()
```

```python
# Using SovereignSandbox
sovereignsandbox = SovereignSandbox()
```

```python
# Using SovereignActionPlaneAgent
sovereignactionplaneagent = SovereignActionPlaneAgent()
sovereignactionplaneagent.get_capabilities()
sovereignactionplaneagent.get_available_tools()
```

### Function Usage

```python
# Using create_sovereign_action_plane
result = create_sovereign_action_plane(safety_layer, SignalLedger)
```

```python
# Using get_sovereign_action_plane
result = get_sovereign_action_plane()
```

```python
# Using __init__
result = __init__(output_dir)
```



---
**Generated**: 2026-03-26T09:39:05.406303
**Type**: api_reference
**Quality**: comprehensive
