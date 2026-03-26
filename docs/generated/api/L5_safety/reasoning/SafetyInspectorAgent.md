# API Documentation: SafetyInspectorAgent

**Target Audience**: developers, api_users

# SafetyInspectorAgent API Documentation

**File**: `SafetyInspectorAgent.py`
**Classes**: 3
**Functions**: 11

## Classes

- **ViolationCheck**
- **ConstitutionalOverseer**
- **SafetyInspectorAgent** (inherits from SovereignBaseAgent)

## Functions

- **create_overseer** -> ConstitutionalOverseer
- **create_safety_inspector** -> SafetyInspectorAgent
- **__init__** -> None
- **__init__** -> None
- **_check_forbidden_patterns** -> ViolationCheck
- **add_forbidden_pattern** -> Any
- **get_forbidden_patterns** -> list[str]
- **__init__** -> None
- **clear_false_positive_cache** -> Any
- **heal_repository** -> dict[str, Any]
- **heal** -> dict


## Class: ViolationCheck

**Description**: Result of a safety Violation check.

### Methods

#### __init__
**Parameters**: self, is_violation, reason
**Returns**: None



## Class: ConstitutionalOverseer

**Description**: Overseer that validates ActionRequests against safety rules.

### Methods

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the overseer with default safety rules.

#### _check_forbidden_patterns
**Parameters**: self, text
**Returns**: ViolationCheck
**Description**: Check text against forbidden command patterns.

        Args:
            text: Text to check

        Returns:
            ViolationCheck if Violation found, None if safe
        

#### add_forbidden_pattern
**Parameters**: self, pattern
**Returns**: Any
**Description**: Add a new forbidden pattern.

        Args:
            pattern: Regex pattern to add
        

#### get_forbidden_patterns
**Parameters**: self
**Returns**: list[str]
**Description**: Get list of forbidden patterns.

        Returns:
            List of forbidden command patterns
        



## Class: SafetyInspectorAgent

**Description**: 
    L5 Safety Inspector with Socratic Judge for false positive mitigation.

    KEYS: 0 (Secrets), 1 (TODO/FIXME), 2 (Print), 3 (Debugger), 4 (Empty Except), 5 (Bare Except), 6 (Eval/Exec)
    ROLE: Security Compliance with intelligent Violation verification.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, enable_socratic_judge, max_socratic_calls
**Returns**: None
**Description**: 
        Initialize the SafetyInspectorAgent.

        Args:
            enable_socratic_judge: Whether to use LLM verification for false positives
            max_socratic_calls: Maximum Socratic Judge LLM calls per scan run (rate limit)
        

#### clear_false_positive_cache
**Parameters**: self
**Returns**: Any
**Description**: Clear the false positive cache.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: Scan repository for security violations and report findings.

        Scans Python files for hardcoded secrets, debug statements, eval/exec
        usage, and other security concerns. Safety violations require manual
        review and cannot be auto-fixed.

        Args:
            dry_run: If True, only report violations (default: True).
            execute: If True, generate detailed security report.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal safety inspection violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (safety, constitutional, socratic)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Function: create_overseer

**Returns**: ConstitutionalOverseer
**Description**: Factory function to create overseer instance.



## Function: create_safety_inspector

**Parameters**: enable_socratic_judge
**Returns**: SafetyInspectorAgent
**Description**: Factory function to create SafetyInspectorAgent instance.



## Function: __init__

**Parameters**: self, is_violation, reason
**Returns**: None


## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the overseer with default safety rules.



## Function: _check_forbidden_patterns

**Parameters**: self, text
**Returns**: ViolationCheck
**Description**: Check text against forbidden command patterns.

        Args:
            text: Text to check

        Returns:
            ViolationCheck if Violation found, None if safe
        



## Function: add_forbidden_pattern

**Parameters**: self, pattern
**Returns**: Any
**Description**: Add a new forbidden pattern.

        Args:
            pattern: Regex pattern to add
        



## Function: get_forbidden_patterns

**Parameters**: self
**Returns**: list[str]
**Description**: Get list of forbidden patterns.

        Returns:
            List of forbidden command patterns
        



## Function: __init__

**Parameters**: self, enable_socratic_judge, max_socratic_calls
**Returns**: None
**Description**: 
        Initialize the SafetyInspectorAgent.

        Args:
            enable_socratic_judge: Whether to use LLM verification for false positives
            max_socratic_calls: Maximum Socratic Judge LLM calls per scan run (rate limit)
        



## Function: clear_false_positive_cache

**Parameters**: self
**Returns**: Any
**Description**: Clear the false positive cache.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: Scan repository for security violations and report findings.

        Scans Python files for hardcoded secrets, debug statements, eval/exec
        usage, and other security concerns. Safety violations require manual
        review and cannot be auto-fixed.

        Args:
            dry_run: If True, only report violations (default: True).
            execute: If True, generate detailed security report.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal safety inspection violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (safety, constitutional, socratic)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        



## Usage Examples

### Class Usage

```python
# Using ViolationCheck
violationcheck = ViolationCheck()
```

```python
# Using ConstitutionalOverseer
constitutionaloverseer = ConstitutionalOverseer()
constitutionaloverseer.add_forbidden_pattern()
constitutionaloverseer.get_forbidden_patterns()
```

```python
# Using SafetyInspectorAgent
safetyinspectoragent = SafetyInspectorAgent()
safetyinspectoragent.clear_false_positive_cache()
safetyinspectoragent.heal_repository()
```

### Function Usage

```python
# Using create_overseer
result = create_overseer()
```

```python
# Using create_safety_inspector
result = create_safety_inspector(enable_socratic_judge)
```

```python
# Using __init__
result = __init__(is_violation, reason)
```



---
**Generated**: 2026-03-26T09:39:05.390731
**Type**: api_reference
**Quality**: comprehensive
