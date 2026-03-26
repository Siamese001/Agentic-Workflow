# API Documentation: AgentFactory

**Target Audience**: developers, api_users

# AgentFactory API Documentation

**File**: `AgentFactory.py`
**Classes**: 1
**Functions**: 12

## Classes

- **AgentFactory**

## Functions

- **_get_CodeEnforcerAgent**
- **create_all_agents** -> dict
- **_run_self_tests** -> dict
- **_create_impl** -> CanonBaseAgentInterface
- **create_system_architect** -> SystemArchitect
- **create_healer_agent** -> HealerAgent
- **create_generative_guard** -> GenerativeGuard
- **create_code_janitor** -> CodeJanitor
- **create_dependency_sentinel** -> DependencySentinelAgent
- **create_safety_inspector** -> SafetyInspectorAgent
- **create_pattern_enforcer** -> CodeEnforcerAgent
- **create_agent_by_capability** -> Any


## Class: AgentFactory

**Description**: 
    Centralized factory for sovereign agent injection.

    Phase 9A DDD Compliance:
    - Only L3 knows how to instantiate L2 concrete implementations
    - L1 agents receive implementations via dependency injection
    - Maintains separation of concerns across layers
    

### Methods

#### _create_impl
**Parameters**: ctx
**Returns**: CanonBaseAgentInterface
**Description**: 
        Create base agent implementation with configurable mode support.

        Phase 11: Advanced Factory Pattern
        - Respects global AGENT_IMPLEMENTATION_MODE configuration
        - Supports "real" (standard), "mock" (testing), "aggressive" (fast-healing)
        - Only L3 knows how to instantiate the L2 concrete implementation

        Args:
            ctx: Optional context object to pass to the agent implementation

        Returns:
            CanonBaseAgentInterface: Concrete implementation based on configured mode
        

#### create_system_architect
**Parameters**: ctx
**Returns**: SystemArchitect
**Description**: 
        Create SystemArchitect with injected L2 implementation.
        Injects L2 execution capabilities into L1 strategic architecture reasoning.
        

#### create_healer_agent
**Parameters**: ctx
**Returns**: HealerAgent
**Description**: 
        Create HealerAgent with injected L2 implementation.

        Injects L2 repair logic into L1 strategic healing.
        

#### create_generative_guard
**Parameters**: ctx
**Returns**: GenerativeGuard
**Description**: 
        Create GenerativeGuard with injected L2 implementation.

        Injects L2 validation capabilities into L1 generative oversight.
        

#### create_code_janitor
**Parameters**: ctx
**Returns**: CodeJanitor
**Description**: 
        Create CodeJanitor with injected L2 implementation.

        Injects L2 action into L1 syntax reasoning.
        

#### create_dependency_sentinel
**Parameters**: ctx
**Returns**: DependencySentinelAgent
**Description**: 
        Create DependencySentinelAgent with injected L2 implementation.

        Injects L2 import management into L1 dependency reasoning.
        

#### create_safety_inspector
**Parameters**: ctx
**Returns**: SafetyInspectorAgent
**Description**: 
        Create SafetyInspectorAgent with injected L2 implementation.

        Injects L2 security checks into L1 safety reasoning.
        

#### create_pattern_enforcer
**Parameters**: ctx
**Returns**: CodeEnforcerAgent
**Description**: 
        Create CodeEnforcerAgent with injected L2 implementation.

        Injects L2 pattern detection into L1 quality reasoning.
        

#### create_agent_by_capability
**Parameters**: capability, ctx
**Returns**: Any
**Description**: R5: Dynamically discover and instantiate agent by capability via ADG.

        Uses ADG composition graph index for O(1) capability lookup.
        Speedup: 10-50x over linear registry search.

        Example: create_agent_by_capability("PromptLoader")
        



## Function: _get_CodeEnforcerAgent

**Description**: Lazy loader for CodeEnforcerAgent (upward L3->L5 seam).



## Function: create_all_agents

**Parameters**: ctx
**Returns**: dict
**Description**: 
    Create all L1 agents with injected L2 implementations.

    Args:
        ctx: Optional context object to pass to all agents

    Returns:
        dict: Dictionary of agent name to agent instance
    



## Function: _run_self_tests

**Parameters**: self
**Returns**: dict
**Description**: Run internal self-tests.



## Function: _create_impl

**Parameters**: ctx
**Returns**: CanonBaseAgentInterface
**Description**: 
        Create base agent implementation with configurable mode support.

        Phase 11: Advanced Factory Pattern
        - Respects global AGENT_IMPLEMENTATION_MODE configuration
        - Supports "real" (standard), "mock" (testing), "aggressive" (fast-healing)
        - Only L3 knows how to instantiate the L2 concrete implementation

        Args:
            ctx: Optional context object to pass to the agent implementation

        Returns:
            CanonBaseAgentInterface: Concrete implementation based on configured mode
        



## Function: create_system_architect

**Parameters**: ctx
**Returns**: SystemArchitect
**Description**: 
        Create SystemArchitect with injected L2 implementation.
        Injects L2 execution capabilities into L1 strategic architecture reasoning.
        



## Function: create_healer_agent

**Parameters**: ctx
**Returns**: HealerAgent
**Description**: 
        Create HealerAgent with injected L2 implementation.

        Injects L2 repair logic into L1 strategic healing.
        



## Function: create_generative_guard

**Parameters**: ctx
**Returns**: GenerativeGuard
**Description**: 
        Create GenerativeGuard with injected L2 implementation.

        Injects L2 validation capabilities into L1 generative oversight.
        



## Function: create_code_janitor

**Parameters**: ctx
**Returns**: CodeJanitor
**Description**: 
        Create CodeJanitor with injected L2 implementation.

        Injects L2 action into L1 syntax reasoning.
        



## Function: create_dependency_sentinel

**Parameters**: ctx
**Returns**: DependencySentinelAgent
**Description**: 
        Create DependencySentinelAgent with injected L2 implementation.

        Injects L2 import management into L1 dependency reasoning.
        



## Function: create_safety_inspector

**Parameters**: ctx
**Returns**: SafetyInspectorAgent
**Description**: 
        Create SafetyInspectorAgent with injected L2 implementation.

        Injects L2 security checks into L1 safety reasoning.
        



## Function: create_pattern_enforcer

**Parameters**: ctx
**Returns**: CodeEnforcerAgent
**Description**: 
        Create CodeEnforcerAgent with injected L2 implementation.

        Injects L2 pattern detection into L1 quality reasoning.
        



## Function: create_agent_by_capability

**Parameters**: capability, ctx
**Returns**: Any
**Description**: R5: Dynamically discover and instantiate agent by capability via ADG.

        Uses ADG composition graph index for O(1) capability lookup.
        Speedup: 10-50x over linear registry search.

        Example: create_agent_by_capability("PromptLoader")
        



## Usage Examples

### Class Usage

```python
# Using AgentFactory
agentfactory = AgentFactory()
agentfactory.create_system_architect()
agentfactory.create_healer_agent()
```

### Function Usage

```python
# Using _get_CodeEnforcerAgent
result = _get_CodeEnforcerAgent()
```

```python
# Using create_all_agents
result = create_all_agents(ctx)
```

```python
# Using _run_self_tests
result = _run_self_tests()
```



---
**Generated**: 2026-03-26T09:39:04.131049
**Type**: api_reference
**Quality**: comprehensive
