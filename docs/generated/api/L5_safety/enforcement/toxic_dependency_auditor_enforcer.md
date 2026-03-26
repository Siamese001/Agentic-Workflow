# API Documentation: toxic_dependency_auditor_enforcer

**Target Audience**: developers, api_users

# toxic_dependency_auditor_enforcer API Documentation

**File**: `toxic_dependency_auditor_enforcer.py`
**Classes**: 1
**Functions**: 8

## Classes

- **ToxicDependencyAuditor** (inherits from SovereignBaseAgent)

## Functions

- **__init__**
- **audit_toxicity** -> list[dict]
- **_build_fan_in_map**
- **_extract_internal_imports** -> set[str]
- **_get_module_name** -> str
- **report**
- **heal_repository** -> dict
- **heal** -> dict


## Class: ToxicDependencyAuditor

**Description**: 
    The Risk-Assessor Agent.
    Identifies the most critical components of the Sovereign Architecture.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, root_dir, toxic_threshold

#### audit_toxicity
**Parameters**: self, coverage_data
**Returns**: list[dict]
**Description**: Builds the fan-in map and identifies toxic hubs with coverage weighting.

        Args:
            coverage_data: Optional dict mapping module paths to coverage percentages (0.0-1.0)

        Returns:
            List of toxic hubs sorted by systemic risk score
        

#### _build_fan_in_map
**Parameters**: self
**Description**: Walks all python files to see who imports what.

#### _extract_internal_imports
**Parameters**: self, file_path
**Returns**: set[str]
**Description**: Uses AST to find internal agentic_core imports.

#### _get_module_name
**Parameters**: self, file_path
**Returns**: str
**Description**: Maps file path to standard dot-notation module name.

#### report
**Parameters**: self, toxic_hubs
**Description**: Generates a Sovereign Toxicity Report with coverage weighting.

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal toxic dependency violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (toxic_hub, high_fan_in)
                - module: Module with high fan-in
                - fan_in: Number of dependencies

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: __init__

**Parameters**: self, root_dir, toxic_threshold


## Function: audit_toxicity

**Parameters**: self, coverage_data
**Returns**: list[dict]
**Description**: Builds the fan-in map and identifies toxic hubs with coverage weighting.

        Args:
            coverage_data: Optional dict mapping module paths to coverage percentages (0.0-1.0)

        Returns:
            List of toxic hubs sorted by systemic risk score
        



## Function: _build_fan_in_map

**Parameters**: self
**Description**: Walks all python files to see who imports what.



## Function: _extract_internal_imports

**Parameters**: self, file_path
**Returns**: set[str]
**Description**: Uses AST to find internal agentic_core imports.



## Function: _get_module_name

**Parameters**: self, file_path
**Returns**: str
**Description**: Maps file path to standard dot-notation module name.



## Function: report

**Parameters**: self, toxic_hubs
**Description**: Generates a Sovereign Toxicity Report with coverage weighting.



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal toxic dependency violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (toxic_hub, high_fan_in)
                - module: Module with high fan-in
                - fan_in: Number of dependencies

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using ToxicDependencyAuditor
toxicdependencyauditor = ToxicDependencyAuditor()
toxicdependencyauditor.audit_toxicity()
toxicdependencyauditor.report()
```

### Function Usage

```python
# Using __init__
result = __init__(root_dir, toxic_threshold)
```

```python
# Using audit_toxicity
result = audit_toxicity(coverage_data)
```

```python
# Using _build_fan_in_map
result = _build_fan_in_map()
```



---
**Generated**: 2026-03-26T09:39:04.977500
**Type**: api_reference
**Quality**: comprehensive
