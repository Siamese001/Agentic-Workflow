# API Documentation: structured_agent_output_types

**Target Audience**: developers, api_users

# structured_agent_output_types API Documentation

**File**: `structured_agent_output_types.py`
**Classes**: 3
**Functions**: 4

## Classes

- **StructuredOutputViolation** (inherits from ValueError)
- **ToolRequest**
- **StructuredAgentOutput**

## Functions

- **__post_init__** -> None
- **__post_init__** -> None
- **empty** -> StructuredAgentOutput
- **to_dict** -> dict[str, Any]


## Class: StructuredOutputViolation

**Description**: Raised when StructuredAgentOutput invariants are broken.

**Inherits from**: ValueError



## Class: ToolRequest

**Description**: A single tool invocation request emitted by an apps_* agent.

    Spec: AgentOutputContract tool_requests[] schema element.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: StructuredAgentOutput

**Description**: Structured output schema for all apps_* agent execute() returns.

    Spec: AgentOutputContract [7], Guarantee #12.

    Fields:
        intent_delta: Non-empty description of agent intent / what is changing.
        tool_requests: Zero or more tool invocation requests.
        state_diff_proposal: Dict of proposed state mutations (may be empty dict).
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### empty
**Parameters**: cls, intent_delta
**Returns**: StructuredAgentOutput
**Description**: Create a StructuredAgentOutput with no tool requests and empty state diff.

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Serialize to a plain dict for AgentOutputContract payload.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: empty

**Parameters**: cls, intent_delta
**Returns**: StructuredAgentOutput
**Description**: Create a StructuredAgentOutput with no tool requests and empty state diff.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Serialize to a plain dict for AgentOutputContract payload.



## Usage Examples

### Class Usage

```python
# Using StructuredOutputViolation
structuredoutputviolation = StructuredOutputViolation()
```

```python
# Using ToolRequest
toolrequest = ToolRequest()
```

```python
# Using StructuredAgentOutput
structuredagentoutput = StructuredAgentOutput()
structuredagentoutput.empty()
structuredagentoutput.to_dict()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using empty
result = empty(cls, intent_delta)
```



---
**Generated**: 2026-03-26T09:39:04.007982
**Type**: api_reference
**Quality**: comprehensive
