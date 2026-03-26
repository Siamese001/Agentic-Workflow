# API Documentation: governance_validator

**Target Audience**: developers, api_users

# governance_validator API Documentation

**File**: `governance_validator.py`
**Classes**: 2
**Functions**: 8

## Classes

- **GovernanceResult**
- **GovernanceShieldValidator**

## Functions

- **__post_init__** -> None
- **__init__** -> None
- **scan_risk_level** -> GovernanceResult
- **detect_privacy_language** -> GovernanceResult
- **check_forbidden_patterns** -> GovernanceResult
- **generate_safety_protocol** -> GovernanceResult
- **audit_content_compliance** -> GovernanceResult
- **sanitize_claims** -> GovernanceResult


## Class: GovernanceResult

**Description**: Result of governance validation with deterministic scoring.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: GovernanceShieldValidator

**Description**: 
    Pure deterministic governance and risk validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: 
        Initialize with governance validation configuration.

        Args:
            config: Configuration dictionary containing governance rules
        

#### scan_risk_level
**Parameters**: self, content
**Returns**: GovernanceResult
**Description**: 
        Scan content for risk level using deterministic keyword matching.

        Moved to Deterministic: Pure keyword-based risk classification
        

#### detect_privacy_language
**Parameters**: self, content
**Returns**: GovernanceResult
**Description**: 
        Detect privacy-sensitive language using deterministic patterns.

        Moved to Deterministic: Pure regex pattern matching
        

#### check_forbidden_patterns
**Parameters**: self, content
**Returns**: GovernanceResult
**Description**: 
        Check for forbidden patterns using deterministic regex.

        Moved to Deterministic: Pure forbidden pattern detection
        

#### generate_safety_protocol
**Parameters**: self, risk_level, content
**Returns**: GovernanceResult
**Description**: 
        Generate safety protocol using deterministic templates.

        Moved to Deterministic: Pure template-based protocol generation
        

#### audit_content_compliance
**Parameters**: self, content
**Returns**: GovernanceResult
**Description**: 
        Perform comprehensive content audit using deterministic rules.

        Combines all deterministic validation methods.
        

#### sanitize_claims
**Parameters**: self, content
**Returns**: GovernanceResult
**Description**: 
        Sanitize claims using deterministic rule-based logic.

        Moved to Deterministic: Pure claim sanitization rules
        



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: 
        Initialize with governance validation configuration.

        Args:
            config: Configuration dictionary containing governance rules
        



## Function: scan_risk_level

**Parameters**: self, content
**Returns**: GovernanceResult
**Description**: 
        Scan content for risk level using deterministic keyword matching.

        Moved to Deterministic: Pure keyword-based risk classification
        



## Function: detect_privacy_language

**Parameters**: self, content
**Returns**: GovernanceResult
**Description**: 
        Detect privacy-sensitive language using deterministic patterns.

        Moved to Deterministic: Pure regex pattern matching
        



## Function: check_forbidden_patterns

**Parameters**: self, content
**Returns**: GovernanceResult
**Description**: 
        Check for forbidden patterns using deterministic regex.

        Moved to Deterministic: Pure forbidden pattern detection
        



## Function: generate_safety_protocol

**Parameters**: self, risk_level, content
**Returns**: GovernanceResult
**Description**: 
        Generate safety protocol using deterministic templates.

        Moved to Deterministic: Pure template-based protocol generation
        



## Function: audit_content_compliance

**Parameters**: self, content
**Returns**: GovernanceResult
**Description**: 
        Perform comprehensive content audit using deterministic rules.

        Combines all deterministic validation methods.
        



## Function: sanitize_claims

**Parameters**: self, content
**Returns**: GovernanceResult
**Description**: 
        Sanitize claims using deterministic rule-based logic.

        Moved to Deterministic: Pure claim sanitization rules
        



## Usage Examples

### Class Usage

```python
# Using GovernanceResult
governanceresult = GovernanceResult()
```

```python
# Using GovernanceShieldValidator
governanceshieldvalidator = GovernanceShieldValidator()
governanceshieldvalidator.scan_risk_level()
governanceshieldvalidator.detect_privacy_language()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __init__
result = __init__(config)
```

```python
# Using scan_risk_level
result = scan_risk_level(content)
```



---
**Generated**: 2026-03-26T09:39:05.799238
**Type**: api_reference
**Quality**: comprehensive
