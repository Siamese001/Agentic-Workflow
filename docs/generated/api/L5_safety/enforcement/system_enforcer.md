# API Documentation: system_enforcer

**Target Audience**: developers, api_users

# system_enforcer API Documentation

**File**: `system_enforcer.py`
**Classes**: 3
**Functions**: 12

## Classes

- **ValidationResult**
- **ValidationReport**
- **SystemValidator**

## Functions

- **main**
- **add_result**
- **__init__**
- **load_discovery** -> list[dict]
- **check_has_healing** -> bool
- **check_has_testing** -> bool
- **check_external_touch** -> bool
- **check_mcp_hardened** -> bool
- **validate_syntax** -> str | None
- **validate_agent** -> ValidationResult
- **run_validation** -> ValidationReport
- **print_report**


## Class: ValidationResult

**Description**: Tracks validation results for an agent.



## Class: ValidationReport

**Description**: Aggregated validation report.

### Methods

#### add_result
**Parameters**: self, result



## Class: SystemValidator

**Description**: Full system validation for sovereignty verification.

### Methods

#### __init__
**Parameters**: self, project_root

#### load_discovery
**Parameters**: self
**Returns**: list[dict]
**Description**: Load agent discovery JSON.

#### check_has_healing
**Parameters**: self, code
**Returns**: bool
**Description**: Check if code contains HealerMixin inheritance.

#### check_has_testing
**Parameters**: self, code
**Returns**: bool
**Description**: Check if code contains self-testing methods.

#### check_external_touch
**Parameters**: self, code
**Returns**: bool
**Description**: Check if code touches external resources.

#### check_mcp_hardened
**Parameters**: self, code
**Returns**: bool
**Description**: Check if code has MCPHardenedMixin.

#### validate_syntax
**Parameters**: self, file_path
**Returns**: str | None
**Description**: Check file for syntax errors.

#### validate_agent
**Parameters**: self, agent
**Returns**: ValidationResult
**Description**: Validate a single agent using discovery JSON data.

#### run_validation
**Parameters**: self
**Returns**: ValidationReport
**Description**: Run full system validation.

#### print_report
**Parameters**: self
**Description**: Print validation report.



## Function: main

**Description**: Main entry point.



## Function: add_result

**Parameters**: self, result


## Function: __init__

**Parameters**: self, project_root


## Function: load_discovery

**Parameters**: self
**Returns**: list[dict]
**Description**: Load agent discovery JSON.



## Function: check_has_healing

**Parameters**: self, code
**Returns**: bool
**Description**: Check if code contains HealerMixin inheritance.



## Function: check_has_testing

**Parameters**: self, code
**Returns**: bool
**Description**: Check if code contains self-testing methods.



## Function: check_external_touch

**Parameters**: self, code
**Returns**: bool
**Description**: Check if code touches external resources.



## Function: check_mcp_hardened

**Parameters**: self, code
**Returns**: bool
**Description**: Check if code has MCPHardenedMixin.



## Function: validate_syntax

**Parameters**: self, file_path
**Returns**: str | None
**Description**: Check file for syntax errors.



## Function: validate_agent

**Parameters**: self, agent
**Returns**: ValidationResult
**Description**: Validate a single agent using discovery JSON data.



## Function: run_validation

**Parameters**: self
**Returns**: ValidationReport
**Description**: Run full system validation.



## Function: print_report

**Parameters**: self
**Description**: Print validation report.



## Usage Examples

### Class Usage

```python
# Using ValidationResult
validationresult = ValidationResult()
```

```python
# Using ValidationReport
validationreport = ValidationReport()
validationreport.add_result()
```

```python
# Using SystemValidator
systemvalidator = SystemValidator()
systemvalidator.load_discovery()
systemvalidator.check_has_healing()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using add_result
result = add_result(result)
```

```python
# Using __init__
result = __init__(project_root)
```



---
**Generated**: 2026-03-26T09:39:04.964104
**Type**: api_reference
**Quality**: comprehensive
