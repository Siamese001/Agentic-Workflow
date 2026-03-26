# API Documentation: gravity_validator

**Target Audience**: developers, api_users

# gravity_validator API Documentation

**File**: `gravity_validator.py`
**Classes**: 6
**Functions**: 16

## Classes

- **GravityViolation**
- **ImportViolation**
- **HierarchyViolation**
- **DriftViolation**
- **SovereignHealthReport**
- **UnifiedSSOTValidator**

## Functions

- **__str__** -> str
- **__str__** -> str
- **__str__** -> str
- **__str__** -> str
- **total_violations** -> int
- **is_compliant** -> bool
- **to_markdown** -> str
- **__init__**
- **validate_all** -> SovereignHealthReport
- **_check_gravity_violations** -> list[GravityViolation]
- **_check_import_violations** -> list[ImportViolation]
- **_check_hierarchy_violations** -> list[HierarchyViolation]
- **_check_drift_violations** -> list[DriftViolation]
- **_get_layer_from_path** -> str | None
- **_extract_target_layer** -> str | None
- **_get_import_line** -> str


## Class: GravityViolation

**Description**: Agent in wrong layer (physical location mismatch).

### Methods

#### __str__
**Parameters**: self
**Returns**: str



## Class: ImportViolation

**Description**: Illegal upward dependency (lower layer importing from higher layer).

### Methods

#### __str__
**Parameters**: self
**Returns**: str



## Class: HierarchyViolation

**Description**: Depth limit exceeded (too many nested folders).

### Methods

#### __str__
**Parameters**: self
**Returns**: str



## Class: DriftViolation

**Description**: Unauthorized folder not in blueprint.

### Methods

#### __str__
**Parameters**: self
**Returns**: str



## Class: SovereignHealthReport

**Description**: 
    Comprehensive SSOT health report.

    Consolidates all validation results into a single report.
    

### Methods

#### total_violations
**Parameters**: self
**Returns**: int
**Description**: Total number of violations across all categories.

#### is_compliant
**Parameters**: self
**Returns**: bool
**Description**: Check if system is fully compliant (zero violations).

#### to_markdown
**Parameters**: self
**Returns**: str
**Description**: Generate Markdown report optimized for LLM/Human consumption.



## Class: UnifiedSSOTValidator

**Description**: 
    Unified SSOT Validator - Single source of truth for all validation.

    Consolidates logic from:
    - audit_ssot.py (gravity violations)
    - audit_architectural_violations.py (import violations)
    - HierarchyAgent (depth compliance)
    - LocationAgent (territory compliance)
    - FilesystemSSOTReconcilerAgent (drift detection)
    

### Methods

#### __init__
**Parameters**: self, project_root
**Description**: 
        Initialize unified validator.

        Args:
            project_root: Root directory of the project
        

#### validate_all
**Parameters**: self
**Returns**: SovereignHealthReport
**Description**: 
        Run all validation checks and generate comprehensive report.

        Returns:
            SovereignHealthReport with all violations and statistics
        

#### _check_gravity_violations
**Parameters**: self
**Returns**: list[GravityViolation]
**Description**: Check for agents in wrong layers (physical location mismatch).

#### _check_import_violations
**Parameters**: self
**Returns**: list[ImportViolation]
**Description**: Check for illegal upward dependencies (lower layer importing from higher).

#### _check_hierarchy_violations
**Parameters**: self
**Returns**: list[HierarchyViolation]
**Description**: Check for folders exceeding maximum depth limits.

#### _check_drift_violations
**Parameters**: self
**Returns**: list[DriftViolation]
**Description**: Check for unauthorized folders not in blueprint.

#### _get_layer_from_path
**Parameters**: self, file_path
**Returns**: str | None
**Description**: Extract layer (L0-L5) from file path.

#### _extract_target_layer
**Parameters**: self, node
**Returns**: str | None
**Description**: Extract target layer from import statement.

#### _get_import_line
**Parameters**: self, node, content
**Returns**: str
**Description**: Extract import line text from AST node.



## Function: __str__

**Parameters**: self
**Returns**: str


## Function: __str__

**Parameters**: self
**Returns**: str


## Function: __str__

**Parameters**: self
**Returns**: str


## Function: __str__

**Parameters**: self
**Returns**: str


## Function: total_violations

**Parameters**: self
**Returns**: int
**Description**: Total number of violations across all categories.



## Function: is_compliant

**Parameters**: self
**Returns**: bool
**Description**: Check if system is fully compliant (zero violations).



## Function: to_markdown

**Parameters**: self
**Returns**: str
**Description**: Generate Markdown report optimized for LLM/Human consumption.



## Function: __init__

**Parameters**: self, project_root
**Description**: 
        Initialize unified validator.

        Args:
            project_root: Root directory of the project
        



## Function: validate_all

**Parameters**: self
**Returns**: SovereignHealthReport
**Description**: 
        Run all validation checks and generate comprehensive report.

        Returns:
            SovereignHealthReport with all violations and statistics
        



## Function: _check_gravity_violations

**Parameters**: self
**Returns**: list[GravityViolation]
**Description**: Check for agents in wrong layers (physical location mismatch).



## Function: _check_import_violations

**Parameters**: self
**Returns**: list[ImportViolation]
**Description**: Check for illegal upward dependencies (lower layer importing from higher).



## Function: _check_hierarchy_violations

**Parameters**: self
**Returns**: list[HierarchyViolation]
**Description**: Check for folders exceeding maximum depth limits.



## Function: _check_drift_violations

**Parameters**: self
**Returns**: list[DriftViolation]
**Description**: Check for unauthorized folders not in blueprint.



## Function: _get_layer_from_path

**Parameters**: self, file_path
**Returns**: str | None
**Description**: Extract layer (L0-L5) from file path.



## Function: _extract_target_layer

**Parameters**: self, node
**Returns**: str | None
**Description**: Extract target layer from import statement.



## Function: _get_import_line

**Parameters**: self, node, content
**Returns**: str
**Description**: Extract import line text from AST node.



## Usage Examples

### Class Usage

```python
# Using GravityViolation
gravityviolation = GravityViolation()
```

```python
# Using ImportViolation
importviolation = ImportViolation()
```

```python
# Using HierarchyViolation
hierarchyviolation = HierarchyViolation()
```

### Function Usage

```python
# Using __str__
result = __str__()
```

```python
# Using __str__
result = __str__()
```

```python
# Using __str__
result = __str__()
```



---
**Generated**: 2026-03-26T09:39:05.810900
**Type**: api_reference
**Quality**: comprehensive
