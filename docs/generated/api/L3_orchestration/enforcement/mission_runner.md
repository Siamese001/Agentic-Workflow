# API Documentation: mission_runner

**Target Audience**: developers, api_users

# mission_runner API Documentation

**File**: `mission_runner.py`
**Classes**: 1
**Functions**: 14

## Classes

- **WatchdogAdapter** (inherits from FileSystemEventHandler)

## Functions

- **_get_imports**
- **_v15_build_mission_manifest**
- **_v15_gateway_audit** -> None
- **run_daemon_mode**
- **run_surgical_mode**
- **run_standard_mode**
- **_start_websocket_server**
- **_build_agenda** -> list
- **_deduplicate_agenda** -> list
- **_handle_max_cycles_reached**
- **_remote_sync**
- **run_ws_server**
- **__init__**
- **on_modified**


## Class: WatchdogAdapter

**Inherits from**: FileSystemEventHandler

### Methods

#### __init__
**Parameters**: self, watchman_handler

#### on_modified
**Parameters**: self, event



## Function: _get_imports

**Description**: Lazy import to avoid circular dependencies.

    NOTE: We import from scripts/CanonValidatorAgent/agents/ which has the FULL
    self-healing agents with mutation logic. The agentic_core/agents/ versions
    are detection-only stubs without healing capabilities.
    



## Function: _v15_build_mission_manifest

**Parameters**: mode_name, target_layer
**Description**: §8.1c — Construct SurgicalManifest for mission runner mode entry.

    Returns None when V15 enforcement is off (zero overhead).
    Lazy imports to avoid pulling heavy dependency chains at module level.
    



## Function: _v15_gateway_audit

**Parameters**: manifest, trace_id
**Returns**: None
**Description**: §8.1c — Invoke gateway.execute in LOG_ONLY mode for audit trail.



## Function: run_daemon_mode

**Description**: 
    L5 Autonomous Mode: The Watchman - monitors repository for changes.

    Watches the repository for file modifications and automatically triggers
    surgical validation missions using blast radius analysis.
    



## Function: run_surgical_mode

**Parameters**: target_file
**Description**: 
    Surgical mode: Target a specific file for validation.

    Uses blast radius analysis to determine which files need to be validated
    based on the dependency graph.

    Args:
        target_file: Path to the file to validate
    



## Function: run_standard_mode

**Description**: 
    Standard L4 Mode: Full validation mission with self-healing cycles.

    Executes a complete validation mission with:
    - GitOps branch creation
    - Multi-cycle self-healing
    - Signal-based agent scheduling
    - Human-in-the-loop intervention
    - Rollback on critical regression
    - Remote sync on completion
    



## Function: _start_websocket_server

**Parameters**: ctx
**Description**: Start WebSocket server for live reasoning stream.



## Function: _build_agenda

**Parameters**: cycle, ctx, agents, GitAgent, StrategicPlannerAgent, ReflectionAgent
**Returns**: list
**Description**: Build the agent execution agenda based on cycle and signals.



## Function: _deduplicate_agenda

**Parameters**: agenda
**Returns**: list
**Description**: Deduplicate agenda while preserving order.



## Function: _handle_max_cycles_reached

**Parameters**: ctx
**Description**: Handle the case when max healing cycles are reached.



## Function: _remote_sync

**Parameters**: ctx, branch_name
**Description**: Sync to remote repository on mission completion.



## Function: run_ws_server



## Function: __init__

**Parameters**: self, watchman_handler


## Function: on_modified

**Parameters**: self, event


## Usage Examples

### Class Usage

```python
# Using WatchdogAdapter
watchdogadapter = WatchdogAdapter()
watchdogadapter.on_modified()
```

### Function Usage

```python
# Using _get_imports
result = _get_imports()
```

```python
# Using _v15_build_mission_manifest
result = _v15_build_mission_manifest(mode_name, target_layer)
```

```python
# Using _v15_gateway_audit
result = _v15_gateway_audit(manifest, trace_id)
```



---
**Generated**: 2026-03-26T09:39:04.121092
**Type**: api_reference
**Quality**: comprehensive
