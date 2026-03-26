# API Documentation: injection_regression_gate

**Target Audience**: developers, api_users

# injection_regression_gate API Documentation

**File**: `injection_regression_gate.py`
**Classes**: 3
**Functions**: 2

## Classes

- **RegressionThresholds**
- **InjectionMetrics**
- **InjectionRegressionError** (inherits from PermissionError)

## Functions

- **evaluate_against_baseline** -> None
- **check_regression_compliance** -> bool


## Class: RegressionThresholds

**Description**: Thresholds for injection regression detection.



## Class: InjectionMetrics

**Description**: Deterministic injection detection metrics.



## Class: InjectionRegressionError

**Description**: Raised when injection regression is detected.

**Inherits from**: PermissionError



## Function: evaluate_against_baseline

**Parameters**: current_result, baseline_result, thresholds
**Returns**: None
**Description**: Evaluate current injection results against baseline for regression detection.

    Args:
        current_result: Current injection evaluation results
        baseline_result: Baseline injection evaluation results
        thresholds: Optional custom thresholds

    Raises:
        InjectionRegressionError: If regression detected
    



## Function: check_regression_compliance

**Parameters**: current_metrics, baseline_metrics, thresholds
**Returns**: bool
**Description**: Check if current metrics comply with baseline thresholds.

    Args:
        current_metrics: Current injection metrics
        baseline_metrics: Baseline injection metrics
        thresholds: Optional custom thresholds

    Returns:
        True if compliant (no regression), False otherwise
    



## Usage Examples

### Class Usage

```python
# Using RegressionThresholds
regressionthresholds = RegressionThresholds()
```

```python
# Using InjectionMetrics
injectionmetrics = InjectionMetrics()
```

```python
# Using InjectionRegressionError
injectionregressionerror = InjectionRegressionError()
```

### Function Usage

```python
# Using evaluate_against_baseline
result = evaluate_against_baseline(current_result, baseline_result)
```

```python
# Using check_regression_compliance
result = check_regression_compliance(current_metrics, baseline_metrics)
```



---
**Generated**: 2026-03-26T09:39:05.464629
**Type**: api_reference
**Quality**: comprehensive
