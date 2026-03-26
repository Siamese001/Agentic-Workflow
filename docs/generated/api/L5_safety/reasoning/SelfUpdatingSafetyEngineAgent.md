# API Documentation: SelfUpdatingSafetyEngineAgent

**Target Audience**: developers, api_users

# SelfUpdatingSafetyEngineAgent API Documentation

**File**: `SelfUpdatingSafetyEngineAgent.py`
**Classes**: 6
**Functions**: 18

## Classes

- **ThreatLevel** (inherits from Enum)
- **RuleType** (inherits from Enum)
- **ThreatPattern**
- **SafetyRule**
- **ThreatDetection**
- **SelfUpdatingSafetyEngineAgent** (inherits from SovereignBaseAgent)

## Functions

- **create_self_updating_safety_engine** -> SelfUpdatingSafetyEngine
- **confidence_score** -> float
- **matches** -> bool
- **to_dict** -> dict[str, Any]
- **from_dict** -> SafetyRule
- **__init__** -> None
- **_initialize_base_rules** -> Any
- **_load_rules** -> Any
- **_save_rules** -> Any
- **_generate_pattern_variations** -> list[str]
- **report_false_positive** -> Any
- **_compare_threat_levels** -> int
- **_generate_recommendations** -> list[str]
- **escalate_threat_level** -> Any
- **get_rule_effectiveness** -> dict[str, Any]
- **get_threat_statistics** -> dict[str, Any]
- **heal_repository** -> dict[str, int]
- **heal** -> dict


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



## Class: SelfUpdatingSafetyEngineAgent

**Description**: 
    Safety engine that learns and adapts to new threats.

    Features:
    - Automatic threat pattern detection
    - Dynamic rule generation
    - False positive learning
    - Threat Severity escalation
    - Rule effectiveness tracking
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, rules_storage_path
**Returns**: None
**Description**: Initialize the self-updating safety engine.

#### _initialize_base_rules
**Parameters**: self
**Returns**: Any
**Description**: Initialize base safety rules.

#### _load_rules
**Parameters**: self
**Returns**: Any
**Description**: Load rules from storage.

#### _save_rules
**Parameters**: self
**Returns**: Any
**Description**: Save rules to storage.

#### _generate_pattern_variations
**Parameters**: self, pattern
**Returns**: list[str]
**Description**: Generate variations of a threat pattern.

#### report_false_positive
**Parameters**: self, rule_id, text
**Returns**: Any
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
**Returns**: Any
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

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L5 safety agent - operational only.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal safety engine violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (threat, pattern, rule)
                - rule_id: ID of the triggered rule
                - threat_level: Severity level

        Returns:
            Dictionary with healing results following standard_heal format.
        



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
**Returns**: None
**Description**: Initialize the self-updating safety engine.



## Function: _initialize_base_rules

**Parameters**: self
**Returns**: Any
**Description**: Initialize base safety rules.



## Function: _load_rules

**Parameters**: self
**Returns**: Any
**Description**: Load rules from storage.



## Function: _save_rules

**Parameters**: self
**Returns**: Any
**Description**: Save rules to storage.



## Function: _generate_pattern_variations

**Parameters**: self, pattern
**Returns**: list[str]
**Description**: Generate variations of a threat pattern.



## Function: report_false_positive

**Parameters**: self, rule_id, text
**Returns**: Any
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
**Returns**: Any
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



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L5 safety agent - operational only.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal safety engine violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (threat, pattern, rule)
                - rule_id: ID of the triggered rule
                - threat_level: Severity level

        Returns:
            Dictionary with healing results following standard_heal format.
        



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
**Generated**: 2026-03-26T09:39:05.399133
**Type**: api_reference
**Quality**: comprehensive
