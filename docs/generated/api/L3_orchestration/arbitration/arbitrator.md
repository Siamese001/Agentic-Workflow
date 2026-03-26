# API Documentation: arbitrator

**Target Audience**: developers, api_users

# arbitrator API Documentation

**File**: `arbitrator.py`
**Classes**: 1
**Functions**: 3

## Classes

- **Arbitrator**

## Functions

- **__init__**
- **calculate_score** -> int
- **arbitrate** -> ArbitrationDecision


## Class: Arbitrator

**Description**: Deterministic arbitrator for multi-agent decisions.

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize arbitrator with default scoring rules.

#### calculate_score
**Parameters**: self, proposal
**Returns**: int
**Description**: Calculate deterministic score for a proposal.

        Scoring rules:
        - Base = confidence
        - +2 per rationale item (cap 10)
        - -3 per risk item (cap 15)
        - +1 per artifact (cap 5)

        Args:
            proposal: Advisor proposal to score

        Returns:
            Calculated score
        

#### arbitrate
**Parameters**: self, input_data
**Returns**: ArbitrationDecision
**Description**: Perform deterministic arbitration on proposals.

        Args:
            input_data: Arbitration input with proposals

        Returns:
            Selected decision with score breakdown

        Raises:
            ValueError: If no proposals provided
        



## Function: __init__

**Parameters**: self
**Description**: Initialize arbitrator with default scoring rules.



## Function: calculate_score

**Parameters**: self, proposal
**Returns**: int
**Description**: Calculate deterministic score for a proposal.

        Scoring rules:
        - Base = confidence
        - +2 per rationale item (cap 10)
        - -3 per risk item (cap 15)
        - +1 per artifact (cap 5)

        Args:
            proposal: Advisor proposal to score

        Returns:
            Calculated score
        



## Function: arbitrate

**Parameters**: self, input_data
**Returns**: ArbitrationDecision
**Description**: Perform deterministic arbitration on proposals.

        Args:
            input_data: Arbitration input with proposals

        Returns:
            Selected decision with score breakdown

        Raises:
            ValueError: If no proposals provided
        



## Usage Examples

### Class Usage

```python
# Using Arbitrator
arbitrator = Arbitrator()
arbitrator.calculate_score()
arbitrator.arbitrate()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using calculate_score
result = calculate_score(proposal)
```

```python
# Using arbitrate
result = arbitrate(input_data)
```



---
**Generated**: 2026-03-26T09:39:04.083123
**Type**: api_reference
**Quality**: comprehensive
