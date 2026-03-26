# API Documentation: core_contracts_types

**Target Audience**: developers, api_users

# core_contracts_types API Documentation

**File**: `core_contracts_types.py`
**Classes**: 3
**Functions**: 1

## Classes

- **RetryPolicy** (inherits from BaseModel)
- **HopSpec** (inherits from BaseModel)
- **AgentContract** (inherits from BaseModel)

## Functions

- **validate_retry_on** -> list[str]


## Class: RetryPolicy

**Description**: Retry policy for agent operations.

**Inherits from**: BaseModel

### Methods

#### validate_retry_on
**Parameters**: cls, v
**Returns**: list[str]
**Description**: [HARDENED] Ensure retry_on list is not empty.



## Class: HopSpec

**Description**: Specification for a HOP (Handoff Operation Protocol) stage.

**Inherits from**: BaseModel



## Class: AgentContract

**Description**: Contract specification for an agent.

**Inherits from**: BaseModel



## Function: validate_retry_on

**Parameters**: cls, v
**Returns**: list[str]
**Description**: [HARDENED] Ensure retry_on list is not empty.



## Usage Examples

### Class Usage

```python
# Using RetryPolicy
retrypolicy = RetryPolicy()
retrypolicy.validate_retry_on()
```

```python
# Using HopSpec
hopspec = HopSpec()
```

```python
# Using AgentContract
agentcontract = AgentContract()
```

### Function Usage

```python
# Using validate_retry_on
result = validate_retry_on(cls, v)
```



---
**Generated**: 2026-03-26T09:39:05.496082
**Type**: api_reference
**Quality**: comprehensive
