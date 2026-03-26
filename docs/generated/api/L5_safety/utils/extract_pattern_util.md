# API Documentation: extract_pattern_util

**Target Audience**: developers, api_users

# extract_pattern_util API Documentation

**File**: `extract_pattern_util.py`
**Classes**: 0
**Functions**: 4


## Functions

- **extract_class_with_context** -> tuple[str, int, int]
- **create_pattern_enforcer_file**
- **update_source_file**
- **main**


## Function: extract_class_with_context

**Parameters**: content, class_name
**Returns**: tuple[str, int, int]
**Description**: Extract class source with preceding comments.



## Function: create_pattern_enforcer_file

**Parameters**: class_source
**Description**: Create sovereign file for PatternEnforcerAgent.



## Function: update_source_file

**Parameters**: source_file
**Description**: Remove PatternEnforcerAgent and SubAtomicAgent stub, add proper import.



## Function: main



## Usage Examples

### Function Usage

```python
# Using extract_class_with_context
result = extract_class_with_context(content, class_name)
```

```python
# Using create_pattern_enforcer_file
result = create_pattern_enforcer_file(class_source)
```

```python
# Using update_source_file
result = update_source_file(source_file)
```



---
**Generated**: 2026-03-26T09:39:05.634405
**Type**: api_reference
**Quality**: comprehensive
