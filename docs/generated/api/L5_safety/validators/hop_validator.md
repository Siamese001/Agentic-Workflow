# API Documentation: hop_validator

**Target Audience**: developers, api_users

# hop_validator API Documentation

**File**: `hop_validator.py`
**Classes**: 7
**Functions**: 23

## Classes

- **HOPValidationResult**
- **HOP1ProfileDeterministic**
- **HOP3DataExtractionDeterministic**
- **HOP4ConditionDeterministic**
- **HOP6PlaceholderDeterministic**
- **HOP7GateDecisionDeterministic**
- **HOPValidationDeterministic**

## Functions

- **__post_init__** -> None
- **__init__** -> None
- **classify_profile_heuristic** -> HOPValidationResult
- **_calculate_profile_completeness** -> float
- **_classify_industry** -> str
- **_classify_seniority** -> str
- **__init__** -> None
- **extract_grounded_entities** -> HOPValidationResult
- **_apply_entity_patterns** -> dict[str, Any]
- **__init__** -> None
- **check_conditions** -> HOPValidationResult
- **_evaluate_condition** -> dict[str, Any]
- **__init__** -> None
- **validate_placeholders** -> HOPValidationResult
- **__init__** -> None
- **classify_gate_decision** -> HOPValidationResult
- **_calculate_decision_score** -> float
- **__init__** -> None
- **validate_hop1_profile** -> HOPValidationResult
- **validate_hop3_extraction** -> HOPValidationResult
- **validate_hop4_conditions** -> HOPValidationResult
- **validate_hop6_placeholders** -> HOPValidationResult
- **validate_hop7_decision** -> HOPValidationResult


## Class: HOPValidationResult

**Description**: Result of HOP validation with deterministic scoring.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: HOP1ProfileDeterministic

**Description**: Deterministic profile classification for HOP1.

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize with HOP1 classification rules.

#### classify_profile_heuristic
**Parameters**: self, profile
**Returns**: HOPValidationResult
**Description**: 
        Classify profile using deterministic heuristic rules.

        Moved to Deterministic: Pure rule-based classification
        

#### _calculate_profile_completeness
**Parameters**: self, profile
**Returns**: float
**Description**: Calculate profile completeness using deterministic rules.

#### _classify_industry
**Parameters**: self, profile
**Returns**: str
**Description**: Classify industry using deterministic keyword matching.

#### _classify_seniority
**Parameters**: self, profile
**Returns**: str
**Description**: Classify seniority using deterministic keyword matching.



## Class: HOP3DataExtractionDeterministic

**Description**: Deterministic data extraction for HOP3.

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize with HOP3 extraction rules.

#### extract_grounded_entities
**Parameters**: self, json_data
**Returns**: HOPValidationResult
**Description**: 
        Extract grounded entities from JSON data.

        Moved to Deterministic: Pure JSON parsing and extraction
        

#### _apply_entity_patterns
**Parameters**: self, json_data
**Returns**: dict[str, Any]
**Description**: Apply deterministic entity extraction patterns.



## Class: HOP4ConditionDeterministic

**Description**: Deterministic condition checking for HOP4.

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize with HOP4 condition rules.

#### check_conditions
**Parameters**: self, context
**Returns**: HOPValidationResult
**Description**: 
        Check routing conditions using deterministic boolean logic.

        Moved to Deterministic: Pure boolean condition evaluation
        

#### _evaluate_condition
**Parameters**: self, condition, context
**Returns**: dict[str, Any]
**Description**: Evaluate single condition using deterministic logic.



## Class: HOP6PlaceholderDeterministic

**Description**: Deterministic placeholder validation for HOP6.

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize with HOP6 placeholder patterns.

#### validate_placeholders
**Parameters**: self, content
**Returns**: HOPValidationResult
**Description**: 
        Validate placeholders using deterministic regex patterns.

        Moved to Deterministic: Pure pattern matching
        



## Class: HOP7GateDecisionDeterministic

**Description**: Deterministic gate decision classification for HOP7.

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize with HOP7 gate decision rules.

#### classify_gate_decision
**Parameters**: self, violations
**Returns**: HOPValidationResult
**Description**: 
        Classify gate decision using deterministic rule-based logic.

        Moved to Deterministic: Pure rule-based classification
        

#### _calculate_decision_score
**Parameters**: self, violation_counts, decision
**Returns**: float
**Description**: Calculate decision score using deterministic algorithm.



## Class: HOPValidationDeterministic

**Description**: 
    Unified deterministic validation for HOP series agents.

    Consolidates all HOP deterministic logic into a single interface.
    

### Methods

#### __init__
**Parameters**: self, hop_config
**Returns**: None
**Description**: Initialize with HOP configuration.

