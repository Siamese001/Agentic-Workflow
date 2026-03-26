# API Documentation: AutonomousThreatEvolutionAgent

**Target Audience**: developers, api_users

# AutonomousThreatEvolutionAgent API Documentation

**File**: `AutonomousThreatEvolutionAgent.py`
**Classes**: 1
**Functions**: 11

## Classes

- **AutonomousThreatEvolutionAgent** (inherits from SovereignBaseAgent)

## Functions

- **create_threat_evolution_agent** -> AutonomousThreatEvolution
- **__init__** -> None
- **_load_recent_detections** -> list[dict]
- **_analyze_patterns** -> list[dict]
- **heal_repository** -> dict[str, int]
- **stop** -> Any
- **get_status** -> dict
- **set_evolution_interval** -> Any
- **set_confidence_threshold** -> Any
- **manual_evolution_cycle** -> int
- **heal** -> dict


## Class: AutonomousThreatEvolutionAgent

**Description**: L5: Self-healing security agent

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, SafetyEngine
**Returns**: None
**Description**: 
        Initialize autonomous threat evolution agent.

        Args:
            SafetyEngine: Optional safety engine instance
        

#### _load_recent_detections
**Parameters**: self, hours
**Returns**: list[dict]
**Description**: Load recent detections.

#### _analyze_patterns
**Parameters**: self, detections
**Returns**: list[dict]
**Description**: Clustering logic for emerging threats

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L5 safety agent - operational only.

#### stop
**Parameters**: self
**Returns**: Any
**Description**: Graceful shutdown

#### get_status
**Parameters**: self
**Returns**: dict
**Description**: Get current agent status

#### set_evolution_interval
**Parameters**: self, seconds
**Returns**: Any
**Description**: Update evolution cycle interval

#### set_confidence_threshold
**Parameters**: self, threshold
**Returns**: Any
**Description**: Update confidence threshold for rule generation

#### manual_evolution_cycle
**Parameters**: self
**Returns**: int
**Description**: Trigger an immediate evolution cycle (synchronous for testing)

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal threat evolution violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (threat_pattern)
                - pattern: Detected threat pattern
                - confidence: Confidence level

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: create_threat_evolution_agent

**Parameters**: SafetyEngine
**Returns**: AutonomousThreatEvolution
**Description**: Create and configure the threat evolution agent



## Function: __init__

**Parameters**: self, SafetyEngine
**Returns**: None
**Description**: 
        Initialize autonomous threat evolution agent.

        Args:
            SafetyEngine: Optional safety engine instance
        



## Function: _load_recent_detections

**Parameters**: self, hours
**Returns**: list[dict]
**Description**: Load recent detections.



## Function: _analyze_patterns

**Parameters**: self, detections
**Returns**: list[dict]
**Description**: Clustering logic for emerging threats



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L5 safety agent - operational only.



## Function: stop

**Parameters**: self
**Returns**: Any
**Description**: Graceful shutdown



## Function: get_status

**Parameters**: self
**Returns**: dict
**Description**: Get current agent status



## Function: set_evolution_interval

**Parameters**: self, seconds
**Returns**: Any
**Description**: Update evolution cycle interval



## Function: set_confidence_threshold

**Parameters**: self, threshold
**Returns**: Any
**Description**: Update confidence threshold for rule generation



## Function: manual_evolution_cycle

**Parameters**: self
**Returns**: int
**Description**: Trigger an immediate evolution cycle (synchronous for testing)



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal threat evolution violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (threat_pattern)
                - pattern: Detected threat pattern
                - confidence: Confidence level

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using AutonomousThreatEvolutionAgent
autonomousthreatevolutionagent = AutonomousThreatEvolutionAgent()
autonomousthreatevolutionagent.heal_repository()
autonomousthreatevolutionagent.stop()
```

### Function Usage

```python
# Using create_threat_evolution_agent
result = create_threat_evolution_agent(SafetyEngine)
```

```python
# Using __init__
result = __init__(SafetyEngine)
```

```python
# Using _load_recent_detections
result = _load_recent_detections(hours)
```



---
**Generated**: 2026-03-26T09:39:05.047443
**Type**: api_reference
**Quality**: comprehensive
