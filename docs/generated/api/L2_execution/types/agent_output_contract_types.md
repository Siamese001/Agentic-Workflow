# API Documentation: agent_output_contract_types

**Target Audience**: developers, api_users

# agent_output_contract_types API Documentation

**File**: `agent_output_contract_types.py`
**Classes**: 2
**Functions**: 5

## Classes

- **OutputContractViolation** (inherits from ValueError)
- **AgentOutputContract**

## Functions

- **wrap_output** -> AgentOutputContract
- **__post_init__** -> None
- **_signable_dict** -> dict
- **sign** -> AgentOutputContract
- **verify** -> None


## Class: OutputContractViolation

**Description**: Raised when AgentOutputContract invariants are broken.

**Inherits from**: ValueError



## Class: AgentOutputContract

**Description**: Signed envelope for a single agent execute() call result.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### _signable_dict
**Parameters**: self
**Returns**: dict

#### sign
**Parameters**: self, secret
**Returns**: AgentOutputContract

#### verify
**Parameters**: self, secret
**Returns**: None



## Function: wrap_output

**Parameters**: agent_id, trace_id, payload_model, secret
**Returns**: AgentOutputContract
**Description**: Convenience: hash + sign a Pydantic model output.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: _signable_dict

**Parameters**: self
**Returns**: dict


## Function: sign

**Parameters**: self, secret
**Returns**: AgentOutputContract


## Function: verify

**Parameters**: self, secret
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using OutputContractViolation
outputcontractviolation = OutputContractViolation()
```

```python
# Using AgentOutputContract
agentoutputcontract = AgentOutputContract()
agentoutputcontract.sign()
agentoutputcontract.verify()
```

### Function Usage

```python
# Using wrap_output
result = wrap_output(agent_id, trace_id)
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _signable_dict
result = _signable_dict()
```



---
**Generated**: 2026-03-26T09:39:03.941716
**Type**: api_reference
**Quality**: comprehensive
