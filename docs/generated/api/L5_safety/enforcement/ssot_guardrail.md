# API Documentation: ssot_guardrail

**Target Audience**: developers, api_users

# ssot_guardrail API Documentation

**File**: `ssot_guardrail.py`
**Classes**: 2
**Functions**: 6

## Classes

- **Violation**
- **ScanResult**

## Functions

- **_normalize_path** -> str
- **scan_shadow_functions** -> list[Violation]
- **scan_endswith_agent** -> list[Violation]
- **scan_repository** -> ScanResult
- **main** -> int
- **passed** -> bool


## Class: Violation

**Description**: A single guardrail violation.



## Class: ScanResult

**Description**: Aggregated scan results.

### Methods

#### passed
**Parameters**: self
**Returns**: bool



## Function: _normalize_path

**Parameters**: path, project_root
**Returns**: str
**Description**: Convert absolute path to forward-slash relative path.



## Function: scan_shadow_functions

**Parameters**: tree, rel_path
**Returns**: list[Violation]
**Description**: Detect function definitions that shadow kernel classification.



## Function: scan_endswith_agent

**Parameters**: tree, rel_path
**Returns**: list[Violation]
**Description**: Detect usage of endswith('Agent') string checks in logic functions.

    This is a heuristic for inline shadow classification. We look for
    ast.Call nodes where the function is an Attribute named 'endswith'
    and the argument is a string containing 'Agent'.
    



## Function: scan_repository

**Parameters**: project_root
**Returns**: ScanResult
**Description**: Scan all Python files in the repository for SSOT violations.



## Function: main

**Returns**: int
**Description**: Run the SSOT guardrail scanner.



## Function: passed

**Parameters**: self
**Returns**: bool


## Usage Examples

### Class Usage

```python
# Using Violation
violation = Violation()
```

```python
# Using ScanResult
scanresult = ScanResult()
scanresult.passed()
```

### Function Usage

```python
# Using _normalize_path
result = _normalize_path(path, project_root)
```

```python
# Using scan_shadow_functions
result = scan_shadow_functions(tree, rel_path)
```

```python
# Using scan_endswith_agent
result = scan_endswith_agent(tree, rel_path)
```



---
**Generated**: 2026-03-26T09:39:04.941164
**Type**: api_reference
**Quality**: comprehensive
