# API Documentation: CredentialScannerAgent

**Target Audience**: developers, api_users

# CredentialScannerAgent API Documentation

**File**: `CredentialScannerAgent.py`
**Classes**: 2
**Functions**: 10

## Classes

- **CredentialMatch**
- **CredentialScannerAgent** (inherits from SovereignBaseAgent)

## Functions

- **__post_init__**
- **heal** -> dict[str, Any]
- **scan_for_credentials** -> dict[str, Any]
- **_get_scannable_files** -> list[Path]
- **_scan_file** -> None
- **_is_false_positive** -> bool
- **_generate_summary** -> dict[str, Any]
- **_generate_recommendations** -> list[str]
- **_match_to_dict** -> dict[str, Any]
- **heal_repository** -> dict[str, Any]


## Class: CredentialMatch

**Description**: Represents a detected credential in source code.



## Class: CredentialScannerAgent

**Description**: 
    L5 Safety Agent for detecting hardcoded credentials.

    Implements comprehensive regex patterns to identify:
    - API keys (generic, AWS, Azure, GCP, GitHub, Stripe, etc.)
    - Secret tokens and access tokens
    - Private keys (RSA, SSH, PGP)
    - Hardcoded passwords
    - Database connection strings
    - OAuth secrets

    Uses FileCache for efficient repository scanning.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Description**: Initialize the credential scanner.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for CredentialScannerAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        

#### scan_for_credentials
**Parameters**: self, target_path, file_patterns
**Returns**: dict[str, Any]
**Description**: 
        Scan for hardcoded credentials in the codebase.

        Args:
            target_path: Root path to scan (defaults to project root)
            file_patterns: Optional list of file patterns to scan

        Returns:
            Dict with scan results including matches, summary, and recommendations
        

#### _get_scannable_files
**Parameters**: self, root_path
**Returns**: list[Path]
**Description**: Get list of files to scan using FileCache.

#### _scan_file
**Parameters**: self, file_path
**Returns**: None
**Description**: Scan a single file for credentials.

#### _is_false_positive
**Parameters**: self, line, pattern_name
**Returns**: bool
**Description**: Check if a match is likely a false positive.

#### _generate_summary
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Generate summary statistics.

#### _generate_recommendations
**Parameters**: self
**Returns**: list[str]
**Description**: Generate security recommendations based on findings.

#### _match_to_dict
**Parameters**: self, match
**Returns**: dict[str, Any]
**Description**: Convert CredentialMatch to dictionary.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: Scan repository for hardcoded credentials and report findings.

        Scans Python files for hardcoded API keys, passwords, tokens, and
        other sensitive credentials. Credential violations require manual
        review and cannot be auto-fixed for safety reasons.

        Args:
            dry_run: If True, only report violations (default: True).
            execute: If True, generate detailed credential report.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        



## Function: __post_init__

**Parameters**: self
**Description**: Initialize the credential scanner.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        [HEALER PROTOCOL] Standardized healing interface for CredentialScannerAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        



## Function: scan_for_credentials

**Parameters**: self, target_path, file_patterns
**Returns**: dict[str, Any]
**Description**: 
        Scan for hardcoded credentials in the codebase.

        Args:
            target_path: Root path to scan (defaults to project root)
            file_patterns: Optional list of file patterns to scan

        Returns:
            Dict with scan results including matches, summary, and recommendations
        



## Function: _get_scannable_files

**Parameters**: self, root_path
**Returns**: list[Path]
**Description**: Get list of files to scan using FileCache.



## Function: _scan_file

**Parameters**: self, file_path
**Returns**: None
**Description**: Scan a single file for credentials.



## Function: _is_false_positive

**Parameters**: self, line, pattern_name
**Returns**: bool
**Description**: Check if a match is likely a false positive.



## Function: _generate_summary

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Generate summary statistics.



## Function: _generate_recommendations

**Parameters**: self
**Returns**: list[str]
**Description**: Generate security recommendations based on findings.



## Function: _match_to_dict

**Parameters**: self, match
**Returns**: dict[str, Any]
**Description**: Convert CredentialMatch to dictionary.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: Scan repository for hardcoded credentials and report findings.

        Scans Python files for hardcoded API keys, passwords, tokens, and
        other sensitive credentials. Credential violations require manual
        review and cannot be auto-fixed for safety reasons.

        Args:
            dry_run: If True, only report violations (default: True).
            execute: If True, generate detailed credential report.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        



## Usage Examples

### Class Usage

```python
# Using CredentialMatch
credentialmatch = CredentialMatch()
```

```python
# Using CredentialScannerAgent
credentialscanneragent = CredentialScannerAgent()
credentialscanneragent.heal()
credentialscanneragent.scan_for_credentials()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using heal
result = heal(violation)
```

```python
# Using scan_for_credentials
result = scan_for_credentials(target_path, file_patterns)
```



---
**Generated**: 2026-03-26T09:39:05.116252
**Type**: api_reference
**Quality**: comprehensive
