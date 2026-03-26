# API Documentation: orchestrator_types

**Target Audience**: developers, api_users

# orchestrator_types API Documentation

**File**: `orchestrator_types.py`
**Classes**: 6
**Functions**: 12

## Classes

- **ExecutionPhase** (inherits from str, Enum)
- **ExecutionContext**
- **AgentResult**
- **MissionResult**
- **IOrchestratorAgent** (inherits from Protocol)
- **IHealable** (inherits from Protocol)

## Functions

- **with_depth** -> ExecutionContext
- **with_phase** -> ExecutionContext
- **with_accumulated_context** -> ExecutionContext
- **get_successor_chain** -> list[str]
- **get_depth** -> int
- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **run_mission** -> MissionResult
- **run_agent** -> AgentResult
- **get_available_agents** -> list[str]
- **validate_mission** -> bool
- **heal_repository** -> dict[str, Any]


## Class: ExecutionPhase

**Description**: Execution phases for orchestrator lifecycle.

**Inherits from**: str, Enum



## Class: ExecutionContext

**Description**: 
    Context passed through orchestrator execution chain.

    Provides shared state and configuration for mission execution.

    [PHASE 1] Forward-Rolling Recursion Enhancement:
    - accumulated_context: Zero-loss context preservation across successor spawns
    - successor_chain tracking in metadata for DNA integrity
    

### Methods

#### with_depth
**Parameters**: self, new_depth
**Returns**: ExecutionContext
**Description**: Create new context with updated depth.

#### with_phase
**Parameters**: self, new_phase
**Returns**: ExecutionContext
**Description**: Create new context with updated phase.

#### with_accumulated_context
**Parameters**: self, new_context
**Returns**: ExecutionContext
**Description**: Create new context with merged accumulated_context for DNA preservation.

#### get_successor_chain
**Parameters**: self
**Returns**: list[str]
**Description**: Get the current successor chain from metadata.

#### get_depth
**Parameters**: self
**Returns**: int
**Description**: Get current recursion depth from metadata or current_depth.



## Class: AgentResult

**Description**: 
    Standardized result from agent execution.

    Provides consistent return format for orchestrator coordination.
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Class: MissionResult

**Description**: 
    Aggregated result from mission execution.

    Combines results from multiple agents into a unified summary.
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Class: IOrchestratorAgent

**Description**: 
    Protocol defining the canonical interface for orchestrator agents.

    All orchestrators in L3_orchestration should implement this protocol
    to ensure consistent behavior and enable unified orchestration.

    Methods:
        run_mission: Execute a mission across multiple agents
        run_agent: Execute a single agent with standardized result
        get_available_agents: List agents this orchestrator can coordinate
        validate_mission: Pre-flight validation before execution

    Usage:
        @runtime_checkable allows isinstance() checks at runtime:

        if isinstance(agent, IOrchestratorAgent):
            result = agent.run_mission(agents, dry_run=True)
    

**Inherits from**: Protocol

### Methods

#### run_mission
**Parameters**: self, agents, dry_run, execute, context
**Returns**: MissionResult
**Description**: 
        Execute a mission across multiple agents.

        Args:
            agents: List of agent names to coordinate
            dry_run: If True, only simulate execution
            execute: If True, apply changes (opposite of dry_run)
            context: Optional execution context for shared state

        Returns:
            MissionResult with aggregated outcomes
        

#### run_agent
**Parameters**: self, agent_name, dry_run, context
**Returns**: AgentResult
**Description**: 
        Execute a single agent with standardized result.

        Args:
            agent_name: Name of the agent to execute
            dry_run: If True, only simulate execution
            context: Optional execution context

        Returns:
            AgentResult with execution outcome
        

#### get_available_agents
**Parameters**: self
**Returns**: list[str]
**Description**: 
        Get list of agents this orchestrator can coordinate.

        Returns:
            List of agent class names
        

#### validate_mission
**Parameters**: self, agents, context
**Returns**: bool
**Description**: 
        Pre-flight validation before mission execution.

        Args:
            agents: List of agent names to validate
            context: Optional execution context

        Returns:
            True if mission can proceed, False otherwise
        



## Class: IHealable

**Description**: 
    Protocol for agents that support healing operations.

    This is a superset of the signatures found in BiasAuditorAgent,
    NamingAgent, and other healing-capable agents.

    Zero-Loss Guarantee:
        All existing heal_repository signatures are compatible with this protocol.
        The **kwargs ensures backward compatibility with legacy callers.
    

**Inherits from**: Protocol

### Methods

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth
**Returns**: dict[str, Any]
**Description**: 
        Repository-level healing method.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            **kwargs: Additional arguments for backward compatibility

        Returns:
            Dict with healing summary (violations_found, violations_fixed, etc.)
        



## Function: with_depth

**Parameters**: self, new_depth
**Returns**: ExecutionContext
**Description**: Create new context with updated depth.



## Function: with_phase

**Parameters**: self, new_phase
**Returns**: ExecutionContext
**Description**: Create new context with updated phase.



## Function: with_accumulated_context

**Parameters**: self, new_context
**Returns**: ExecutionContext
**Description**: Create new context with merged accumulated_context for DNA preservation.



## Function: get_successor_chain

**Parameters**: self
**Returns**: list[str]
**Description**: Get the current successor chain from metadata.



## Function: get_depth

**Parameters**: self
**Returns**: int
**Description**: Get current recursion depth from metadata or current_depth.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: run_mission

**Parameters**: self, agents, dry_run, execute, context
**Returns**: MissionResult
**Description**: 
        Execute a mission across multiple agents.

        Args:
            agents: List of agent names to coordinate
            dry_run: If True, only simulate execution
            execute: If True, apply changes (opposite of dry_run)
            context: Optional execution context for shared state

        Returns:
            MissionResult with aggregated outcomes
        



## Function: run_agent

**Parameters**: self, agent_name, dry_run, context
**Returns**: AgentResult
**Description**: 
        Execute a single agent with standardized result.

        Args:
            agent_name: Name of the agent to execute
            dry_run: If True, only simulate execution
            context: Optional execution context

        Returns:
            AgentResult with execution outcome
        



## Function: get_available_agents

**Parameters**: self
**Returns**: list[str]
**Description**: 
        Get list of agents this orchestrator can coordinate.

        Returns:
            List of agent class names
        



## Function: validate_mission

**Parameters**: self, agents, context
**Returns**: bool
**Description**: 
        Pre-flight validation before mission execution.

        Args:
            agents: List of agent names to validate
            context: Optional execution context

        Returns:
            True if mission can proceed, False otherwise
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth
**Returns**: dict[str, Any]
**Description**: 
        Repository-level healing method.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            **kwargs: Additional arguments for backward compatibility

        Returns:
            Dict with healing summary (violations_found, violations_fixed, etc.)
        



## Usage Examples

### Class Usage

```python
# Using ExecutionPhase
executionphase = ExecutionPhase()
```

```python
# Using ExecutionContext
executioncontext = ExecutionContext()
executioncontext.with_depth()
executioncontext.with_phase()
```

```python
# Using AgentResult
agentresult = AgentResult()
agentresult.to_dict()
```

### Function Usage

```python
# Using with_depth
result = with_depth(new_depth)
```

```python
# Using with_phase
result = with_phase(new_phase)
```

```python
# Using with_accumulated_context
result = with_accumulated_context(new_context)
```



---
**Generated**: 2026-03-26T09:39:04.391054
**Type**: api_reference
**Quality**: comprehensive
