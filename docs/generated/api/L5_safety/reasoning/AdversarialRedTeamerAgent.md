# API Documentation: AdversarialRedTeamerAgent

**Target Audience**: developers, api_users

# AdversarialRedTeamerAgent API Documentation

**File**: `AdversarialRedTeamerAgent.py`
**Classes**: 3
**Functions**: 10

## Classes

- **VulnerabilityTest**
- **RedTeamResult**
- **AdversarialRedTeamerAgent** (inherits from SovereignBaseAgent, SubAtomicAgent)

## Functions

- **get_adversarial_red_teamer** -> AdversarialRedTeamer
- **__init__** -> None
- **_build_test_suite** -> list[VulnerabilityTest]
- **_build_preservation_tests** -> list[VulnerabilityTest]
- **_build_sandbox_tests** -> list[VulnerabilityTest]
- **_build_connectivity_tests** -> list[VulnerabilityTest]
- **_build_edge_case_tests** -> list[VulnerabilityTest]
- **_generate_report** -> Any
- **heal_repository** -> dict[str, int]
- **heal** -> dict


## Class: VulnerabilityTest

**Description**: Represents a vulnerability test case.



## Class: RedTeamResult

**Description**: Result of a red team test.



## Class: AdversarialRedTeamerAgent

**Description**: 
    The Skeptic - Adversarial Red Team Agent

    Acts as counter-agent to CodeJanitor and SystemArchitect.
    Probes boundaries and attempts to induce common pipeline failures
    in safe, ephemeral environment.

    Test Categories:
    1. Preservation Attacks - Try to violate 90% rule
    2. Sandbox Escapes - Attempt to break security boundaries
    3. Connectivity Breaks - Induce stage-to-stage failures
    4. Edge Cases - Test boundary conditions
    

**Inherits from**: SovereignBaseAgent, SubAtomicAgent

### Methods

#### __init__
**Parameters**: self, ctx
**Returns**: None
**Description**: 
        Initialize Adversarial Red-Teamer.

        Args:
            ctx: The context object for the agent. (e.g., AgentContext)
        

#### _build_test_suite
**Parameters**: self
**Returns**: list[VulnerabilityTest]
**Description**: Build comprehensive test suite.

#### _build_preservation_tests
**Parameters**: self
**Returns**: list[VulnerabilityTest]
**Description**: Build tests for preservation attacks.

#### _build_sandbox_tests
**Parameters**: self
**Returns**: list[VulnerabilityTest]
**Description**: Build tests for sandbox escapes.

#### _build_connectivity_tests
**Parameters**: self
**Returns**: list[VulnerabilityTest]
**Description**: Build tests for connectivity breaks.

#### _build_edge_case_tests
**Parameters**: self
**Returns**: list[VulnerabilityTest]
**Description**: Build tests for edge cases.

#### _generate_report
**Parameters**: self
**Returns**: Any
**Description**: Generate red team report.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L5 safety agent - operational only.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal adversarial red team violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (vulnerability, sandbox_escape, etc.)
                - test_id: ID of the failed test
                - severity: Severity level

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: get_adversarial_red_teamer

**Parameters**: ctx
**Returns**: AdversarialRedTeamer
**Description**: Get or create global Red Teamer instance.



## Function: __init__

**Parameters**: self, ctx
**Returns**: None
**Description**: 
        Initialize Adversarial Red-Teamer.

        Args:
            ctx: The context object for the agent. (e.g., AgentContext)
        



## Function: _build_test_suite

**Parameters**: self
**Returns**: list[VulnerabilityTest]
**Description**: Build comprehensive test suite.



## Function: _build_preservation_tests

**Parameters**: self
**Returns**: list[VulnerabilityTest]
**Description**: Build tests for preservation attacks.



## Function: _build_sandbox_tests

**Parameters**: self
**Returns**: list[VulnerabilityTest]
**Description**: Build tests for sandbox escapes.



## Function: _build_connectivity_tests

**Parameters**: self
**Returns**: list[VulnerabilityTest]
**Description**: Build tests for connectivity breaks.



## Function: _build_edge_case_tests

**Parameters**: self
**Returns**: list[VulnerabilityTest]
**Description**: Build tests for edge cases.



## Function: _generate_report

**Parameters**: self
**Returns**: Any
**Description**: Generate red team report.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L5 safety agent - operational only.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal adversarial red team violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (vulnerability, sandbox_escape, etc.)
                - test_id: ID of the failed test
                - severity: Severity level

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using VulnerabilityTest
vulnerabilitytest = VulnerabilityTest()
```

```python
# Using RedTeamResult
redteamresult = RedTeamResult()
```

```python
# Using AdversarialRedTeamerAgent
adversarialredteameragent = AdversarialRedTeamerAgent()
adversarialredteameragent.heal_repository()
adversarialredteameragent.heal()
```

### Function Usage

```python
# Using get_adversarial_red_teamer
result = get_adversarial_red_teamer(ctx)
```

```python
# Using __init__
result = __init__(ctx)
```

```python
# Using _build_test_suite
result = _build_test_suite()
```



---
**Generated**: 2026-03-26T09:39:05.026811
**Type**: api_reference
**Quality**: comprehensive
