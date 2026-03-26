# API Documentation: OrchestrationHandshakeAgent

**Target Audience**: developers, api_users

# OrchestrationHandshakeAgent API Documentation

**File**: `OrchestrationHandshakeAgent.py`
**Classes**: 1
**Functions**: 6

## Classes

- **OrchestrationHandshakeAgent** (inherits from SovereignBaseAgent, CoreOrchestrationAgent)

## Functions

- **__init__**
- **discover_capable_agents** -> list[dict]
- **delegate_task** -> dict
- **execute_mission** -> list[dict]
- **heal_repository** -> dict
- **heal** -> dict[str, Any]


## Class: OrchestrationHandshakeAgent

**Description**: 
    Sovereign handshake protocol — now with deep L3 caching.
    Renamed from OrchestrationHandshake for consistent Agent suffix pattern.
    

**Inherits from**: SovereignBaseAgent, CoreOrchestrationAgent

### Methods

#### __init__
**Parameters**: self, project_root, requesting_agent

#### discover_capable_agents
**Parameters**: self, Task, min_confidence
**Returns**: list[dict]
**Description**: 
        Discover agents/methods capable of Task via hybrid registry search.
        cache-first — Redis hit -> instant discovery.
        

#### delegate_task
**Parameters**: self, Task, args, kwargs, min_confidence
**Returns**: dict
**Description**: 
        Sovereign delegation — find best method and invoke.
        

#### execute_mission
**Parameters**: self, steps
**Returns**: list[dict]
**Description**: 
        Multi-hop mission logic: Sequential delegation.
        

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: Invoke healing chain via super().

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by OrchestrationHandshakeAgent.

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

**Parameters**: self, project_root, requesting_agent


## Function: discover_capable_agents

**Parameters**: self, Task, min_confidence
**Returns**: list[dict]
**Description**: 
        Discover agents/methods capable of Task via hybrid registry search.
        cache-first — Redis hit -> instant discovery.
        



## Function: delegate_task

**Parameters**: self, Task, args, kwargs, min_confidence
**Returns**: dict
**Description**: 
        Sovereign delegation — find best method and invoke.
        



## Function: execute_mission

**Parameters**: self, steps
**Returns**: list[dict]
**Description**: 
        Multi-hop mission logic: Sequential delegation.
        



## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: Invoke healing chain via super().



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by OrchestrationHandshakeAgent.

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
        



## Usage Examples

### Class Usage

```python
# Using OrchestrationHandshakeAgent
orchestrationhandshakeagent = OrchestrationHandshakeAgent()
orchestrationhandshakeagent.discover_capable_agents()
orchestrationhandshakeagent.delegate_task()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root, requesting_agent)
```

```python
# Using discover_capable_agents
result = discover_capable_agents(Task, min_confidence)
```

```python
# Using delegate_task
result = delegate_task(Task, args)
```



---
**Generated**: 2026-03-26T09:39:04.299614
**Type**: api_reference
**Quality**: comprehensive
