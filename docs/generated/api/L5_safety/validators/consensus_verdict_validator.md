# API Documentation: consensus_verdict_validator

**Target Audience**: developers, api_users

# consensus_verdict_validator API Documentation

**File**: `consensus_verdict_validator.py`
**Classes**: 2
**Functions**: 1

## Classes

- **ConsensusVerdict** (inherits from BaseModel)
- **ModelOpinion** (inherits from BaseModel)

## Functions

- **validate_risk_assessment** -> str


## Class: ConsensusVerdict

**Description**: Result of a consensus deliberation across multiple models.

**Inherits from**: BaseModel



## Class: ModelOpinion

**Description**: Individual model's opinion on a proposed plan.

**Inherits from**: BaseModel

### Methods

#### validate_risk_assessment
**Parameters**: cls, v
**Returns**: str
**Description**: [HARDENED] Ensure risk assessment is valid.



## Function: validate_risk_assessment

**Parameters**: cls, v
**Returns**: str
**Description**: [HARDENED] Ensure risk assessment is valid.



## Usage Examples

### Class Usage

```python
# Using ConsensusVerdict
consensusverdict = ConsensusVerdict()
```

```python
# Using ModelOpinion
modelopinion = ModelOpinion()
modelopinion.validate_risk_assessment()
```

### Function Usage

```python
# Using validate_risk_assessment
result = validate_risk_assessment(cls, v)
```



---
**Generated**: 2026-03-26T09:39:05.761229
**Type**: api_reference
**Quality**: comprehensive
