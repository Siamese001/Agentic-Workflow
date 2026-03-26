# API Documentation: safety_strategy

**Target Audience**: developers, api_users

# safety_strategy API Documentation

**File**: `safety_strategy.py`
**Classes**: 2
**Functions**: 9

## Classes

- **SafetyStrategy**
- **CodeValidatorAgentProxy**

## Functions

- **__post_init__** -> None
- **name** -> str
- **get_tiers** -> dict[str, list[str]]
- **_get_agent** -> Any | None
- **execute_agent** -> dict[str, Any]
- **should_abort_tier** -> bool
- **__init__**
- **validate_repository**
- **heal_repository**


## Class: SafetyStrategy

**Description**: 
    Strategy for safety-focused orchestration missions.

    Consolidates:
    - Compliance validation (from ComplianceOrchestratorAgent)
    - Guardian protection (from GuardianOrchestratorAgent)
    - Healing coordination (from HealingOrchestratorAgent)

    Usage:
        strategy = SafetyStrategy(project_root=Path.cwd())
        orchestrator = Orchestrator(strategy=strategy)
        result = orchestrator.run_mission({"dry_run": True})
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### name
**Parameters**: self
**Returns**: str
**Description**: Return the strategy name.

#### get_tiers
**Parameters**: self
**Returns**: dict[str, list[str]]
**Description**: 
        Return the tiered execution plan for safety missions.

        Returns:
            Dictionary mapping tier names to lists of agent names.
        

#### _get_agent
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
        



## Class: CodeValidatorAgentProxy

### Methods

#### __init__
**Parameters**: self, project_root

#### validate_repository
**Parameters**: self

#### heal_repository
**Parameters**: self, directory



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: name

**Parameters**: self
**Returns**: str
**Description**: Return the strategy name.



## Function: get_tiers

**Parameters**: self
**Returns**: dict[str, list[str]]
**Description**: 
        Return the tiered execution plan for safety missions.

        Returns:
            Dictionary mapping tier names to lists of agent names.
        



## Function: _get_agent

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
        



## Function: __init__

**Parameters**: self, project_root


## Function: validate_repository

**Parameters**: self


## Function: heal_repository

**Parameters**: self, directory


## Usage Examples

### Class Usage

```python
# Using SafetyStrategy
safetystrategy = SafetyStrategy()
safetystrategy.name()
safetystrategy.get_tiers()
```

```python
# Using CodeValidatorAgentProxy
codevalidatoragentproxy = CodeValidatorAgentProxy()
codevalidatoragentproxy.validate_repository()
codevalidatoragentproxy.heal_repository()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
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
**Generated**: 2026-03-26T09:39:04.125899
**Type**: api_reference
**Quality**: comprehensive
