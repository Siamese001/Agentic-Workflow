# API Documentation: human_decision_artifact_types

**Target Audience**: developers, api_users

# human_decision_artifact_types API Documentation

**File**: `human_decision_artifact_types.py`
**Classes**: 2
**Functions**: 5

## Classes

- **HumanDecisionViolation** (inherits from ValueError)
- **HumanDecisionArtifact**

## Functions

- **__post_init__** -> None
- **_signable_dict** -> dict
- **sign** -> HumanDecisionArtifact
- **verify** -> None
- **assert_plan_hash_matches** -> None


## Class: HumanDecisionViolation

**Description**: Raised when HumanDecisionArtifact invariants are broken.

**Inherits from**: ValueError



## Class: HumanDecisionArtifact

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### _signable_dict
**Parameters**: self
**Returns**: dict

#### sign
**Parameters**: self, secret
**Returns**: HumanDecisionArtifact

#### verify
**Parameters**: self, secret
**Returns**: None

#### assert_plan_hash_matches
**Parameters**: self, submitted_plan_hash
**Returns**: None
**Description**: Hard-fail if this artifact references a different plan than what was submitted.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: _signable_dict

**Parameters**: self
**Returns**: dict


## Function: sign

**Parameters**: self, secret
**Returns**: HumanDecisionArtifact


## Function: verify

**Parameters**: self, secret
**Returns**: None


## Function: assert_plan_hash_matches

**Parameters**: self, submitted_plan_hash
**Returns**: None
**Description**: Hard-fail if this artifact references a different plan than what was submitted.



## Usage Examples

### Class Usage

```python
# Using HumanDecisionViolation
humandecisionviolation = HumanDecisionViolation()
```

```python
# Using HumanDecisionArtifact
humandecisionartifact = HumanDecisionArtifact()
humandecisionartifact.sign()
humandecisionartifact.verify()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _signable_dict
result = _signable_dict()
```

```python
# Using sign
result = sign(secret)
```



---
**Generated**: 2026-03-26T09:39:05.525563
**Type**: api_reference
**Quality**: comprehensive
