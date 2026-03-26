# API Documentation: gatekeeper_lock_util

**Target Audience**: developers, api_users

# gatekeeper_lock_util API Documentation

**File**: `gatekeeper_lock_util.py`
**Classes**: 0
**Functions**: 5


## Functions

- **get_staged_files** -> list[str]
- **get_commit_message** -> str
- **check_env_bypass** -> bool
- **check_commit_message_override** -> bool
- **main** -> int


## Function: get_staged_files

**Returns**: list[str]
**Description**: Get list of staged files from git.



## Function: get_commit_message

**Parameters**: commit_msg_file
**Returns**: str
**Description**: Read commit message from file if provided.



## Function: check_env_bypass

**Returns**: bool
**Description**: Check if bypass environment variable is set.



## Function: check_commit_message_override

**Parameters**: commit_message
**Returns**: bool
**Description**: Check if commit message contains override token.



## Function: main

**Returns**: int
**Description**: TODO: Add documentation for main.



## Usage Examples

### Function Usage

```python
# Using get_staged_files
result = get_staged_files()
```

```python
# Using get_commit_message
result = get_commit_message(commit_msg_file)
```

```python
# Using check_env_bypass
result = check_env_bypass()
```



---
**Generated**: 2026-03-26T09:39:03.156157
**Type**: api_reference
**Quality**: comprehensive
