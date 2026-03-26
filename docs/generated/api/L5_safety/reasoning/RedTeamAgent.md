# API Documentation: RedTeamAgent

**Target Audience**: developers, api_users

# RedTeamAgent API Documentation

**File**: `RedTeamAgent.py`
**Classes**: 1
**Functions**: 4

## Classes

- **RedTeamAgent** (inherits from SovereignBaseAgent)

## Functions

- **get_RedTeamAgent** -> Any
- **_detect_bypass** -> bool
- **heal_repository** -> dict[str, int]
- **heal** -> dict


## Class: RedTeamAgent

**Description**: 
    Sovereign red-teaming agent for guardrail penetration testing.

    Safety model:
    - Only active when ctx.mission_type == "red_team_validation"
    - Uses meta-prompt governance for authorization
    - All payloads sourced from prompt_governance/templates/
    - Full audit logging on every attempt
    - Automatic escalation on successful bypass

    Registered templates:
    - red_team_governance.jinja: Governance and authorization
    - jailbreak_classic.jinja: Classic jailbreak testing (used in ADVERSARIAL_FRAGMENTS)
    

**Inherits from**: SovereignBaseAgent

### Methods

#### _detect_bypass
**Parameters**: self, response
**Returns**: bool
**Description**: Simple heuristic bypass detection — extend with LLM judgment if needed.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Execute red team adversarial testing on repository guardrails.

        Runs adversarial tests against safety guardrails to identify potential
        bypasses. Findings require manual security review and cannot be auto-fixed.

        Args:
            dry_run: If True, only report findings (default: True).
            execute: If True, run full adversarial test suite.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal red team violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (adversarial, bypass, escalation)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: get_RedTeamAgent

**Returns**: Any
**Description**: Brief description of functionality and purpose.



## Function: _detect_bypass

**Parameters**: self, response
**Returns**: bool
**Description**: Simple heuristic bypass detection — extend with LLM judgment if needed.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Execute red team adversarial testing on repository guardrails.

        Runs adversarial tests against safety guardrails to identify potential
        bypasses. Findings require manual security review and cannot be auto-fixed.

        Args:
            dry_run: If True, only report findings (default: True).
            execute: If True, run full adversarial test suite.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dictionary with violations_found, violations_fixed, errors, skipped.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal red team violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (adversarial, bypass, escalation)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using RedTeamAgent
redteamagent = RedTeamAgent()
redteamagent.heal_repository()
redteamagent.heal()
```

### Function Usage

```python
# Using get_RedTeamAgent
result = get_RedTeamAgent()
```

```python
# Using _detect_bypass
result = _detect_bypass(response)
```

```python
# Using heal_repository
result = heal_repository(dry_run, execute)
```



---
**Generated**: 2026-03-26T09:39:05.361908
**Type**: api_reference
**Quality**: comprehensive
