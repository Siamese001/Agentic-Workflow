# API Documentation: strategist_bio_writer_config

**Target Audience**: developers, api_users

# strategist_bio_writer_config API Documentation

**File**: `strategist_bio_writer_config.py`
**Classes**: 3
**Functions**: 6

## Classes

- **BioWriterConfig**
- **BioWriterResult**
- **StrategistBioWriter**

## Functions

- **create_strategist_biowriter** -> StrategistBioWriter
- **__init__**
- **generate_summary** -> BioWriterResult
- **_generate_content** -> str
- **_build_prompt** -> str
- **_validate_voice** -> ValidationResult


## Class: BioWriterConfig

**Description**: TODO: Add docstring.



## Class: BioWriterResult

**Description**: Docstring.



## Class: StrategistBioWriter

**Description**: 
    K.1 - Executive Summary Generator

    Zero Tolerance Constraints:
    - Length: Strict 118-135 words
    - Voice: Third-Person Implied ONLY (block I/My/We)
    - Grounding: All claims must exist in Bullet_Pool
    

### Methods

#### __init__
**Parameters**: self, config, gate_executor, recovery_loop

#### generate_summary
**Parameters**: self, bullet_pool, context
**Returns**: BioWriterResult
**Description**: 
        Generate executive summary with validation loop.

        Args:
            bullet_pool: List of achievement bullets for grounding
            context: Additional context (JD, industry, etc.)

        Returns:
            BioWriterResult with summary and validation details
        

#### _generate_content
**Parameters**: self, bullet_pool, context, temperature, attempt
**Returns**: str
**Description**: 
        Generate summary content using LLM.
        This is a placeholder - actual implementation would call LLM.
        

#### _build_prompt
**Parameters**: self, bullet_pool, context, attempt
**Returns**: str
**Description**: Build prompt for summary generation

#### _validate_voice
**Parameters**: self, content
**Returns**: ValidationResult
**Description**: 
        Validate third-person voice constraint.
        BLOCKS if first-person pronouns detected.
        



## Function: create_strategist_biowriter

**Parameters**: config
**Returns**: StrategistBioWriter
**Description**: Factory function to create StrategistBioWriter instance



## Function: __init__

**Parameters**: self, config, gate_executor, recovery_loop


## Function: generate_summary

**Parameters**: self, bullet_pool, context
**Returns**: BioWriterResult
**Description**: 
        Generate executive summary with validation loop.

        Args:
            bullet_pool: List of achievement bullets for grounding
            context: Additional context (JD, industry, etc.)

        Returns:
            BioWriterResult with summary and validation details
        



## Function: _generate_content

**Parameters**: self, bullet_pool, context, temperature, attempt
**Returns**: str
**Description**: 
        Generate summary content using LLM.
        This is a placeholder - actual implementation would call LLM.
        



## Function: _build_prompt

**Parameters**: self, bullet_pool, context, attempt
**Returns**: str
**Description**: Build prompt for summary generation



## Function: _validate_voice

**Parameters**: self, content
**Returns**: ValidationResult
**Description**: 
        Validate third-person voice constraint.
        BLOCKS if first-person pronouns detected.
        



## Usage Examples

### Class Usage

```python
# Using BioWriterConfig
biowriterconfig = BioWriterConfig()
```

```python
# Using BioWriterResult
biowriterresult = BioWriterResult()
```

```python
# Using StrategistBioWriter
strategistbiowriter = StrategistBioWriter()
strategistbiowriter.generate_summary()
```

### Function Usage

```python
# Using create_strategist_biowriter
result = create_strategist_biowriter(config)
```

```python
# Using __init__
result = __init__(config, gate_executor)
```

```python
# Using generate_summary
result = generate_summary(bullet_pool, context)
```



---
**Generated**: 2026-03-26T09:39:03.631496
**Type**: api_reference
**Quality**: comprehensive
