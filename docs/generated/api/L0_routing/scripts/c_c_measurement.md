# API Documentation: c_c_measurement

**Target Audience**: developers, api_users

# c_c_measurement API Documentation

**File**: `c_c_measurement.py`
**Classes**: 1
**Functions**: 8

## Classes

- **CCMeasurement**

## Functions

- **main**
- **__init__**
- **measure_cc** -> dict
- **analyze_results** -> dict
- **print_report**
- **save_report**
- **compare_reports** -> dict
- **print_comparison**


## Class: CCMeasurement

**Description**: Measure and report cyclomatic complexity metrics.

### Methods

#### __init__
**Parameters**: self, project_root
**Description**: Initialize measurement tool.

#### measure_cc
**Parameters**: self, target_path
**Returns**: dict
**Description**: 
        Measure cyclomatic complexity using radon.

        Args:
            target_path: Path to measure (relative to project root)

        Returns:
            Dictionary with CC metrics
        

#### analyze_results
**Parameters**: self, data
**Returns**: dict
**Description**: 
        Analyze CC data and extract metrics.

        Args:
            data: Raw radon output

        Returns:
            Analyzed metrics
        

#### print_report
**Parameters**: self, metrics, title
**Description**: 
        Print formatted CC report.

        Args:
            metrics: Analyzed metrics
            title: Report title
        

#### save_report
**Parameters**: self, metrics, output_file
**Description**: 
        Save metrics to JSON file.

        Args:
            metrics: Analyzed metrics
            output_file: Output file path
        

#### compare_reports
**Parameters**: self, baseline, current
**Returns**: dict
**Description**: 
        Compare two CC reports.

        Args:
            baseline: Baseline metrics
            current: Current metrics

        Returns:
            Comparison results
        

#### print_comparison
**Parameters**: self, baseline, current, title
**Description**: 
        Print comparison report.

        Args:
            baseline: Baseline metrics
            current: Current metrics
            title: Report title
        



## Function: main

**Description**: Main entry point.



## Function: __init__

**Parameters**: self, project_root
**Description**: Initialize measurement tool.



## Function: measure_cc

**Parameters**: self, target_path
**Returns**: dict
**Description**: 
        Measure cyclomatic complexity using radon.

        Args:
            target_path: Path to measure (relative to project root)

        Returns:
            Dictionary with CC metrics
        



## Function: analyze_results

**Parameters**: self, data
**Returns**: dict
**Description**: 
        Analyze CC data and extract metrics.

        Args:
            data: Raw radon output

        Returns:
            Analyzed metrics
        



## Function: print_report

**Parameters**: self, metrics, title
**Description**: 
        Print formatted CC report.

        Args:
            metrics: Analyzed metrics
            title: Report title
        



## Function: save_report

**Parameters**: self, metrics, output_file
**Description**: 
        Save metrics to JSON file.

        Args:
            metrics: Analyzed metrics
            output_file: Output file path
        



## Function: compare_reports

**Parameters**: self, baseline, current
**Returns**: dict
**Description**: 
        Compare two CC reports.

        Args:
            baseline: Baseline metrics
            current: Current metrics

        Returns:
            Comparison results
        



## Function: print_comparison

**Parameters**: self, baseline, current, title
**Description**: 
        Print comparison report.

        Args:
            baseline: Baseline metrics
            current: Current metrics
            title: Report title
        



## Usage Examples

### Class Usage

```python
# Using CCMeasurement
ccmeasurement = CCMeasurement()
ccmeasurement.measure_cc()
ccmeasurement.analyze_results()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using measure_cc
result = measure_cc(target_path)
```



---
**Generated**: 2026-03-26T09:39:02.843266
**Type**: api_reference
**Quality**: comprehensive
