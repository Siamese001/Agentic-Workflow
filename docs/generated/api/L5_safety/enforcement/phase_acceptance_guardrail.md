# API Documentation: phase_acceptance_guardrail

**Target Audience**: developers, api_users

# phase_acceptance_guardrail API Documentation

**File**: `phase_acceptance_guardrail.py`
**Classes**: 1
**Functions**: 8

## Classes

- **PhaseAcceptanceGuard**

## Functions

- **main**
- **__init__**
- **check_testpaths_contract_sync** -> None
- **check_evidence_files_protocol** -> None
- **_is_allowed_truncation** -> bool
- **check_phase_evidence_completeness** -> None
- **validate** -> bool
- **report** -> str


## Class: PhaseAcceptanceGuard

**Description**: Enforces Phase 2 closeout lessons learned.

### Methods

#### __init__
**Parameters**: self, repo_root

#### check_testpaths_contract_sync
**Parameters**: self
**Returns**: None
**Description**: Rule 46: Testpaths contract must be synchronized with pytest.ini.

#### check_evidence_files_protocol
**Parameters**: self
**Returns**: None
**Description**: Rule 48: Evidence files must contain raw, untruncated outputs.

#### _is_allowed_truncation
**Parameters**: self, content, pattern
**Returns**: bool
**Description**: Check if truncation is allowed in this context.

#### check_phase_evidence_completeness
**Parameters**: self
**Returns**: None
**Description**: Rule 47: Phase evidence must distinguish pre-existing vs new issues.

#### validate
**Parameters**: self
**Returns**: bool
**Description**: Run all validation checks.

#### report
**Parameters**: self
**Returns**: str
**Description**: Generate validation report.



## Function: main

**Description**: Run phase acceptance enforcement validation.



## Function: __init__

**Parameters**: self, repo_root


## Function: check_testpaths_contract_sync

**Parameters**: self
**Returns**: None
**Description**: Rule 46: Testpaths contract must be synchronized with pytest.ini.



## Function: check_evidence_files_protocol

**Parameters**: self
**Returns**: None
**Description**: Rule 48: Evidence files must contain raw, untruncated outputs.



## Function: _is_allowed_truncation

**Parameters**: self, content, pattern
**Returns**: bool
**Description**: Check if truncation is allowed in this context.



## Function: check_phase_evidence_completeness

**Parameters**: self
**Returns**: None
**Description**: Rule 47: Phase evidence must distinguish pre-existing vs new issues.



## Function: validate

**Parameters**: self
**Returns**: bool
**Description**: Run all validation checks.



## Function: report

**Parameters**: self
**Returns**: str
**Description**: Generate validation report.



## Usage Examples

### Class Usage

```python
# Using PhaseAcceptanceGuard
phaseacceptanceguard = PhaseAcceptanceGuard()
phaseacceptanceguard.check_testpaths_contract_sync()
phaseacceptanceguard.check_evidence_files_protocol()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using __init__
result = __init__(repo_root)
```

```python
# Using check_testpaths_contract_sync
result = check_testpaths_contract_sync()
```



---
**Generated**: 2026-03-26T09:39:04.890690
**Type**: api_reference
**Quality**: comprehensive
