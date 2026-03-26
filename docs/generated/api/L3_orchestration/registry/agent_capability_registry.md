# API Documentation: agent_capability_registry

**Target Audience**: developers, api_users

# agent_capability_registry API Documentation

**File**: `agent_capability_registry.py`
**Classes**: 2
**Functions**: 11

## Classes

- **AgentCapabilitySpec**
- **AgentCapabilityRegistry**

## Functions

- **get_agent_capability_registry** -> AgentCapabilityRegistry
- **reset_agent_capability_registry** -> None
- **can_handoff_to** -> bool
- **has_capability** -> bool
- **__init__** -> None
- **register** -> None
- **get** -> AgentCapabilitySpec | None
- **can_handoff** -> bool
- **registered_agents** -> list[str]
- **all_handoff_edges** -> list[tuple[str, str]]
- **agents_with_capability** -> list[str]


## Class: AgentCapabilitySpec

**Description**: Declared capability specification for a single agent.

### Methods

#### can_handoff_to
**Parameters**: self, target
**Returns**: bool

#### has_capability
**Parameters**: self, cap
**Returns**: bool



## Class: AgentCapabilityRegistry

**Description**: Central registry of agent capabilities and handoff graphs.

    Usage::

        registry = AgentCapabilityRegistry()
        registry.register(AgentCapabilitySpec(
            agent_name="ResearchOrchestrator",
            layer="L3",
            capabilities=["fetch_sources", "summarise"],
            handoff_targets=["SummaryAgent", "BriefAssembler"],
        ))

        spec = registry.get("ResearchOrchestrator")
        assert spec.can_handoff_to("SummaryAgent")
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### register
**Parameters**: self, spec
**Returns**: None
**Description**: Register an agent's capability spec.

        Emits ``declares_capability`` ADG edge.
        

#### get
**Parameters**: self, agent_name
**Returns**: AgentCapabilitySpec | None

#### can_handoff
**Parameters**: self, src, dst
**Returns**: bool
**Description**: Check whether ``src`` agent is allowed to hand off to ``dst``.

#### registered_agents
**Parameters**: self
**Returns**: list[str]

#### all_handoff_edges
**Parameters**: self
**Returns**: list[tuple[str, str]]
**Description**: Return all (src, dst) handoff pairs declared in the registry.

#### agents_with_capability
**Parameters**: self, cap
**Returns**: list[str]



## Function: get_agent_capability_registry

**Returns**: AgentCapabilityRegistry


## Function: reset_agent_capability_registry

**Returns**: None


## Function: can_handoff_to

**Parameters**: self, target
**Returns**: bool


## Function: has_capability

**Parameters**: self, cap
**Returns**: bool


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: register

**Parameters**: self, spec
**Returns**: None
**Description**: Register an agent's capability spec.

        Emits ``declares_capability`` ADG edge.
        



## Function: get

**Parameters**: self, agent_name
**Returns**: AgentCapabilitySpec | None


## Function: can_handoff

**Parameters**: self, src, dst
**Returns**: bool
**Description**: Check whether ``src`` agent is allowed to hand off to ``dst``.



## Function: registered_agents

**Parameters**: self
**Returns**: list[str]


## Function: all_handoff_edges

**Parameters**: self
**Returns**: list[tuple[str, str]]
**Description**: Return all (src, dst) handoff pairs declared in the registry.



## Function: agents_with_capability

**Parameters**: self, cap
**Returns**: list[str]


## Usage Examples

### Class Usage

```python
# Using AgentCapabilitySpec
agentcapabilityspec = AgentCapabilitySpec()
agentcapabilityspec.can_handoff_to()
agentcapabilityspec.has_capability()
```

```python
# Using AgentCapabilityRegistry
agentcapabilityregistry = AgentCapabilityRegistry()
agentcapabilityregistry.register()
agentcapabilityregistry.get()
```

### Function Usage

```python
# Using get_agent_capability_registry
result = get_agent_capability_registry()
```

```python
# Using reset_agent_capability_registry
result = reset_agent_capability_registry()
```

```python
# Using can_handoff_to
result = can_handoff_to(target)
```



---
**Generated**: 2026-03-26T09:39:04.333338
**Type**: api_reference
**Quality**: comprehensive
