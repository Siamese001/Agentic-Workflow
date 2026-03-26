# API Documentation: forward_rolling_types

**Target Audience**: developers, api_users

# forward_rolling_types API Documentation

**File**: `forward_rolling_types.py`
**Classes**: 5
**Functions**: 22

## Classes

- **ExecutionMode** (inherits from str, Enum)
- **RolloutStage** (inherits from str, Enum)
- **FeatureFlag**
- **RolloutConfig**
- **ForwardRollingConfig**

## Functions

- **__init__**
- **_init_default_flags** -> None
- **get_execution_mode** -> ExecutionMode
- **_calculate_execution_mode** -> ExecutionMode
- **_should_route_to_forward_rolling** -> bool
- **set_rollout_stage** -> None
- **rollback** -> bool
- **emergency_disable** -> None
- **set_feature_flag** -> FeatureFlag
- **is_feature_enabled** -> bool
- **get_feature_flag** -> FeatureFlag | None
- **get_all_feature_flags** -> dict[str, FeatureFlag]
- **update_config** -> None
- **get_config** -> RolloutConfig
- **get_rollout_percentage** -> int
- **get_routing_stats** -> dict[str, Any]
- **clear_routing_cache** -> int
- **add_agent_to_allowlist** -> bool
- **add_agent_to_blocklist** -> bool
- **remove_agent_from_allowlist** -> bool
- **remove_agent_from_blocklist** -> bool
- **export_config** -> dict[str, Any]


## Class: ExecutionMode

**Description**: Execution mode for orchestration.

**Inherits from**: str, Enum



## Class: RolloutStage

**Description**: Rollout stage for gradual deployment.

**Inherits from**: str, Enum



## Class: FeatureFlag

**Description**: Feature flag configuration.



## Class: RolloutConfig

**Description**: Configuration for Forward-Rolling Recursion rollout.



## Class: ForwardRollingConfig

**Description**: 
    Configuration manager for Forward-Rolling Recursion rollout.

    Features:
    - Feature flags with percentage-based rollout
    - Sticky routing for consistent user experience
    - Runtime configuration updates
    - Instant rollback capability
    - A/B testing support
    

### Methods

#### __init__
**Parameters**: self, initial_stage, config_update_callback
**Description**: 
        Initialize configuration manager.

        Args:
            initial_stage: Initial rollout stage
            config_update_callback: Callback when config changes
        

#### _init_default_flags
**Parameters**: self
**Returns**: None
**Description**: Initialize default feature flags.

#### get_execution_mode
**Parameters**: self, agent_id, mission_id
**Returns**: ExecutionMode
**Description**: 
        Determine execution mode for a specific agent/mission.

        Uses sticky routing to ensure consistent experience.

        Args:
            agent_id: Agent identifier
            mission_id: Optional mission identifier

        Returns:
            ExecutionMode to use for this request
        

#### _calculate_execution_mode
**Parameters**: self, agent_id, mission_id
**Returns**: ExecutionMode
**Description**: Calculate execution mode based on rollout configuration.

#### _should_route_to_forward_rolling
**Parameters**: self, agent_id, mission_id, percentage
**Returns**: bool
**Description**: 
        Determine if request should be routed to Forward-Rolling.

        Uses consistent hashing for deterministic routing.

        Args:
            agent_id: Agent identifier
            mission_id: Mission identifier
            percentage: Rollout percentage (0-100)

        Returns:
            True if should use Forward-Rolling
        

#### set_rollout_stage
**Parameters**: self, stage
**Returns**: None
**Description**: 
        Set the rollout stage.

        Args:
            stage: New rollout stage
        

#### rollback
**Parameters**: self
**Returns**: bool
**Description**: 
        Rollback to previous configuration.

        Returns:
            True if rollback successful
        

#### emergency_disable
**Parameters**: self
**Returns**: None
**Description**: Emergency disable of Forward-Rolling Recursion.

#### set_feature_flag
**Parameters**: self, name, enabled, rollout_percentage, allowed_agents, blocked_agents
**Returns**: FeatureFlag
**Description**: 
        Set or update a feature flag.

        Args:
            name: Flag name
            enabled: Whether flag is enabled
            rollout_percentage: Percentage of traffic (0-100)
            allowed_agents: Set of allowed agent IDs
            blocked_agents: Set of blocked agent IDs

        Returns:
            Updated FeatureFlag
        

#### is_feature_enabled
**Parameters**: self, name, agent_id
**Returns**: bool
**Description**: 
        Check if a feature is enabled for an agent.

        Args:
            name: Feature flag name
            agent_id: Optional agent ID for percentage-based check

        Returns:
            True if feature is enabled
        

#### get_feature_flag
**Parameters**: self, name
**Returns**: FeatureFlag | None
**Description**: Get a feature flag by name.

#### get_all_feature_flags
**Parameters**: self
**Returns**: dict[str, FeatureFlag]
**Description**: Get all feature flags.

#### update_config
**Parameters**: self
**Returns**: None
**Description**: 
        Update configuration values.

        Args:
            **kwargs: Configuration values to update
        

#### get_config
**Parameters**: self
**Returns**: RolloutConfig
**Description**: Get current configuration.

#### get_rollout_percentage
**Parameters**: self
**Returns**: int
**Description**: Get current rollout percentage.

#### get_routing_stats
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get routing statistics.

#### clear_routing_cache
**Parameters**: self
**Returns**: int
**Description**: Clear routing cache and return count cleared.

