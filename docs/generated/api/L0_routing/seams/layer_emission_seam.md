# API Documentation: layer_emission_seam

**Target Audience**: developers, api_users

# layer_emission_seam API Documentation

**File**: `layer_emission_seam.py`
**Classes**: 1
**Functions**: 3

## Classes

- **LayerEmissionValidator** (inherits from Protocol)

## Functions

- **get_layer_emission_validator** -> LayerEmissionValidator
- **assert_layer_may_emit** -> None
- **validate_emission** -> None


## Class: LayerEmissionValidator

**Description**: Protocol for layer emission validation.

**Inherits from**: Protocol

### Methods

#### validate_emission
**Parameters**: self, artifact_type, emitting_layer, trace_id
**Returns**: None
**Description**: Validate that a layer may emit a specific artifact type.



## Function: get_layer_emission_validator

**Returns**: LayerEmissionValidator
**Description**: Get the layer emission validator implementation.

    This function uses dynamic import to avoid static L0→L5 dependency
    while providing runtime access to L5 validation logic.
    



## Function: assert_layer_may_emit

**Parameters**: artifact_type, emitting_layer, trace_id
**Returns**: None
**Description**: Assert that a layer may emit a specific artifact type.

    This is the approved interface for L0 types to validate emissions.
    



## Function: validate_emission

**Parameters**: self, artifact_type, emitting_layer, trace_id
**Returns**: None
**Description**: Validate that a layer may emit a specific artifact type.



## Usage Examples

### Class Usage

```python
# Using LayerEmissionValidator
layeremissionvalidator = LayerEmissionValidator()
layeremissionvalidator.validate_emission()
```

### Function Usage

```python
# Using get_layer_emission_validator
result = get_layer_emission_validator()
```

```python
# Using assert_layer_may_emit
result = assert_layer_may_emit(artifact_type, emitting_layer)
```

```python
# Using validate_emission
result = validate_emission(artifact_type, emitting_layer)
```



---
**Generated**: 2026-03-26T09:39:03.398837
**Type**: api_reference
**Quality**: comprehensive
