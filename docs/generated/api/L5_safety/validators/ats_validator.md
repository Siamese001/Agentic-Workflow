# API Documentation: ats_validator

**Target Audience**: developers, api_users

# ats_validator API Documentation

**File**: `ats_validator.py`
**Classes**: 2
**Functions**: 9

## Classes

- **ATSValidationResult**
- **AtsValidator**

## Functions

- **__post_init__** -> None
- **__init__** -> None
- **validate_ats_compatibility** -> ATSValidationResult
- **_check_ats_unfriendly_patterns** -> list[str]
- **_validate_section_headers** -> list[str]
- **calculate_keyword_score** -> float
- **normalize_text** -> str
- **extract_keywords** -> set[str]
- **validate_formatting** -> list[str]


## Class: ATSValidationResult

**Description**: Result of ATS validation with deterministic scoring.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: AtsValidator

**Description**: 
    Pure deterministic ATS validation logic.

    All methods in this class are 100% deterministic and can be
    executed without external dependencies or LLM calls.
    

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: 
        Initialize with ATS validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        

#### validate_ats_compatibility
**Parameters**: self, resume, job_desc
**Returns**: ATSValidationResult
**Description**: 
        Validate ATS compatibility using purely deterministic logic.

        Args:
            resume: Resume data dictionary
            job_desc: Optional job description for keyword scoring

        Returns:
            ATSValidationResult with deterministic findings
        

#### _check_ats_unfriendly_patterns
**Parameters**: self, resume
**Returns**: list[str]
**Description**: 
        Check for ATS-unfriendly patterns using deterministic regex.

        Moved to Deterministic: Pure pattern matching logic
        

#### _validate_section_headers
**Parameters**: self, resume
**Returns**: list[str]
**Description**: 
        Validate section headers using deterministic string comparison.

        Moved to Deterministic: Pure string validation logic
        

#### calculate_keyword_score
**Parameters**: self, resume, job_desc
**Returns**: float
**Description**: 
        Calculate keyword match score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical calculation
        

#### normalize_text
**Parameters**: self, text
**Returns**: str
**Description**: 
        Normalize text for consistent processing.

        Moved to Deterministic: Pure string manipulation
        

#### extract_keywords
**Parameters**: self, text, min_length
**Returns**: set[str]
**Description**: 
        Extract keywords from text using deterministic regex.

        Moved to Deterministic: Pure pattern extraction
        

#### validate_formatting
**Parameters**: self, content
**Returns**: list[str]
**Description**: 
        Validate content formatting using deterministic rules.

        Moved to Deterministic: Pure formatting validation
        



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: 
        Initialize with ATS validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        



## Function: validate_ats_compatibility

**Parameters**: self, resume, job_desc
**Returns**: ATSValidationResult
**Description**: 
        Validate ATS compatibility using purely deterministic logic.

        Args:
            resume: Resume data dictionary
            job_desc: Optional job description for keyword scoring

        Returns:
            ATSValidationResult with deterministic findings
        



## Function: _check_ats_unfriendly_patterns

**Parameters**: self, resume
**Returns**: list[str]
**Description**: 
        Check for ATS-unfriendly patterns using deterministic regex.

        Moved to Deterministic: Pure pattern matching logic
        



## Function: _validate_section_headers

**Parameters**: self, resume
**Returns**: list[str]
**Description**: 
        Validate section headers using deterministic string comparison.

        Moved to Deterministic: Pure string validation logic
        



## Function: calculate_keyword_score

**Parameters**: self, resume, job_desc
**Returns**: float
**Description**: 
        Calculate keyword match score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical calculation
        



## Function: normalize_text

**Parameters**: self, text
**Returns**: str
**Description**: 
        Normalize text for consistent processing.

        Moved to Deterministic: Pure string manipulation
        



## Function: extract_keywords

**Parameters**: self, text, min_length
**Returns**: set[str]
**Description**: 
        Extract keywords from text using deterministic regex.

        Moved to Deterministic: Pure pattern extraction
        



## Function: validate_formatting

**Parameters**: self, content
**Returns**: list[str]
**Description**: 
        Validate content formatting using deterministic rules.

        Moved to Deterministic: Pure formatting validation
        



## Usage Examples

### Class Usage

```python
# Using ATSValidationResult
atsvalidationresult = ATSValidationResult()
```

```python
# Using AtsValidator
atsvalidator = AtsValidator()
atsvalidator.validate_ats_compatibility()
atsvalidator.calculate_keyword_score()
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
# Using validate_ats_compatibility
result = validate_ats_compatibility(resume, job_desc)
```



---
**Generated**: 2026-03-26T09:39:05.738294
**Type**: api_reference
**Quality**: comprehensive
