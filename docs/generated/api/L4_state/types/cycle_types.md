# API Documentation: cycle_types

**Target Audience**: developers, api_users

# cycle_types API Documentation

**File**: `cycle_types.py`
**Classes**: 3
**Functions**: 5

## Classes

- **CycleConfig**
- **CycleState**
- **ThinkActObserveEngine**

## Functions

- **_get_write_gateway**
- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **__init__**
- **get_state** -> dict[str, Any] | None


## Class: CycleConfig

**Description**: configuration for Think-Act-Observe cycle.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: CycleState

**Description**: State of the Think-Act-Observe cycle.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: ThinkActObserveEngine

**Description**: Engine for executing the Think-Act-Observe cycle.

    Integrates:
    - ReAct engine for structured reasoning (Pillar 6)
    - DAG engine for Task dependencies (Pillar 4)
    - State persistence for pause/resume

    5-Step Cycle:
    1. MISSION - Define the goal
    2. SCENE - Gather context
    3. THINK - Plan next actions (uses ReAct)
    4. ACT - Execute actions (uses DAG)
    5. OBSERVE - Interpret results and update state
    

### Methods

#### __init__
**Parameters**: self, config, enable_logging
**Description**: Initialize Think-Act-Observe engine.

        Args:
            config: Cycle configuration
            enable_logging: Enable logging
        

#### get_state
**Parameters**: self
**Returns**: dict[str, Any] | None
**Description**: Get current cycle state.

        Returns:
            Current state or None
        



## Function: _get_write_gateway

**Description**: Get UWG instance - L4 may only use, not import tools.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: __init__

**Parameters**: self, config, enable_logging
**Description**: Initialize Think-Act-Observe engine.

        Args:
            config: Cycle configuration
            enable_logging: Enable logging
        



## Function: get_state

**Parameters**: self
**Returns**: dict[str, Any] | None
**Description**: Get current cycle state.

        Returns:
            Current state or None
        



## Usage Examples

### Class Usage

```python
# Using CycleConfig
cycleconfig = CycleConfig()
cycleconfig.to_dict()
```

```python
# Using CycleState
cyclestate = CycleState()
cyclestate.to_dict()
```

```python
# Using ThinkActObserveEngine
thinkactobserveengine = ThinkActObserveEngine()
thinkactobserveengine.get_state()
```

### Function Usage

```python
# Using _get_write_gateway
result = _get_write_gateway()
```

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:04.633365
**Type**: api_reference
**Quality**: comprehensive
