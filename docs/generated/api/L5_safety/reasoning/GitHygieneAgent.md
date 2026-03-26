# API Documentation: GitHygieneAgent

**Target Audience**: developers, api_users

# GitHygieneAgent API Documentation

**File**: `GitHygieneAgent.py`
**Classes**: 1
**Functions**: 8

## Classes

- **GitHygieneAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__** -> None
- **_run_git** -> str
- **_get_stale_branches** -> list[dict[str, Any]]
- **_get_large_files** -> list[dict]
- **_get_repo_status** -> dict
- **heal_repository** -> dict[str, int]
- **heal** -> dict
- **safe_git_execute**


## Class: GitHygieneAgent

**Description**: L5 Safety agent that enforces Git repository hygiene.

    This batch agent audits repository health by detecting stale branches,
    large files in history, and uncommitted/unpushed changes.

    Attributes:
        project_root: Root directory of the Git repository.
        ctx: Execution context with reporting capabilities.
        dry_run: If True, only report what would be done (default: True).
        stale_days: Days after which a branch is considered stale (default: 90).
        large_file_mb: Size threshold in MB for large files (default: 10).

    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, project_root, ctx
**Returns**: None
**Description**: Initialize the Git hygiene agent.

        Args:
            project_root: Root directory of the Git repository.
            ctx: Execution context with optional report() method.
        

#### _run_git
**Parameters**: self, cmd
**Returns**: str
**Description**: Run a git command and return stdout.

        Args:
            cmd: Git command arguments (without 'git' prefix).
            **kwargs: Additional arguments passed to safe_git_execute.

        Returns:
            Command stdout if successful, empty string otherwise.
        

#### _get_stale_branches
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Find branches with no commits in the last N days.

        Returns:
            List of dictionaries with branch info:
                - branch: Branch name
                - age_days: Days since last commit
        

#### _get_large_files
**Parameters**: self
**Returns**: list[dict]
**Description**: Find large files in Git history (>10MB).

#### _get_repo_status
**Parameters**: self
**Returns**: dict
**Description**: Check for uncommitted and unpushed changes.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Audit and heal Git repository hygiene issues.

        Scans for stale branches, large files, uncommitted changes,
        and unpushed commits. Can clean up stale branches when execute=True.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal git hygiene violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (stale_branch, uncommitted, unpushed)
                - path: Path to the repository
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: __init__

**Parameters**: self, project_root, ctx
**Returns**: None
**Description**: Initialize the Git hygiene agent.

        Args:
            project_root: Root directory of the Git repository.
            ctx: Execution context with optional report() method.
        



## Function: _run_git

**Parameters**: self, cmd
**Returns**: str
**Description**: Run a git command and return stdout.

        Args:
            cmd: Git command arguments (without 'git' prefix).
            **kwargs: Additional arguments passed to safe_git_execute.

        Returns:
            Command stdout if successful, empty string otherwise.
        



## Function: _get_stale_branches

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Find branches with no commits in the last N days.

        Returns:
            List of dictionaries with branch info:
                - branch: Branch name
                - age_days: Days since last commit
        



## Function: _get_large_files

**Parameters**: self
**Returns**: list[dict]
**Description**: Find large files in Git history (>10MB).



## Function: _get_repo_status

**Parameters**: self
**Returns**: dict
**Description**: Check for uncommitted and unpushed changes.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Audit and heal Git repository hygiene issues.

        Scans for stale branches, large files, uncommitted changes,
        and unpushed commits. Can clean up stale branches when execute=True.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal git hygiene violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (stale_branch, uncommitted, unpushed)
                - path: Path to the repository
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: safe_git_execute

**Parameters**: cmd
**Description**: Stub safe_git_execute when security_util is not available.



## Usage Examples

### Class Usage

```python
# Using GitHygieneAgent
githygieneagent = GitHygieneAgent()
githygieneagent.heal_repository()
githygieneagent.heal()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root, ctx)
```

```python
# Using _run_git
result = _run_git(cmd)
```

```python
# Using _get_stale_branches
result = _get_stale_branches()
```



---
**Generated**: 2026-03-26T09:39:05.220322
**Type**: api_reference
**Quality**: comprehensive
