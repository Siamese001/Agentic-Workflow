# API Documentation: scan_testing_compliance_util

**Target Audience**: developers, api_users

# scan_testing_compliance_util API Documentation

**File**: `scan_testing_compliance_util.py`
**Classes**: 0
**Functions**: 6


## Functions

- **extract_bases** -> set[str]
- **has_method** -> bool
- **analyze_agent** -> dict
- **regenerate_discovery_json**
- **load_from_canonical_json** -> list[dict]
- **main**


## Function: extract_bases

**Parameters**: class_node
**Returns**: set[str]
**Description**: Extract base class names from class definition.



## Function: has_method

**Parameters**: class_node, method_name
**Returns**: bool
**Description**: Check if class has a specific method.



## Function: analyze_agent

**Parameters**: class_node, file_path
**Returns**: dict
**Description**: Analyze a single agent class for testing compliance.



## Function: regenerate_discovery_json

**Description**: Regenerate the canonical agent discovery JSON.



## Function: load_from_canonical_json

**Returns**: list[dict]
**Description**: Load agents from canonical JSON, regenerating if needed.



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
# Using analyze_agent
result = analyze_agent(class_node, file_path)
```



---
**Generated**: 2026-03-26T09:39:03.255961
**Type**: api_reference
**Quality**: comprehensive
