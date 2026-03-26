# API Documentation: integrity_validation_types

**Target Audience**: developers, api_users

# integrity_validation_types API Documentation

**File**: `integrity_validation_types.py`
**Classes**: 3
**Functions**: 5

## Classes

- **IntegrityViolation**
- **IntegrityResult**
- **IntegrityValidationGuardrail**

## Functions

- **__init__**
- **register_checksum** -> None
- **calculate_checksum** -> str
- **verify_checksum** -> bool
- **get_statistics** -> dict[str, Any]


## Class: IntegrityViolation

**Description**: Integrity violation record.



## Class: IntegrityResult

**Description**: Result of integrity validation.



## Class: IntegrityValidationGuardrail

**Description**: 
    Consolidated Integrity Validation Guardrail.

    Provides unified integrity checks with:
    - Data integrity validation (checksums, signatures)
    - Gravity compliance (import structure enforcement)
    - State consistency checks
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize integrity validation guardrail.

#### register_checksum
**Parameters**: self, data_id, checksum
**Returns**: None
**Description**: Register expected checksum for data.

#### calculate_checksum
**Parameters**: self, data
**Returns**: str
**Description**: Calculate SHA256 checksum for data.

#### verify_checksum
**Parameters**: self, data, expected
**Returns**: bool
**Description**: Verify data matches expected checksum.

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get integrity validation statistics.



## Function: __init__

**Parameters**: self
**Description**: Initialize integrity validation guardrail.



## Function: register_checksum

**Parameters**: self, data_id, checksum
**Returns**: None
**Description**: Register expected checksum for data.



## Function: calculate_checksum

**Parameters**: self, data
**Returns**: str
**Description**: Calculate SHA256 checksum for data.



## Function: verify_checksum

**Parameters**: self, data, expected
**Returns**: bool
**Description**: Verify data matches expected checksum.



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get integrity validation statistics.



## Usage Examples

### Class Usage

```python
# Using IntegrityViolation
integrityviolation = IntegrityViolation()
```

```python
# Using IntegrityResult
integrityresult = IntegrityResult()
```

```python
# Using IntegrityValidationGuardrail
integrityvalidationguardrail = IntegrityValidationGuardrail()
integrityvalidationguardrail.register_checksum()
integrityvalidationguardrail.calculate_checksum()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using register_checksum
result = register_checksum(data_id, checksum)
```

```python
# Using calculate_checksum
result = calculate_checksum(data)
```



---
**Generated**: 2026-03-26T09:39:05.528677
**Type**: api_reference
**Quality**: comprehensive
