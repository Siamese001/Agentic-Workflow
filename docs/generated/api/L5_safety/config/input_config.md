# API Documentation: input_config

**Target Audience**: developers, api_users

# input_config API Documentation

**File**: `input_config.py`
**Classes**: 1
**Functions**: 8

## Classes

- **InputValidator**

## Functions

- **validate_input** -> bool
- **__init__**
- **add_rule** -> None
- **validate** -> bool
- **sanitize_string** -> str
- **validate_type** -> bool
- **validate_range** -> bool
- **validate_length** -> bool


## Class: InputValidator

**Description**: Validator for input sanitization and validation.

### Methods

#### __init__
**Parameters**: self

#### add_rule
**Parameters**: self, rule
**Returns**: None
**Description**: Add a validation rule.

#### validate
**Parameters**: self, input_data
**Returns**: bool
**Description**: Validate input against all rules.

#### sanitize_string
**Parameters**: self, text
**Returns**: str
**Description**: Sanitize a string input.

#### validate_type
**Parameters**: self, value, expected_type
**Returns**: bool
**Description**: Validate that value is of expected type.

#### validate_range
**Parameters**: self, value, min_val, max_val
**Returns**: bool
**Description**: Validate that value is within range.

#### validate_length
**Parameters**: self, value, min_len, max_len
**Returns**: bool
**Description**: Validate that value length is within bounds.



## Function: validate_input

**Parameters**: data, schema
**Returns**: bool
**Description**: Validate input data against a schema.



## Function: __init__

**Parameters**: self


## Function: add_rule

**Parameters**: self, rule
**Returns**: None
**Description**: Add a validation rule.



## Function: validate

**Parameters**: self, input_data
**Returns**: bool
**Description**: Validate input against all rules.



## Function: sanitize_string

**Parameters**: self, text
**Returns**: str
**Description**: Sanitize a string input.



## Function: validate_type

**Parameters**: self, value, expected_type
**Returns**: bool
**Description**: Validate that value is of expected type.



## Function: validate_range

**Parameters**: self, value, min_val, max_val
**Returns**: bool
**Description**: Validate that value is within range.



## Function: validate_length

**Parameters**: self, value, min_len, max_len
**Returns**: bool
**Description**: Validate that value length is within bounds.



## Usage Examples

### Class Usage

```python
# Using InputValidator
inputvalidator = InputValidator()
inputvalidator.add_rule()
inputvalidator.validate()
```

### Function Usage

```python
# Using validate_input
result = validate_input(data, schema)
```

```python
# Using __init__
result = __init__()
```

```python
# Using add_rule
result = add_rule(rule)
```



---
**Generated**: 2026-03-26T09:39:04.746047
**Type**: api_reference
**Quality**: comprehensive
