# API Documentation: data_enforcer

**Target Audience**: developers, api_users

# data_enforcer API Documentation

**File**: `data_enforcer.py`
**Classes**: 1
**Functions**: 11

## Classes

- **DataValidator**

## Functions

- **main**
- **__init__**
- **validate_all** -> bool
- **check_base_agent_uniqueness**
- **check_layer_consistency**
- **check_path_integrity**
- **check_metric_sanity**
- **check_inheritance_patterns**
- **check_naming_conventions**
- **check_data_completeness**
- **print_summary**


## Class: DataValidator

**Description**: Comprehensive data validator.

### Methods

#### __init__
**Parameters**: self, data

#### validate_all
**Parameters**: self
**Returns**: bool
**Description**: Run all validation checks.

#### check_base_agent_uniqueness
**Parameters**: self
**Description**: Validate each layer has exactly 1 base agent.

#### check_layer_consistency
**Parameters**: self
**Description**: Validate agents are in correct layer directories.

#### check_path_integrity
**Parameters**: self
**Description**: Validate all paths exist and no duplicates.

#### check_metric_sanity
**Parameters**: self
**Description**: Validate metrics are within reasonable ranges.

#### check_inheritance_patterns
**Parameters**: self
**Description**: Validate inheritance makes sense.

#### check_naming_conventions
**Parameters**: self
**Description**: Validate agent naming follows conventions.

#### check_data_completeness
**Parameters**: self
**Description**: Validate required fields are present.

#### print_summary
**Parameters**: self
**Description**: Print validation summary.



## Function: main

**Description**: Main entry point.



## Function: __init__

**Parameters**: self, data


## Function: validate_all

**Parameters**: self
**Returns**: bool
**Description**: Run all validation checks.



## Function: check_base_agent_uniqueness

**Parameters**: self
**Description**: Validate each layer has exactly 1 base agent.



## Function: check_layer_consistency

**Parameters**: self
**Description**: Validate agents are in correct layer directories.



## Function: check_path_integrity

**Parameters**: self
**Description**: Validate all paths exist and no duplicates.



## Function: check_metric_sanity

**Parameters**: self
**Description**: Validate metrics are within reasonable ranges.



## Function: check_inheritance_patterns

**Parameters**: self
**Description**: Validate inheritance makes sense.



## Function: check_naming_conventions

**Parameters**: self
**Description**: Validate agent naming follows conventions.



## Function: check_data_completeness

**Parameters**: self
**Description**: Validate required fields are present.



## Function: print_summary

**Parameters**: self
**Description**: Print validation summary.



## Usage Examples

### Class Usage

```python
# Using DataValidator
datavalidator = DataValidator()
datavalidator.validate_all()
datavalidator.check_base_agent_uniqueness()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using __init__
result = __init__(data)
```

```python
# Using validate_all
result = validate_all()
```



---
**Generated**: 2026-03-26T09:39:04.805266
**Type**: api_reference
**Quality**: comprehensive
