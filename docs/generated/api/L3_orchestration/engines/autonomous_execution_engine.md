# API Documentation: autonomous_execution_engine

**Target Audience**: developers, api_users

# autonomous_execution_engine API Documentation

**File**: `autonomous_execution_engine.py`
**Classes**: 1
**Functions**: 9

## Classes

- **autonomous_execution_engine**

## Functions

- **_get_create_proactive_resource_manager**
- **_get_create_autonomous_checkpoint_manager**
- **create_autonomous_execution_engine** -> AutonomousExecutionEngine
- **__init__**
- **awaken**
- **load_state**
- **save_state**
- **get_execution_status** -> dict[str, Any]
- **reset_circuit_breaker**


## Class: autonomous_execution_engine

**Description**: 
    L3 Execution Engine that continuously validates and heals the Canon.

    Features:
    - Eternal execution cycle with configurable intervals
    - Circuit breaker pattern for failure protection
    - Atomic state saves to prevent corruption
    - Resource-aware execution
    - Checkpoint integration for recovery
    

### Methods

#### __init__
**Parameters**: self

#### awaken
**Parameters**: self
**Description**: L3: Explicitly wake the execution heart of the Canon

#### load_state
**Parameters**: self
**Description**: Load previous execution state

#### save_state
**Parameters**: self
**Description**: L3: Atomic state save to prevent corruption

#### get_execution_status
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current execution status

#### reset_circuit_breaker
**Parameters**: self
**Description**: Reset circuit breaker and resume execution



## Function: _get_create_proactive_resource_manager

**Description**: Lazy load create_proactive_resource_manager to avoid upward import.



## Function: _get_create_autonomous_checkpoint_manager

**Description**: Lazy loader for create_autonomous_checkpoint_manager (upward L3->L4 seam).



## Function: create_autonomous_execution_engine

**Returns**: AutonomousExecutionEngine
**Description**: Factory function to create autonomous execution engine



## Function: __init__

**Parameters**: self


## Function: awaken

**Parameters**: self
**Description**: L3: Explicitly wake the execution heart of the Canon



## Function: load_state

**Parameters**: self
**Description**: Load previous execution state



## Function: save_state

**Parameters**: self
**Description**: L3: Atomic state save to prevent corruption



## Function: get_execution_status

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current execution status



## Function: reset_circuit_breaker

**Parameters**: self
**Description**: Reset circuit breaker and resume execution



## Usage Examples

### Class Usage

```python
# Using autonomous_execution_engine
autonomous_execution_engine = autonomous_execution_engine()
autonomous_execution_engine.awaken()
autonomous_execution_engine.load_state()
```

### Function Usage

```python
# Using _get_create_proactive_resource_manager
result = _get_create_proactive_resource_manager()
```

```python
# Using _get_create_autonomous_checkpoint_manager
result = _get_create_autonomous_checkpoint_manager()
```

```python
# Using create_autonomous_execution_engine
result = create_autonomous_execution_engine()
```



---
**Generated**: 2026-03-26T09:39:04.137335
**Type**: api_reference
**Quality**: comprehensive
