# API Documentation: TerritoryChangeHandlerAgent

**Target Audience**: developers, api_users

# TerritoryChangeHandlerAgent API Documentation

**File**: `TerritoryChangeHandlerAgent.py`
**Classes**: 2
**Functions**: 7

## Classes

- **TerritoryChangeHandlerAgent** (inherits from SovereignBaseAgent, FileSystemEventHandler)
- **AutonomousRagDaemon**

## Functions

- **timeout**
- **decorator**
- **__init__** -> None
- **on_modified** -> None
- **heal_repository** -> dict[str, Any]
- **heal**
- **__init__** -> None


## Class: TerritoryChangeHandlerAgent

**Description**: 
    L5 Safety Agent: Watches for territory changes with debouncing.
    Informs the AutonomousRagDaemon when re-indexing is required.
    

**Inherits from**: SovereignBaseAgent, FileSystemEventHandler

### Methods

#### __init__
**Parameters**: self, daemon
**Returns**: None
**Description**: Initialize the agent with debouncing logic.

#### on_modified
**Parameters**: self, event
**Returns**: None
**Description**: Execute on_modified operation when files change.

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: L5 validation - operational health check.

#### heal
**Parameters**: self, violation



## Class: AutonomousRagDaemon

**Description**: 
    L5/L3 Hybrid: Self-monitoring RAG system with autonomous health checks.
    Uses TerritoryChangeHandlerAgent to maintain sync between disk and vector DB.
    

### Methods

#### __init__
**Parameters**: self, orchestrator, retriever, historian
**Returns**: None
**Description**: Initialize the daemon with its dependencies.



## Function: timeout

**Parameters**: seconds


## Function: decorator

**Parameters**: func


## Function: __init__

**Parameters**: self, daemon
**Returns**: None
**Description**: Initialize the agent with debouncing logic.



## Function: on_modified

**Parameters**: self, event
**Returns**: None
**Description**: Execute on_modified operation when files change.



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: L5 validation - operational health check.



## Function: heal

**Parameters**: self, violation


## Function: __init__

**Parameters**: self, orchestrator, retriever, historian
**Returns**: None
**Description**: Initialize the daemon with its dependencies.



## Usage Examples

### Class Usage

```python
# Using TerritoryChangeHandlerAgent
territorychangehandleragent = TerritoryChangeHandlerAgent()
territorychangehandleragent.on_modified()
territorychangehandleragent.heal_repository()
```

```python
# Using AutonomousRagDaemon
autonomousragdaemon = AutonomousRagDaemon()
```

### Function Usage

```python
# Using timeout
result = timeout(seconds)
```

```python
# Using decorator
result = decorator(func)
```

```python
# Using __init__
result = __init__(daemon)
```



---
**Generated**: 2026-03-26T09:39:05.438335
**Type**: api_reference
**Quality**: comprehensive
