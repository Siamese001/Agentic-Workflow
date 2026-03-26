# API Documentation: specificity_prose_types

**Target Audience**: developers, api_users

# specificity_prose_types API Documentation

**File**: `specificity_prose_types.py`
**Classes**: 4
**Functions**: 9

## Classes

- **SpecificityProseConfig**
- **CompanySpecificDetail**
- **SpecificityProseResult**
- **SpecificityProseEngine**

## Functions

- **create_specificity_prose_engine** -> SpecificityProseEngine
- **__init__**
- **generate_cover_letter** -> SpecificityProseResult
- **_generate_content** -> str
- **_split_paragraphs** -> list[str]
- **_validate_paragraph_structure** -> ValidationResult
- **_extract_company_specifics** -> list[CompanySpecificDetail]
- **_validate_company_specifics** -> ValidationResult
- **_execute_find_replace_test** -> bool


## Class: SpecificityProseConfig

**Description**: Docstring.



## Class: CompanySpecificDetail

**Description**: Docstring.



## Class: SpecificityProseResult

**Description**: Docstring.



## Class: SpecificityProseEngine

**Description**: 
    K.10 - Cover Letter Generator

    Specificity Constraints:
    - 3 Paragraphs @ 85-100 words per paragraph
    - MUST INCLUDE ≥4 company-specific details
    - Details must pass find-replace test (not generic)
    

### Methods

#### __init__
**Parameters**: self, config, gate_executor, recovery_loop

#### generate_cover_letter
**Parameters**: self, company_research, resume_highlights, context
**Returns**: SpecificityProseResult
**Description**: 
        Generate cover letter with company-specific details.

        Args:
            company_research: Research data about target company
            resume_highlights: Key achievements from resume
            context: Additional context (JD, role, etc.)

        Returns:
            SpecificityProseResult with cover letter and validation details
        

#### _generate_content
**Parameters**: self, company_research, resume_highlights, context, temperature, attempt
**Returns**: str
**Description**: 
        Generate cover letter content using LLM.
        Placeholder for actual LLM integration.
        

#### _split_paragraphs
**Parameters**: self, text
**Returns**: list[str]
**Description**: Split text into paragraphs

#### _validate_paragraph_structure
**Parameters**: self, paragraphs
**Returns**: ValidationResult
**Description**: 
        Validate paragraph count and word counts.
        BLOCKS if structure is invalid.
        

#### _extract_company_specifics
**Parameters**: self, cover_letter, company_research
**Returns**: list[CompanySpecificDetail]
**Description**: Extract company-specific details from cover letter

#### _validate_company_specifics
**Parameters**: self, company_specifics
**Returns**: ValidationResult
**Description**: 
        Validate ≥4 company-specific details present.
        BLOCKS if insufficient specifics.
        

#### _execute_find_replace_test
**Parameters**: self, cover_letter, company_specifics
**Returns**: bool
**Description**: 
        Execute find-replace test - letter should break if specifics removed.
        Returns True if test passes (letter is truly specific).
        



## Function: create_specificity_prose_engine

**Parameters**: config
**Returns**: SpecificityProseEngine
**Description**: Factory function to create SpecificityProseEngine instance



## Function: __init__

**Parameters**: self, config, gate_executor, recovery_loop


## Function: generate_cover_letter

**Parameters**: self, company_research, resume_highlights, context
**Returns**: SpecificityProseResult
**Description**: 
        Generate cover letter with company-specific details.

        Args:
            company_research: Research data about target company
            resume_highlights: Key achievements from resume
            context: Additional context (JD, role, etc.)

        Returns:
            SpecificityProseResult with cover letter and validation details
        



## Function: _generate_content

**Parameters**: self, company_research, resume_highlights, context, temperature, attempt
**Returns**: str
**Description**: 
        Generate cover letter content using LLM.
        Placeholder for actual LLM integration.
        



## Function: _split_paragraphs

**Parameters**: self, text
**Returns**: list[str]
**Description**: Split text into paragraphs



## Function: _validate_paragraph_structure

**Parameters**: self, paragraphs
**Returns**: ValidationResult
**Description**: 
        Validate paragraph count and word counts.
        BLOCKS if structure is invalid.
        



## Function: _extract_company_specifics

**Parameters**: self, cover_letter, company_research
**Returns**: list[CompanySpecificDetail]
**Description**: Extract company-specific details from cover letter



## Function: _validate_company_specifics

**Parameters**: self, company_specifics
**Returns**: ValidationResult
**Description**: 
        Validate ≥4 company-specific details present.
        BLOCKS if insufficient specifics.
        



## Function: _execute_find_replace_test

**Parameters**: self, cover_letter, company_specifics
**Returns**: bool
**Description**: 
        Execute find-replace test - letter should break if specifics removed.
        Returns True if test passes (letter is truly specific).
        



## Usage Examples

### Class Usage

```python
# Using SpecificityProseConfig
specificityproseconfig = SpecificityProseConfig()
```

```python
# Using CompanySpecificDetail
companyspecificdetail = CompanySpecificDetail()
```

```python
# Using SpecificityProseResult
specificityproseresult = SpecificityProseResult()
```

### Function Usage

```python
# Using create_specificity_prose_engine
result = create_specificity_prose_engine(config)
```

```python
# Using __init__
result = __init__(config, gate_executor)
```

```python
# Using generate_cover_letter
result = generate_cover_letter(company_research, resume_highlights)
```



---
**Generated**: 2026-03-26T09:39:05.577917
**Type**: api_reference
**Quality**: comprehensive
