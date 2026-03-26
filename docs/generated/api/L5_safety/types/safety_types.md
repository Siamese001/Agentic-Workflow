# API Documentation: safety_types

**Target Audience**: developers, api_users

# safety_types API Documentation

**File**: `safety_types.py`
**Classes**: 6
**Functions**: 16

## Classes

- **ThreatLevel** (inherits from Enum)
- **RuleType** (inherits from Enum)
- **ThreatPattern**
- **SafetyRule**
- **ThreatDetection**
- **SelfUpdatingSafetyEngine**

## Functions

- **create_self_updating_safety_engine** -> SelfUpdatingSafetyEngine
- **confidence_score** -> float
- **matches** -> bool
- **to_dict** -> dict[str, Any]
- **from_dict** -> SafetyRule
- **__init__**
- **_initialize_base_rules**
- **_load_rules**
- **_save_rules**
- **_generate_pattern_variations** -> list[str]
- **report_false_positive**
- **_compare_threat_levels** -> int
- **_generate_recommendations** -> list[str]
- **escalate_threat_level**
- **get_rule_effectiveness** -> dict[str, Any]
- **get_threat_statistics** -> dict[str, Any]


## Class: ThreatLevel

**Description**: Threat Severity levels.

**Inherits from**: Enum



## Class: RuleType

**Description**: Types of safety rules.

**Inherits from**: Enum



## Class: ThreatPattern

**Description**: Represents a detected threat pattern.

### Methods

#### confidence_score
**Parameters**: self
**Returns**: float
**Description**: Calculate confidence score for this pattern.



## Class: SafetyRule

**Description**: Represents a safety rule.

### Methods

#### matches
**Parameters**: self, text
**Returns**: bool
**Description**: Check if text matches this rule.

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert rule to dictionary.

#### from_dict
**Parameters**: cls, data
**Returns**: SafetyRule
**Description**: Create rule from dictionary.



## Class: ThreatDetection

**Description**: Result of threat detection.



## Class: SelfUpdatingSafetyEngine

**Description**: 
    Safety engine that learns and adapts to new threats.

    Features:
    - Automatic threat pattern detection
    - Dynamic rule generation
    - False positive learning
    - Threat Severity escalation
    - Rule effectiveness tracking
    

### Methods

#### __init__
**Parameters**: self, rules_storage_path
**Description**: Initialize the self-updating safety engine.

#### _initialize_base_rules
**Parameters**: self
**Description**: Initialize base safety rules.

#### _load_rules
**Parameters**: self
**Description**: Load rules from storage.

#### _save_rules
**Parameters**: self
**Description**: Save rules to storage.

#### _generate_pattern_variations
**Parameters**: self, pattern
**Returns**: list[str]
**Description**: Generate variations of a threat pattern.

#### report_false_positive
**Parameters**: self, rule_id, text
**Description**: 
        Report a false positive detection.

        Args:
            rule_id: Rule that triggered false positive
            text: Text that was incorrectly flagged
        

#### _compare_threat_levels
**Parameters**: self, level1, level2
**Returns**: int
**Description**: Compare two threat levels.

#### _generate_recommendations
**Parameters**: self, matched_rules
**Returns**: list[str]
**Description**: Generate recommendations based on matched rules.

#### escalate_threat_level
**Parameters**: self, rule_id
**Description**: 
        Escalate threat level for a rule.

        Args:
            rule_id: Rule to escalate
        

#### get_rule_effectiveness
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get effectiveness metrics for rules.

#### get_threat_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get threat detection statistics.



## Function: create_self_updating_safety_engine

**Parameters**: rules_storage_path
**Returns**: SelfUpdatingSafetyEngine
**Description**: Factory function to create self-updating safety engine.



## Function: confidence_score

**Parameters**: self
**Returns**: float
**Description**: Calculate confidence score for this pattern.



## Function: matches

**Parameters**: self, text
**Returns**: bool
**Description**: Check if text matches this rule.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert rule to dictionary.



## Function: from_dict

**Parameters**: cls, data
**Returns**: SafetyRule
**Description**: Create rule from dictionary.



## Function: __init__

**Parameters**: self, rules_storage_path
**Description**: Initialize the self-updating safety engine.



## Function: _initialize_base_rules

**Parameters**: self
**Description**: Initialize base safety rules.



## Function: _load_rules

**Parameters**: self
**Description**: Load rules from storage.



## Function: _save_rules

**Parameters**: self
**Description**: Save rules to storage.



## Function: _generate_pattern_variations

**Parameters**: self, pattern
**Returns**: list[str]
**Description**: Generate variations of a threat pattern.



## Function: report_false_positive

**Parameters**: self, rule_id, text
**Description**: 
        Report a false positive detection.

        Args:
            rule_id: Rule that triggered false positive
            text: Text that was incorrectly flagged
        



## Function: _compare_threat_levels

**Parameters**: self, level1, level2
**Returns**: int
**Description**: Compare two threat levels.



## Function: _generate_recommendations

**Parameters**: self, matched_rules
**Returns**: list[str]
**Description**: Generate recommendations based on matched rules.



## Function: escalate_threat_level

**Parameters**: self, rule_id
**Description**: 
        Escalate threat level for a rule.

        Args:
            rule_id: Rule to escalate
        



## Function: get_rule_effectiveness

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get effectiveness metrics for rules.



## Function: get_threat_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get threat detection statistics.



## Usage Examples

### Class Usage

```python
# Using ThreatLevel
threatlevel = ThreatLevel()
```

```python
# Using RuleType
ruletype = RuleType()
```

```python
# Using ThreatPattern
threatpattern = ThreatPattern()
threatpattern.confidence_score()
```

### Function Usage

```python
# Using create_self_updating_safety_engine
result = create_self_updating_safety_engine(rules_storage_path)
```

```python
# Using confidence_score
result = confidence_score()
```

```python
# Using matches
result = matches(text)
```



---
**Generated**: 2026-03-26T09:39:05.561880
**Type**: api_reference
**Quality**: comprehensive
