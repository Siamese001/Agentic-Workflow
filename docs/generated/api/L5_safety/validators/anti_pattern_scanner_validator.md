# API Documentation: anti_pattern_scanner_validator

**Target Audience**: developers, api_users

# anti_pattern_scanner_validator API Documentation

**File**: `anti_pattern_scanner_validator.py`
**Classes**: 2
**Functions**: 10

## Classes

- **ScanReport**
- **AntiPatternScanner**

## Functions

- **run_scan** -> ScanReport
- **summary** -> str
- **to_dict** -> dict[str, Any]
- **passed** -> bool
- **get_default_scan_dirs** -> list[str]
- **__init__**
- **scan_repository** -> ScanReport
- **scan_file** -> list[AntiPatternViolation]
- **scan_changed_files** -> ScanReport
- **get_enforcement_action** -> str


## Class: ScanReport

**Description**: Report from anti-pattern scanning.

### Methods

#### summary
**Parameters**: self
**Returns**: str
**Description**: Generate human-readable summary.

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for JSON serialization.

#### passed
**Parameters**: self
**Returns**: bool
**Description**: Check if scan passed (no violations).



## Class: AntiPatternScanner

**Description**: 
    Unified anti-pattern scanner for repository-wide detection.

    Combines all Phase 2 landmine detectors into a single scanning interface
    with configurable enforcement levels and reporting.
    

### Methods

#### get_default_scan_dirs
**Parameters**: cls
**Returns**: list[str]
**Description**: Get default scan directories using dynamic apps discovery.
        
        Returns:
            List of directory names to scan, including all apps_* directories.
        

#### __init__
**Parameters**: self, project_root, enforcement_level, scan_dirs, exclude_patterns
**Description**: 
        Initialize the anti-pattern scanner.

        Args:
            project_root: Root directory of the project
            enforcement_level: Enforcement level for all detectors
            scan_dirs: Directories to scan (relative to project_root)
            exclude_patterns: Glob patterns to exclude
        

#### scan_repository
**Parameters**: self
**Returns**: ScanReport
**Description**: 
        Scan the entire repository for anti-patterns.

        Returns:
            ScanReport with all findings
        

#### scan_file
**Parameters**: self, file_path
**Returns**: list[AntiPatternViolation]
**Description**: 
        Scan a single file for anti-patterns.

        Args:
            file_path: Path to the file to scan

        Returns:
            List of violations found
        

#### scan_changed_files
**Parameters**: self, file_paths
**Returns**: ScanReport
**Description**: 
        Scan only specific files (for incremental PR checks).

        Args:
            file_paths: List of files to scan

        Returns:
            ScanReport with findings for the specified files
        

#### get_enforcement_action
**Parameters**: self, report
**Returns**: str
**Description**: 
        Determine the enforcement action based on scan results.

        Args:
            report: Scan report

        Returns:
            Action to take: "pass", "warn", "soft_block", "hard_block"
        



## Function: run_scan

**Parameters**: project_root
**Returns**: ScanReport
**Description**: 
    Convenience function to run a full repository scan.

    Args:
        project_root: Optional project root (defaults to current working directory)

    Returns:
        ScanReport with all findings
    



## Function: summary

**Parameters**: self
**Returns**: str
**Description**: Generate human-readable summary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for JSON serialization.



## Function: passed

**Parameters**: self
**Returns**: bool
**Description**: Check if scan passed (no violations).



## Function: get_default_scan_dirs

**Parameters**: cls
**Returns**: list[str]
**Description**: Get default scan directories using dynamic apps discovery.
        
        Returns:
            List of directory names to scan, including all apps_* directories.
        



## Function: __init__

**Parameters**: self, project_root, enforcement_level, scan_dirs, exclude_patterns
**Description**: 
        Initialize the anti-pattern scanner.

        Args:
            project_root: Root directory of the project
            enforcement_level: Enforcement level for all detectors
            scan_dirs: Directories to scan (relative to project_root)
            exclude_patterns: Glob patterns to exclude
        



## Function: scan_repository

**Parameters**: self
**Returns**: ScanReport
**Description**: 
        Scan the entire repository for anti-patterns.

        Returns:
            ScanReport with all findings
        



## Function: scan_file

**Parameters**: self, file_path
**Returns**: list[AntiPatternViolation]
**Description**: 
        Scan a single file for anti-patterns.

        Args:
            file_path: Path to the file to scan

        Returns:
            List of violations found
        



## Function: scan_changed_files

**Parameters**: self, file_paths
**Returns**: ScanReport
**Description**: 
        Scan only specific files (for incremental PR checks).

        Args:
            file_paths: List of files to scan

        Returns:
            ScanReport with findings for the specified files
        



## Function: get_enforcement_action

**Parameters**: self, report
**Returns**: str
**Description**: 
        Determine the enforcement action based on scan results.

        Args:
            report: Scan report

        Returns:
            Action to take: "pass", "warn", "soft_block", "hard_block"
        



## Usage Examples

### Class Usage

```python
# Using ScanReport
scanreport = ScanReport()
scanreport.summary()
scanreport.to_dict()
```

```python
# Using AntiPatternScanner
antipatternscanner = AntiPatternScanner()
antipatternscanner.get_default_scan_dirs()
antipatternscanner.scan_repository()
```

### Function Usage

```python
# Using run_scan
result = run_scan(project_root)
```

```python
# Using summary
result = summary()
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:05.734557
**Type**: api_reference
**Quality**: comprehensive
