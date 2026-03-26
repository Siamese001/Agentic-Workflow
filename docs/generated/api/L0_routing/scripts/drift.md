# API Documentation: drift

**Target Audience**: developers, api_users

# drift API Documentation

**File**: `drift.py`
**Classes**: 1
**Functions**: 4

## Classes

- **DriftDetector** (inherits from <ast.Attribute object at 0x000001CBFAD7CF50>)

## Functions

- **scan_repository** -> int
- **__init__**
- **visit_ImportFrom** -> None
- **visit_ClassDef** -> None


## Class: DriftDetector

**Description**: 
    Parses python source to find classes inheriting from TARGET_VIOLATION.
    Uses AST to bypass regex limitations (aliasing, formatting).
    

**Inherits from**: ast.NodeVisitor

### Methods

#### __init__
**Parameters**: self, filename

#### visit_ImportFrom
**Parameters**: self, node
**Returns**: None
**Description**: Track imports to detect aliasing e.g. 'from x import L2Agent as Base'

#### visit_ClassDef
**Parameters**: self, node
**Returns**: None
**Description**: Inspect class inheritance signatures.



## Function: scan_repository

**Parameters**: root_path
**Returns**: int
**Description**: 
    Recursively scans the repo for violations.
    Returns exit code: 0 if success, 1 if violations OR parse errors found.
    



## Function: __init__

**Parameters**: self, filename


## Function: visit_ImportFrom

**Parameters**: self, node
**Returns**: None
**Description**: Track imports to detect aliasing e.g. 'from x import L2Agent as Base'



## Function: visit_ClassDef

**Parameters**: self, node
**Returns**: None
**Description**: Inspect class inheritance signatures.



## Usage Examples

### Class Usage

```python
# Using DriftDetector
driftdetector = DriftDetector()
driftdetector.visit_ImportFrom()
driftdetector.visit_ClassDef()
```

### Function Usage

```python
# Using scan_repository
result = scan_repository(root_path)
```

```python
# Using __init__
result = __init__(filename)
```

```python
# Using visit_ImportFrom
result = visit_ImportFrom(node)
```



---
**Generated**: 2026-03-26T09:39:02.867015
**Type**: api_reference
**Quality**: comprehensive
