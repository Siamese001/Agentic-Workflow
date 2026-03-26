# API Documentation: security_validation_types

**Target Audience**: developers, api_users

# security_validation_types API Documentation

**File**: `security_validation_types.py`
**Classes**: 3
**Functions**: 8

## Classes

- **SecurityValidationResult**
- **SecuritySuiteResult**
- **RedTeamValidationSuite**

## Functions

- **get_security_suite** -> RedTeamValidationSuite
- **run_security_validation** -> SecuritySuiteResult
- **__init__** -> None
- **_ensure_initialized** -> None
- **run_validator** -> SecurityValidationResult
- **run_all** -> SecuritySuiteResult
- **get_available_validators** -> list[str]
- **get_status** -> dict[str, Any]


## Class: SecurityValidationResult

**Description**: Result from a security validation run.



## Class: SecuritySuiteResult

**Description**: Aggregated result from running the full security suite.



## Class: RedTeamValidationSuite

**Description**: 
    Orchestrates security validation across multiple red team validators.

    Usage:
        suite = RedTeamValidationSuite()
        result = suite.run_all(content={"test": "data"})
        if not result.overall_valid:
            print(f"Security issues found: {result.validators_failed} validators failed")
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the security validation suite.

#### _ensure_initialized
**Parameters**: self
**Returns**: None
**Description**: Lazy initialization of validators.

#### run_validator
**Parameters**: self, validator_name, content, context
**Returns**: SecurityValidationResult
**Description**: 
        Run a specific validator.

        Args:
            validator_name: Name of the validator to run
            content: Content to validate
            context: Optional validation context

        Returns:
            SecurityValidationResult with validation details
        

#### run_all
**Parameters**: self, content, context
**Returns**: SecuritySuiteResult
**Description**: 
        Run all registered security validators.

        Args:
            content: Content to validate
            context: Optional validation context

        Returns:
            SecuritySuiteResult with aggregated results
        

#### get_available_validators
**Parameters**: self
**Returns**: list[str]
**Description**: Get list of available validator names.

#### get_status
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current status of the security suite.



## Function: get_security_suite

**Returns**: RedTeamValidationSuite
**Description**: Get or create the global security validation suite.



## Function: run_security_validation

**Parameters**: content, context
**Returns**: SecuritySuiteResult
**Description**: 
    Convenience function to run full security validation.

    Args:
        content: Content to validate
        context: Optional validation context

    Returns:
        SecuritySuiteResult with all validation results
    



## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the security validation suite.



## Function: _ensure_initialized

**Parameters**: self
**Returns**: None
**Description**: Lazy initialization of validators.



## Function: run_validator

**Parameters**: self, validator_name, content, context
**Returns**: SecurityValidationResult
**Description**: 
        Run a specific validator.

        Args:
            validator_name: Name of the validator to run
            content: Content to validate
            context: Optional validation context

        Returns:
            SecurityValidationResult with validation details
        



## Function: run_all

**Parameters**: self, content, context
**Returns**: SecuritySuiteResult
**Description**: 
        Run all registered security validators.

        Args:
            content: Content to validate
            context: Optional validation context

        Returns:
            SecuritySuiteResult with aggregated results
        



## Function: get_available_validators

**Parameters**: self
**Returns**: list[str]
**Description**: Get list of available validator names.



## Function: get_status

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get current status of the security suite.



## Usage Examples

### Class Usage

```python
# Using SecurityValidationResult
securityvalidationresult = SecurityValidationResult()
```

```python
# Using SecuritySuiteResult
securitysuiteresult = SecuritySuiteResult()
```

```python
# Using RedTeamValidationSuite
redteamvalidationsuite = RedTeamValidationSuite()
redteamvalidationsuite.run_validator()
redteamvalidationsuite.run_all()
```

### Function Usage

```python
# Using get_security_suite
result = get_security_suite()
```

```python
# Using run_security_validation
result = run_security_validation(content, context)
```

```python
# Using __init__
result = __init__()
```



---
**Generated**: 2026-03-26T09:39:05.565526
**Type**: api_reference
**Quality**: comprehensive
