# API Documentation: content_quality_validator

**Target Audience**: developers, api_users

# content_quality_validator API Documentation

**File**: `content_quality_validator.py`
**Classes**: 2
**Functions**: 10

## Classes

- **QualityValidationResult**
- **ContentQualityValidator**

## Functions

- **__post_init__** -> None
- **__init__** -> None
- **validate_content_quality** -> QualityValidationResult
- **_check_placeholders** -> list[str]
- **_check_quantified_achievements** -> list[str]
- **_validate_skills** -> tuple[list[str], list[str]]
- **_calculate_skill_alignment** -> float
- **_calculate_quality_score** -> float
- **extract_resume_text** -> str
- **detect_formatting_issues** -> list[str]


## Class: QualityValidationResult

**Description**: Result of content quality validation.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: ContentQualityValidator

**Description**: 
    Pure deterministic content quality validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: 
        Initialize with content quality validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        

#### validate_content_quality
**Parameters**: self, resume, job_desc
**Returns**: QualityValidationResult
**Description**: 
        Validate content quality using purely deterministic logic.

        Args:
            resume: Resume data dictionary
            job_desc: Optional job description for skill matching

        Returns:
            QualityValidationResult with deterministic findings
        

#### _check_placeholders
**Parameters**: self, resume
**Returns**: list[str]
**Description**: 
        Check for placeholder text using deterministic regex patterns.

        Moved to Deterministic: Pure pattern matching logic
        

#### _check_quantified_achievements
**Parameters**: self, resume
**Returns**: list[str]
**Description**: 
        Check for quantified achievements using deterministic patterns.

        Moved to Deterministic: Pure pattern matching logic
        

#### _validate_skills
**Parameters**: self, resume, job_desc
**Returns**: tuple[list[str], list[str]]
**Description**: 
        Validate skills using deterministic rule-based logic.

        Moved to Deterministic: Pure string matching and validation
        

#### _calculate_skill_alignment
**Parameters**: self, skills, job_desc
**Returns**: float
**Description**: 
        Calculate skill alignment using deterministic text analysis.

        Moved to Deterministic: Pure text processing and calculation
        

#### _calculate_quality_score
**Parameters**: self, issues, resume
**Returns**: float
**Description**: 
        Calculate overall quality score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical scoring
        

#### extract_resume_text
**Parameters**: self, resume
**Returns**: str
**Description**: 
        Extract and normalize resume text for processing.

        Moved to Deterministic: Pure text extraction and normalization
        

#### detect_formatting_issues
**Parameters**: self, text
**Returns**: list[str]
**Description**: 
        Detect formatting issues using deterministic rules.

        Moved to Deterministic: Pure formatting validation
        



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: 
        Initialize with content quality validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        



## Function: validate_content_quality

**Parameters**: self, resume, job_desc
**Returns**: QualityValidationResult
**Description**: 
        Validate content quality using purely deterministic logic.

        Args:
            resume: Resume data dictionary
            job_desc: Optional job description for skill matching

        Returns:
            QualityValidationResult with deterministic findings
        



## Function: _check_placeholders

**Parameters**: self, resume
**Returns**: list[str]
**Description**: 
        Check for placeholder text using deterministic regex patterns.

        Moved to Deterministic: Pure pattern matching logic
        



## Function: _check_quantified_achievements

**Parameters**: self, resume
**Returns**: list[str]
**Description**: 
        Check for quantified achievements using deterministic patterns.

        Moved to Deterministic: Pure pattern matching logic
        



## Function: _validate_skills

**Parameters**: self, resume, job_desc
**Returns**: tuple[list[str], list[str]]
**Description**: 
        Validate skills using deterministic rule-based logic.

        Moved to Deterministic: Pure string matching and validation
        



## Function: _calculate_skill_alignment

**Parameters**: self, skills, job_desc
**Returns**: float
**Description**: 
        Calculate skill alignment using deterministic text analysis.

        Moved to Deterministic: Pure text processing and calculation
        



## Function: _calculate_quality_score

**Parameters**: self, issues, resume
**Returns**: float
**Description**: 
        Calculate overall quality score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical scoring
        



## Function: extract_resume_text

**Parameters**: self, resume
**Returns**: str
**Description**: 
        Extract and normalize resume text for processing.

        Moved to Deterministic: Pure text extraction and normalization
        



## Function: detect_formatting_issues

**Parameters**: self, text
**Returns**: list[str]
**Description**: 
        Detect formatting issues using deterministic rules.

        Moved to Deterministic: Pure formatting validation
        



## Usage Examples

### Class Usage

```python
# Using QualityValidationResult
qualityvalidationresult = QualityValidationResult()
```

```python
# Using ContentQualityValidator
contentqualityvalidator = ContentQualityValidator()
contentqualityvalidator.validate_content_quality()
contentqualityvalidator.extract_resume_text()
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
# Using validate_content_quality
result = validate_content_quality(resume, job_desc)
```



---
**Generated**: 2026-03-26T09:39:05.764944
**Type**: api_reference
**Quality**: comprehensive
