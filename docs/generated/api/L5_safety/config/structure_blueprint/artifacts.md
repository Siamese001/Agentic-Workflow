# API Documentation: artifacts

**Target Audience**: developers, api_users

# artifacts API Documentation

**File**: `artifacts.py`
**Classes**: 0
**Functions**: 13


## Functions

- **get_correct_app_folder** -> str | None
- **get_correct_app_path** -> str | None
- **has_forbidden_layer_prefix** -> str | None
- **get_app_specific_patterns_compiled** -> list[Pattern]
- **get_forbidden_backup_patterns_compiled** -> list[Pattern]
- **get_forbidden_ephemeral_patterns_compiled** -> list[Pattern]
- **get_ephemeral_exemption_patterns_compiled** -> list[Pattern]
- **is_app_specific_file** -> bool
- **is_broken_backup_file** -> bool
- **APP_SPECIFIC_PATTERNS** -> list[Pattern]
- **FORBIDDEN_BACKUP_PATTERNS** -> list[Pattern]
- **validate_artifact_routing** -> tuple[bool, str | None, str | None]
- **check_forbidden_signals** -> str | None


## Function: get_correct_app_folder

**Parameters**: filename
**Returns**: str | None
**Description**: Return the correct root app folder for a file based on prefix.



## Function: get_correct_app_path

**Parameters**: filename
**Returns**: str | None
**Description**: Return the full recommended path for app-specific files.



## Function: has_forbidden_layer_prefix

**Parameters**: filename
**Returns**: str | None
**Description**: Check if filename starts with a forbidden layer/priority prefix.



## Function: get_app_specific_patterns_compiled

**Returns**: list[Pattern]
**Description**: Compile and cache app-specific patterns.



## Function: get_forbidden_backup_patterns_compiled

**Returns**: list[Pattern]
**Description**: Compile and cache forbidden backup patterns.



## Function: get_forbidden_ephemeral_patterns_compiled

**Returns**: list[Pattern]
**Description**: Compile and cache forbidden ephemeral patterns.



## Function: get_ephemeral_exemption_patterns_compiled

**Returns**: list[Pattern]
**Description**: Compile and cache ephemeral exemption patterns.



## Function: is_app_specific_file

**Parameters**: filename
**Returns**: bool
**Description**: Check if a file should be in an app folder, not agentic_core.



## Function: is_broken_backup_file

**Parameters**: filename
**Returns**: bool
**Description**: Check if filename matches broken backup pattern.



## Function: APP_SPECIFIC_PATTERNS

**Returns**: list[Pattern]
**Description**: Backward compatibility accessor for compiled patterns.



## Function: FORBIDDEN_BACKUP_PATTERNS

**Returns**: list[Pattern]
**Description**: Backward compatibility accessor for compiled patterns.



## Function: validate_artifact_routing

**Parameters**: filename, content
**Returns**: tuple[bool, str | None, str | None]
**Description**: 
    Validate file against ARTIFACT_ROUTING_MAP negative logic.

    Implements HARD REJECT for files that match forbidden_extensions or forbidden_keywords
    ONLY when they would otherwise match the positive signals for that destination.
    This prevents gravity leakage where code files get misclassified as reports/logs/data.

    Args:
        filename: Name of the file to validate
        content: Optional file content for keyword checking

    Returns:
        Tuple of (is_valid, matched_destination, rejection_reason)
        - is_valid: False if file matches forbidden signals (HARD REJECT)
        - matched_destination: Destination path if positive match found
        - rejection_reason: Reason for rejection if is_valid is False

    Example:
        >>> validate_artifact_routing("test_report.py", "def main():")
        (False, None, "Forbidden extension .py for destination docs/reports")

        >>> validate_artifact_routing("audit_results.md", "# Assessment Report")
        (True, "docs/reports", None)
    



## Function: check_forbidden_signals

**Parameters**: filename, content
**Returns**: str | None
**Description**: 
    Quick check for forbidden signals across all routing rules.

    Returns rejection reason if file matches any forbidden_extensions or forbidden_keywords,
    None otherwise.

    This is a fast-path check for agents that only need to know if a file is forbidden,
    without needing the full routing destination.

    Args:
        filename: Name of the file to check
        content: Optional file content for keyword checking

    Returns:
        Rejection reason string if forbidden, None if allowed
    



## Usage Examples

### Function Usage

```python
# Using get_correct_app_folder
result = get_correct_app_folder(filename)
```

```python
# Using get_correct_app_path
result = get_correct_app_path(filename)
```

```python
# Using has_forbidden_layer_prefix
result = has_forbidden_layer_prefix(filename)
```



---
**Generated**: 2026-03-26T09:39:05.907556
**Type**: api_reference
**Quality**: comprehensive
