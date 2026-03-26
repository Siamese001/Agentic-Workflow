# API Documentation: rl_strategy

**Target Audience**: developers, api_users

# rl_strategy API Documentation

**File**: `rl_strategy.py`
**Classes**: 1
**Functions**: 6

## Classes

- **RLStrategy**

## Functions

- **name** -> str
- **get_tiers** -> dict[str, list[str]]
- **_get_optimizer_agent** -> str
- **get_agent** -> Any | None
- **execute_agent** -> dict[str, Any]
- **should_abort_tier** -> bool


## Class: RLStrategy

**Description**: 
    Strategy for reinforcement learning orchestration missions.

    Consolidates:
    - Actor-Critic methods (from ActorCriticOrchestratorAgent)
    - PPO optimization (from PPOOrchestratorAgent)
    - Q-Learning (from QLearningOrchestratorAgent)
    - General RL (from RLOrchestratorAgent)
    - REINFORCE with critic (from ReinforceCriticOrchestratorAgent)

    Usage:
        strategy = RLStrategy(project_root=Path.cwd())
        orchestrator = Orchestrator(strategy=strategy)
        result = orchestrator.run_mission({"dry_run": True})
    

### Methods

#### name
**Parameters**: self
**Returns**: str
**Description**: Return the strategy name.

#### get_tiers
**Parameters**: self
**Returns**: dict[str, list[str]]
**Description**: 
        Return the tiered execution plan for RL missions.

        Returns:
            Dictionary mapping tier names to lists of agent names.
        

#### _get_optimizer_agent
**Parameters**: self
**Returns**: str
**Description**: Get the optimizer agent based on algorithm.

#### get_agent
**Parameters**: self, agent_name
**Returns**: Any | None
**Description**: 
        Get or create an agent instance by name.

        Args:
            agent_name: Name of the agent to retrieve

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

        Returns:
            Dictionary with execution results
        

#### should_abort_tier
**Parameters**: self, tier_name, tier_results, execute
**Returns**: bool
**Description**: 
        Determine if execution should abort after a tier.

        Args:
            tier_name: Name of the completed tier
            tier_results: Results from all agents in the tier
            execute: Whether we're in execute mode

        Returns:
            True if execution should abort, False to continue
        



## Function: name

**Parameters**: self
**Returns**: str
**Description**: Return the strategy name.



## Function: get_tiers

**Parameters**: self
**Returns**: dict[str, list[str]]
**Description**: 
        Return the tiered execution plan for RL missions.

        Returns:
            Dictionary mapping tier names to lists of agent names.
        



## Function: _get_optimizer_agent

**Parameters**: self
**Returns**: str
**Description**: Get the optimizer agent based on algorithm.



## Function: get_agent

**Parameters**: self, agent_name
**Returns**: Any | None
**Description**: 
        Get or create an agent instance by name.

        Args:
            agent_name: Name of the agent to retrieve

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

        Returns:
            Dictionary with execution results
        



## Function: should_abort_tier

**Parameters**: self, tier_name, tier_results, execute
**Returns**: bool
**Description**: 
        Determine if execution should abort after a tier.

        Args:
            tier_name: Name of the completed tier
            tier_results: Results from all agents in the tier
            execute: Whether we're in execute mode

        Returns:
            True if execution should abort, False to continue
        



## Usage Examples

### Class Usage

```python
# Using RLStrategy
rlstrategy = RLStrategy()
rlstrategy.name()
rlstrategy.get_tiers()
```

### Function Usage

```python
# Using name
result = name()
```

```python
# Using get_tiers
result = get_tiers()
```

```python
# Using _get_optimizer_agent
result = _get_optimizer_agent()
```



---
**Generated**: 2026-03-26T09:39:04.123119
**Type**: api_reference
**Quality**: comprehensive
