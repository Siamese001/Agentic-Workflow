# API Documentation: SafetyDetectorAgent

**Target Audience**: developers, api_users

# SafetyDetectorAgent API Documentation

**File**: `SafetyDetectorAgent.py`
**Classes**: 5
**Functions**: 13

## Classes

- **SafetyThreatType** (inherits from Enum)
- **ThreatSeverity** (inherits from Enum)
- **SafetyThreat**
- **SafetyConfig**
- **SafetyDetectorAgent** (inherits from SovereignBaseAgent)

## Functions

- **create_legacy_bias_detector** -> SafetyDetectorAgent
- **create_legacy_injection_detector** -> SafetyDetectorAgent
- **heal_repository** -> dict[str, Any]
- **__init__**
- **detect_all** -> list[SafetyThreat]
- **detect_injection** -> list[SafetyThreat]
- **detect_bias** -> list[SafetyThreat]
- **detect_hallucination** -> list[SafetyThreat]
- **is_safe** -> bool
- **get_safety_score** -> float
- **get_threats** -> list[SafetyThreat]
- **clear_threats** -> None
- **heal** -> dict


## Class: SafetyThreatType

**Description**: Types of safety threats.

**Inherits from**: Enum



## Class: ThreatSeverity

**Description**: Severity levels for threats.

**Inherits from**: Enum



## Class: SafetyThreat

**Description**: Represents a detected safety threat.



## Class: SafetyConfig

**Description**: configuration for safety detection.



## Class: SafetyDetectorAgent

**Description**: 
    Unified safety and security detector.

    Consolidates:
    - BiasDetectorAgent
    - HallucinationDetectorAgent
    - PromptInjectionDetectorAgent

    Usage:
        detector = SafetyDetectorAgent()

        # Check user input for injection
        threats = detector.detect_injection("user input here")

        # Check model output for bias
        threats = detector.detect_bias("model output here")
    

**Inherits from**: SovereignBaseAgent

### Methods

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        

#### __init__
**Parameters**: self, agent_config

#### detect_all
**Parameters**: self, text, source
**Returns**: list[SafetyThreat]
**Description**: Run all enabled detections on text.

#### detect_injection
**Parameters**: self, text, source
**Returns**: list[SafetyThreat]
**Description**: Detect prompt injection attacks.

#### detect_bias
**Parameters**: self, text, source
**Returns**: list[SafetyThreat]
**Description**: Detect bias patterns in text.

#### detect_hallucination
**Parameters**: self, text, source
**Returns**: list[SafetyThreat]
**Description**: Detect hallucination indicators in text.

#### is_safe
**Parameters**: self, text, source
**Returns**: bool
**Description**: Quick check if text is safe (no high-severity threats).

#### get_safety_score
**Parameters**: self, text
**Returns**: float
**Description**: Calculate safety score (0.0 = unsafe, 1.0 = safe).

#### get_threats
**Parameters**: self
**Returns**: list[SafetyThreat]
**Description**: Get all recorded threats.

#### clear_threats
**Parameters**: self
**Returns**: None
**Description**: Clear recorded threats.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal safety detection violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (bias, hallucination, injection)
                - source: Source of the threat
                - severity: Severity level

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: create_legacy_bias_detector

**Returns**: SafetyDetectorAgent
**Description**: Create detector for bias only.



## Function: create_legacy_injection_detector

**Returns**: SafetyDetectorAgent
**Description**: Create detector for prompt injection only.



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        



## Function: __init__

**Parameters**: self, agent_config


## Function: detect_all

**Parameters**: self, text, source
**Returns**: list[SafetyThreat]
**Description**: Run all enabled detections on text.



## Function: detect_injection

**Parameters**: self, text, source
**Returns**: list[SafetyThreat]
**Description**: Detect prompt injection attacks.



## Function: detect_bias

**Parameters**: self, text, source
**Returns**: list[SafetyThreat]
**Description**: Detect bias patterns in text.



## Function: detect_hallucination

**Parameters**: self, text, source
**Returns**: list[SafetyThreat]
**Description**: Detect hallucination indicators in text.



## Function: is_safe

**Parameters**: self, text, source
**Returns**: bool
**Description**: Quick check if text is safe (no high-severity threats).



## Function: get_safety_score

**Parameters**: self, text
**Returns**: float
**Description**: Calculate safety score (0.0 = unsafe, 1.0 = safe).



## Function: get_threats

**Parameters**: self
**Returns**: list[SafetyThreat]
**Description**: Get all recorded threats.



## Function: clear_threats

**Parameters**: self
**Returns**: None
**Description**: Clear recorded threats.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal safety detection violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (bias, hallucination, injection)
                - source: Source of the threat
                - severity: Severity level

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using SafetyThreatType
safetythreattype = SafetyThreatType()
```

```python
# Using ThreatSeverity
threatseverity = ThreatSeverity()
```

```python
# Using SafetyThreat
safetythreat = SafetyThreat()
```

### Function Usage

```python
# Using create_legacy_bias_detector
result = create_legacy_bias_detector()
```

```python
# Using create_legacy_injection_detector
result = create_legacy_injection_detector()
```

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```



---
**Generated**: 2026-03-26T09:39:05.383854
**Type**: api_reference
**Quality**: comprehensive
