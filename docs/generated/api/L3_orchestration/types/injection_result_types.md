# API Documentation: injection_result_types

**Target Audience**: developers, api_users

# injection_result_types API Documentation

**File**: `injection_result_types.py`
**Classes**: 1
**Functions**: 3

## Classes

- **InjectionResult**

## Functions

- **_score_prompt** -> tuple[int, str]
- **detect_injection** -> InjectionResult
- **validate_safety_threshold** -> bool


## Class: InjectionResult

**Description**: Result of prompt injection detection.



## Function: _score_prompt

**Parameters**: prompt
**Returns**: tuple[int, str]
**Description**: Score prompt for injection attempts.

    Args:
        prompt: User input to analyze

    Returns:
        Tuple of (score: int, rationale: str)
    



## Function: detect_injection

**Parameters**: prompt
**Returns**: InjectionResult
**Description**: Detect prompt injection attempts in user input.

    Args:
        prompt: User input to analyze for injection attempts

    Returns:
        InjectionResult with detection details and Severity assessment
    



## Function: validate_safety_threshold

**Parameters**: result, threshold
**Returns**: bool
**Description**: Validate injection result against safety threshold.

    Args:
        result: InjectionResult from detect_injection
        threshold: Safety confidence threshold (default 0.8)

    Returns:
        True if safe (below threshold), False if unsafe
    



## Usage Examples

### Class Usage

```python
# Using InjectionResult
injectionresult = InjectionResult()
```

### Function Usage

```python
# Using _score_prompt
result = _score_prompt(prompt)
```

```python
# Using detect_injection
result = detect_injection(prompt)
```

```python
# Using validate_safety_threshold
result = validate_safety_threshold(result, threshold)
```



---
**Generated**: 2026-03-26T09:39:04.387833
**Type**: api_reference
**Quality**: comprehensive
