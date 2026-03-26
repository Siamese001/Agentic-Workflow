# API Documentation: DocstringComplianceAgent

**Target Audience**: developers, api_users

# DocstringComplianceAgent API Documentation

**File**: `DocstringComplianceAgent.py`
**Classes**: 1
**Functions**: 4

## Classes

- **DocstringComplianceAgent** (inherits from PromptRenderingMixin, SovereignBaseAgent)

## Functions

- **get_docstring_compliance_agent** -> Any
- **__init__** -> None
- **heal** -> dict[str, Any]
- **heal_repository** -> dict[str, int]


## Class: DocstringComplianceAgent

**Description**: 
    Ensures public functions, classes, and modules have docstrings.

    Rules:
    - Module-level docstring required (first statement)
    - Public classes (not starting with _) must have docstring
    - Public functions/methods (not starting with _) must have docstring
    - Minimal stub: '''Brief description of functionality and purpose.'''

    Why ungated healing is safe:
    - Only adds Missing triple-quoted strings immediately after def/class
    - Never removes or modifies existing content
    - Single-file scope
    

**Inherits from**: PromptRenderingMixin, SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, ctx, project_root
**Returns**: None
**Description**: 
        Initialize with mandatory ctx for sovereign operation.

        Args:
            ctx: Execution context (mandatory)
            project_root: Optional project root directory

        Raises:
            ValueError: If ctx is None
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal a specific violation (IHealerProtocol compliance).

        Args:
            violation: Dict containing violation details

        Returns:
            Dict with status, details, artifacts, errors
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Autonomous docstring compliance enforcement.



## Function: get_docstring_compliance_agent

**Returns**: Any
**Description**: Brief description of functionality and purpose.



## Function: __init__

**Parameters**: self, ctx, project_root
**Returns**: None
**Description**: 
        Initialize with mandatory ctx for sovereign operation.

        Args:
            ctx: Execution context (mandatory)
            project_root: Optional project root directory

        Raises:
            ValueError: If ctx is None
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal a specific violation (IHealerProtocol compliance).

        Args:
            violation: Dict containing violation details

        Returns:
            Dict with status, details, artifacts, errors
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Autonomous docstring compliance enforcement.



## Usage Examples

### Class Usage

```python
# Using DocstringComplianceAgent
docstringcomplianceagent = DocstringComplianceAgent()
docstringcomplianceagent.heal()
docstringcomplianceagent.heal_repository()
```

### Function Usage

```python
# Using get_docstring_compliance_agent
result = get_docstring_compliance_agent()
```

```python
# Using __init__
result = __init__(ctx, project_root)
```

```python
# Using heal
result = heal(violation)
```



---
**Generated**: 2026-03-26T09:39:05.125130
**Type**: api_reference
**Quality**: comprehensive
