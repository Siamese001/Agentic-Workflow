# API Documentation: base_detector_validator

**Target Audience**: developers, api_users

# base_detector_validator API Documentation

**File**: `base_detector_validator.py`
**Classes**: 6
**Functions**: 17

## Classes

- **EnforcementLevel** (inherits from str, Enum)
- **AntiPatternCategory** (inherits from str, Enum)
- **AntiPatternViolation**
- **DetectionResult**
- **AntiPatternDetector** (inherits from ABC)
- **CompositeDetector**

## Functions

- **to_dict** -> dict[str, Any]
- **has_violations** -> bool
- **violation_count** -> int
- **__init__**
- **category** -> AntiPatternCategory
- **detect** -> list[AntiPatternViolation]
- **scan_file** -> DetectionResult
- **scan_directory** -> list[DetectionResult]
- **_get_ast** -> ast.Module | None
- **_is_file_whitelisted** -> bool
- **_is_violation_whitelisted** -> bool
- **_get_source_line** -> str
- **__init__**
- **add_detector** -> None
- **scan_file** -> list[DetectionResult]
- **scan_directory** -> dict[AntiPatternCategory, list[DetectionResult]]
- **get_summary** -> dict[str, Any]


## Class: EnforcementLevel

**Description**: Enforcement level for anti-pattern violations.

**Inherits from**: str, Enum



## Class: AntiPatternCategory

**Description**: Categories of anti-patterns.

**Inherits from**: str, Enum



## Class: AntiPatternViolation

**Description**: Represents a detected anti-pattern violation.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for reporting.



## Class: DetectionResult

**Description**: Result of anti-pattern detection for a file.

### Methods

#### has_violations
**Parameters**: self
**Returns**: bool
**Description**: Check if any violations were found.

#### violation_count
**Parameters**: self
**Returns**: int
**Description**: Count non-whitelisted violations.



## Class: AntiPatternDetector

**Description**: 
    Abstract base class for anti-pattern detectors.

    Subclasses implement specific detection logic for each anti-pattern category.
    

**Inherits from**: ABC

### Methods

#### __init__
**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files

#### category
**Parameters**: self
**Returns**: AntiPatternCategory
**Description**: Return the category of anti-pattern this detector handles.

#### detect
**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: 
        Detect anti-patterns in the given AST.

        Args:
            file_path: Path to the file being analyzed
            tree: Parsed AST of the file

        Returns:
            List of detected violations
        

#### scan_file
**Parameters**: self, file_path
**Returns**: DetectionResult
**Description**: 
        Scan a single file for anti-patterns.

        Args:
            file_path: Path to the file to scan

        Returns:
            DetectionResult with violations and metadata
        

#### scan_directory
**Parameters**: self, directory, include_patterns, exclude_patterns
**Returns**: list[DetectionResult]
**Description**: 
        Scan all Python files in a directory.

        Args:
            directory: Directory to scan
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude

        Returns:
            List of DetectionResults
        

#### _get_ast
**Parameters**: self, file_path
**Returns**: ast.Module | None
**Description**: Get AST for file with caching.

#### _is_file_whitelisted
**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if file matches whitelist patterns.

#### _is_violation_whitelisted
**Parameters**: self, violation
**Returns**: bool
**Description**: Check if violation matches whitelist patterns.

#### _get_source_line
**Parameters**: self, file_path, line_number
**Returns**: str
**Description**: Get a specific line from the source file.



## Class: CompositeDetector

**Description**: 
    Combines multiple detectors into a single scanning interface.
    

### Methods

#### __init__
**Parameters**: self, detectors

#### add_detector
**Parameters**: self, detector
**Returns**: None
**Description**: Add a detector to the composite.

#### scan_file
**Parameters**: self, file_path
**Returns**: list[DetectionResult]
**Description**: Scan file with all detectors.

#### scan_directory
**Parameters**: self, directory, include_patterns, exclude_patterns
**Returns**: dict[AntiPatternCategory, list[DetectionResult]]
**Description**: Scan directory with all detectors, grouped by category.

#### get_summary
**Parameters**: self, results
**Returns**: dict[str, Any]
**Description**: Generate summary statistics from scan results.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for reporting.



## Function: has_violations

**Parameters**: self
**Returns**: bool
**Description**: Check if any violations were found.



## Function: violation_count

**Parameters**: self
**Returns**: int
**Description**: Count non-whitelisted violations.



## Function: __init__

**Parameters**: self, enforcement_level, whitelisted_patterns, whitelisted_files


## Function: category

**Parameters**: self
**Returns**: AntiPatternCategory
**Description**: Return the category of anti-pattern this detector handles.



## Function: detect

**Parameters**: self, file_path, tree
**Returns**: list[AntiPatternViolation]
**Description**: 
        Detect anti-patterns in the given AST.

        Args:
            file_path: Path to the file being analyzed
            tree: Parsed AST of the file

        Returns:
            List of detected violations
        



## Function: scan_file

**Parameters**: self, file_path
**Returns**: DetectionResult
**Description**: 
        Scan a single file for anti-patterns.

        Args:
            file_path: Path to the file to scan

        Returns:
            DetectionResult with violations and metadata
        



## Function: scan_directory

**Parameters**: self, directory, include_patterns, exclude_patterns
**Returns**: list[DetectionResult]
**Description**: 
        Scan all Python files in a directory.

        Args:
            directory: Directory to scan
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude

        Returns:
            List of DetectionResults
        



## Function: _get_ast

**Parameters**: self, file_path
**Returns**: ast.Module | None
**Description**: Get AST for file with caching.



## Function: _is_file_whitelisted

**Parameters**: self, file_path
**Returns**: bool
**Description**: Check if file matches whitelist patterns.



## Function: _is_violation_whitelisted

**Parameters**: self, violation
**Returns**: bool
**Description**: Check if violation matches whitelist patterns.



## Function: _get_source_line

**Parameters**: self, file_path, line_number
**Returns**: str
**Description**: Get a specific line from the source file.



## Function: __init__

**Parameters**: self, detectors


## Function: add_detector

**Parameters**: self, detector
**Returns**: None
**Description**: Add a detector to the composite.



## Function: scan_file

**Parameters**: self, file_path
**Returns**: list[DetectionResult]
**Description**: Scan file with all detectors.



## Function: scan_directory

**Parameters**: self, directory, include_patterns, exclude_patterns
**Returns**: dict[AntiPatternCategory, list[DetectionResult]]
**Description**: Scan directory with all detectors, grouped by category.



## Function: get_summary

**Parameters**: self, results
**Returns**: dict[str, Any]
**Description**: Generate summary statistics from scan results.



## Usage Examples

### Class Usage

```python
# Using EnforcementLevel
enforcementlevel = EnforcementLevel()
```

```python
# Using AntiPatternCategory
antipatterncategory = AntiPatternCategory()
```

```python
# Using AntiPatternViolation
antipatternviolation = AntiPatternViolation()
antipatternviolation.to_dict()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using has_violations
result = has_violations()
```

```python
# Using violation_count
result = violation_count()
```



---
**Generated**: 2026-03-26T09:39:05.741995
**Type**: api_reference
**Quality**: comprehensive
