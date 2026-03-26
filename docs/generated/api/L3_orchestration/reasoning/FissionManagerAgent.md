# API Documentation: FissionManagerAgent

**Target Audience**: developers, api_users

# FissionManagerAgent API Documentation

**File**: `FissionManagerAgent.py`
**Classes**: 2
**Functions**: 5

## Classes

- **FissionResult**
- **FissionManagerAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__** -> None
- **_get_fission_prompt** -> str
- **_parse_fission_response** -> dict[str, str]
- **heal** -> dict[str, Any]
- **heal_repository** -> dict


## Class: FissionResult



## Class: FissionManagerAgent

**Description**: L3 Orchestration Layer: Atomic Fission via Gateway.

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, line_limit, deletion_guardrail, max_rounds
**Returns**: None

#### _get_fission_prompt
**Parameters**: self, file_name, content
**Returns**: str

#### _parse_fission_response
**Parameters**: self, text, original_file
**Returns**: dict[str, str]

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by FissionManagerAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        

#### heal_repository
**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for FissionManagerAgent.



## Function: __init__

**Parameters**: self, line_limit, deletion_guardrail, max_rounds
**Returns**: None


## Function: _get_fission_prompt

**Parameters**: self, file_name, content
**Returns**: str


## Function: _parse_fission_response

**Parameters**: self, text, original_file
**Returns**: dict[str, str]


## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by FissionManagerAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Function: heal_repository

**Parameters**: self
**Returns**: dict
**Description**: heal_repository() not implemented for FissionManagerAgent.



## Usage Examples

### Class Usage

```python
# Using FissionResult
fissionresult = FissionResult()
```

```python
# Using FissionManagerAgent
fissionmanageragent = FissionManagerAgent()
fissionmanageragent.heal()
fissionmanageragent.heal_repository()
```

### Function Usage

```python
# Using __init__
result = __init__(line_limit, deletion_guardrail)
```

```python
# Using _get_fission_prompt
result = _get_fission_prompt(file_name, content)
```

```python
# Using _parse_fission_response
result = _parse_fission_response(text, original_file)
```



---
**Generated**: 2026-03-26T09:39:04.278598
**Type**: api_reference
**Quality**: comprehensive
