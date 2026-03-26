# API Documentation: learning_types

**Target Audience**: developers, api_users

# learning_types API Documentation

**File**: `learning_types.py`
**Classes**: 3
**Functions**: 14

## Classes

- **HealingPattern**
- **ViolationPrediction**
- **AdaptiveLearningEngine**

## Functions

- **create_adaptive_learning_engine** -> AdaptiveLearningEngine
- **success_rate** -> float
- **update_confidence** -> Any
- **__init__**
- **awaken** -> Any
- **_load_patterns**
- **_save_patterns**
- **learn_from_healing** -> Any
- **_create_violation_signature** -> str
- **_extract_keywords** -> list[str]
- **_extract_file_pattern** -> str
- **_find_matching_pattern** -> HealingPattern | None
- **get_recommended_fix** -> str | None
- **get_statistics** -> dict[str, Any]


## Class: HealingPattern

**Description**: Represents a learned healing pattern.

### Methods

#### success_rate
**Parameters**: self
**Returns**: float
**Description**: Calculate success rate.

#### update_confidence
**Parameters**: self
**Returns**: Any
**Description**: Update confidence score based on success rate and usage.



## Class: ViolationPrediction

**Description**: Prediction of potential Violation.



## Class: AdaptiveLearningEngine

**Description**: 
    Learns from healing patterns to predict and prevent violations.

    Features:
    - Pattern recognition from successful healing attempts
    - Predictive Violation detection
    - Automatic fix suggestion based on learned patterns
    - Continuous learning from new healing attempts
    

### Methods

#### __init__
**Parameters**: self, pattern_storage_path, autonomous_mode
**Description**: Initialize the adaptive learning engine.

#### awaken
**Parameters**: self
**Returns**: Any
**Description**: L1: Explicitly trigger the autonomous learning loop

#### _load_patterns
**Parameters**: self
**Description**: Load learned patterns from storage.

#### _save_patterns
**Parameters**: self
**Description**: Save learned patterns to storage with versioned rotation (Keep Last 10).

#### learn_from_healing
**Parameters**: self, file_path, violation_key, violation_details, fix_code, success, rounds_taken
**Returns**: Any
**Description**: 
        Learn from a healing attempt.

        Args:
            file_path: Path to the healed file
            violation_key: Canon key that was fixed
            violation_details: Description of the Violation
            fix_code: The code that fixed the issue
            success: Whether healing succeeded
            rounds_taken: Number of rounds it took
        

#### _create_violation_signature
**Parameters**: self, violation_details, file_path
**Returns**: str
**Description**: Create a signature for a Violation type.

#### _extract_keywords
**Parameters**: self, text
**Returns**: list[str]
**Description**: Extract key terms from Violation details.

#### _extract_file_pattern
**Parameters**: self, file_path
**Returns**: str
**Description**: Extract pattern from file path.

#### _find_matching_pattern
**Parameters**: self, violation_key, signature
**Returns**: HealingPattern | None
**Description**: Find existing pattern matching the signature.

#### get_recommended_fix
**Parameters**: self, violation_key, violation_details, file_path
**Returns**: str | None
**Description**: 
        Get recommended fix based on learned patterns.

        Args:
            violation_key: Canon key
            violation_details: Violation description
            file_path: File path

        Returns:
            Recommended fix strategy or None
        

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get learning statistics.



## Function: create_adaptive_learning_engine

**Parameters**: storage_path, autonomous_mode
**Returns**: AdaptiveLearningEngine
**Description**: Factory function to create adaptive learning engine.



## Function: success_rate

**Parameters**: self
**Returns**: float
**Description**: Calculate success rate.



## Function: update_confidence

**Parameters**: self
**Returns**: Any
**Description**: Update confidence score based on success rate and usage.



## Function: __init__

**Parameters**: self, pattern_storage_path, autonomous_mode
**Description**: Initialize the adaptive learning engine.



## Function: awaken

**Parameters**: self
**Returns**: Any
**Description**: L1: Explicitly trigger the autonomous learning loop



## Function: _load_patterns

**Parameters**: self
**Description**: Load learned patterns from storage.



## Function: _save_patterns

**Parameters**: self
**Description**: Save learned patterns to storage with versioned rotation (Keep Last 10).



## Function: learn_from_healing

**Parameters**: self, file_path, violation_key, violation_details, fix_code, success, rounds_taken
**Returns**: Any
**Description**: 
        Learn from a healing attempt.

        Args:
            file_path: Path to the healed file
            violation_key: Canon key that was fixed
            violation_details: Description of the Violation
            fix_code: The code that fixed the issue
            success: Whether healing succeeded
            rounds_taken: Number of rounds it took
        



## Function: _create_violation_signature

**Parameters**: self, violation_details, file_path
**Returns**: str
**Description**: Create a signature for a Violation type.



## Function: _extract_keywords

**Parameters**: self, text
**Returns**: list[str]
**Description**: Extract key terms from Violation details.



## Function: _extract_file_pattern

**Parameters**: self, file_path
**Returns**: str
**Description**: Extract pattern from file path.



## Function: _find_matching_pattern

**Parameters**: self, violation_key, signature
**Returns**: HealingPattern | None
**Description**: Find existing pattern matching the signature.



## Function: get_recommended_fix

**Parameters**: self, violation_key, violation_details, file_path
**Returns**: str | None
**Description**: 
        Get recommended fix based on learned patterns.

        Args:
            violation_key: Canon key
            violation_details: Violation description
            file_path: File path

        Returns:
            Recommended fix strategy or None
        



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get learning statistics.



## Usage Examples

### Class Usage

```python
# Using HealingPattern
healingpattern = HealingPattern()
healingpattern.success_rate()
healingpattern.update_confidence()
```

```python
# Using ViolationPrediction
violationprediction = ViolationPrediction()
```

```python
# Using AdaptiveLearningEngine
adaptivelearningengine = AdaptiveLearningEngine()
adaptivelearningengine.awaken()
adaptivelearningengine.learn_from_healing()
```

### Function Usage

```python
# Using create_adaptive_learning_engine
result = create_adaptive_learning_engine(storage_path, autonomous_mode)
```

```python
# Using success_rate
result = success_rate()
```

```python
# Using update_confidence
result = update_confidence()
```



---
**Generated**: 2026-03-26T09:39:05.536343
**Type**: api_reference
**Quality**: comprehensive
