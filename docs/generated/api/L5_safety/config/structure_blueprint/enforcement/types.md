# API Documentation: types

**Target Audience**: developers, api_users

# types API Documentation

**File**: `types.py`
**Classes**: 3
**Functions**: 3

## Classes

- **Violation** (inherits from TypedDict)
- **EnforcementResult** (inherits from TypedDict)
- **EnforcementReport** (inherits from TypedDict)

## Functions

- **make_result** -> EnforcementResult
- **make_report** -> EnforcementReport
- **emit_report_json** -> dict[str, Any]


## Class: Violation

**Description**: A single enforcement violation.

**Inherits from**: TypedDict



## Class: EnforcementResult

**Description**: Result from a single enforcement module's check() call.

**Inherits from**: TypedDict



## Class: EnforcementReport

**Description**: Aggregated report from all enforcement modules.

**Inherits from**: TypedDict



## Function: make_result

**Parameters**: name, violations, stats
**Returns**: EnforcementResult
**Description**: Create an EnforcementResult with computed passed status.



## Function: make_report

**Parameters**: results
**Returns**: EnforcementReport
**Description**: Aggregate individual results into a full report.



## Function: emit_report_json

**Parameters**: report
**Returns**: dict[str, Any]
**Description**: Convert report to JSON-serializable dict (identity for TypedDict).



## Usage Examples

### Class Usage

```python
# Using Violation
violation = Violation()
```

```python
# Using EnforcementResult
enforcementresult = EnforcementResult()
```

```python
# Using EnforcementReport
enforcementreport = EnforcementReport()
```

### Function Usage

```python
# Using make_result
result = make_result(name, violations)
```

```python
# Using make_report
result = make_report(results)
```

```python
# Using emit_report_json
result = emit_report_json(report)
```



---
**Generated**: 2026-03-26T09:39:05.987930
**Type**: api_reference
**Quality**: comprehensive
