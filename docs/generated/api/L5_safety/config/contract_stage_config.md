# API Documentation: contract_stage_config

**Target Audience**: developers, api_users

# contract_stage_config API Documentation

**File**: `contract_stage_config.py`
**Classes**: 8
**Functions**: 10

## Classes

- **ContractStage**
- **CognitiveContract**
- **CognitiveContractEnforcer**
- **Constraint**
- **Plan**
- **PlanQualityError** (inherits from Exception)
- **ConsistencyError** (inherits from Exception)
- **CognitiveContractValidatorSchema** (inherits from SovereignBaseAgent)

## Functions

- **__init__**
- **__init__**
- **enforce** -> bool
- **add_contract** -> None
- **__init__**
- **__init__**
- **__init__**
- **add_contract** -> None
- **validate_contract** -> bool
- **list_contracts** -> list[str]


## Class: ContractStage

**Description**: Stage in a cognitive contract.



## Class: CognitiveContract

**Description**: A cognitive contract definition.

### Methods

#### __init__
**Parameters**: self, name, required



## Class: CognitiveContractEnforcer

**Description**: Enforcer for cognitive contracts.

### Methods

#### __init__
**Parameters**: self, contracts

#### enforce
**Parameters**: self, data
**Returns**: bool

#### add_contract
**Parameters**: self, contract
**Returns**: None



## Class: Constraint

**Description**: A constraint in a cognitive contract.

### Methods

#### __init__
**Parameters**: self, name, condition



## Class: Plan

**Description**: A plan in a cognitive contract.

### Methods

#### __init__
**Parameters**: self, name, steps



## Class: PlanQualityError

**Description**: Error raised when plan quality is insufficient.

**Inherits from**: Exception



## Class: ConsistencyError

**Description**: Error raised when consistency checks fail.

**Inherits from**: Exception



## Class: CognitiveContractValidatorSchema

**Description**: 
    schema validator for cognitive contracts (data model, not an agent).

    This is a schema/model class that provides validation structures for cognitive contracts.
    Distinct from the active CognitiveContractValidatorAgent in L1_cognition which performs
    runtime contract validation.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self

#### add_contract
**Parameters**: self, contract
**Returns**: None
**Description**: Add a contract to the validator schema.

#### validate_contract
**Parameters**: self, contract_name, data
**Returns**: bool
**Description**: Validate data against a named contract schema.

#### list_contracts
**Parameters**: self
**Returns**: list[str]
**Description**: List all registered contract schemas.



## Function: __init__

**Parameters**: self, name, required


## Function: __init__

**Parameters**: self, contracts


## Function: enforce

**Parameters**: self, data
**Returns**: bool


## Function: add_contract

**Parameters**: self, contract
**Returns**: None


## Function: __init__

**Parameters**: self, name, condition


## Function: __init__

**Parameters**: self, name, steps


## Function: __init__

**Parameters**: self


## Function: add_contract

**Parameters**: self, contract
**Returns**: None
**Description**: Add a contract to the validator schema.



## Function: validate_contract

**Parameters**: self, contract_name, data
**Returns**: bool
**Description**: Validate data against a named contract schema.



## Function: list_contracts

**Parameters**: self
**Returns**: list[str]
**Description**: List all registered contract schemas.



## Usage Examples

### Class Usage

```python
# Using ContractStage
contractstage = ContractStage()
```

```python
# Using CognitiveContract
cognitivecontract = CognitiveContract()
```

```python
# Using CognitiveContractEnforcer
cognitivecontractenforcer = CognitiveContractEnforcer()
cognitivecontractenforcer.enforce()
cognitivecontractenforcer.add_contract()
```

### Function Usage

```python
# Using __init__
result = __init__(name, required)
```

```python
# Using __init__
result = __init__(contracts)
```

```python
# Using enforce
result = enforce(data)
```



---
**Generated**: 2026-03-26T09:39:04.738357
**Type**: api_reference
**Quality**: comprehensive
