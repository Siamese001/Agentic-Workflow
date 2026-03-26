# API Documentation: conf_calib_gate

**Target Audience**: developers, api_users

# conf_calib_gate API Documentation

**File**: `conf_calib_gate.py`
**Classes**: 3
**Functions**: 1

## Classes

- **RiskLevel** (inherits from Enum)
- **RiskDecision**
- **ConfCalibRiskGate**

## Functions

- **evaluate** -> RiskDecision


## Class: RiskLevel

**Description**: Risk level enumeration for structured decision making.

**Inherits from**: Enum



## Class: RiskDecision

**Description**: Structured risk decision with deterministic reasons.



## Class: ConfCalibRiskGate

**Description**: 
    CONF_CALIB Risk Gate for deterministic risk evaluation.

    Evaluates payload and D0 injections to produce structured RiskDecision.
    No imports from L0/L2, no wall-clock usage.
    

### Methods

#### evaluate
**Parameters**: self
**Returns**: RiskDecision
**Description**: 
        Evaluate risk for given payload and D0 injections.

        Deterministic rules (no ML, no clocks):
        - Start with LOW/allow=True
        - If payload sanitized => at least MEDIUM, reason "SANITIZED_INPUT"
        - If >=5 check_ids => at least MEDIUM, reason "MANY_CHECK_IDS"
        - If D0 contains "DENY_EXECUTION" => HIGH and allow=False, reason "D0_DENY_EXECUTION"
        - Always sort reasons lexicographically

        Args:
            payload_like: Object to evaluate (must not be mutated)
            d0_injections: D0 injection string to evaluate

        Returns:
            Structured RiskDecision with deterministic reasons
        



## Function: evaluate

**Parameters**: self
**Returns**: RiskDecision
**Description**: 
        Evaluate risk for given payload and D0 injections.

        Deterministic rules (no ML, no clocks):
        - Start with LOW/allow=True
        - If payload sanitized => at least MEDIUM, reason "SANITIZED_INPUT"
        - If >=5 check_ids => at least MEDIUM, reason "MANY_CHECK_IDS"
        - If D0 contains "DENY_EXECUTION" => HIGH and allow=False, reason "D0_DENY_EXECUTION"
        - Always sort reasons lexicographically

        Args:
            payload_like: Object to evaluate (must not be mutated)
            d0_injections: D0 injection string to evaluate

        Returns:
            Structured RiskDecision with deterministic reasons
        



## Usage Examples

### Class Usage

```python
# Using RiskLevel
risklevel = RiskLevel()
```

```python
# Using RiskDecision
riskdecision = RiskDecision()
```

```python
# Using ConfCalibRiskGate
confcalibriskgate = ConfCalibRiskGate()
confcalibriskgate.evaluate()
```

### Function Usage

```python
# Using evaluate
result = evaluate()
```



---
**Generated**: 2026-03-26T09:39:04.791232
**Type**: api_reference
**Quality**: comprehensive
