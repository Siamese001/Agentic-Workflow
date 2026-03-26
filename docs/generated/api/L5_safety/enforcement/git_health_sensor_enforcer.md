# API Documentation: git_health_sensor_enforcer

**Target Audience**: developers, api_users

# git_health_sensor_enforcer API Documentation

**File**: `git_health_sensor_enforcer.py`
**Classes**: 1
**Functions**: 8

## Classes

- **GitHealthSensor**

## Functions

- **check_git_health** -> DetectionSignal
- **__init__**
- **_run_git_command** -> tuple[int, str, str]
- **_check_uncommitted_changes** -> DetectionSignal | None
- **_check_merge_conflicts** -> DetectionSignal | None
- **_check_detached_head** -> DetectionSignal | None
- **check_repository_health** -> DetectionSignal
- **get_all_signals** -> list[DetectionSignal]


## Class: GitHealthSensor

**Description**: 
    Deterministic binary sensor for Git repository health.

    Performs the following checks:
    - Uncommitted Changes: Dirty working directory (Severity.HIGH)
    - Merge Conflicts: Active conflict markers (Severity.CRITICAL)
    - Detached HEAD: Risk to mission trace persistence (Severity.MEDIUM)
    

### Methods

#### __init__
**Parameters**: self, repo_root
**Description**: 
        Initialize the Git health sensor.

        Args:
            repo_root: Path to the Git repository root. If None, uses current directory.
        

#### _run_git_command
**Parameters**: self, args
**Returns**: tuple[int, str, str]
**Description**: 
        Run a git command and return exit code, stdout, stderr.

        Args:
            args: Git command arguments (without 'git' prefix)

        Returns:
            Tuple of (exit_code, stdout, stderr)
        

#### _check_uncommitted_changes
**Parameters**: self
**Returns**: DetectionSignal | None
**Description**: 
        Check for uncommitted changes in the working directory.

        Returns:
            DetectionSignal if dirty, None if clean
        

#### _check_merge_conflicts
**Parameters**: self
**Returns**: DetectionSignal | None
**Description**: 
        Check for active merge conflicts.

        Returns:
            DetectionSignal if conflicts exist, None if clean
        

#### _check_detached_head
**Parameters**: self
**Returns**: DetectionSignal | None
**Description**: 
        Check if repository is in detached HEAD state.

        Returns:
            DetectionSignal if detached, None if on branch
        

#### check_repository_health
**Parameters**: self
**Returns**: DetectionSignal
**Description**: 
        Perform all Git health checks and return the most severe signal.

        Returns:
            DetectionSignal with is_failure=True if any blocker found,
            or is_failure=False if repository is healthy.
        

#### get_all_signals
**Parameters**: self
**Returns**: list[DetectionSignal]
**Description**: 
        Get all detection signals (not just the most severe).

        Returns:
            List of all DetectionSignal objects for each check.
        



## Function: check_git_health

**Parameters**: repo_root
**Returns**: DetectionSignal
**Description**: 
    Convenience function to check Git repository health.

    Args:
        repo_root: Path to the Git repository root. If None, uses current directory.

    Returns:
        DetectionSignal with health status.
    



## Function: __init__

**Parameters**: self, repo_root
**Description**: 
        Initialize the Git health sensor.

        Args:
            repo_root: Path to the Git repository root. If None, uses current directory.
        



## Function: _run_git_command

**Parameters**: self, args
**Returns**: tuple[int, str, str]
**Description**: 
        Run a git command and return exit code, stdout, stderr.

        Args:
            args: Git command arguments (without 'git' prefix)

        Returns:
            Tuple of (exit_code, stdout, stderr)
        



## Function: _check_uncommitted_changes

**Parameters**: self
**Returns**: DetectionSignal | None
**Description**: 
        Check for uncommitted changes in the working directory.

        Returns:
            DetectionSignal if dirty, None if clean
        



## Function: _check_merge_conflicts

**Parameters**: self
**Returns**: DetectionSignal | None
**Description**: 
        Check for active merge conflicts.

        Returns:
            DetectionSignal if conflicts exist, None if clean
        



## Function: _check_detached_head

**Parameters**: self
**Returns**: DetectionSignal | None
**Description**: 
        Check if repository is in detached HEAD state.

        Returns:
            DetectionSignal if detached, None if on branch
        



## Function: check_repository_health

**Parameters**: self
**Returns**: DetectionSignal
**Description**: 
        Perform all Git health checks and return the most severe signal.

        Returns:
            DetectionSignal with is_failure=True if any blocker found,
            or is_failure=False if repository is healthy.
        



## Function: get_all_signals

**Parameters**: self
**Returns**: list[DetectionSignal]
**Description**: 
        Get all detection signals (not just the most severe).

        Returns:
            List of all DetectionSignal objects for each check.
        



## Usage Examples

### Class Usage

```python
# Using GitHealthSensor
githealthsensor = GitHealthSensor()
githealthsensor.check_repository_health()
githealthsensor.get_all_signals()
```

### Function Usage

```python
# Using check_git_health
result = check_git_health(repo_root)
```

```python
# Using __init__
result = __init__(repo_root)
```

```python
# Using _run_git_command
result = _run_git_command(args)
```



---
**Generated**: 2026-03-26T09:39:04.823100
**Type**: api_reference
**Quality**: comprehensive
