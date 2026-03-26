# API Documentation: integration_contract_types

**Target Audience**: developers, api_users

# integration_contract_types API Documentation

**File**: `integration_contract_types.py`
**Classes**: 2
**Functions**: 5

## Classes

- **Finding**
- **ResultEnvelope**

## Functions

- **to_ordered_dict** -> dict
- **status** -> str
- **to_ordered_dict** -> dict
- **to_json** -> str
- **write_json** -> None


## Class: Finding

**Description**: A single finding from a governance tool run.

### Methods

#### to_ordered_dict
**Parameters**: self
**Returns**: dict



## Class: ResultEnvelope

**Description**: Deterministic JSON result envelope for governance CLIs.

### Methods

#### status
**Parameters**: self
**Returns**: str
**Description**: Derive status from exit_code and findings.

#### to_ordered_dict
**Parameters**: self
**Returns**: dict
**Description**: Return a plain dict with stable key ordering.

#### to_json
**Parameters**: self
**Returns**: str
**Description**: Deterministic JSON string: sorted keys, compact separators.

#### write_json
**Parameters**: self, path
**Returns**: None
**Description**: Write deterministic JSON bytes to file.



## Function: to_ordered_dict

**Parameters**: self
**Returns**: dict


## Function: status

**Parameters**: self
**Returns**: str
**Description**: Derive status from exit_code and findings.



## Function: to_ordered_dict

**Parameters**: self
**Returns**: dict
**Description**: Return a plain dict with stable key ordering.



## Function: to_json

**Parameters**: self
**Returns**: str
**Description**: Deterministic JSON string: sorted keys, compact separators.



## Function: write_json

**Parameters**: self, path
**Returns**: None
**Description**: Write deterministic JSON bytes to file.



## Usage Examples

### Class Usage

```python
# Using Finding
finding = Finding()
finding.to_ordered_dict()
```

```python
# Using ResultEnvelope
resultenvelope = ResultEnvelope()
resultenvelope.status()
resultenvelope.to_ordered_dict()
```

### Function Usage

```python
# Using to_ordered_dict
result = to_ordered_dict()
```

```python
# Using status
result = status()
```

```python
# Using to_ordered_dict
result = to_ordered_dict()
```



---
**Generated**: 2026-03-26T09:39:03.460347
**Type**: api_reference
**Quality**: comprehensive
