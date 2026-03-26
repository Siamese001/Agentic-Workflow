# API Documentation: ssot_relocator_types

**Target Audience**: developers, api_users

# ssot_relocator_types API Documentation

**File**: `ssot_relocator_types.py`
**Classes**: 3
**Functions**: 11

## Classes

- **RelocationResult**
- **EnforcementReport**
- **SSOTRelocator**

## Functions

- **__post_init__**
- **__post_init__**
- **success_rate** -> float
- **__init__**
- **relocate_orphans** -> EnforcementReport
- **enforce_hierarchy** -> EnforcementReport
- **relocate_agents** -> EnforcementReport
- **_relocate_file** -> RelocationResult
- **_relocate_folder** -> RelocationResult
- **_flatten_folder** -> RelocationResult
- **_cleanup_empty_dirs** -> None


## Class: RelocationResult

**Description**: Result of a single relocation operation.

### Methods

#### __post_init__
**Parameters**: self



## Class: EnforcementReport

**Description**: Summary of enforcement operations.

### Methods

#### __post_init__
**Parameters**: self

#### success_rate
**Parameters**: self
**Returns**: float
**Description**: Calculate success rate percentage.



## Class: SSOTRelocator

**Description**: 
    Automated SSOT violation remediation.

    Provides reusable methods for fixing violations detected by UnifiedSSOTValidator:
    - relocate_orphans(): Move drift violations to archives
    - enforce_hierarchy(): Flatten folders exceeding depth limits
    - relocate_agents(): Move agents to correct layers
    

### Methods

#### __init__
**Parameters**: self, project_root, dry_run, log_file
**Description**: 
        Initialize SSOT relocator.

        Args:
            project_root: Root directory of the project
            dry_run: If True, preview operations without executing
            log_file: Path to enforcement history log
        

#### relocate_orphans
**Parameters**: self, drift_violations
**Returns**: EnforcementReport
**Description**: 
        Move orphaned folders (drift violations) to archives.

        Args:
            drift_violations: List of DriftViolation objects from validator

        Returns:
            EnforcementReport with operation results
        

#### enforce_hierarchy
**Parameters**: self, hierarchy_violations
**Returns**: EnforcementReport
**Description**: 
        Flatten folders exceeding depth limits.

        Moves files from deep folders to parent folders within depth limits.

        Args:
            hierarchy_violations: List of HierarchyViolation objects from validator

        Returns:
            EnforcementReport with operation results
        

#### relocate_agents
**Parameters**: self, gravity_violations
**Returns**: EnforcementReport
**Description**: 
        Move agents to their correct layers (gravity violation remediation).

        Args:
            gravity_violations: List of GravityViolation objects from validator

        Returns:
            EnforcementReport with operation results
        

#### _relocate_file
**Parameters**: self, source, target, action
**Returns**: RelocationResult
**Description**: 
        Relocate a single file with safety checks.

        Args:
            source: Source file path
            target: Target file path
            action: Action description

        Returns:
            RelocationResult with operation details
        

#### _relocate_folder
**Parameters**: self, source, target, action
**Returns**: RelocationResult
**Description**: 
        Relocate an entire folder with safety checks.

        Args:
            source: Source folder path
            target: Target folder path
            action: Action description

        Returns:
            RelocationResult with operation details
        

#### _flatten_folder
**Parameters**: self, source, target, max_depth
**Returns**: RelocationResult
**Description**: 
        Flatten a folder by moving its contents to a shallower location.

        Args:
            source: Source folder path (too deep)
            target: Target folder path (within depth limit)
            max_depth: Maximum allowed depth

        Returns:
            RelocationResult with operation details
        

#### _cleanup_empty_dirs
**Parameters**: self, directory
**Returns**: None
**Description**: 
        Recursively remove empty parent directories.

        Args:
            directory: Directory to check and clean up
        



## Function: __post_init__

**Parameters**: self


## Function: __post_init__

**Parameters**: self


## Function: success_rate

**Parameters**: self
**Returns**: float
**Description**: Calculate success rate percentage.



## Function: __init__

**Parameters**: self, project_root, dry_run, log_file
**Description**: 
        Initialize SSOT relocator.

        Args:
            project_root: Root directory of the project
            dry_run: If True, preview operations without executing
            log_file: Path to enforcement history log
        



## Function: relocate_orphans

**Parameters**: self, drift_violations
**Returns**: EnforcementReport
**Description**: 
        Move orphaned folders (drift violations) to archives.

        Args:
            drift_violations: List of DriftViolation objects from validator

        Returns:
            EnforcementReport with operation results
        



## Function: enforce_hierarchy

**Parameters**: self, hierarchy_violations
**Returns**: EnforcementReport
**Description**: 
        Flatten folders exceeding depth limits.

        Moves files from deep folders to parent folders within depth limits.

        Args:
            hierarchy_violations: List of HierarchyViolation objects from validator

        Returns:
            EnforcementReport with operation results
        



## Function: relocate_agents

**Parameters**: self, gravity_violations
**Returns**: EnforcementReport
**Description**: 
        Move agents to their correct layers (gravity violation remediation).

        Args:
            gravity_violations: List of GravityViolation objects from validator

        Returns:
            EnforcementReport with operation results
        



## Function: _relocate_file

**Parameters**: self, source, target, action
**Returns**: RelocationResult
**Description**: 
        Relocate a single file with safety checks.

        Args:
            source: Source file path
            target: Target file path
            action: Action description

        Returns:
            RelocationResult with operation details
        



## Function: _relocate_folder

**Parameters**: self, source, target, action
**Returns**: RelocationResult
**Description**: 
        Relocate an entire folder with safety checks.

        Args:
            source: Source folder path
            target: Target folder path
            action: Action description

        Returns:
            RelocationResult with operation details
        



## Function: _flatten_folder

**Parameters**: self, source, target, max_depth
**Returns**: RelocationResult
**Description**: 
        Flatten a folder by moving its contents to a shallower location.

        Args:
            source: Source folder path (too deep)
            target: Target folder path (within depth limit)
            max_depth: Maximum allowed depth

        Returns:
            RelocationResult with operation details
        



## Function: _cleanup_empty_dirs

**Parameters**: self, directory
**Returns**: None
**Description**: 
        Recursively remove empty parent directories.

        Args:
            directory: Directory to check and clean up
        



## Usage Examples

### Class Usage

```python
# Using RelocationResult
relocationresult = RelocationResult()
```

```python
# Using EnforcementReport
enforcementreport = EnforcementReport()
enforcementreport.success_rate()
```

```python
# Using SSOTRelocator
ssotrelocator = SSOTRelocator()
ssotrelocator.relocate_orphans()
ssotrelocator.enforce_hierarchy()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using success_rate
result = success_rate()
```



---
**Generated**: 2026-03-26T09:39:05.583557
**Type**: api_reference
**Quality**: comprehensive
