# API Documentation: shift_report_types

**Target Audience**: developers, api_users

# shift_report_types API Documentation

**File**: `shift_report_types.py`
**Classes**: 2
**Functions**: 7

## Classes

- **ShiftReport**
- **CovariateShiftDetector**

## Functions

- **_compute_psi** -> float
- **_compute_mmd_rbf** -> float
- **create** -> ShiftReport
- **skipped** -> ShiftReport
- **_bin_proportions** -> list[float]
- **_rbf** -> float
- **detect_shift** -> ShiftReport


## Class: ShiftReport

**Description**: Formal drift detection report.

    Included in LearningArtifact for replay and audit integrity.
    

### Methods

#### create
**Returns**: ShiftReport
**Description**: Construct with frozen timestamp.

#### skipped
**Parameters**: reason
**Returns**: ShiftReport
**Description**: Create a report for skipped detection.



## Class: CovariateShiftDetector

**Description**: Multivariate drift detector with MMD + PSI.

    Usage::

        detector = CovariateShiftDetector(
            feature_names=["accuracy", "latency"]
        )
        report = detector.detect_shift(
            baseline=[[0.9, 10], [0.8, 12]],
            treatment=[[0.5, 50], [0.4, 55]],
        )
        assert report.joint_shift is True
    

### Methods

#### detect_shift
**Parameters**: self, baseline, treatment, threshold
**Returns**: ShiftReport
**Description**: Run multivariate drift detection.

        Returns a ShiftReport with per-feature and joint flags.
        



## Function: _compute_psi

**Parameters**: baseline, treatment, bins
**Returns**: float
**Description**: Compute Population Stability Index between two distributions.

    Uses equal-width binning.  Clips to avoid log(0).
    



## Function: _compute_mmd_rbf

**Parameters**: baseline, treatment, gamma
**Returns**: float
**Description**: Compute MMD with RBF kernel (simplified).

    For production, consider a proper kernel library.
    This implementation is correct for governance testing.
    



## Function: create

**Returns**: ShiftReport
**Description**: Construct with frozen timestamp.



## Function: skipped

**Parameters**: reason
**Returns**: ShiftReport
**Description**: Create a report for skipped detection.



## Function: _bin_proportions

**Parameters**: data
**Returns**: list[float]


## Function: _rbf

**Parameters**: x, y
**Returns**: float


## Function: detect_shift

**Parameters**: self, baseline, treatment, threshold
**Returns**: ShiftReport
**Description**: Run multivariate drift detection.

        Returns a ShiftReport with per-feature and joint flags.
        



## Usage Examples

### Class Usage

```python
# Using ShiftReport
shiftreport = ShiftReport()
shiftreport.create()
shiftreport.skipped()
```

```python
# Using CovariateShiftDetector
covariateshiftdetector = CovariateShiftDetector()
covariateshiftdetector.detect_shift()
```

### Function Usage

```python
# Using _compute_psi
result = _compute_psi(baseline, treatment)
```

```python
# Using _compute_mmd_rbf
result = _compute_mmd_rbf(baseline, treatment)
```

```python
# Using create
result = create()
```



---
**Generated**: 2026-03-26T09:39:05.569567
**Type**: api_reference
**Quality**: comprehensive
