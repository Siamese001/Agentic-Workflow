# API Documentation: validate_drilldown_util

**Target Audience**: developers, api_users

# validate_drilldown_util API Documentation

**File**: `validate_drilldown_util.py`
**Classes**: 0
**Functions**: 3


## Functions

- **extract_dashboard_data** -> list[dict[str, Any]]
- **validate_drilldown_infrastructure** -> dict[str, bool]
- **main**


## Function: extract_dashboard_data

**Parameters**: html
**Returns**: list[dict[str, Any]]
**Description**: Extract dashboardData JSON from HTML safely.



## Function: validate_drilldown_infrastructure

**Parameters**: html
**Returns**: dict[str, bool]
**Description**: Validate that drill-down infrastructure exists.



## Function: main



## Usage Examples

### Function Usage

```python
# Using extract_dashboard_data
result = extract_dashboard_data(html)
```

```python
# Using validate_drilldown_infrastructure
result = validate_drilldown_infrastructure(html)
```

```python
# Using main
result = main()
```



---
**Generated**: 2026-03-26T09:39:03.284419
**Type**: api_reference
**Quality**: comprehensive