#### add_agent_to_allowlist
**Parameters**: self, flag_name, agent_id
**Returns**: bool
**Description**: Add agent to a feature flag's allowlist.

#### add_agent_to_blocklist
**Parameters**: self, flag_name, agent_id
**Returns**: bool
**Description**: Add agent to a feature flag's blocklist.

#### remove_agent_from_allowlist
**Parameters**: self, flag_name, agent_id
**Returns**: bool
**Description**: Remove agent from a feature flag's allowlist.

#### remove_agent_from_blocklist
**Parameters**: self, flag_name, agent_id
**Returns**: bool
**Description**: Remove agent from a feature flag's blocklist.

#### export_config
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Export current configuration as dictionary.



## Function: __init__

**Parameters**: self, initial_stage, config_update_callback
**Description**: 
        Initialize configuration manager.

        Args:
            initial_stage: Initial rollout stage
            config_update_callback: Callback when config changes
        



## Function: _init_default_flags

**Parameters**: self
**Returns**: None
**Description**: Initialize default feature flags.



## Function: get_execution_mode

**Parameters**: self, agent_id, mission_id
**Returns**: ExecutionMode
**Description**: 
        Determine execution mode for a specific agent/mission.

        Uses sticky routing to ensure consistent experience.

        Args:
            agent_id: Agent identifier
            mission_id: Optional mission identifier

        Returns:
            ExecutionMode to use for this request
        



## Function: _calculate_execution_mode

**Parameters**: self, agent_id, mission_id
**Returns**: ExecutionMode
**Description**: Calculate execution mode based on rollout configuration.



## Function: _should_route_to_forward_rolling

**Parameters**: self, agent_id, mission_id, percentage
**Returns**: bool
**Description**: 
        Determine if request should be routed to Forward-Rolling.

        Uses consistent hashing for deterministic routing.

        Args:
            agent_id: Agent identifier
            mission_id: Mission identifier
            percentage: Rollout percentage (0-100)

        Returns:
            True if should use Forward-Rolling
        



## Function: set_rollout_stage

**Parameters**: self, stage
**Returns**: None
**Description**: 
        Set the rollout stage.

        Args:
            stage: New rollout stage
        



## Function: rollback

**Parameters**: self
**Returns**: bool
**Description**: 
        Rollback to previous configuration.

        Returns:
            True if rollback successful
        



## Function: emergency_disable

**Parameters**: self
**Returns**: None
**Description**: Emergency disable of Forward-Rolling Recursion.



## Function: set_feature_flag

**Parameters**: self, name, enabled, rollout_percentage, allowed_agents, blocked_agents
**Returns**: FeatureFlag
**Description**: 
        Set or update a feature flag.

        Args:
            name: Flag name
            enabled: Whether flag is enabled
            rollout_percentage: Percentage of traffic (0-100)
            allowed_agents: Set of allowed agent IDs
            blocked_agents: Set of blocked agent IDs

        Returns:
            Updated FeatureFlag
        



## Function: is_feature_enabled

**Parameters**: self, name, agent_id
**Returns**: bool
**Description**: 
        Check if a feature is enabled for an agent.

        Args:
            name: Feature flag name
            agent_id: Optional agent ID for percentage-based check

        Returns:
            True if feature is enabled
        



## Function: get_feature_flag

**Parameters**: self, name
**Returns**: FeatureFlag | None
**Description**: Get a feature flag by name.



## Function: get_all_feature_flags

**Parameters**: self
**Returns**: dict[str, FeatureFlag]
**Description**: Get all feature flags.



## Function: update_config

**Parameters**: self
**Returns**: None
**Description**: 
        Update configuration values.

        Args:
            **kwargs: Configuration values to update
        



## Function: get_config

**Parameters**: self
**Returns**: RolloutConfig
**Description**: Get current configuration.



## Function: get_rollout_percentage

**Parameters**: self
**Returns**: int
**Description**: Get current rollout percentage.



## Function: get_routing_stats

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get routing statistics.



## Function: clear_routing_cache

**Parameters**: self
**Returns**: int
**Description**: Clear routing cache and return count cleared.



## Function: add_agent_to_allowlist

**Parameters**: self, flag_name, agent_id
**Returns**: bool
**Description**: Add agent to a feature flag's allowlist.



## Function: add_agent_to_blocklist

**Parameters**: self, flag_name, agent_id
**Returns**: bool
**Description**: Add agent to a feature flag's blocklist.



## Function: remove_agent_from_allowlist

**Parameters**: self, flag_name, agent_id
**Returns**: bool
**Description**: Remove agent from a feature flag's allowlist.



## Function: remove_agent_from_blocklist

**Parameters**: self, flag_name, agent_id
**Returns**: bool
**Description**: Remove agent from a feature flag's blocklist.



## Function: export_config

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Export current configuration as dictionary.



## Usage Examples

### Class Usage

```python
# Using ExecutionMode
executionmode = ExecutionMode()
```

```python
# Using RolloutStage
rolloutstage = RolloutStage()
```

```python
# Using FeatureFlag
featureflag = FeatureFlag()
```

### Function Usage

```python
# Using __init__
result = __init__(initial_stage, config_update_callback)
```

```python
# Using _init_default_flags
result = _init_default_flags()
```

```python
# Using get_execution_mode
result = get_execution_mode(agent_id, mission_id)
```



---
**Generated**: 2026-03-26T09:39:04.378608
**Type**: api_reference
**Quality**: comprehensive
