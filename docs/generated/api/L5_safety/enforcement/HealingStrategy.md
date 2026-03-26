# API Documentation: HealingStrategy

**Target Audience**: developers, api_users

# HealingStrategy API Documentation

**File**: `HealingStrategy.py`
**Classes**: 1
**Functions**: 11

## Classes

- **HealingStrategy**

## Functions

- **__init__** -> None
- **name** -> str
- **get_tiers** -> dict[str, list[str]]
- **should_run_tier** -> bool
- **get_tier_skip_message** -> str
- **get_agent** -> Any | None
- **_get_dedup_agent** -> Any | None
- **_load_agent** -> Any | None
- **execute_agent** -> dict[str, Any]
- **_normalize_result** -> dict[str, Any]
- **should_abort_tier** -> bool


## Class: HealingStrategy

**Description**: 
    Tiered healing execution strategy.

    Implements the MissionStrategy protocol for the Orchestrator.
    Encapsulates the 5-tier healing execution flow from SSOTOrchestratorAgent.
    

### Methods

#### __init__
**Parameters**: self, project_root, target_tier
**Returns**: None
**Description**: 
        Initialize the healing strategy.

        Args:
            project_root: Root path for the project (defaults to cwd)
            target_tier: If specified, only run this tier (0-4). None runs all tiers.
        

#### name
**Parameters**: self
**Returns**: str
**Description**: Return the strategy name.

#### get_tiers
**Parameters**: self
**Returns**: dict[str, list[str]]
**Description**: 
        Return the tiered execution plan.

        Returns:
            Dictionary mapping tier names to lists of agent names.
        

#### should_run_tier
**Parameters**: self, tier_name
**Returns**: bool
**Description**: 
        Check if a tier should be executed based on target_tier filter.

        Args:
            tier_name: Name of the tier (e.g., "Tier 0: Pre-Flight")

        Returns:
            True if the tier should run, False to skip
        

#### get_tier_skip_message
**Parameters**: self, tier_name
**Returns**: str
**Description**: 
        Get a message explaining why a tier is being skipped.

        Args:
            tier_name: Name of the tier being skipped

        Returns:
            Skip message for logging
        

#### get_agent
**Parameters**: self, agent_name
**Returns**: Any | None
**Description**: 
        Get or create an agent instance by name.

        Uses lazy loading to instantiate agents only when needed.

        Args:
            agent_name: Name of the agent to retrieve

        Returns:
            Agent instance or None if not available
        

#### _get_dedup_agent
**Parameters**: self
**Returns**: Any | None
**Description**: Get or create the shared TwoPhaseDeduplicationAgent instance.

#### _load_agent
**Parameters**: self, agent_name
**Returns**: Any | None
**Description**: 
        Load an agent by name.

        Args:
            agent_name: Name of the agent to load

        Returns:
            Agent instance or None if not available
        

#### execute_agent
**Parameters**: self, agent, agent_name, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Execute a single agent and return results.

        Args:
            agent: The agent instance to execute
            agent_name: Name of the agent (for logging)
            dry_run: If True, only report violations
            execute: If True, apply fixes
            **kwargs: Additional agent-specific parameters
                route_decision_artifact: audit payload dict from L3 routing
                    (required under V15; ignored otherwise)

        Returns:
            Dictionary with execution results
        

#### _normalize_result
**Parameters**: self, result, execution_time_ms
**Returns**: dict[str, Any]
**Description**: 
        Normalize agent result to standard format.

        Args:
            result: Raw result from agent
            execution_time_ms: Execution time in milliseconds

        Returns:
            Normalized result dictionary
        

#### should_abort_tier
**Parameters**: self, tier_name, tier_results, execute
**Returns**: bool
**Description**: 
        Determine if execution should abort after a tier.

        Implements stability gates:
        - Tier 0 (Pre-Flight): Always fatal if failed (syntax must be valid)
        - Tier 1 (Structural): Fatal only during execute mode

        Args:
            tier_name: Name of the completed tier
            tier_results: Results from all agents in the tier
            execute: Whether we're in execute mode

        Returns:
            True if execution should abort, False to continue
        



## Function: __init__

**Parameters**: self, project_root, target_tier
**Returns**: None
**Description**: 
        Initialize the healing strategy.

        Args:
            project_root: Root path for the project (defaults to cwd)
            target_tier: If specified, only run this tier (0-4). None runs all tiers.
        



## Function: name

**Parameters**: self
**Returns**: str
**Description**: Return the strategy name.



## Function: get_tiers

**Parameters**: self
**Returns**: dict[str, list[str]]
**Description**: 
        Return the tiered execution plan.

        Returns:
            Dictionary mapping tier names to lists of agent names.
        



## Function: should_run_tier

**Parameters**: self, tier_name
**Returns**: bool
**Description**: 
        Check if a tier should be executed based on target_tier filter.

        Args:
            tier_name: Name of the tier (e.g., "Tier 0: Pre-Flight")

        Returns:
            True if the tier should run, False to skip
        



## Function: get_tier_skip_message

**Parameters**: self, tier_name
**Returns**: str
**Description**: 
        Get a message explaining why a tier is being skipped.

        Args:
            tier_name: Name of the tier being skipped

        Returns:
            Skip message for logging
        



## Function: get_agent

**Parameters**: self, agent_name
**Returns**: Any | None
**Description**: 
        Get or create an agent instance by name.

        Uses lazy loading to instantiate agents only when needed.

        Args:
            agent_name: Name of the agent to retrieve

        Returns:
            Agent instance or None if not available
        



## Function: _get_dedup_agent

**Parameters**: self
**Returns**: Any | None
**Description**: Get or create the shared TwoPhaseDeduplicationAgent instance.



## Function: _load_agent

**Parameters**: self, agent_name
**Returns**: Any | None
**Description**: 
        Load an agent by name.

        Args:
            agent_name: Name of the agent to load

        Returns:
            Agent instance or None if not available
        



## Function: execute_agent

**Parameters**: self, agent, agent_name, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Execute a single agent and return results.

        Args:
            agent: The agent instance to execute
            agent_name: Name of the agent (for logging)
            dry_run: If True, only report violations
            execute: If True, apply fixes
            **kwargs: Additional agent-specific parameters
                route_decision_artifact: audit payload dict from L3 routing
                    (required under V15; ignored otherwise)

        Returns:
            Dictionary with execution results
        



## Function: _normalize_result

**Parameters**: self, result, execution_time_ms
**Returns**: dict[str, Any]
**Description**: 
        Normalize agent result to standard format.

        Args:
            result: Raw result from agent
            execution_time_ms: Execution time in milliseconds

        Returns:
            Normalized result dictionary
        



## Function: should_abort_tier

**Parameters**: self, tier_name, tier_results, execute
**Returns**: bool
**Description**: 
        Determine if execution should abort after a tier.

        Implements stability gates:
        - Tier 0 (Pre-Flight): Always fatal if failed (syntax must be valid)
        - Tier 1 (Structural): Fatal only during execute mode

        Args:
            tier_name: Name of the completed tier
            tier_results: Results from all agents in the tier
            execute: Whether we're in execute mode

        Returns:
            True if execution should abort, False to continue
        



## Usage Examples

### Class Usage

```python
# Using HealingStrategy
healingstrategy = HealingStrategy()
healingstrategy.name()
healingstrategy.get_tiers()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root, target_tier)
```

```python
# Using name
result = name()
```

```python
# Using get_tiers
result = get_tiers()
```



---
**Generated**: 2026-03-26T09:39:04.831803
**Type**: api_reference
**Quality**: comprehensive
