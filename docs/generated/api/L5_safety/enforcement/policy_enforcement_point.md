# API Documentation: policy_enforcement_point

**Target Audience**: developers, api_users

# policy_enforcement_point API Documentation

**File**: `policy_enforcement_point.py`
**Classes**: 4
**Functions**: 18

## Classes

- **PolicyVerdict** (inherits from str, Enum)
- **PolicyCheckResult**
- **PolicyViolationError** (inherits from PermissionError)
- **PolicyEnforcementPoint**

## Functions

- **get_policy_enforcement_point** -> PolicyEnforcementPoint
- **reset_policy_enforcement_point** -> None
- **allowed** -> bool
- **needs_escalation** -> bool
- **__init__** -> None
- **__init__** -> None
- **_trace_id** -> str
- **_verify_policy_hash** -> bool
- **check** -> PolicyCheckResult
- **enforce**
- **enforced** -> Callable
- **reenter_safety** -> PolicyCheckResult
- **audit_log** -> list[PolicyCheckResult]
- **allow_count** -> int
- **deny_count** -> int
- **escalation_count** -> int
- **decorator** -> Callable
- **wrapper**


## Class: PolicyVerdict

**Description**: Outcome of a policy enforcement check.

**Inherits from**: str, Enum



## Class: PolicyCheckResult

**Description**: Immutable result of a policy enforcement point check.

### Methods

#### allowed
**Parameters**: self
**Returns**: bool

#### needs_escalation
**Parameters**: self
**Returns**: bool



## Class: PolicyViolationError

**Description**: Raised when a policy enforcement point denies an action.

**Inherits from**: PermissionError

### Methods

#### __init__
**Parameters**: self, result
**Returns**: None



## Class: PolicyEnforcementPoint

**Description**: Wraps every L5-originated action with policy hash verification.

    Usage — context manager (applies_guardrail)::

        pep = PolicyEnforcementPoint(policy_hash="abc123")
        with pep.enforce("invoke_tool", "code_interpreter"):
            tool.run(code)

    Usage — decorator::

        @pep.enforced("execute_plan")
        def execute_plan(self, plan: dict) -> dict:
            ...

    Usage — explicit check::

        result = pep.check("write_artifact", target="artifacts/out.json")
        if result.needs_escalation:
            handle_escalation(result)
    

### Methods

#### __init__
**Parameters**: self, policy_hash, strict_mode, blocked_actions
**Returns**: None

#### _trace_id
**Parameters**: self
**Returns**: str

#### _verify_policy_hash
**Parameters**: self, action
**Returns**: bool
**Description**: Verify the policy hash is non-empty and structurally valid.

#### check
**Parameters**: self, action, target, metadata
**Returns**: PolicyCheckResult
**Description**: Perform a policy enforcement check before ``action``.

        Returns a :class:`PolicyCheckResult`. In strict mode, raises
        :class:`PolicyViolationError` on DENY.
        

#### enforce
**Parameters**: self, action, target, metadata
**Description**: Context manager: enforce policy before executing body.

        Satisfies the ``applies_guardrail`` + ``references_policy_hash``
        ADG edge contract from L5.
        

#### enforced
**Parameters**: self, action, target
**Returns**: Callable
**Description**: Decorator: enforce policy before every call.

        Usage::

            @pep.enforced("execute_plan")
            def execute_plan(self, plan: dict) -> dict:
                ...
        

#### reenter_safety
**Parameters**: self, action, reason
**Returns**: PolicyCheckResult
**Description**: Signal that this action must re-enter the safety evaluation loop.

        Emits the ``reenters_safety`` ADG edge.
        

#### audit_log
**Parameters**: self
**Returns**: list[PolicyCheckResult]

#### allow_count
**Parameters**: self
**Returns**: int

#### deny_count
**Parameters**: self
**Returns**: int

#### escalation_count
**Parameters**: self
**Returns**: int



## Function: get_policy_enforcement_point

**Parameters**: policy_hash
**Returns**: PolicyEnforcementPoint
**Description**: Return the process-level PolicyEnforcementPoint.



## Function: reset_policy_enforcement_point

**Returns**: None
**Description**: Reset the global PEP (for testing).



## Function: allowed

**Parameters**: self
**Returns**: bool


## Function: needs_escalation

**Parameters**: self
**Returns**: bool


## Function: __init__

**Parameters**: self, result
**Returns**: None


## Function: __init__

**Parameters**: self, policy_hash, strict_mode, blocked_actions
**Returns**: None


## Function: _trace_id

**Parameters**: self
**Returns**: str


## Function: _verify_policy_hash

**Parameters**: self, action
**Returns**: bool
**Description**: Verify the policy hash is non-empty and structurally valid.



## Function: check

**Parameters**: self, action, target, metadata
**Returns**: PolicyCheckResult
**Description**: Perform a policy enforcement check before ``action``.

        Returns a :class:`PolicyCheckResult`. In strict mode, raises
        :class:`PolicyViolationError` on DENY.
        



## Function: enforce

**Parameters**: self, action, target, metadata
**Description**: Context manager: enforce policy before executing body.

        Satisfies the ``applies_guardrail`` + ``references_policy_hash``
        ADG edge contract from L5.
        



## Function: enforced

**Parameters**: self, action, target
**Returns**: Callable
**Description**: Decorator: enforce policy before every call.

        Usage::

            @pep.enforced("execute_plan")
            def execute_plan(self, plan: dict) -> dict:
                ...
        



## Function: reenter_safety

**Parameters**: self, action, reason
**Returns**: PolicyCheckResult
**Description**: Signal that this action must re-enter the safety evaluation loop.

        Emits the ``reenters_safety`` ADG edge.
        



## Function: audit_log

**Parameters**: self
**Returns**: list[PolicyCheckResult]


## Function: allow_count

**Parameters**: self
**Returns**: int


## Function: deny_count

**Parameters**: self
**Returns**: int


## Function: escalation_count

**Parameters**: self
**Returns**: int


## Function: decorator

**Parameters**: fn
**Returns**: Callable


## Function: wrapper



## Usage Examples

### Class Usage

```python
# Using PolicyVerdict
policyverdict = PolicyVerdict()
```

```python
# Using PolicyCheckResult
policycheckresult = PolicyCheckResult()
policycheckresult.allowed()
policycheckresult.needs_escalation()
```

```python
# Using PolicyViolationError
policyviolationerror = PolicyViolationError()
```

### Function Usage

```python
# Using get_policy_enforcement_point
result = get_policy_enforcement_point(policy_hash)
```

```python
# Using reset_policy_enforcement_point
result = reset_policy_enforcement_point()
```

```python
# Using allowed
result = allowed()
```



---
**Generated**: 2026-03-26T09:39:04.898878
**Type**: api_reference
**Quality**: comprehensive
