# API Documentation: validation_utils_util

**Target Audience**: developers, api_users

# validation_utils_util API Documentation

**File**: `validation_utils_util.py`
**Classes**: 0
**Functions**: 3


## Functions

- **validate_email** -> bool
- **validate_url** -> bool
- **sanitize_filename** -> str


## Function: validate_email

**Parameters**: email
**Returns**: bool
**Description**: Simple email validation.



## Function: validate_url

**Parameters**: url
**Returns**: bool
**Description**: Simple URL validation.



## Function: sanitize_filename

**Parameters**: filename
**Returns**: str
**Description**: Sanitize filename for filesystem operations.



## Usage Examples

### Function Usage

```python
# Using validate_email
result = validate_email(email)
```

```python
# Using validate_url
result = validate_url(url)
```

```python
# Using sanitize_filename
result = sanitize_filename(filename)
```



---
**Generated**: 2026-03-26T09:39:05.713256
**Type**: api_reference
**Quality**: comprehensive
