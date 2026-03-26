# API Documentation: StructuredEngineAgent

**Target Audience**: developers, api_users

# StructuredEngineAgent API Documentation

**File**: `StructuredEngineAgent.py`
**Classes**: 2
**Functions**: 4

## Classes

- **AgentPlan**
- **StructuredEngineAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__**
- **heal**
- **heal**
- **heal_repository** -> dict


## Class: AgentPlan

**Description**: Simple plan structure for structured output.

### Methods

#### __init__
**Parameters**: self, reasoning, tool_calls

#### heal
**Parameters**: self, violation



## Class: StructuredEngineAgent

**Description**: 
    L2 Execution: Structured LLM output engine.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### heal
**Parameters**: self, violation

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for StructuredEngineAgent.



## Function: __init__

**Parameters**: self, reasoning, tool_calls


## Function: heal

**Parameters**: self, violation


## Function: heal

**Parameters**: self, violation


## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for StructuredEngineAgent.



## Usage Examples

### Class Usage

```python
# Using AgentPlan
agentplan = AgentPlan()
agentplan.heal()
```

```python
# Using StructuredEngineAgent
structuredengineagent = StructuredEngineAgent()
structuredengineagent.heal()
structuredengineagent.heal_repository()
```

### Function Usage

```python
# Using __init__
result = __init__(reasoning, tool_calls)
```

```python
# Using heal
result = heal(violation)
```

```python
# Using heal
result = heal(violation)
```



---
**Generated**: 2026-03-26T09:39:03.876500
**Type**: api_reference
**Quality**: comprehensive
