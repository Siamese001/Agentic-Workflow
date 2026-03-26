# API Documentation: CognitiveDispositionAgent

**Target Audience**: developers, api_users

# CognitiveDispositionAgent API Documentation

**File**: `CognitiveDispositionAgent.py`
**Classes**: 2
**Functions**: 7

## Classes

- **DispositionDecision**
- **CognitiveDispositionAgent** (inherits from PromptRenderingMixin, SovereignBaseAgent)

## Functions

- **__init__**
- **analyze_violation** -> DispositionDecision
- **get_analytics** -> dict
- **_build_prompt** -> str
- **heal** -> dict
- **heal_repository** -> dict
- **_heal_cognitive_disposition** -> dict


## Class: DispositionDecision



## Class: CognitiveDispositionAgent

**Description**: AI-Powered Architectural Triage Agent via Sovereign Gateway.

    DEPRECATION STATUS: KEEP - This agent is actively used and valuable.

    USAGE:
    - Integrated in execute_ssot.py with --enable-cda flag
    - Enhances decision making with cognitive analysis
    - Provides intelligent violation triage

    FUTURE ENHANCEMENTS:
    - Add more sophisticated violation pattern recognition
    - Integrate with more LLM providers
    - Add learning from historical dispositions
    - Expand beyond file-level to architectural analysis
    

**Inherits from**: PromptRenderingMixin, SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root, confidence_threshold

#### analyze_violation
**Parameters**: self, file_path, violation_type, context
**Returns**: DispositionDecision
**Description**: Sync wrapper around analyze_violation_async.

        Wave 1 fix: callers should use this instead of asyncio.run() directly.
        

#### get_analytics
**Parameters**: self
**Returns**: dict
**Description**: Get usage analytics for the CognitiveDispositionAgent.

        Returns:
            dict: Analytics data including usage statistics and performance metrics
        

#### _build_prompt
**Parameters**: self, file_path, violation_type, context
**Returns**: str

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal cognitive disposition violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (cognitive_disposition)
                - path: Path to the violating file
                - context: Additional context for the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for CognitiveDispositionAgent.



## Function: __init__

**Parameters**: self, project_root, confidence_threshold


## Function: analyze_violation

**Parameters**: self, file_path, violation_type, context
**Returns**: DispositionDecision
**Description**: Sync wrapper around analyze_violation_async.

        Wave 1 fix: callers should use this instead of asyncio.run() directly.
        



## Function: get_analytics

**Parameters**: self
**Returns**: dict
**Description**: Get usage analytics for the CognitiveDispositionAgent.

        Returns:
            dict: Analytics data including usage statistics and performance metrics
        



## Function: _build_prompt

**Parameters**: self, file_path, violation_type, context
**Returns**: str


## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal cognitive disposition violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (cognitive_disposition)
                - path: Path to the violating file
                - context: Additional context for the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for CognitiveDispositionAgent.



## Function: _heal_cognitive_disposition

**Parameters**: self, violation
**Returns**: dict
**Description**: Internal heal method with standard_heal decorator.



## Usage Examples

### Class Usage

```python
# Using DispositionDecision
dispositiondecision = DispositionDecision()
```

```python
# Using CognitiveDispositionAgent
cognitivedispositionagent = CognitiveDispositionAgent()
cognitivedispositionagent.analyze_violation()
cognitivedispositionagent.get_analytics()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root, confidence_threshold)
```

```python
# Using analyze_violation
result = analyze_violation(file_path, violation_type)
```

```python
# Using get_analytics
result = get_analytics()
```



---
**Generated**: 2026-03-26T09:39:05.105337
**Type**: api_reference
**Quality**: comprehensive
