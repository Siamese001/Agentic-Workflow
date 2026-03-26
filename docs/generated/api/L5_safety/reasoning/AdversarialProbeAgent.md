# API Documentation: AdversarialProbeAgent

**Target Audience**: developers, api_users

# AdversarialProbeAgent API Documentation

**File**: `AdversarialProbeAgent.py`
**Classes**: 1
**Functions**: 11

## Classes

- **AdversarialProbeAgent** (inherits from SovereignBaseAgent)

## Functions

- **__post_init__** -> None
- **_test_adversarial_examples** -> dict[str, Any]
- **_test_semantic_attacks** -> dict[str, Any]
- **_test_contradiction_injection** -> dict[str, Any]
- **_test_false_premise** -> dict[str, Any]
- **_test_confidence_manipulation** -> dict[str, Any]
- **_test_output_poisoning** -> dict[str, Any]
- **_test_model_extraction** -> dict[str, Any]
- **_run_self_tests** -> bool
- **heal_repository** -> dict[str, Any]
- **heal** -> dict


## Class: AdversarialProbeAgent

**Description**: 
    Red team agent specializing in adversarial attacks and probing.
    Executes strategic attack patterns:
    - Adversarial examples designed to confuse models
    - Semantic attacks (meaning-preserving but harmful)
    - Contradiction injection
    - False premise attacks
    - Confidence manipulation
    - Output poisoning
    - Model extraction attempts
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None
**Description**: Post-initialization setup.

#### _test_adversarial_examples
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system with adversarial examples.

#### _test_semantic_attacks
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system with semantic attacks.

#### _test_contradiction_injection
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system with contradiction injection.

#### _test_false_premise
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system with false premise attacks.

#### _test_confidence_manipulation
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system confidence manipulation.

#### _test_output_poisoning
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system output poisoning.

#### _test_model_extraction
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system model extraction attacks.

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Validate agent structure.

#### heal_repository
**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: Repository healing with parent chain invocation.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal adversarial probe violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details.

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: __post_init__

**Parameters**: self
**Returns**: None
**Description**: Post-initialization setup.



## Function: _test_adversarial_examples

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system with adversarial examples.



## Function: _test_semantic_attacks

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system with semantic attacks.



## Function: _test_contradiction_injection

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system with contradiction injection.



## Function: _test_false_premise

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system with false premise attacks.



## Function: _test_confidence_manipulation

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system confidence manipulation.



## Function: _test_output_poisoning

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system output poisoning.



## Function: _test_model_extraction

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Test system model extraction attacks.



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Validate agent structure.



## Function: heal_repository

**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: Repository healing with parent chain invocation.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal adversarial probe violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details.

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using AdversarialProbeAgent
adversarialprobeagent = AdversarialProbeAgent()
adversarialprobeagent.heal_repository()
adversarialprobeagent.heal()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _test_adversarial_examples
result = _test_adversarial_examples()
```

```python
# Using _test_semantic_attacks
result = _test_semantic_attacks()
```



---
**Generated**: 2026-03-26T09:39:05.021665
**Type**: api_reference
**Quality**: comprehensive
