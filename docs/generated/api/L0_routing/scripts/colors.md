# API Documentation: colors

**Target Audience**: developers, api_users

# colors API Documentation

**File**: `colors.py`
**Classes**: 1
**Functions**: 22

## Classes

- **Colors**

## Functions

- **_get_orchestrator_class**
- **_get_checkpoint_manager**
- **_save_runtime_state**
- **_add_event**
- **_update_meta_learning_state**
- **_update_redis_state**
- **_update_pinecone_state**
- **_update_agent_execution**
- **main**
- **report_consolidated_summary**
- **process_discovery_data**
- **list_available_agents** -> list
- **phase_header**
- **tier_summary**
- **mission_header**
- **mission_summary**
- **agent_status**
- **progress_bar**
- **log_status**
- **heartbeat**
- **discover_agent** -> tuple
- **get_performance_analyst_safe**


## Class: Colors



## Function: _get_orchestrator_class



## Function: _get_checkpoint_manager



## Function: _save_runtime_state

**Parameters**: project_root_path
**Description**: Persist runtime state to JSON for dashboard polling.



## Function: _add_event

**Parameters**: event_type, message
**Description**: Add timestamped event to runtime state.



## Function: _update_meta_learning_state

**Parameters**: experience_data
**Description**: Update runtime state with new meta-learning experience.



## Function: _update_redis_state

**Parameters**: operation, key, hit
**Description**: Update runtime state with Redis operation.



## Function: _update_pinecone_state

**Parameters**: operation, metadata
**Description**: Update runtime state with Pinecone operation.



## Function: _update_agent_execution

**Parameters**: agent_name, layer, start_time, end_time, success
**Description**: Update execution timeline with agent completion.



## Function: main

**Description**: Main entry point for the Canon Validator.



## Function: report_consolidated_summary

**Parameters**: results, gemini_active
**Description**: Phase 4.5: Generates the Consolidated Sovereign Health Report.



## Function: process_discovery_data

**Parameters**: data


## Function: list_available_agents

**Parameters**: dedupe
**Returns**: list
**Description**: 
        STRICT SSOT DISCOVERY: Always runs live AST scan.
        No caching, no stale artifacts. Guaranteed fresh truth.
        



## Function: phase_header



## Function: tier_summary



## Function: mission_header



## Function: mission_summary



## Function: agent_status



## Function: progress_bar



## Function: log_status

**Parameters**: level, msg


## Function: heartbeat

**Parameters**: i


## Function: discover_agent

**Parameters**: agent_name
**Returns**: tuple
**Description**: Discover agent by searching for matching class name via AST.



## Function: get_performance_analyst_safe

**Parameters**: root


## Usage Examples

### Class Usage

```python
# Using Colors
colors = Colors()
```

### Function Usage

```python
# Using _get_orchestrator_class
result = _get_orchestrator_class()
```

```python
# Using _get_checkpoint_manager
result = _get_checkpoint_manager()
```

```python
# Using _save_runtime_state
result = _save_runtime_state(project_root_path)
```



---
**Generated**: 2026-03-26T09:39:02.819265
**Type**: api_reference
**Quality**: comprehensive
