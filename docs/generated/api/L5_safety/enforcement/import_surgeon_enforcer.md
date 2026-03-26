# API Documentation: import_surgeon_enforcer

**Target Audience**: developers, api_users

# import_surgeon_enforcer API Documentation

**File**: `import_surgeon_enforcer.py`
**Classes**: 2
**Functions**: 9

## Classes

- **ImportViolation**
- **SovereignImportSurgeon**

## Functions

- **main** -> Any
- **__init__**
- **__repr__**
- **__init__**
- **scan_file** -> list[ImportViolation]
- **_convert_relative_to_absolute** -> str
- **scan_all_files** -> Any
- **generate_report** -> str
- **apply_fixes** -> Any


## Class: ImportViolation

**Description**: Represents a single import Violation.

### Methods

#### __init__
**Parameters**: self, file_path, line_num, line, ViolationType, suggested_fix

#### __repr__
**Parameters**: self



## Class: SovereignImportSurgeon

**Description**: Scans and fixes import statements across the codebase.

### Methods

#### __init__
**Parameters**: self, root_path

#### scan_file
**Parameters**: self, file_path
**Returns**: list[ImportViolation]
**Description**: Scan a single Python file for import violations.

#### _convert_relative_to_absolute
**Parameters**: self, line, file_path
**Returns**: str
**Description**: Convert relative imports to absolute imports.

#### scan_all_files
**Parameters**: self
**Returns**: Any
**Description**: Scan all Python files in the project.

#### generate_report
**Parameters**: self
**Returns**: str
**Description**: Generate a detailed dry run report.

#### apply_fixes
**Parameters**: self
**Returns**: Any
**Description**: Apply all identified fixes (ONLY after user confirmation).



## Function: main

**Returns**: Any
**Description**: Main entry point.



## Function: __init__

**Parameters**: self, file_path, line_num, line, ViolationType, suggested_fix


## Function: __repr__

**Parameters**: self


## Function: __init__

**Parameters**: self, root_path


## Function: scan_file

**Parameters**: self, file_path
**Returns**: list[ImportViolation]
**Description**: Scan a single Python file for import violations.



## Function: _convert_relative_to_absolute

**Parameters**: self, line, file_path
**Returns**: str
**Description**: Convert relative imports to absolute imports.



## Function: scan_all_files

**Parameters**: self
**Returns**: Any
**Description**: Scan all Python files in the project.



## Function: generate_report

**Parameters**: self
**Returns**: str
**Description**: Generate a detailed dry run report.



## Function: apply_fixes

**Parameters**: self
**Returns**: Any
**Description**: Apply all identified fixes (ONLY after user confirmation).



## Usage Examples

### Class Usage

```python
# Using ImportViolation
importviolation = ImportViolation()
```

```python
# Using SovereignImportSurgeon
sovereignimportsurgeon = SovereignImportSurgeon()
sovereignimportsurgeon.scan_file()
sovereignimportsurgeon.scan_all_files()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using __init__
result = __init__(file_path, line_num)
```

```python
# Using __repr__
result = __repr__()
```



---
**Generated**: 2026-03-26T09:39:04.858950
**Type**: api_reference
**Quality**: comprehensive
