# API Documentation: lead_quality_validator

**Target Audience**: developers, api_users

# lead_quality_validator API Documentation

**File**: `lead_quality_validator.py`
**Classes**: 2
**Functions**: 11

## Classes

- **LeadQualityResult**
- **LeadQualityValidator**

## Functions

- **__post_init__** -> None
- **__init__** -> None
- **validate_lead_quality** -> LeadQualityResult
- **_check_required_fields** -> list[str]
- **_check_contact_info** -> list[str]
- **_check_email_domain** -> list[str]
- **_check_spam_indicators** -> list[str]
- **_calculate_quality_score** -> float
- **validate_single_lead** -> LeadQualityResult
- **get_lead_completeness** -> float
- **analyze_lead_risk** -> dict[str, Any]


## Class: LeadQualityResult

**Description**: Result of lead quality validation.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: LeadQualityValidator

**Description**: 
    Pure deterministic lead quality validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: 
        Initialize with lead quality validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        

#### validate_lead_quality
**Parameters**: self, leads
**Returns**: LeadQualityResult
**Description**: 
        Validate lead quality using purely deterministic logic.

        Args:
            leads: List of lead dictionaries

        Returns:
            LeadQualityResult with deterministic findings
        

#### _check_required_fields
**Parameters**: self, lead, lead_index
**Returns**: list[str]
**Description**: 
        Check required fields using deterministic existence checks.

        Moved to Deterministic: Pure field existence validation
        

#### _check_contact_info
**Parameters**: self, lead, lead_index
**Returns**: list[str]
**Description**: 
        Check contact information using deterministic field presence.

        Moved to Deterministic: Pure field presence validation
        

#### _check_email_domain
**Parameters**: self, lead, lead_index
**Returns**: list[str]
**Description**: 
        Check email domain using deterministic pattern matching.

        Moved to Deterministic: Pure domain validation
        

#### _check_spam_indicators
**Parameters**: self, lead, lead_index
**Returns**: list[str]
**Description**: 
        Check spam indicators using deterministic keyword matching.

        Moved to Deterministic: Pure keyword matching
        

#### _calculate_quality_score
**Parameters**: self, issues, lead_count
**Returns**: float
**Description**: 
        Calculate quality score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical scoring
        

#### validate_single_lead
**Parameters**: self, lead
**Returns**: LeadQualityResult
**Description**: 
        Validate a single lead for quality issues.

        Convenience method for single lead validation.
        

#### get_lead_completeness
**Parameters**: self, lead
**Returns**: float
**Description**: 
        Calculate lead completeness score.

        Moved to Deterministic: Pure completeness calculation
        

#### analyze_lead_risk
**Parameters**: self, lead
**Returns**: dict[str, Any]
**Description**: 
        Analyze lead risk using deterministic rules.

        Returns detailed risk analysis for a lead.
        



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: 
        Initialize with lead quality validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        



## Function: validate_lead_quality

**Parameters**: self, leads
**Returns**: LeadQualityResult
**Description**: 
        Validate lead quality using purely deterministic logic.

        Args:
            leads: List of lead dictionaries

        Returns:
            LeadQualityResult with deterministic findings
        



## Function: _check_required_fields

**Parameters**: self, lead, lead_index
**Returns**: list[str]
**Description**: 
        Check required fields using deterministic existence checks.

        Moved to Deterministic: Pure field existence validation
        



## Function: _check_contact_info

**Parameters**: self, lead, lead_index
**Returns**: list[str]
**Description**: 
        Check contact information using deterministic field presence.

        Moved to Deterministic: Pure field presence validation
        



## Function: _check_email_domain

**Parameters**: self, lead, lead_index
**Returns**: list[str]
**Description**: 
        Check email domain using deterministic pattern matching.

        Moved to Deterministic: Pure domain validation
        



## Function: _check_spam_indicators

**Parameters**: self, lead, lead_index
**Returns**: list[str]
**Description**: 
        Check spam indicators using deterministic keyword matching.

        Moved to Deterministic: Pure keyword matching
        



## Function: _calculate_quality_score

**Parameters**: self, issues, lead_count
**Returns**: float
**Description**: 
        Calculate quality score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical scoring
        



## Function: validate_single_lead

**Parameters**: self, lead
**Returns**: LeadQualityResult
**Description**: 
        Validate a single lead for quality issues.

        Convenience method for single lead validation.
        



## Function: get_lead_completeness

**Parameters**: self, lead
**Returns**: float
**Description**: 
        Calculate lead completeness score.

        Moved to Deterministic: Pure completeness calculation
        



## Function: analyze_lead_risk

**Parameters**: self, lead
**Returns**: dict[str, Any]
**Description**: 
        Analyze lead risk using deterministic rules.

        Returns detailed risk analysis for a lead.
        



## Usage Examples

### Class Usage

```python
# Using LeadQualityResult
leadqualityresult = LeadQualityResult()
```

```python
# Using LeadQualityValidator
leadqualityvalidator = LeadQualityValidator()
leadqualityvalidator.validate_lead_quality()
leadqualityvalidator.validate_single_lead()
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
# Using validate_lead_quality
result = validate_lead_quality(leads)
```



---
**Generated**: 2026-03-26T09:39:05.836019
**Type**: api_reference
**Quality**: comprehensive
