# API Documentation: arbitration_contract

**Target Audience**: developers, api_users

# arbitration_contract API Documentation

**File**: `arbitration_contract.py`
**Classes**: 3
**Functions**: 9

## Classes

- **AdvisorProposal**
- **ArbitrationInput**
- **ArbitrationDecision**

## Functions

- **proposal_to_json** -> str
- **proposal_from_json** -> AdvisorProposal
- **arbitration_input_to_json** -> str
- **arbitration_input_from_json** -> ArbitrationInput
- **decision_to_json** -> str
- **decision_from_json** -> ArbitrationDecision
- **__post_init__**
- **__post_init__**
- **__post_init__**


## Class: AdvisorProposal

**Description**: Immutable proposal from an advisor agent.

### Methods

#### __post_init__
**Parameters**: self
**Description**: Validate proposal constraints and normalize list ordering.



## Class: ArbitrationInput

**Description**: Immutable input for arbitration process.

### Methods

#### __post_init__
**Parameters**: self
**Description**: Validate input constraints.



## Class: ArbitrationDecision

**Description**: Immutable final arbitration decision.

### Methods

#### __post_init__
**Parameters**: self
**Description**: Validate decision constraints and normalize list ordering.



## Function: proposal_to_json

**Parameters**: proposal
**Returns**: str
**Description**: Serialize AdvisorProposal to deterministic JSON.



## Function: proposal_from_json

**Parameters**: json_str
**Returns**: AdvisorProposal
**Description**: Deserialize JSON string to AdvisorProposal.



## Function: arbitration_input_to_json

**Parameters**: input_data
**Returns**: str
**Description**: Serialize ArbitrationInput to deterministic JSON.



## Function: arbitration_input_from_json

**Parameters**: json_str
**Returns**: ArbitrationInput
**Description**: Deserialize JSON string to ArbitrationInput.



## Function: decision_to_json

**Parameters**: decision
**Returns**: str
**Description**: Serialize ArbitrationDecision to deterministic JSON.



## Function: decision_from_json

**Parameters**: json_str
**Returns**: ArbitrationDecision
**Description**: Deserialize JSON string to ArbitrationDecision.



## Function: __post_init__

**Parameters**: self
**Description**: Validate proposal constraints and normalize list ordering.



## Function: __post_init__

**Parameters**: self
**Description**: Validate input constraints.



## Function: __post_init__

**Parameters**: self
**Description**: Validate decision constraints and normalize list ordering.



## Usage Examples

### Class Usage

```python
# Using AdvisorProposal
advisorproposal = AdvisorProposal()
```

```python
# Using ArbitrationInput
arbitrationinput = ArbitrationInput()
```

```python
# Using ArbitrationDecision
arbitrationdecision = ArbitrationDecision()
```

### Function Usage

```python
# Using proposal_to_json
result = proposal_to_json(proposal)
```

```python
# Using proposal_from_json
result = proposal_from_json(json_str)
```

```python
# Using arbitration_input_to_json
result = arbitration_input_to_json(input_data)
```



---
**Generated**: 2026-03-26T09:39:04.081516
**Type**: api_reference
**Quality**: comprehensive
