# API Documentation: detection_signal_config

**Target Audience**: developers, api_users

# detection_signal_config API Documentation

**File**: `detection_signal_config.py`
**Classes**: 5
**Functions**: 4

## Classes

- **Severity** (inherits from Enum)
- **ImpactScope** (inherits from Enum)
- **ImpactAssessment**
- **FailureContext**
- **DetectionSignal**

## Functions

- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **classify_risk_level** -> str


## Class: Severity

**Description**: Severity levels for detection signals.

**Inherits from**: Enum



## Class: ImpactScope

**Description**: Scope of impact for detected issues.

**Inherits from**: Enum



## Class: ImpactAssessment

**Description**: Structured impact assessment for detection signals.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: FailureContext

**Description**: Structured failure context for detection signals.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: DetectionSignal

**Description**: Unified detection signal with structured context.

    This is the standard output format for all sensors in the system.
    Implements the target state SCRIPT (SENSOR) component requirements.

    Attributes:
        signal_id: Unique identifier for this signal
        timestamp: When the signal was generated
        source_sensor: Name of the sensor that generated this signal
        detection_type: Type of detection (e.g., "import_violation")
        is_failure: Binary check result
        failure_context: Structured context about the failure
        severity: Severity level of the detection
        impact: Impact assessment
        confidence: Confidence score (0.0 to 1.0)
        is_auto_fixable: Whether this can be auto-fixed
        suggested_fix: Optional suggested fix description
    

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization and logging.

#### classify_risk_level
**Parameters**: self
**Returns**: str
**Description**: Classify risk level based on severity and impact.

        Used by Validator Agent for enforcement policy decisions.
        Returns: 'low', 'medium', or 'high'
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization and logging.



## Function: classify_risk_level

**Parameters**: self
**Returns**: str
**Description**: Classify risk level based on severity and impact.

        Used by Validator Agent for enforcement policy decisions.
        Returns: 'low', 'medium', or 'high'
        



## Usage Examples

### Class Usage

```python
# Using Severity
severity = Severity()
```

```python
# Using ImpactScope
impactscope = ImpactScope()
```

```python
# Using ImpactAssessment
impactassessment = ImpactAssessment()
impactassessment.to_dict()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:04.741451
**Type**: api_reference
**Quality**: comprehensive
