# API Documentation: guard_observability_footprint_util

**Target Audience**: developers, api_users

# guard_observability_footprint_util API Documentation

**File**: `guard_observability_footprint_util.py`
**Classes**: 0
**Functions**: 2


## Functions

- **check_dark_reasoning** -> list[str]
- **validate_observability_footprint** -> tuple[float, list[str]]


## Function: check_dark_reasoning

**Parameters**: filepath
**Returns**: list[str]
**Description**: 
    Check for reasoning operations without corresponding observability footprints.

    Dark Reasoning occurs when an agent performs cognitive operations (think, plan, decide)
    without leaving a trace in the L6 observability layer (logging, telemetry).

    Args:
        filepath: Path to Python file to audit

    Returns:
        List of issues found (empty if compliant)
    



## Function: validate_observability_footprint

**Parameters**: target_dir
**Returns**: tuple[float, list[str]]
**Description**: 
    Validate that all reasoning operations have observability footprints.

    Args:
        target_dir: Directory to audit

    Returns:
        Tuple of (score percentage, list of issues)
    



## Usage Examples

### Function Usage

```python
# Using check_dark_reasoning
result = check_dark_reasoning(filepath)
```

```python
# Using validate_observability_footprint
result = validate_observability_footprint(target_dir)
```



---
**Generated**: 2026-03-26T09:39:05.660895
**Type**: api_reference
**Quality**: comprehensive
