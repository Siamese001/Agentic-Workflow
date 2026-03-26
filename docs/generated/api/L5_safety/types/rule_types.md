# API Documentation: rule_types

**Target Audience**: developers, api_users

# rule_types API Documentation

**File**: `rule_types.py`
**Classes**: 7
**Functions**: 10

## Classes

- **RuleType** (inherits from Enum)
- **RuleSeverity** (inherits from Enum)
- **ViolationType** (inherits from Enum)
- **ConstitutionalRule**
- **ViolationReport**
- **ConstitutionalReviewResult**
- **ConstitutionalAISystem**

## Functions

- **review_content** -> ConstitutionalReviewResult
- **__init__**
- **add_rule** -> None
- **remove_rule** -> None
- **review_content** -> ConstitutionalReviewResult
- **_check_compliance** -> list[ViolationReport]
- **_check_rule** -> list[ViolationReport]
- **_calculate_compliance_score** -> float
- **_generate_recommendations** -> list[str]
- **_load_default_rules** -> None


## Class: RuleType

**Description**: Types of constitutional rules.

**Inherits from**: Enum



## Class: RuleSeverity

**Description**: Severity levels for rule violations.

**Inherits from**: Enum



## Class: ViolationType

**Description**: Types of constitutional violations.

**Inherits from**: Enum



## Class: ConstitutionalRule

**Description**: Individual constitutional rule.



## Class: ViolationReport

**Description**: Report of constitutional Violation.



## Class: ConstitutionalReviewResult

**Description**: Result of constitutional review.



## Class: ConstitutionalAISystem

**Description**: Constitutional AI System for Safety and Alignment.

    Provides rule-based validation, ethical guidelines,
    and content compliance checking.
    

### Methods

#### __init__
**Parameters**: self, enable_logging
**Description**: Initialize Constitutional AI system.

        Args:
            enable_logging: Enable logging of violations
        

#### add_rule
**Parameters**: self, rule
**Returns**: None
**Description**: Add a constitutional rule.

        Args:
            rule: Rule to add
        

#### remove_rule
**Parameters**: self, rule_id
**Returns**: None
**Description**: Remove a constitutional rule.

        Args:
            rule_id: ID of rule to remove
        

#### review_content
**Parameters**: self, content, context
**Returns**: ConstitutionalReviewResult
**Description**: Review content against constitutional rules.

        Args:
            content: Content to review
            context: Optional context for evaluation

        Returns:
            ConstitutionalReviewResult with violations and recommendations
        

#### _check_compliance
**Parameters**: self, content, context
**Returns**: list[ViolationReport]
**Description**: Check content against all rules.

        Args:
            content: Content to check
            context: Optional context

        Returns:
            List of violations
        

#### _check_rule
**Parameters**: self, content, rule, context
**Returns**: list[ViolationReport]
**Description**: Check content against a specific rule.

        Args:
            content: Content to check
            rule: Rule to apply
            context: Optional context

        Returns:
            List of violations for this rule
        

#### _calculate_compliance_score
**Parameters**: self, violations
**Returns**: float
**Description**: Calculate compliance score based on violations.

        Args:
            violations: List of violations

        Returns:
            Compliance score (0.0-1.0)
        

#### _generate_recommendations
**Parameters**: self, violations
**Returns**: list[str]
**Description**: Generate recommendations based on violations.

        Args:
            violations: List of violations

        Returns:
            List of recommendations
        

#### _load_default_rules
**Parameters**: self
**Returns**: None
**Description**: Load default constitutional rules.



## Function: review_content

**Parameters**: content, context
**Returns**: ConstitutionalReviewResult
**Description**: Convenience function to review content.

    Args:
        content: Content to review
        context: Optional context

    Returns:
        ConstitutionalReviewResult
    



## Function: __init__

**Parameters**: self, enable_logging
**Description**: Initialize Constitutional AI system.

        Args:
            enable_logging: Enable logging of violations
        



## Function: add_rule

**Parameters**: self, rule
**Returns**: None
**Description**: Add a constitutional rule.

        Args:
            rule: Rule to add
        



## Function: remove_rule

**Parameters**: self, rule_id
**Returns**: None
**Description**: Remove a constitutional rule.

        Args:
            rule_id: ID of rule to remove
        



## Function: review_content

**Parameters**: self, content, context
**Returns**: ConstitutionalReviewResult
**Description**: Review content against constitutional rules.

        Args:
            content: Content to review
            context: Optional context for evaluation

        Returns:
            ConstitutionalReviewResult with violations and recommendations
        



## Function: _check_compliance

**Parameters**: self, content, context
**Returns**: list[ViolationReport]
**Description**: Check content against all rules.

        Args:
            content: Content to check
            context: Optional context

        Returns:
            List of violations
        



## Function: _check_rule

**Parameters**: self, content, rule, context
**Returns**: list[ViolationReport]
**Description**: Check content against a specific rule.

        Args:
            content: Content to check
            rule: Rule to apply
            context: Optional context

        Returns:
            List of violations for this rule
        



## Function: _calculate_compliance_score

**Parameters**: self, violations
**Returns**: float
**Description**: Calculate compliance score based on violations.

        Args:
            violations: List of violations

        Returns:
            Compliance score (0.0-1.0)
        



## Function: _generate_recommendations

**Parameters**: self, violations
**Returns**: list[str]
**Description**: Generate recommendations based on violations.

        Args:
            violations: List of violations

        Returns:
            List of recommendations
        



## Function: _load_default_rules

**Parameters**: self
**Returns**: None
**Description**: Load default constitutional rules.



## Usage Examples

### Class Usage

```python
# Using RuleType
ruletype = RuleType()
```

```python
# Using RuleSeverity
ruleseverity = RuleSeverity()
```

```python
# Using ViolationType
violationtype = ViolationType()
```

### Function Usage

```python
# Using review_content
result = review_content(content, context)
```

```python
# Using __init__
result = __init__(enable_logging)
```

```python
# Using add_rule
result = add_rule(rule)
```



---
**Generated**: 2026-03-26T09:39:05.553701
**Type**: api_reference
**Quality**: comprehensive
