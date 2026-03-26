# API Documentation: deliverability_validator

**Target Audience**: developers, api_users

# deliverability_validator API Documentation

**File**: `deliverability_validator.py`
**Classes**: 2
**Functions**: 10

## Classes

- **DeliverabilityResult**
- **DeliverabilityValidator**

## Functions

- **__post_init__** -> None
- **__init__** -> None
- **validate_deliverability** -> DeliverabilityResult
- **_check_spam_triggers** -> list[str]
- **_check_link_count** -> list[str]
- **_check_image_count** -> list[str]
- **_calculate_deliverability_score** -> float
- **check_single_message** -> DeliverabilityResult
- **get_spam_trigger_count** -> int
- **analyze_content_risk** -> dict[str, Any]


## Class: DeliverabilityResult

**Description**: Result of deliverability validation.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: DeliverabilityValidator

**Description**: 
    Pure deterministic deliverability validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: 
        Initialize with deliverability validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        

#### validate_deliverability
**Parameters**: self, messages
**Returns**: DeliverabilityResult
**Description**: 
        Validate deliverability using purely deterministic logic.

        Args:
            messages: List of message dictionaries with 'content' field

        Returns:
            DeliverabilityResult with deterministic findings
        

#### _check_spam_triggers
**Parameters**: self, content, message_index
**Returns**: list[str]
**Description**: 
        Check for spam triggers using deterministic keyword matching.

        Moved to Deterministic: Pure keyword matching logic
        

#### _check_link_count
**Parameters**: self, content, message_index
**Returns**: list[str]
**Description**: 
        Check link count using deterministic counting.

        Moved to Deterministic: Pure counting logic
        

#### _check_image_count
**Parameters**: self, content, message_index
**Returns**: list[str]
**Description**: 
        Check image count using deterministic counting.

        Moved to Deterministic: Pure counting logic
        

#### _calculate_deliverability_score
**Parameters**: self, issues, message_count
**Returns**: float
**Description**: 
        Calculate deliverability score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical scoring
        

#### check_single_message
**Parameters**: self, content
**Returns**: DeliverabilityResult
**Description**: 
        Check a single message for deliverability issues.

        Convenience method for single message validation.
        

#### get_spam_trigger_count
**Parameters**: self, content
**Returns**: int
**Description**: 
        Count spam triggers in content.

        Moved to Deterministic: Pure counting logic
        

#### analyze_content_risk
**Parameters**: self, content
**Returns**: dict[str, Any]
**Description**: 
        Analyze content risk using deterministic rules.

        Returns detailed risk analysis for content.
        



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: 
        Initialize with deliverability validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        



## Function: validate_deliverability

**Parameters**: self, messages
**Returns**: DeliverabilityResult
**Description**: 
        Validate deliverability using purely deterministic logic.

        Args:
            messages: List of message dictionaries with 'content' field

        Returns:
            DeliverabilityResult with deterministic findings
        



## Function: _check_spam_triggers

**Parameters**: self, content, message_index
**Returns**: list[str]
**Description**: 
        Check for spam triggers using deterministic keyword matching.

        Moved to Deterministic: Pure keyword matching logic
        



## Function: _check_link_count

**Parameters**: self, content, message_index
**Returns**: list[str]
**Description**: 
        Check link count using deterministic counting.

        Moved to Deterministic: Pure counting logic
        



## Function: _check_image_count

**Parameters**: self, content, message_index
**Returns**: list[str]
**Description**: 
        Check image count using deterministic counting.

        Moved to Deterministic: Pure counting logic
        



## Function: _calculate_deliverability_score

**Parameters**: self, issues, message_count
**Returns**: float
**Description**: 
        Calculate deliverability score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical scoring
        



## Function: check_single_message

**Parameters**: self, content
**Returns**: DeliverabilityResult
**Description**: 
        Check a single message for deliverability issues.

        Convenience method for single message validation.
        



## Function: get_spam_trigger_count

**Parameters**: self, content
**Returns**: int
**Description**: 
        Count spam triggers in content.

        Moved to Deterministic: Pure counting logic
        



## Function: analyze_content_risk

**Parameters**: self, content
**Returns**: dict[str, Any]
**Description**: 
        Analyze content risk using deterministic rules.

        Returns detailed risk analysis for content.
        



## Usage Examples

### Class Usage

```python
# Using DeliverabilityResult
deliverabilityresult = DeliverabilityResult()
```

```python
# Using DeliverabilityValidator
deliverabilityvalidator = DeliverabilityValidator()
deliverabilityvalidator.validate_deliverability()
deliverabilityvalidator.check_single_message()
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
# Using validate_deliverability
result = validate_deliverability(messages)
```



---
**Generated**: 2026-03-26T09:39:05.775430
**Type**: api_reference
**Quality**: comprehensive
