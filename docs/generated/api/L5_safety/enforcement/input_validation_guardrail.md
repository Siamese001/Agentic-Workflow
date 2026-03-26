# API Documentation: input_validation_guardrail

**Target Audience**: developers, api_users

# input_validation_guardrail API Documentation

**File**: `input_validation_guardrail.py`
**Classes**: 1
**Functions**: 8

## Classes

- **InputValidationGuardrail** (inherits from SovereignBaseAgent)

## Functions

- **__post_init__**
- **_detect_pii** -> dict[str, Any]
- **_detect_prompt_injection** -> dict[str, Any]
- **_detect_bias** -> dict[str, Any]
- **_validate_format** -> dict[str, Any]
- **_run_self_tests** -> bool
- **heal_repository** -> dict[str, Any]
- **heal** -> dict


## Class: InputValidationGuardrail

**Description**: 
    Consolidated input validation with composable rule sets.
    Handles: PII detection, prompt injection, bias detection, format validation.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self

#### _detect_pii
**Parameters**: self, text
**Returns**: dict[str, Any]
**Description**: Detect personally identifiable information.

#### _detect_prompt_injection
**Parameters**: self, text
**Returns**: dict[str, Any]
**Description**: Detect prompt injection attempts.

#### _detect_bias
**Parameters**: self, text
**Returns**: dict[str, Any]
**Description**: Detect biased language patterns.

#### _validate_format
**Parameters**: self, text
**Returns**: dict[str, Any]
**Description**: Validate input format.

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
**Description**: Heal input validation violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (pii, injection, bias, format)
                - input: Input that caused the violation
                - severity: Severity level

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: __post_init__

**Parameters**: self


## Function: _detect_pii

**Parameters**: self, text
**Returns**: dict[str, Any]
**Description**: Detect personally identifiable information.



## Function: _detect_prompt_injection

**Parameters**: self, text
**Returns**: dict[str, Any]
**Description**: Detect prompt injection attempts.



## Function: _detect_bias

**Parameters**: self, text
**Returns**: dict[str, Any]
**Description**: Detect biased language patterns.



## Function: _validate_format

**Parameters**: self, text
**Returns**: dict[str, Any]
**Description**: Validate input format.



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
**Description**: Heal input validation violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (pii, injection, bias, format)
                - input: Input that caused the violation
                - severity: Severity level

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using InputValidationGuardrail
inputvalidationguardrail = InputValidationGuardrail()
inputvalidationguardrail.heal_repository()
inputvalidationguardrail.heal()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _detect_pii
result = _detect_pii(text)
```

```python
# Using _detect_prompt_injection
result = _detect_prompt_injection(text)
```



---
**Generated**: 2026-03-26T09:39:04.863101
**Type**: api_reference
**Quality**: comprehensive
