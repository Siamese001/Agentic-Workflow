# API Documentation: PreCommitSovereignAgent

**Target Audience**: developers, api_users

# PreCommitSovereignAgent API Documentation

**File**: `PreCommitSovereignAgent.py`
**Classes**: 2
**Functions**: 16

## Classes

- **ViolationReport**
- **PreCommitSovereignAgent** (inherits from SovereignBaseAgent, L0RoutingBase)

## Functions

- **purge_repository_cache** -> None
- **main** -> Any
- **heal_repository** -> dict[str, Any]
- **__init__** -> None
- **get_staged_files** -> list[str]
- **_create_empty_result** -> dict[str, Any]
- **_create_error_result** -> dict[str, Any]
- **_paths_match** -> bool
- **_filter_staged_violations** -> list[ViolationReport]
- **_print_violations** -> None
- **validate_staged_files** -> dict[str, Any]
- **validate_sovereignty** -> int
- **_report_failure** -> Any
- **install_hook** -> bool
- **uninstall_hook** -> bool
- **heal** -> dict[str, Any]


## Class: ViolationReport

**Description**: Report of a single violation found during pre-commit scan.



## Class: PreCommitSovereignAgent

**Description**: 
    The 'Seal-Guard' of the Sovereign Architecture.
    Ensures compliance stays at 99.7%+ by blocking architectural rot at the source.

    Inherits from L0RoutingBaseAgent: HealerMixin, MCPHardenedMixin, L0DelegationTestingMixin

    This agent runs as a git pre-commit hook to prevent new violations from
    entering the codebase. It validates staged files against SSOT gravity laws.

    Usage:
        # As git hook
        agent = PreCommitSovereignAgent()
        sys.exit(agent.validate_sovereignty())

        # Standalone validation
        agent = PreCommitSovereignAgent()
        result = agent.validate_staged_files()
        if result["violations"]:
            print(f"Found {len(result['violations'])} violations")
    

**Inherits from**: SovereignBaseAgent, L0RoutingBase

### Methods

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        

#### __init__
**Parameters**: self, root_dir
**Returns**: None
**Description**: Initialize the Pre-Commit Sovereign Agent.

#### get_staged_files
**Parameters**: self
**Returns**: list[str]
**Description**: 
        Retrieves files currently staged in the git index.

        Returns:
            List of relative paths to staged Python files
        

#### _create_empty_result
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Create empty validation result for no staged files.

#### _create_error_result
**Parameters**: self, error
**Returns**: dict[str, Any]
**Description**: Create error validation result.

#### _paths_match
**Parameters**: self, path1, path2
**Returns**: bool
**Description**: Check if two paths refer to the same file.

#### _filter_staged_violations
**Parameters**: self, report, staged_files
**Returns**: list[ViolationReport]
**Description**: Filter violations to only those in staged files.

#### _print_violations
**Parameters**: self, violations
**Returns**: None
**Description**: Print violation details to console.

#### validate_staged_files
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Validate staged files for architectural compliance.

        Returns:
            Dictionary with validation results.
        

#### validate_sovereignty
**Parameters**: self
**Returns**: int
**Description**: 
        Main execution loop for git hook integration.

        Returns:
            0 if compliant (commit allowed)
            1 if violations found (commit blocked)
        

#### _report_failure
**Parameters**: self
**Returns**: Any
**Description**: Provides a detailed failure report and remediation instructions.

#### install_hook
**Parameters**: self
**Returns**: bool
**Description**: 
        Install this agent as a git pre-commit hook.

        Returns:
            True if installation successful, False otherwise
        

#### uninstall_hook
**Parameters**: self
**Returns**: bool
**Description**: 
        Remove the pre-commit hook.

        Returns:
            True if uninstallation successful, False otherwise
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by PreCommitSovereignAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Function: purge_repository_cache

**Parameters**: target_path
**Returns**: None
**Description**: Remove __pycache__ dirs and .pyc files under target_path.



## Function: main

**Returns**: Any
**Description**: CLI entry point for the Pre-Commit Sovereign Agent.



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        



## Function: __init__

**Parameters**: self, root_dir
**Returns**: None
**Description**: Initialize the Pre-Commit Sovereign Agent.



## Function: get_staged_files

**Parameters**: self
**Returns**: list[str]
**Description**: 
        Retrieves files currently staged in the git index.

        Returns:
            List of relative paths to staged Python files
        



## Function: _create_empty_result

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Create empty validation result for no staged files.



## Function: _create_error_result

**Parameters**: self, error
**Returns**: dict[str, Any]
**Description**: Create error validation result.



## Function: _paths_match

**Parameters**: self, path1, path2
**Returns**: bool
**Description**: Check if two paths refer to the same file.



## Function: _filter_staged_violations

**Parameters**: self, report, staged_files
**Returns**: list[ViolationReport]
**Description**: Filter violations to only those in staged files.



## Function: _print_violations

**Parameters**: self, violations
**Returns**: None
**Description**: Print violation details to console.



## Function: validate_staged_files

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Validate staged files for architectural compliance.

        Returns:
            Dictionary with validation results.
        



## Function: validate_sovereignty

**Parameters**: self
**Returns**: int
**Description**: 
        Main execution loop for git hook integration.

        Returns:
            0 if compliant (commit allowed)
            1 if violations found (commit blocked)
        



## Function: _report_failure

**Parameters**: self
**Returns**: Any
**Description**: Provides a detailed failure report and remediation instructions.



## Function: install_hook

**Parameters**: self
**Returns**: bool
**Description**: 
        Install this agent as a git pre-commit hook.

        Returns:
            True if installation successful, False otherwise
        



## Function: uninstall_hook

**Parameters**: self
**Returns**: bool
**Description**: 
        Remove the pre-commit hook.

        Returns:
            True if uninstallation successful, False otherwise
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by PreCommitSovereignAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Usage Examples

### Class Usage

```python
# Using ViolationReport
violationreport = ViolationReport()
```

```python
# Using PreCommitSovereignAgent
precommitsovereignagent = PreCommitSovereignAgent()
precommitsovereignagent.heal_repository()
precommitsovereignagent.get_staged_files()
```

### Function Usage

```python
# Using purge_repository_cache
result = purge_repository_cache(target_path)
```

```python
# Using main
result = main()
```

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```



---
**Generated**: 2026-03-26T09:39:05.349148
**Type**: api_reference
**Quality**: comprehensive
