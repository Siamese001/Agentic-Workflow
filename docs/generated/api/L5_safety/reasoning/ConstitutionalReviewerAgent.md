# API Documentation: ConstitutionalReviewerAgent

**Target Audience**: developers, api_users

# ConstitutionalReviewerAgent API Documentation

**File**: `ConstitutionalReviewerAgent.py`
**Classes**: 3
**Functions**: 6

## Classes

- **ConstitutionalReviewResult**
- **ConstitutionalReviewerAgent** (inherits from SovereignBaseAgent, L5SafetyBase)
- **L5SafetyBase**

## Functions

- **track_metrics**
- **__init__** -> None
- **decorator**
- **heal_repository** -> dict[str, int]
- **_run_self_tests** -> dict
- **heal** -> dict


## Class: ConstitutionalReviewResult

**Description**: Stub for ConstitutionalReviewResult - TODO: Replace with sovereign equivalent

### Methods

#### __init__
**Parameters**: self, review_passed, violations_found, feedback
**Returns**: None



## Class: ConstitutionalReviewerAgent

**Description**: Performs final constitutional review of the output.

**Inherits from**: SovereignBaseAgent, L5SafetyBase

### Methods

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Operational guardrail agent - no repository healing required.

#### _run_self_tests
**Parameters**: self
**Returns**: dict
**Description**: Run internal self-tests.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal constitutional review violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (constitutional)
                - content: Content that failed review
                - violations_found: List of constitutional violations

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Class: L5SafetyBase

**Description**: Stub L5SafetyBase.



## Function: track_metrics

**Parameters**: name
**Description**: Stub decorator for track_metrics - TODO: Replace with sovereign equivalent



## Function: __init__

**Parameters**: self, review_passed, violations_found, feedback
**Returns**: None


## Function: decorator

**Parameters**: func


## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Operational guardrail agent - no repository healing required.



## Function: _run_self_tests

**Parameters**: self
**Returns**: dict
**Description**: Run internal self-tests.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal constitutional review violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (constitutional)
                - content: Content that failed review
                - violations_found: List of constitutional violations

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using ConstitutionalReviewResult
constitutionalreviewresult = ConstitutionalReviewResult()
```

```python
# Using ConstitutionalReviewerAgent
constitutionalrevieweragent = ConstitutionalReviewerAgent()
constitutionalrevieweragent.heal_repository()
constitutionalrevieweragent.heal()
```

```python
# Using L5SafetyBase
l5safetybase = L5SafetyBase()
```

### Function Usage

```python
# Using track_metrics
result = track_metrics(name)
```

```python
# Using __init__
result = __init__(review_passed, violations_found)
```

```python
# Using decorator
result = decorator(func)
```



---
**Generated**: 2026-03-26T09:39:05.110535
**Type**: api_reference
**Quality**: comprehensive
