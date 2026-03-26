# API Documentation: add_test_coverage_util

**Target Audience**: developers, api_users

# add_test_coverage_util API Documentation

**File**: `add_test_coverage_util.py`
**Classes**: 0
**Functions**: 6


## Functions

- **has_tests**
- **add_test_to_file** -> bool
- **main**
- **find_class_end** -> tuple[int, int]
- **add_test_method_to_class** -> bool
- **main**


## Function: has_tests

**Parameters**: path, content


## Function: add_test_to_file

**Parameters**: filepath, class_name
**Returns**: bool
**Description**: Add _run_self_tests to a class in a file.



## Function: main

**Description**: Add test coverage to all agents missing tests.



## Function: find_class_end

**Parameters**: content, class_name
**Returns**: tuple[int, int]
**Description**: Find the end position of a class definition.



## Function: add_test_method_to_class

**Parameters**: filepath, class_name
**Returns**: bool
**Description**: Add _run_self_tests method to a class if it doesn't exist.



## Function: main

**Description**: Add test coverage to all agents missing tests.



## Usage Examples

### Function Usage

```python
# Using has_tests
result = has_tests(path, content)
```

```python
# Using add_test_to_file
result = add_test_to_file(filepath, class_name)
```

```python
# Using main
result = main()
```



---
**Generated**: 2026-03-26T09:39:03.490608
**Type**: api_reference
**Quality**: comprehensive
