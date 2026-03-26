# API Documentation: three_tier_compliance_enforcer

**Target Audience**: developers, api_users

# three_tier_compliance_enforcer API Documentation

**File**: `three_tier_compliance_enforcer.py`
**Classes**: 4
**Functions**: 18

## Classes

- **TierStatus**
- **AgentCompliance**
- **ComplianceResult**
- **ThreeTierComplianceChecker**

## Functions

- **run_compliance_check** -> ComplianceResult
- **is_fully_compliant** -> bool
- **compliance_score** -> int
- **contract_coverage_pct** -> float
- **blueprint_coverage_pct** -> float
- **soul_coverage_pct** -> float
- **overall_compliance_pct** -> float
- **__init__**
- **_scan_guardian_tests** -> list[Path]
- **_scan_unit_tests** -> list[Path]
- **_build_unit_test_map** -> dict[str, list[Path]]
- **_normalize_agent_name** -> str
- **_check_contract_tier** -> TierStatus
- **_check_blueprint_tier** -> TierStatus
- **_check_soul_tier** -> TierStatus
- **_suggest_test_path** -> str
- **check_compliance** -> ComplianceResult
- **generate_report** -> str


## Class: TierStatus

**Description**: Status of a single tier for an agent.



## Class: AgentCompliance

**Description**: Compliance status for a single agent across all three tiers.

### Methods

#### is_fully_compliant
**Parameters**: self
**Returns**: bool
**Description**: Check if agent is compliant across all tiers.

#### compliance_score
**Parameters**: self
**Returns**: int
**Description**: Return compliance score (0-3).



## Class: ComplianceResult

**Description**: Result of three-tier compliance check.

### Methods

#### contract_coverage_pct
**Parameters**: self
**Returns**: float
**Description**: Contract tier coverage percentage.

#### blueprint_coverage_pct
**Parameters**: self
**Returns**: float
**Description**: Blueprint tier coverage percentage.

#### soul_coverage_pct
**Parameters**: self
**Returns**: float
**Description**: Soul tier coverage percentage.

#### overall_compliance_pct
**Parameters**: self
**Returns**: float
**Description**: Overall compliance percentage.



## Class: ThreeTierComplianceChecker

**Description**: Checks three-tier compliance for all agents.

### Methods

#### __init__
**Parameters**: self, project_root
**Description**: Initialize checker with project root.

#### _scan_guardian_tests
**Parameters**: self
**Returns**: list[Path]
**Description**: Scan for Guardian tests.

#### _scan_unit_tests
**Parameters**: self
**Returns**: list[Path]
**Description**: Scan for unit tests.

#### _build_unit_test_map
**Parameters**: self
**Returns**: dict[str, list[Path]]
**Description**: Build mapping of agent names to their unit tests.

#### _normalize_agent_name
**Parameters**: self, class_name
**Returns**: str
**Description**: Normalize agent class name for matching.

#### _check_contract_tier
**Parameters**: self, agent
**Returns**: TierStatus
**Description**: Check Contract tier coverage for an agent.

        All agents are covered by pre-commit hooks if they are Python files
        in the repository (not in excluded directories).
        

#### _check_blueprint_tier
**Parameters**: self, agent
**Returns**: TierStatus
**Description**: Check Blueprint tier coverage for an agent.

        Blueprint coverage is provided by Guardian tests that validate
        architectural patterns across all agents.
        

#### _check_soul_tier
**Parameters**: self, agent
**Returns**: TierStatus
**Description**: Check Soul tier coverage for an agent.

        Soul coverage requires a dedicated unit test file for the agent.
        

#### _suggest_test_path
**Parameters**: self, agent
**Returns**: str
**Description**: Suggest expected unit test path for an agent.

#### check_compliance
**Parameters**: self
**Returns**: ComplianceResult
**Description**: Perform full three-tier compliance check.

#### generate_report
**Parameters**: self, result
**Returns**: str
**Description**: Generate markdown report from compliance result.



## Function: run_compliance_check

**Returns**: ComplianceResult
**Description**: Run three-tier compliance check and return result.



## Function: is_fully_compliant

**Parameters**: self
**Returns**: bool
**Description**: Check if agent is compliant across all tiers.



## Function: compliance_score

**Parameters**: self
**Returns**: int
**Description**: Return compliance score (0-3).



## Function: contract_coverage_pct

**Parameters**: self
**Returns**: float
**Description**: Contract tier coverage percentage.



## Function: blueprint_coverage_pct

**Parameters**: self
**Returns**: float
**Description**: Blueprint tier coverage percentage.



## Function: soul_coverage_pct

**Parameters**: self
**Returns**: float
**Description**: Soul tier coverage percentage.



## Function: overall_compliance_pct

**Parameters**: self
**Returns**: float
**Description**: Overall compliance percentage.



## Function: __init__

**Parameters**: self, project_root
**Description**: Initialize checker with project root.



## Function: _scan_guardian_tests

**Parameters**: self
**Returns**: list[Path]
**Description**: Scan for Guardian tests.



## Function: _scan_unit_tests

**Parameters**: self
**Returns**: list[Path]
**Description**: Scan for unit tests.



## Function: _build_unit_test_map

**Parameters**: self
**Returns**: dict[str, list[Path]]
**Description**: Build mapping of agent names to their unit tests.



## Function: _normalize_agent_name

**Parameters**: self, class_name
**Returns**: str
**Description**: Normalize agent class name for matching.



## Function: _check_contract_tier

**Parameters**: self, agent
**Returns**: TierStatus
**Description**: Check Contract tier coverage for an agent.

        All agents are covered by pre-commit hooks if they are Python files
        in the repository (not in excluded directories).
        



## Function: _check_blueprint_tier

**Parameters**: self, agent
**Returns**: TierStatus
**Description**: Check Blueprint tier coverage for an agent.

        Blueprint coverage is provided by Guardian tests that validate
        architectural patterns across all agents.
        



## Function: _check_soul_tier

**Parameters**: self, agent
**Returns**: TierStatus
**Description**: Check Soul tier coverage for an agent.

        Soul coverage requires a dedicated unit test file for the agent.
        



## Function: _suggest_test_path

**Parameters**: self, agent
**Returns**: str
**Description**: Suggest expected unit test path for an agent.



## Function: check_compliance

**Parameters**: self
**Returns**: ComplianceResult
**Description**: Perform full three-tier compliance check.



## Function: generate_report

**Parameters**: self, result
**Returns**: str
**Description**: Generate markdown report from compliance result.



## Usage Examples

### Class Usage

```python
# Using TierStatus
tierstatus = TierStatus()
```

```python
# Using AgentCompliance
agentcompliance = AgentCompliance()
agentcompliance.is_fully_compliant()
agentcompliance.compliance_score()
```

```python
# Using ComplianceResult
complianceresult = ComplianceResult()
complianceresult.contract_coverage_pct()
complianceresult.blueprint_coverage_pct()
```

### Function Usage

```python
# Using run_compliance_check
result = run_compliance_check()
```

```python
# Using is_fully_compliant
result = is_fully_compliant()
```

```python
# Using compliance_score
result = compliance_score()
```



---
**Generated**: 2026-03-26T09:39:04.971205
**Type**: api_reference
**Quality**: comprehensive
