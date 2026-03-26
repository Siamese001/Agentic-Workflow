# API Documentation: constitutional_governance_types

**Target Audience**: developers, api_users

# constitutional_governance_types API Documentation

**File**: `constitutional_governance_types.py`
**Classes**: 4
**Functions**: 8

## Classes

- **ConstitutionalPrinciple** (inherits from Enum)
- **PrincipleViolation**
- **GovernanceResult**
- **ConstitutionalGovernanceGuardrail**

## Functions

- **__init__**
- **_check_principles** -> list[PrincipleViolation]
- **_check_governance** -> list[PrincipleViolation]
- **_create_audit** -> str
- **_generate_notes** -> str
- **revise_content** -> str
- **get_audit_log** -> list[dict[str, Any]]
- **get_statistics** -> dict[str, Any]


## Class: ConstitutionalPrinciple

**Description**: Core constitutional principles.

**Inherits from**: Enum



## Class: PrincipleViolation

**Description**: Violation of a constitutional principle.



## Class: GovernanceResult

**Description**: Result of governance check.



## Class: ConstitutionalGovernanceGuardrail

**Description**: 
    Consolidated Constitutional Governance Guardrail.

    Provides unified constitutional AI with:
    - Constitutional principle enforcement
    - Governance rule checking
    - Oversight and audit trails
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize constitutional governance guardrail.

#### _check_principles
**Parameters**: self, content
**Returns**: list[PrincipleViolation]
**Description**: Check content against constitutional principles.

#### _check_governance
**Parameters**: self, content, context
**Returns**: list[PrincipleViolation]
**Description**: Check governance rules.

#### _create_audit
**Parameters**: self, content, violations
**Returns**: str
**Description**: Create audit trail entry.

#### _generate_notes
**Parameters**: self, violations
**Returns**: str
**Description**: Generate review notes.

#### revise_content
**Parameters**: self, content, violations
**Returns**: str
**Description**: 
        Suggest revised content based on violations.

        Args:
            content: Original content
            violations: List of violations

        Returns:
            Revised content suggestion
        

#### get_audit_log
**Parameters**: self, limit
**Returns**: list[dict[str, Any]]
**Description**: Get recent audit log entries.

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get governance statistics.



## Function: __init__

**Parameters**: self
**Description**: Initialize constitutional governance guardrail.



## Function: _check_principles

**Parameters**: self, content
**Returns**: list[PrincipleViolation]
**Description**: Check content against constitutional principles.



## Function: _check_governance

**Parameters**: self, content, context
**Returns**: list[PrincipleViolation]
**Description**: Check governance rules.



## Function: _create_audit

**Parameters**: self, content, violations
**Returns**: str
**Description**: Create audit trail entry.



## Function: _generate_notes

**Parameters**: self, violations
**Returns**: str
**Description**: Generate review notes.



## Function: revise_content

**Parameters**: self, content, violations
**Returns**: str
**Description**: 
        Suggest revised content based on violations.

        Args:
            content: Original content
            violations: List of violations

        Returns:
            Revised content suggestion
        



## Function: get_audit_log

**Parameters**: self, limit
**Returns**: list[dict[str, Any]]
**Description**: Get recent audit log entries.



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get governance statistics.



## Usage Examples

### Class Usage

```python
# Using ConstitutionalPrinciple
constitutionalprinciple = ConstitutionalPrinciple()
```

```python
# Using PrincipleViolation
principleviolation = PrincipleViolation()
```

```python
# Using GovernanceResult
governanceresult = GovernanceResult()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using _check_principles
result = _check_principles(content)
```

```python
# Using _check_governance
result = _check_governance(content, context)
```



---
**Generated**: 2026-03-26T09:39:05.494553
**Type**: api_reference
**Quality**: comprehensive
