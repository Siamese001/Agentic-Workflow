# API Documentation: CodeDetectorAgent

**Target Audience**: developers, api_users

# CodeDetectorAgent API Documentation

**File**: `CodeDetectorAgent.py`
**Classes**: 5
**Functions**: 10

## Classes

- **DetectionType** (inherits from Enum)
- **Severity** (inherits from Enum)
- **Detection**
- **DetectorConfig**
- **CodeDetectorAgent** (inherits from PromptRenderingMixin, SovereignBaseAgent)

## Functions

- **__init__**
- **heal_repository** -> dict[str, Any]
- **run_full_scan** -> list[Detection]
- **detect_all** -> list[Detection]
- **detect_dead_code** -> list[Detection]
- **detect_deadlocks** -> list[Detection]
- **detect_memory_leaks** -> list[Detection]
- **detect_method_changes** -> list[Detection]
- **_update_baseline**
- **heal** -> dict


## Class: DetectionType

**Inherits from**: Enum



## Class: Severity

**Inherits from**: Enum



## Class: Detection



## Class: DetectorConfig



## Class: CodeDetectorAgent

**Description**: 
    Unified code quality detector.
    Consolidates DeadCode, Drift, Deadlock, and MemoryLeak detection.
    

**Inherits from**: PromptRenderingMixin, SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, config

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Sovereign Interface.
        Detectors primarily REPORT. 'execute' mode can update baselines.
        

#### run_full_scan
**Parameters**: self
**Returns**: list[Detection]
**Description**: Scans all Python files in project.

#### detect_all
**Parameters**: self, file_path
**Returns**: list[Detection]
**Description**: Run all enabled detections on a file.

#### detect_dead_code
**Parameters**: self, file_path, content
**Returns**: list[Detection]

#### detect_deadlocks
**Parameters**: self, file_path, content
**Returns**: list[Detection]

#### detect_memory_leaks
**Parameters**: self, file_path, content
**Returns**: list[Detection]

#### detect_method_changes
**Parameters**: self, file_path, content
**Returns**: list[Detection]

#### _update_baseline
**Parameters**: self
**Description**: Generates a new baseline snapshot of the codebase.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal code detection violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (race_condition, deadlock, memory_leak)
                - path: Path to the violating file
                - line_number: Line number of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Function: __init__

**Parameters**: self, config


## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Sovereign Interface.
        Detectors primarily REPORT. 'execute' mode can update baselines.
        



## Function: run_full_scan

**Parameters**: self
**Returns**: list[Detection]
**Description**: Scans all Python files in project.



## Function: detect_all

**Parameters**: self, file_path
**Returns**: list[Detection]
**Description**: Run all enabled detections on a file.



## Function: detect_dead_code

**Parameters**: self, file_path, content
**Returns**: list[Detection]


## Function: detect_deadlocks

**Parameters**: self, file_path, content
**Returns**: list[Detection]


## Function: detect_memory_leaks

**Parameters**: self, file_path, content
**Returns**: list[Detection]


## Function: detect_method_changes

**Parameters**: self, file_path, content
**Returns**: list[Detection]


## Function: _update_baseline

**Parameters**: self
**Description**: Generates a new baseline snapshot of the codebase.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal code detection violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (race_condition, deadlock, memory_leak)
                - path: Path to the violating file
                - line_number: Line number of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Usage Examples

### Class Usage

```python
# Using DetectionType
detectiontype = DetectionType()
```

```python
# Using Severity
severity = Severity()
```

```python
# Using Detection
detection = Detection()
```

### Function Usage

```python
# Using __init__
result = __init__(config)
```

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```

```python
# Using run_full_scan
result = run_full_scan()
```



---
**Generated**: 2026-03-26T09:39:05.076824
**Type**: api_reference
**Quality**: comprehensive
