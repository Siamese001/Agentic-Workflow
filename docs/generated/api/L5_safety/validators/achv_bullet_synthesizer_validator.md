# API Documentation: achv_bullet_synthesizer_validator

**Target Audience**: developers, api_users

# achv_bullet_synthesizer_validator API Documentation

**File**: `achv_bullet_synthesizer_validator.py`
**Classes**: 1
**Functions**: 8

## Classes

- **AchvBulletSynthesizer**

## Functions

- **create_achv_bullet_synthesizer** -> AchvBulletSynthesizer
- **__init__**
- **generate_bullets** -> BulletSynthesizerResult
- **_generate_bullet_set** -> list[str]
- **_validate_bullet_word_count** -> ValidationResult
- **_analyze_provenance** -> BulletProvenanceLog
- **_validate_provenance_pattern** -> ValidationResult
- **_generate_qa_report** -> dict[str, Any]


## Class: AchvBulletSynthesizer

**Description**: 
    K.5A & K.6A - Achievement Bullet Generator with Provenance

    Zero Tolerance Constraints:
    - K.5A (Unify): 3V-3T-1S pattern, 28-33 words each, 7 bullets
    - K.6A (IBM): 2V-3T-1S pattern, 24-30 words each, 6 bullets
    - VG_BULLET_PROVENANCE_CHECK BLOCKS if pattern invalid
    

### Methods

#### __init__
**Parameters**: self, config, gate_executor, recovery_loop

#### generate_bullets
**Parameters**: self, experience_data, context
**Returns**: BulletSynthesizerResult
**Description**: 
        Generate achievement bullets with provenance tracking.

        Args:
            experience_data: Raw experience data for bullet generation
            context: Additional context (JD, industry, etc.)

        Returns:
            BulletSynthesizerResult with bullets and provenance logs
        

#### _generate_bullet_set
**Parameters**: self, experience_data, context, temperature, attempt
**Returns**: list[str]
**Description**: 
        Generate set of bullets using LLM.
        Placeholder for actual LLM integration.
        

#### _validate_bullet_word_count
**Parameters**: self, bullet, bullet_num
**Returns**: ValidationResult
**Description**: 
        Validate bullet word count is within range.
        BLOCKS if outside min-max range.
        

#### _analyze_provenance
**Parameters**: self, bullet
**Returns**: BulletProvenanceLog
**Description**: 
        Analyze bullet for provenance items (Verbs, Tech, Soft).
        Returns provenance log with categorized items.
        

#### _validate_provenance_pattern
**Parameters**: self, provenance_log, bullet_num
**Returns**: ValidationResult
**Description**: 
        Validate provenance pattern matches expected pattern.
        BLOCKS if pattern is invalid.
        

#### _generate_qa_report
**Parameters**: self, bullets, provenance_logs
**Returns**: dict[str, Any]
**Description**: Generate QA Report with provenance tracking



## Function: create_achv_bullet_synthesizer

**Parameters**: config
**Returns**: AchvBulletSynthesizer
**Description**: Factory function to create AchvBulletSynthesizer instance



## Function: __init__

**Parameters**: self, config, gate_executor, recovery_loop


## Function: generate_bullets

**Parameters**: self, experience_data, context
**Returns**: BulletSynthesizerResult
**Description**: 
        Generate achievement bullets with provenance tracking.

        Args:
            experience_data: Raw experience data for bullet generation
            context: Additional context (JD, industry, etc.)

        Returns:
            BulletSynthesizerResult with bullets and provenance logs
        



## Function: _generate_bullet_set

**Parameters**: self, experience_data, context, temperature, attempt
**Returns**: list[str]
**Description**: 
        Generate set of bullets using LLM.
        Placeholder for actual LLM integration.
        



## Function: _validate_bullet_word_count

**Parameters**: self, bullet, bullet_num
**Returns**: ValidationResult
**Description**: 
        Validate bullet word count is within range.
        BLOCKS if outside min-max range.
        



## Function: _analyze_provenance

**Parameters**: self, bullet
**Returns**: BulletProvenanceLog
**Description**: 
        Analyze bullet for provenance items (Verbs, Tech, Soft).
        Returns provenance log with categorized items.
        



## Function: _validate_provenance_pattern

**Parameters**: self, provenance_log, bullet_num
**Returns**: ValidationResult
**Description**: 
        Validate provenance pattern matches expected pattern.
        BLOCKS if pattern is invalid.
        



## Function: _generate_qa_report

**Parameters**: self, bullets, provenance_logs
**Returns**: dict[str, Any]
**Description**: Generate QA Report with provenance tracking



## Usage Examples

### Class Usage

```python
# Using AchvBulletSynthesizer
achvbulletsynthesizer = AchvBulletSynthesizer()
achvbulletsynthesizer.generate_bullets()
```

### Function Usage

```python
# Using create_achv_bullet_synthesizer
result = create_achv_bullet_synthesizer(config)
```

```python
# Using __init__
result = __init__(config, gate_executor)
```

```python
# Using generate_bullets
result = generate_bullets(experience_data, context)
```



---
**Generated**: 2026-03-26T09:39:05.726739
**Type**: api_reference
**Quality**: comprehensive
