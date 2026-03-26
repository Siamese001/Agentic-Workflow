# API Documentation: ReportLocationAgent

**Target Audience**: developers, api_users

# ReportLocationAgent API Documentation

**File**: `ReportLocationAgent.py`
**Classes**: 2
**Functions**: 12

## Classes

- **ReportLocationHealResult**
- **ReportLocationAgent** (inherits from AtomicExecutionMixin)

## Functions

- **__post_init__**
- **validate** -> dict[str, Any]
- **get_violations** -> list[ReportValidationResult]
- **get_inventory** -> ReportInventory
- **is_git_tracked** -> bool
- **git_move** -> bool
- **backup_file** -> Path | None
- **heal_file** -> dict[str, Any]
- **heal** -> ReportLocationHealResult
- **standard_heal** -> dict[str, Any]
- **save_inventory** -> Path
- **heal_repository** -> dict[str, Any]


## Class: ReportLocationHealResult

**Description**: Result of a report location healing operation.



## Class: ReportLocationAgent

**Description**: 
    SSOT Report Storage Enforcement Agent.

    Validates and heals report file locations to ensure compliance
    with the SSOT principle: all reports in docs/reports/.

    Capabilities:
    - Validate report locations across the repository
    - Generate compliance inventory
    - Heal violations by moving files to SSOT location
    - Git-aware moves to preserve history
    - Backup before healing operations

    Integration:
    - Works with pre-commit hooks for enforcement
    - Integrates with Guardian tests for validation
    - Supports dry-run mode for safe testing
    

**Inherits from**: AtomicExecutionMixin

### Methods

#### __post_init__
**Parameters**: self
**Description**: Initialize the agent.

#### validate
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Validate all report locations in the repository.

        Returns:
            Dictionary with validation results including:
            - total_reports: Total number of report files found
            - compliant_reports: Number of reports in approved locations
            - misplaced_reports: Number of reports in wrong locations
            - compliance_percentage: Percentage of compliant reports
            - violations: List of violation details
        

#### get_violations
**Parameters**: self
**Returns**: list[ReportValidationResult]
**Description**: 
        Get all report location violations.

        Returns:
            List of ReportValidationResult for misplaced reports.
        

#### get_inventory
**Parameters**: self
**Returns**: ReportInventory
**Description**: 
        Generate a comprehensive report inventory.

        Returns:
            ReportInventory with categorized report information.
        

#### is_git_tracked
**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if a file is tracked by git via L5-safe subprocess delegation.

#### git_move
**Parameters**: self, source, destination
**Returns**: bool
**Description**: Move a file using git mv to preserve history (L5-safe delegation).

#### backup_file
**Parameters**: self, file_path
**Returns**: Path | None
**Description**: Create a backup of a file before healing.

#### heal_file
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal a single report location violation.

        Args:
            violation: The violation to heal.

        Returns:
            Dictionary with heal result for this file.
        

#### heal
**Parameters**: self, limit
**Returns**: ReportLocationHealResult
**Description**: 
        Heal all report location violations.

        Args:
            limit: Optional limit on number of files to heal (for pilot runs).

        Returns:
            ReportLocationHealResult with healing statistics.
        

#### standard_heal
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Standard heal interface for integration with healing framework.

        Returns:
            Dictionary with standard heal result keys:
            - violations_found: Number of violations detected
            - violations_fixed: Number of violations healed
            - errors: List of error messages
            - skipped: Number of skipped files
        

#### save_inventory
**Parameters**: self, output_path
**Returns**: Path
**Description**: 
        Save the report inventory to a JSON file.

        Args:
            output_path: Path to save the inventory.

        Returns:
            Path to the saved inventory file.
        

#### heal_repository
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: heal_repository() not implemented for ReportLocationAgent.



## Function: __post_init__

**Parameters**: self
**Description**: Initialize the agent.



## Function: validate

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Validate all report locations in the repository.

        Returns:
            Dictionary with validation results including:
            - total_reports: Total number of report files found
            - compliant_reports: Number of reports in approved locations
            - misplaced_reports: Number of reports in wrong locations
            - compliance_percentage: Percentage of compliant reports
            - violations: List of violation details
        



## Function: get_violations

**Parameters**: self
**Returns**: list[ReportValidationResult]
**Description**: 
        Get all report location violations.

        Returns:
            List of ReportValidationResult for misplaced reports.
        



## Function: get_inventory

**Parameters**: self
**Returns**: ReportInventory
**Description**: 
        Generate a comprehensive report inventory.

        Returns:
            ReportInventory with categorized report information.
        



## Function: is_git_tracked

**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if a file is tracked by git via L5-safe subprocess delegation.



## Function: git_move

**Parameters**: self, source, destination
**Returns**: bool
**Description**: Move a file using git mv to preserve history (L5-safe delegation).



## Function: backup_file

**Parameters**: self, file_path
**Returns**: Path | None
**Description**: Create a backup of a file before healing.



## Function: heal_file

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal a single report location violation.

        Args:
            violation: The violation to heal.

        Returns:
            Dictionary with heal result for this file.
        



## Function: heal

**Parameters**: self, limit
**Returns**: ReportLocationHealResult
**Description**: 
        Heal all report location violations.

        Args:
            limit: Optional limit on number of files to heal (for pilot runs).

        Returns:
            ReportLocationHealResult with healing statistics.
        



## Function: standard_heal

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: 
        Standard heal interface for integration with healing framework.

        Returns:
            Dictionary with standard heal result keys:
            - violations_found: Number of violations detected
            - violations_fixed: Number of violations healed
            - errors: List of error messages
            - skipped: Number of skipped files
        



## Function: save_inventory

**Parameters**: self, output_path
**Returns**: Path
**Description**: 
        Save the report inventory to a JSON file.

        Args:
            output_path: Path to save the inventory.

        Returns:
            Path to the saved inventory file.
        



## Function: heal_repository

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: heal_repository() not implemented for ReportLocationAgent.



## Usage Examples

### Class Usage

```python
# Using ReportLocationHealResult
reportlocationhealresult = ReportLocationHealResult()
```

```python
# Using ReportLocationAgent
reportlocationagent = ReportLocationAgent()
reportlocationagent.validate()
reportlocationagent.get_violations()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using validate
result = validate()
```

```python
# Using get_violations
result = get_violations()
```



---
**Generated**: 2026-03-26T09:39:05.368596
**Type**: api_reference
**Quality**: comprehensive
