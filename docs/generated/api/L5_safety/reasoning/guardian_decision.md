# API Documentation: guardian_decision

**Target Audience**: developers, api_users

# guardian_decision API Documentation

**File**: `guardian_decision.py`
**Classes**: 3
**Functions**: 5

## Classes

- **GuardianDecision**
- **GuardianViolationError** (inherits from Exception)
- **L5Guardian**

## Functions

- **to_dict** -> dict[str, Any]
- **__init__** -> None
- **__init__** -> None
- **validate** -> GuardianDecision
- **log_decision_to_state_bus** -> None


## Class: GuardianDecision

**Description**: Decision from L5 Guardian with enforcement capabilities.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Class: GuardianViolationError

**Description**: Raised when Guardian blocks execution.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, decision, message
**Returns**: None



## Class: L5Guardian

**Description**: 
    Active Guardian that enforces policies before L2.2.

    Enforces:
    - Tool allowlist
    - File access scope
    - Token budget
    - Agent permission map
    - Rate limits
    

### Methods

#### __init__
**Parameters**: self, policy_version
**Returns**: None

#### validate
**Parameters**: self, manifest, state, policy_version
**Returns**: GuardianDecision
**Description**: 
        Validate execution intent against all policies.

        Args:
            manifest: Execution manifest to validate
            state: Current execution state
            policy_version: Policy version to enforce

        Returns:
            GuardianDecision with allow/block result
        

#### log_decision_to_state_bus
**Parameters**: self, decision, trace_id
**Returns**: None
**Description**: Log Guardian decision to L4 state bus.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: __init__

**Parameters**: self, decision, message
**Returns**: None


## Function: __init__

**Parameters**: self, policy_version
**Returns**: None


## Function: validate

**Parameters**: self, manifest, state, policy_version
**Returns**: GuardianDecision
**Description**: 
        Validate execution intent against all policies.

        Args:
            manifest: Execution manifest to validate
            state: Current execution state
            policy_version: Policy version to enforce

        Returns:
            GuardianDecision with allow/block result
        



## Function: log_decision_to_state_bus

**Parameters**: self, decision, trace_id
**Returns**: None
**Description**: Log Guardian decision to L4 state bus.



## Usage Examples

### Class Usage

```python
# Using GuardianDecision
guardiandecision = GuardianDecision()
guardiandecision.to_dict()
```

```python
# Using GuardianViolationError
guardianviolationerror = GuardianViolationError()
```

```python
# Using L5Guardian
l5guardian = L5Guardian()
l5guardian.validate()
l5guardian.log_decision_to_state_bus()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using __init__
result = __init__(decision, message)
```

```python
# Using __init__
result = __init__(policy_version)
```



---
**Generated**: 2026-03-26T09:39:05.247608
**Type**: api_reference
**Quality**: comprehensive
