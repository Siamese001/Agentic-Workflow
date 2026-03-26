# API Documentation: compliance_audit_manager_enforcer

**Target Audience**: developers, api_users

# compliance_audit_manager_enforcer API Documentation

**File**: `compliance_audit_manager_enforcer.py`
**Classes**: 1
**Functions**: 3

## Classes

- **ComplianceAuditManager**

## Functions

- **__init__**
- **audit_event** -> bool
- **generate_report** -> str


## Class: ComplianceAuditManager

**Description**: 
    The Auditor.
    Checks system actions against the SovereignPolicyRegistry.
    

### Methods

#### __init__
**Parameters**: self

#### audit_event
**Parameters**: self, policy_id, context
**Returns**: bool
**Description**: 
        Record an event and check for policy violations.
        Returns False if action should be blocked.
        

#### generate_report
**Parameters**: self
**Returns**: str
**Description**: Generate a compliance report.



## Function: __init__

**Parameters**: self


## Function: audit_event

**Parameters**: self, policy_id, context
**Returns**: bool
**Description**: 
        Record an event and check for policy violations.
        Returns False if action should be blocked.
        



## Function: generate_report

**Parameters**: self
**Returns**: str
**Description**: Generate a compliance report.



## Usage Examples

### Class Usage

```python
# Using ComplianceAuditManager
complianceauditmanager = ComplianceAuditManager()
complianceauditmanager.audit_event()
complianceauditmanager.generate_report()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using audit_event
result = audit_event(policy_id, context)
```

```python
# Using generate_report
result = generate_report()
```



---
**Generated**: 2026-03-26T09:39:04.789685
**Type**: api_reference
**Quality**: comprehensive
