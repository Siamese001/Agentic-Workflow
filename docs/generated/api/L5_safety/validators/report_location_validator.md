# API Documentation: report_location_validator

**Target Audience**: developers, api_users

# report_location_validator API Documentation

**File**: `report_location_validator.py`
**Classes**: 3
**Functions**: 12

## Classes

- **ReportValidationResult**
- **ReportInventory**
- **ReportLocationValidator**

## Functions

- **validate_report_location** -> bool
- **get_misplaced_reports** -> list[ReportValidationResult]
- **generate_report_inventory** -> ReportInventory
- **__init__**
- **is_report_file** -> bool
- **is_excluded_directory** -> bool
- **is_approved_location** -> bool
- **validate_file** -> ReportValidationResult
- **find_all_reports** -> list[Path]
- **get_misplaced_reports** -> list[ReportValidationResult]
- **get_compliant_reports** -> list[ReportValidationResult]
- **generate_inventory** -> ReportInventory


## Class: ReportValidationResult

**Description**: Result of a report location validation.



## Class: ReportInventory

**Description**: Comprehensive inventory of all reports in the repository.



## Class: ReportLocationValidator

**Description**: 
    Validates report file locations against SSOT requirements.

    Ensures all reports are stored in docs/reports/ or approved subdirectories.
    

### Methods

#### __init__
**Parameters**: self, project_root, dry_run
**Description**: 
        Initialize the validator.

        Args:
            project_root: Project root path. If None, uses get_validated_project_root().
            dry_run: If True, only report violations without taking action.
        

#### is_report_file
**Parameters**: self, file_path
**Returns**: bool
**Description**: 
        Check if a file matches report file patterns.

        Args:
            file_path: Path to check.

        Returns:
            True if the file matches a report pattern.
        

#### is_excluded_directory
**Parameters**: self, file_path
**Returns**: bool
**Description**: 
        Check if a file is in an excluded directory.

        Args:
            file_path: Path to check.

        Returns:
            True if the file is in an excluded directory.
        

#### is_approved_location
**Parameters**: self, file_path
**Returns**: bool
**Description**: 
        Check if a file is in an approved report location.

        Args:
            file_path: Path to check.

        Returns:
            True if the file is in an approved location.
        

#### validate_file
**Parameters**: self, file_path
**Returns**: ReportValidationResult
**Description**: 
        Validate a single file's location.

        Args:
            file_path: Path to validate.

        Returns:
            ReportValidationResult with validation details.
        

#### find_all_reports
**Parameters**: self
**Returns**: list[Path]
**Description**: 
        Find all report files in the repository.

        Returns:
            List of paths to report files.
        

#### get_misplaced_reports
**Parameters**: self
**Returns**: list[ReportValidationResult]
**Description**: 
        Get all misplaced report files.

        Returns:
            List of validation results for misplaced reports.
        

#### get_compliant_reports
**Parameters**: self
**Returns**: list[ReportValidationResult]
**Description**: 
        Get all compliant report files.

        Returns:
            List of validation results for compliant reports.
        

#### generate_inventory
**Parameters**: self
**Returns**: ReportInventory
**Description**: 
        Generate a comprehensive inventory of all reports.

        Returns:
            ReportInventory with categorized report information.
        



## Function: validate_report_location

**Parameters**: file_path, project_root
**Returns**: bool
**Description**: 
    Validate if a report file is in the correct SSOT location.

    Args:
        file_path: Path to the report file.
        project_root: Project root path.

    Returns:
        True if the file is in an approved location.
    



## Function: get_misplaced_reports

**Parameters**: project_root
**Returns**: list[ReportValidationResult]
**Description**: 
    Get all misplaced report files in the repository.

    Args:
        project_root: Project root path.

    Returns:
        List of validation results for misplaced reports.
    



## Function: generate_report_inventory

**Parameters**: project_root
**Returns**: ReportInventory
**Description**: 
    Generate a comprehensive inventory of all reports.

    Args:
        project_root: Project root path.

    Returns:
        ReportInventory with categorized report information.
    



## Function: __init__

**Parameters**: self, project_root, dry_run
**Description**: 
        Initialize the validator.

        Args:
            project_root: Project root path. If None, uses get_validated_project_root().
            dry_run: If True, only report violations without taking action.
        



## Function: is_report_file

**Parameters**: self, file_path
**Returns**: bool
**Description**: 
        Check if a file matches report file patterns.

        Args:
            file_path: Path to check.

        Returns:
            True if the file matches a report pattern.
        



## Function: is_excluded_directory

**Parameters**: self, file_path
**Returns**: bool
**Description**: 
        Check if a file is in an excluded directory.

        Args:
            file_path: Path to check.

        Returns:
            True if the file is in an excluded directory.
        



## Function: is_approved_location

**Parameters**: self, file_path
**Returns**: bool
**Description**: 
        Check if a file is in an approved report location.

        Args:
            file_path: Path to check.

        Returns:
            True if the file is in an approved location.
        



## Function: validate_file

**Parameters**: self, file_path
**Returns**: ReportValidationResult
**Description**: 
        Validate a single file's location.

        Args:
            file_path: Path to validate.

        Returns:
            ReportValidationResult with validation details.
        



## Function: find_all_reports

**Parameters**: self
**Returns**: list[Path]
**Description**: 
        Find all report files in the repository.

        Returns:
            List of paths to report files.
        



## Function: get_misplaced_reports

**Parameters**: self
**Returns**: list[ReportValidationResult]
**Description**: 
        Get all misplaced report files.

        Returns:
            List of validation results for misplaced reports.
        



## Function: get_compliant_reports

**Parameters**: self
**Returns**: list[ReportValidationResult]
**Description**: 
        Get all compliant report files.

        Returns:
            List of validation results for compliant reports.
        



## Function: generate_inventory

**Parameters**: self
**Returns**: ReportInventory
**Description**: 
        Generate a comprehensive inventory of all reports.

        Returns:
            ReportInventory with categorized report information.
        



## Usage Examples

### Class Usage

```python
# Using ReportValidationResult
reportvalidationresult = ReportValidationResult()
```

```python
# Using ReportInventory
reportinventory = ReportInventory()
```

```python
# Using ReportLocationValidator
reportlocationvalidator = ReportLocationValidator()
reportlocationvalidator.is_report_file()
reportlocationvalidator.is_excluded_directory()
```

### Function Usage

```python
# Using validate_report_location
result = validate_report_location(file_path, project_root)
```

```python
# Using get_misplaced_reports
result = get_misplaced_reports(project_root)
```

```python
# Using generate_report_inventory
result = generate_report_inventory(project_root)
```



---
**Generated**: 2026-03-26T09:39:05.868641
**Type**: api_reference
**Quality**: comprehensive
