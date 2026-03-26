# API Documentation: verify_agent_status_util

**Target Audience**: developers, api_users

# verify_agent_status_util API Documentation

**File**: `verify_agent_status_util.py`
**Classes**: 0
**Functions**: 5


## Functions

- **extract_bases** -> set[str]
- **has_method** -> bool
- **analyze_file** -> dict[str, Any]
- **print_report** -> None
- **main**


## Function: extract_bases

**Parameters**: class_node
**Returns**: set[str]
**Description**: Extract base class names from class definition.



## Function: has_method

**Parameters**: class_node, method_name
**Returns**: bool
**Description**: Check if class has a specific method.



## Function: analyze_file

**Parameters**: file_path
**Returns**: dict[str, Any]
**Description**: Analyze a Python file for agent characteristics.



## Function: print_report

**Parameters**: results
**Returns**: None
**Description**: Print formatted verification report.



## Function: main



## Usage Examples

### Function Usage

```python
# Using extract_bases
result = extract_bases(class_node)
```

```python
# Using has_method
result = has_method(class_node, method_name)
```

```python
# Using analyze_file
result = analyze_file(file_path)
```



---
**Generated**: 2026-03-26T09:39:03.290648
**Type**: api_reference
**Quality**: comprehensive