#### validate_hop1_profile
**Parameters**: self, profile
**Returns**: HOPValidationResult
**Description**: Validate HOP1 profile classification.

#### validate_hop3_extraction
**Parameters**: self, json_data
**Returns**: HOPValidationResult
**Description**: Validate HOP3 data extraction.

#### validate_hop4_conditions
**Parameters**: self, context
**Returns**: HOPValidationResult
**Description**: Validate HOP4 condition checking.

#### validate_hop6_placeholders
**Parameters**: self, content
**Returns**: HOPValidationResult
**Description**: Validate HOP6 placeholder detection.

#### validate_hop7_decision
**Parameters**: self, violations
**Returns**: HOPValidationResult
**Description**: Validate HOP7 gate decision classification.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize with HOP1 classification rules.



## Function: classify_profile_heuristic

**Parameters**: self, profile
**Returns**: HOPValidationResult
**Description**: 
        Classify profile using deterministic heuristic rules.

        Moved to Deterministic: Pure rule-based classification
        



## Function: _calculate_profile_completeness

**Parameters**: self, profile
**Returns**: float
**Description**: Calculate profile completeness using deterministic rules.



## Function: _classify_industry

**Parameters**: self, profile
**Returns**: str
**Description**: Classify industry using deterministic keyword matching.



## Function: _classify_seniority

**Parameters**: self, profile
**Returns**: str
**Description**: Classify seniority using deterministic keyword matching.



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize with HOP3 extraction rules.



## Function: extract_grounded_entities

**Parameters**: self, json_data
**Returns**: HOPValidationResult
**Description**: 
        Extract grounded entities from JSON data.

        Moved to Deterministic: Pure JSON parsing and extraction
        



## Function: _apply_entity_patterns

**Parameters**: self, json_data
**Returns**: dict[str, Any]
**Description**: Apply deterministic entity extraction patterns.



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize with HOP4 condition rules.



## Function: check_conditions

**Parameters**: self, context
**Returns**: HOPValidationResult
**Description**: 
        Check routing conditions using deterministic boolean logic.

        Moved to Deterministic: Pure boolean condition evaluation
        



## Function: _evaluate_condition

**Parameters**: self, condition, context
**Returns**: dict[str, Any]
**Description**: Evaluate single condition using deterministic logic.



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize with HOP6 placeholder patterns.



## Function: validate_placeholders

**Parameters**: self, content
**Returns**: HOPValidationResult
**Description**: 
        Validate placeholders using deterministic regex patterns.

        Moved to Deterministic: Pure pattern matching
        



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize with HOP7 gate decision rules.



## Function: classify_gate_decision

**Parameters**: self, violations
**Returns**: HOPValidationResult
**Description**: 
        Classify gate decision using deterministic rule-based logic.

        Moved to Deterministic: Pure rule-based classification
        



## Function: _calculate_decision_score

**Parameters**: self, violation_counts, decision
**Returns**: float
**Description**: Calculate decision score using deterministic algorithm.



## Function: __init__

**Parameters**: self, hop_config
**Returns**: None
**Description**: Initialize with HOP configuration.



## Function: validate_hop1_profile

**Parameters**: self, profile
**Returns**: HOPValidationResult
**Description**: Validate HOP1 profile classification.



## Function: validate_hop3_extraction

**Parameters**: self, json_data
**Returns**: HOPValidationResult
**Description**: Validate HOP3 data extraction.



## Function: validate_hop4_conditions

**Parameters**: self, context
**Returns**: HOPValidationResult
**Description**: Validate HOP4 condition checking.



## Function: validate_hop6_placeholders

**Parameters**: self, content
**Returns**: HOPValidationResult
**Description**: Validate HOP6 placeholder detection.



## Function: validate_hop7_decision

**Parameters**: self, violations
**Returns**: HOPValidationResult
**Description**: Validate HOP7 gate decision classification.



## Usage Examples

### Class Usage

```python
# Using HOPValidationResult
hopvalidationresult = HOPValidationResult()
```

```python
# Using HOP1ProfileDeterministic
hop1profiledeterministic = HOP1ProfileDeterministic()
hop1profiledeterministic.classify_profile_heuristic()
```

```python
# Using HOP3DataExtractionDeterministic
hop3dataextractiondeterministic = HOP3DataExtractionDeterministic()
hop3dataextractiondeterministic.extract_grounded_entities()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __init__
result = __init__(config)
```

```python
# Using classify_profile_heuristic
result = classify_profile_heuristic(profile)
```



---
**Generated**: 2026-03-26T09:39:05.814637
**Type**: api_reference
**Quality**: comprehensive
