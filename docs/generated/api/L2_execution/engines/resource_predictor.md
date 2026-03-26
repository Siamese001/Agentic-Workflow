# API Documentation: resource_predictor

**Target Audience**: developers, api_users

# resource_predictor API Documentation

**File**: `resource_predictor.py`
**Classes**: 2
**Functions**: 6

## Classes

- **ResourcePredictor** (inherits from Protocol)
- **DefaultDeterministicResourcePredictor**

## Functions

- **predict** -> ResourcePrediction
- **__init__**
- **predict** -> ResourcePrediction
- **_apply_history_adjustments** -> ResourceEnvelope
- **_clamp_envelope** -> ResourceEnvelope
- **_generate_confidence_and_reasons** -> tuple[float, tuple[str, ...]]


## Class: ResourcePredictor

**Description**: Protocol for resource prediction engines.

**Inherits from**: Protocol

### Methods

#### predict
**Returns**: ResourcePrediction
**Description**: Predict resource envelope for a failure signature.



## Class: DefaultDeterministicResourcePredictor

**Description**: Deterministic resource predictor with bounded outputs.

### Methods

#### __init__
**Parameters**: self, min_cpu_cores, max_cpu_cores, min_memory_mb, max_memory_mb, min_timeout_s, max_timeout_s
**Description**: Initialize with configurable bounds.

#### predict
**Parameters**: self
**Returns**: ResourcePrediction
**Description**: Predict resource envelope deterministically.

#### _apply_history_adjustments
**Parameters**: self, baseline, signature, history_bytes
**Returns**: ResourceEnvelope
**Description**: Apply deterministic adjustments based on history.

#### _clamp_envelope
**Parameters**: self, envelope
**Returns**: ResourceEnvelope
**Description**: Clamp envelope to configured bounds.

#### _generate_confidence_and_reasons
**Parameters**: self, signature, envelope, history_bytes
**Returns**: tuple[float, tuple[str, ...]]
**Description**: Generate deterministic confidence and reasoning.



## Function: predict

**Returns**: ResourcePrediction
**Description**: Predict resource envelope for a failure signature.



## Function: __init__

**Parameters**: self, min_cpu_cores, max_cpu_cores, min_memory_mb, max_memory_mb, min_timeout_s, max_timeout_s
**Description**: Initialize with configurable bounds.



## Function: predict

**Parameters**: self
**Returns**: ResourcePrediction
**Description**: Predict resource envelope deterministically.



## Function: _apply_history_adjustments

**Parameters**: self, baseline, signature, history_bytes
**Returns**: ResourceEnvelope
**Description**: Apply deterministic adjustments based on history.



## Function: _clamp_envelope

**Parameters**: self, envelope
**Returns**: ResourceEnvelope
**Description**: Clamp envelope to configured bounds.



## Function: _generate_confidence_and_reasons

**Parameters**: self, signature, envelope, history_bytes
**Returns**: tuple[float, tuple[str, ...]]
**Description**: Generate deterministic confidence and reasoning.



## Usage Examples

### Class Usage

```python
# Using ResourcePredictor
resourcepredictor = ResourcePredictor()
resourcepredictor.predict()
```

```python
# Using DefaultDeterministicResourcePredictor
defaultdeterministicresourcepredictor = DefaultDeterministicResourcePredictor()
defaultdeterministicresourcepredictor.predict()
```

### Function Usage

```python
# Using predict
result = predict()
```

```python
# Using __init__
result = __init__(min_cpu_cores, max_cpu_cores)
```

```python
# Using predict
result = predict()
```



---
**Generated**: 2026-03-26T09:39:03.764590
**Type**: api_reference
**Quality**: comprehensive
