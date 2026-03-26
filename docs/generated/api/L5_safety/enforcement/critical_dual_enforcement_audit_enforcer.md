# API Documentation: critical_dual_enforcement_audit_enforcer

**Target Audience**: developers, api_users

# critical_dual_enforcement_audit_enforcer API Documentation

**File**: `critical_dual_enforcement_audit_enforcer.py`
**Classes**: 3
**Functions**: 8

## Classes

- **RequirementMetadata**
- **DualEnforcementViolation** (inherits from Exception)
- **CriticalDualEnforcementAuditor**

## Functions

- **run_dual_enforcement_audit** -> int
- **test_dual_enforcement_audit** -> bool
- **__init__**
- **parse_requirements_metadata** -> dict[str, RequirementMetadata]
- **audit_critical_requirements** -> dict[str, list[str]]
- **generate_audit_report** -> str
- **save_audit_report** -> Path
- **run_ci_audit** -> int


## Class: RequirementMetadata

**Description**: Metadata for a requirement from the requirements document.



## Class: DualEnforcementViolation

**Description**: Raised when dual enforcement guarantee is violated.

**Inherits from**: Exception



## Class: CriticalDualEnforcementAuditor

**Description**: Audits CRITICAL requirements for dual enforcement compliance (REQ-416).

### Methods

#### __init__
**Parameters**: self, requirements_path
**Description**: Initialize the auditor.

        Args:
            requirements_path: Path to requirements document
        

#### parse_requirements_metadata
**Parameters**: self
**Returns**: dict[str, RequirementMetadata]
**Description**: Parse requirements from the markdown document.

        Returns:
            Dictionary mapping REQ-ID to RequirementMetadata
        

#### audit_critical_requirements
**Parameters**: self
**Returns**: dict[str, list[str]]
**Description**: Audit all CRITICAL requirements for dual enforcement compliance.

        Returns:
            Dictionary with "violations" and "warnings" keys containing lists of issues
        

#### generate_audit_report
**Parameters**: self
**Returns**: str
**Description**: Generate a comprehensive audit report.

        Returns:
            Formatted audit report as string
        

#### save_audit_report
**Parameters**: self, output_path
**Returns**: Path
**Description**: Save audit report to file.

        Args:
            output_path: Path to save the report

        Returns:
            Path to the saved report
        

#### run_ci_audit
**Parameters**: self
**Returns**: int
**Description**: Run CI audit and return exit code.

        Returns:
            0 if no violations, 1 if violations found
        



## Function: run_dual_enforcement_audit

**Returns**: int
**Description**: Run the dual enforcement audit as a CLI command.

    Returns:
        Exit code (0 for success, 1 for violations)
    



## Function: test_dual_enforcement_audit

**Returns**: bool
**Description**: Test the dual enforcement auditor.

    Returns:
        True if audit works correctly, False otherwise
    



## Function: __init__

**Parameters**: self, requirements_path
**Description**: Initialize the auditor.

        Args:
            requirements_path: Path to requirements document
        



## Function: parse_requirements_metadata

**Parameters**: self
**Returns**: dict[str, RequirementMetadata]
**Description**: Parse requirements from the markdown document.

        Returns:
            Dictionary mapping REQ-ID to RequirementMetadata
        



## Function: audit_critical_requirements

**Parameters**: self
**Returns**: dict[str, list[str]]
**Description**: Audit all CRITICAL requirements for dual enforcement compliance.

        Returns:
            Dictionary with "violations" and "warnings" keys containing lists of issues
        



## Function: generate_audit_report

**Parameters**: self
**Returns**: str
**Description**: Generate a comprehensive audit report.

        Returns:
            Formatted audit report as string
        



## Function: save_audit_report

**Parameters**: self, output_path
**Returns**: Path
**Description**: Save audit report to file.

        Args:
            output_path: Path to save the report

        Returns:
            Path to the saved report
        



## Function: run_ci_audit

**Parameters**: self
**Returns**: int
**Description**: Run CI audit and return exit code.

        Returns:
            0 if no violations, 1 if violations found
        



## Usage Examples

### Class Usage

```python
# Using RequirementMetadata
requirementmetadata = RequirementMetadata()
```

```python
# Using DualEnforcementViolation
dualenforcementviolation = DualEnforcementViolation()
```

```python
# Using CriticalDualEnforcementAuditor
criticaldualenforcementauditor = CriticalDualEnforcementAuditor()
criticaldualenforcementauditor.parse_requirements_metadata()
criticaldualenforcementauditor.audit_critical_requirements()
```

### Function Usage

```python
# Using run_dual_enforcement_audit
result = run_dual_enforcement_audit()
```

```python
# Using test_dual_enforcement_audit
result = test_dual_enforcement_audit()
```

```python
# Using __init__
result = __init__(requirements_path)
```



---
**Generated**: 2026-03-26T09:39:04.798995
**Type**: api_reference
**Quality**: comprehensive
