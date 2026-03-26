# API Documentation: validation_result_types

**Target Audience**: developers, api_users

# validation_result_types API Documentation

**File**: `validation_result_types.py`
**Classes**: 5
**Functions**: 11

## Classes

- **ValidationResult**
- **AdaptiveRecoveryLoop**
- **TitleComposerConfig**
- **TitleComposerResult**
- **executive_title_composer**

## Functions

- **create_executive_title_composer** -> executive_title_composer
- **__init__** -> None
- **__init__** -> None
- **reset**
- **record_failure**
- **get_temperature_log**
- **__init__**
- **generate_headline** -> TitleComposerResult
- **_generate_content** -> str
- **_validate_length** -> ValidationResult
- **_validate_not_tech_first** -> ValidationResult


## Class: ValidationResult

**Description**: Brief description of functionality and purpose.

### Methods

#### __init__
**Parameters**: self, gate_id, PASSED, SEVERITY, MESSAGE, DETAILS, SIGNATURE
**Returns**: None



## Class: AdaptiveRecoveryLoop

**Description**: Brief description of functionality and purpose.

### Methods

#### __init__
**Parameters**: self, initial_temperature
**Returns**: None

#### reset
**Parameters**: self, temperature

#### record_failure
**Parameters**: self, gate_id, MESSAGE, DETAILS

#### get_temperature_log
**Parameters**: self



## Class: TitleComposerConfig

**Description**: TODO: Add docstring.



## Class: TitleComposerResult

**Description**: Docstring.



## Class: executive_title_composer

**Description**: 
    K.4 - Headline Generator

    Industry-First Constraint:
    - Segment 1 MUST be Industry/Sector (e.g., "FinTech")
    - BLOCK if Segment 1 is Technology (e.g., "AI", "Cloud", "Data")
    - Limits: 8-13 words total, ≤90 chars
    

### Methods

#### __init__
**Parameters**: self, config, gate_executor, recovery_loop

#### generate_headline
**Parameters**: self, context
**Returns**: TitleComposerResult
**Description**: 
        Generate headline with industry-first validation.

        Args:
            context: Context including industry, role, skills

        Returns:
            TitleComposerResult with headline and validation details
        

#### _generate_content
**Parameters**: self, context, temperature, attempt
**Returns**: str
**Description**: 
        Generate headline content using LLM.
        Placeholder for actual LLM integration.
        

#### _validate_length
**Parameters**: self, headline, word_count, char_count
**Returns**: ValidationResult
**Description**: 
        Validate headline length constraints.
        BLOCKS if outside word/char limits.
        

#### _validate_not_tech_first
**Parameters**: self, segments
**Returns**: ValidationResult
**Description**: 
        Validate first segment is not a technology keyword.
        BLOCKS if technology-first detected.
        



## Function: create_executive_title_composer

**Parameters**: config
**Returns**: executive_title_composer
**Description**: Factory function to create executive_title_composer instance



## Function: __init__

**Parameters**: self, gate_id, PASSED, SEVERITY, MESSAGE, DETAILS, SIGNATURE
**Returns**: None


## Function: __init__

**Parameters**: self, initial_temperature
**Returns**: None


## Function: reset

**Parameters**: self, temperature


## Function: record_failure

**Parameters**: self, gate_id, MESSAGE, DETAILS


## Function: get_temperature_log

**Parameters**: self


## Function: __init__

**Parameters**: self, config, gate_executor, recovery_loop


## Function: generate_headline

**Parameters**: self, context
**Returns**: TitleComposerResult
**Description**: 
        Generate headline with industry-first validation.

        Args:
            context: Context including industry, role, skills

        Returns:
            TitleComposerResult with headline and validation details
        



## Function: _generate_content

**Parameters**: self, context, temperature, attempt
**Returns**: str
**Description**: 
        Generate headline content using LLM.
        Placeholder for actual LLM integration.
        



## Function: _validate_length

**Parameters**: self, headline, word_count, char_count
**Returns**: ValidationResult
**Description**: 
        Validate headline length constraints.
        BLOCKS if outside word/char limits.
        



## Function: _validate_not_tech_first

**Parameters**: self, segments
**Returns**: ValidationResult
**Description**: 
        Validate first segment is not a technology keyword.
        BLOCKS if technology-first detected.
        



## Usage Examples

### Class Usage

```python
# Using ValidationResult
validationresult = ValidationResult()
```

```python
# Using AdaptiveRecoveryLoop
adaptiverecoveryloop = AdaptiveRecoveryLoop()
adaptiverecoveryloop.reset()
adaptiverecoveryloop.record_failure()
```

```python
# Using TitleComposerConfig
titlecomposerconfig = TitleComposerConfig()
```

### Function Usage

```python
# Using create_executive_title_composer
result = create_executive_title_composer(config)
```

```python
# Using __init__
result = __init__(gate_id, PASSED)
```

```python
# Using __init__
result = __init__(initial_temperature)
```



---
**Generated**: 2026-03-26T09:39:05.594265
**Type**: api_reference
**Quality**: comprehensive
