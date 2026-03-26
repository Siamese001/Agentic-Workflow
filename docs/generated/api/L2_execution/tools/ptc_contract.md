# API Documentation: ptc_contract

**Target Audience**: developers, api_users

# ptc_contract API Documentation

**File**: `ptc_contract.py`
**Classes**: 4
**Functions**: 5

## Classes

- **PTCContractViolation** (inherits from RuntimeError)
- **PTCBytesCapExceeded** (inherits from PTCContractViolation)
- **PTCUnsignedEnvelopeError** (inherits from PTCContractViolation)
- **PTCContractEnforcer**

## Functions

- **redact_output** -> str
- **__post_init__** -> None
- **pre_execute** -> None
- **post_execute** -> str
- **violation_count** -> int


## Class: PTCContractViolation

**Description**: Raised when a PTC runtime contract is violated.

**Inherits from**: RuntimeError



## Class: PTCBytesCapExceeded

**Description**: Raised when PTC output exceeds the hard byte cap.

**Inherits from**: PTCContractViolation



## Class: PTCUnsignedEnvelopeError

**Description**: Raised when PTC execution is attempted with an unsigned envelope.

**Inherits from**: PTCContractViolation



## Class: PTCContractEnforcer

**Description**: Enforces PTC runtime contracts before and after tool execution.

    Usage
    -----
    enforcer = PTCContractEnforcer(secret=b"shared-secret")
    enforcer.pre_execute(envelope)           # raises if envelope not valid
    safe_output = enforcer.post_execute(raw_output)  # redact + cap check
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### pre_execute
**Parameters**: self, envelope
**Returns**: None
**Description**: Verify envelope signature before any side-effect.

        Raises PTCUnsignedEnvelopeError or SignatureVerificationError on failure.
        

#### post_execute
**Parameters**: self, raw_output
**Returns**: str
**Description**: Redact secrets and enforce byte cap on PTC stdout output.

        Raises PTCBytesCapExceeded if the redacted output exceeds byte_cap.
        Returns the safe, redacted output string.
        

#### violation_count
**Parameters**: self
**Returns**: int
**Description**: Total number of contract violations detected by this enforcer.



## Function: redact_output

**Parameters**: text
**Returns**: str
**Description**: Apply deterministic redaction to *text*.

    Patterns are applied in fixed declaration order for determinism.
    Returns the redacted string.
    



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: pre_execute

**Parameters**: self, envelope
**Returns**: None
**Description**: Verify envelope signature before any side-effect.

        Raises PTCUnsignedEnvelopeError or SignatureVerificationError on failure.
        



## Function: post_execute

**Parameters**: self, raw_output
**Returns**: str
**Description**: Redact secrets and enforce byte cap on PTC stdout output.

        Raises PTCBytesCapExceeded if the redacted output exceeds byte_cap.
        Returns the safe, redacted output string.
        



## Function: violation_count

**Parameters**: self
**Returns**: int
**Description**: Total number of contract violations detected by this enforcer.



## Usage Examples

### Class Usage

```python
# Using PTCContractViolation
ptccontractviolation = PTCContractViolation()
```

```python
# Using PTCBytesCapExceeded
ptcbytescapexceeded = PTCBytesCapExceeded()
```

```python
# Using PTCUnsignedEnvelopeError
ptcunsignedenvelopeerror = PTCUnsignedEnvelopeError()
```

### Function Usage

```python
# Using redact_output
result = redact_output(text)
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using pre_execute
result = pre_execute(envelope)
```



---
**Generated**: 2026-03-26T09:39:03.913628
**Type**: api_reference
**Quality**: comprehensive
