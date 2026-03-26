# API Documentation: IntegrityGateExecutorAgent

**Target Audience**: developers, api_users

# IntegrityGateExecutorAgent API Documentation

**File**: `IntegrityGateExecutorAgent.py`
**Classes**: 12
**Functions**: 23

## Classes

- **ValidationRejectionReason** (inherits from Enum)
- **Violation**
- **IntegrityGateResult**
- **FinancialProofPoint**
- **KeyTechnology**
- **KeyExecutive**
- **StrategicLayer**
- **TechnicalLayer**
- **LeadershipLayer**
- **CitationMap**
- **DeepResearchOutput**
- **IntegrityGateExecutorAgent** (inherits from SovereignBaseAgent)

## Functions

- **validate_research_output** -> IntegrityGateResult
- **__init__** -> None
- **__init__** -> None
- **add_violation** -> None
- **__init__** -> None
- **__init__** -> None
- **__init__** -> None
- **__init__** -> None
- **__init__** -> None
- **__init__** -> None
- **__init__** -> None
- **__init__** -> None
- **__init__** -> None
- **_run_self_tests** -> bool
- **execute** -> IntegrityGateResult
- **_check_unbound_metrics** -> None
- **_check_fluff_language** -> None
- **_check_orphaned_claims** -> None
- **_check_citation_coverage** -> None
- **_calculate_depth_score** -> float
- **_has_specific_value** -> bool
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]


## Class: ValidationRejectionReason

**Description**: 
    Enumeration of validation rejection reasons.

    Defines the specific reasons why content validation may fail,
    including depth issues, unbound metrics, and language quality problems.
    

**Inherits from**: Enum



## Class: Violation

**Description**: 
    Represents a validation violation with reason and message.

    Attributes:
        reason: Reason for the validation failure
        message: Detailed violation message
    

### Methods

#### __init__
**Parameters**: self, reason, message
**Returns**: None
**Description**: 
        Initialize a validation violation.

        Args:
            reason: Reason for the validation failure
            message: Detailed violation message
        



## Class: IntegrityGateResult

**Description**: 
    Result of integrity gate validation.

    Attributes:
        passed: Whether validation passed
        depth_score: Depth quality score (0-1)
        violations: List of validation violations
    

### Methods

#### __init__
**Parameters**: self, passed, depth_score
**Returns**: None
**Description**: 
        Initialize integrity gate result.

        Args:
            passed: Whether validation passed
            depth_score: Depth quality score (0-1)
        

#### add_violation
**Parameters**: self, reason, message
**Returns**: None
**Description**: 
        Add a validation violation and mark result as failed.

        Args:
            reason: Reason for the validation failure
            message: Detailed violation message
        



## Class: FinancialProofPoint

**Description**: 
    Financial metric with value and source citation.

    Attributes:
        metric_name: Name of the financial metric
        value: Metric value
        source_citation: Optional source citation
    

### Methods

#### __init__
**Parameters**: self, metric_name, value, source_citation
**Returns**: None
**Description**: 
        Initialize financial proof point.

        Args:
            metric_name: Name of the financial metric
            value: Metric value
            source_citation: Optional source citation
        



## Class: KeyTechnology

**Description**: 
    Technology implementation with details and source.

    Attributes:
        technology_name: Name of the technology
        implementation_details: Implementation details
        source_citation: Optional source citation
    

### Methods

#### __init__
**Parameters**: self, technology_name, implementation_details, source_citation
**Returns**: None
**Description**: 
        Initialize key technology.

        Args:
            technology_name: Name of the technology
            implementation_details: Implementation details
            source_citation: Optional source citation
        



## Class: KeyExecutive

**Description**: 
    Key executive information.

    Attributes:
        name: Executive name
    

### Methods

#### __init__
**Parameters**: self, name
**Returns**: None
**Description**: 
        Initialize key executive.

        Args:
            name: Executive name
        



## Class: StrategicLayer

**Description**: 
    Strategic layer containing core thesis and initiatives.

    Attributes:
        core_thesis: Core strategic thesis
        strategic_initiatives: List of strategic initiatives
        financial_proof_points: List of financial proof points
    

### Methods

#### __init__
**Parameters**: self, core_thesis, strategic_initiatives, financial_proof_points
**Returns**: None
**Description**: 
        Initialize strategic layer.

        Args:
            core_thesis: Core strategic thesis
            strategic_initiatives: List of strategic initiatives
            financial_proof_points: List of financial proof points
        



## Class: TechnicalLayer

**Description**: 
    Technical layer containing implementation details.

    Attributes:
        implementation_summary: Summary of technical implementation
        key_technologies: List of key technologies used
    

### Methods

#### __init__
**Parameters**: self, implementation_summary, key_technologies
**Returns**: None
**Description**: 
        Initialize technical layer.

        Args:
            implementation_summary: Summary of technical implementation
            key_technologies: List of key technologies used
        



## Class: LeadershipLayer

**Description**: 
    Leadership layer containing key executives.

    Attributes:
        key_executives: List of key executives
    

### Methods

#### __init__
**Parameters**: self, key_executives
**Returns**: None
**Description**: 
        Initialize leadership layer.

        Args:
            key_executives: List of key executives
        



## Class: CitationMap

**Description**: 
    Citation map containing source citations.

    Attributes:
        citations: List of source citations
    

### Methods

#### __init__
**Parameters**: self, citations
**Returns**: None
**Description**: 
        Initialize citation map.

        Args:
            citations: List of source citations
        



## Class: DeepResearchOutput

**Description**: 
    Deep research output containing all layers.

    Attributes:
        StrategicLayer: Strategic layer with thesis and initiatives
        TechnicalLayer: Technical layer with implementation details
        LeadershipLayer: Leadership layer with key executives
        CitationMap: Citation map with source citations
    

### Methods

#### __init__
**Parameters**: self, StrategicLayer, TechnicalLayer, LeadershipLayer, CitationMap
**Returns**: None
**Description**: 
        Initialize deep research output.

        Args:
            StrategicLayer: Strategic layer with thesis and initiatives
            TechnicalLayer: Technical layer with implementation details
            LeadershipLayer: Leadership layer with key executives
            CitationMap: Citation map with source citations
        



## Class: IntegrityGateExecutorAgent

**Description**: Executor for integrity gate validation.

    Validates research outputs against quality criteria including
    depth, citations, and structural requirements.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, min_depth_score
**Returns**: None
**Description**: 
        Initialize integrity gate executor.

        Args:
            min_depth_score: Minimum depth score threshold (0-1, default 0.7)
        

#### _run_self_tests
**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L2 compliance.

#### execute
**Parameters**: self, research_output
**Returns**: IntegrityGateResult
**Description**: Execute integrity gate validation on research output.
        Args:
            research_output: The research output to validate

        Returns:
            IntegrityGateResult: Validation result with any violations
        

#### _check_unbound_metrics
**Parameters**: self, research_output, result
**Returns**: None

#### _check_fluff_language
**Parameters**: self, research_output, result
**Returns**: None

#### _check_orphaned_claims
**Parameters**: self, research_output, result
**Returns**: None

#### _check_citation_coverage
**Parameters**: self, research_output, result
**Returns**: None

#### _calculate_depth_score
**Parameters**: self, research_output
**Returns**: float
**Description**: Calculate depth score.

#### _has_specific_value
**Parameters**: self, value
**Returns**: bool
**Description**: Has specific value.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Validate research outputs in the repository for integrity violations.

        Scans for research output files and validates them against integrity
        standards including unbound metrics, fluff language, orphaned claims,
        and citation coverage.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes (generate reports)
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of agent names in call chain for cycle detection

        Returns:
            Dict with violations_found, violations_fixed, errors, skipped
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by IntegrityGateExecutorAgent.

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
        



## Function: validate_research_output

**Parameters**: research_output, min_depth_score
**Returns**: IntegrityGateResult
**Description**: TODO: Add docstring.



## Function: __init__

**Parameters**: self, reason, message
**Returns**: None
**Description**: 
        Initialize a validation violation.

        Args:
            reason: Reason for the validation failure
            message: Detailed violation message
        



## Function: __init__

**Parameters**: self, passed, depth_score
**Returns**: None
**Description**: 
        Initialize integrity gate result.

        Args:
            passed: Whether validation passed
            depth_score: Depth quality score (0-1)
        



## Function: add_violation

**Parameters**: self, reason, message
**Returns**: None
**Description**: 
        Add a validation violation and mark result as failed.

        Args:
            reason: Reason for the validation failure
            message: Detailed violation message
        



## Function: __init__

**Parameters**: self, metric_name, value, source_citation
**Returns**: None
**Description**: 
        Initialize financial proof point.

        Args:
            metric_name: Name of the financial metric
            value: Metric value
            source_citation: Optional source citation
        



## Function: __init__

**Parameters**: self, technology_name, implementation_details, source_citation
**Returns**: None
**Description**: 
        Initialize key technology.

        Args:
            technology_name: Name of the technology
            implementation_details: Implementation details
            source_citation: Optional source citation
        



## Function: __init__

**Parameters**: self, name
**Returns**: None
**Description**: 
        Initialize key executive.

        Args:
            name: Executive name
        



## Function: __init__

**Parameters**: self, core_thesis, strategic_initiatives, financial_proof_points
**Returns**: None
**Description**: 
        Initialize strategic layer.

        Args:
            core_thesis: Core strategic thesis
            strategic_initiatives: List of strategic initiatives
            financial_proof_points: List of financial proof points
        



## Function: __init__

**Parameters**: self, implementation_summary, key_technologies
**Returns**: None
**Description**: 
        Initialize technical layer.

        Args:
            implementation_summary: Summary of technical implementation
            key_technologies: List of key technologies used
        



## Function: __init__

**Parameters**: self, key_executives
**Returns**: None
**Description**: 
        Initialize leadership layer.

        Args:
            key_executives: List of key executives
        



## Function: __init__

**Parameters**: self, citations
**Returns**: None
**Description**: 
        Initialize citation map.

        Args:
            citations: List of source citations
        



## Function: __init__

**Parameters**: self, StrategicLayer, TechnicalLayer, LeadershipLayer, CitationMap
**Returns**: None
**Description**: 
        Initialize deep research output.

        Args:
            StrategicLayer: Strategic layer with thesis and initiatives
            TechnicalLayer: Technical layer with implementation details
            LeadershipLayer: Leadership layer with key executives
            CitationMap: Citation map with source citations
        



## Function: __init__

**Parameters**: self, min_depth_score
**Returns**: None
**Description**: 
        Initialize integrity gate executor.

        Args:
            min_depth_score: Minimum depth score threshold (0-1, default 0.7)
        



## Function: _run_self_tests

**Parameters**: self
**Returns**: bool
**Description**: Phase 1: Self-testing for L2 compliance.



## Function: execute

**Parameters**: self, research_output
**Returns**: IntegrityGateResult
**Description**: Execute integrity gate validation on research output.
        Args:
            research_output: The research output to validate

        Returns:
            IntegrityGateResult: Validation result with any violations
        



## Function: _check_unbound_metrics

**Parameters**: self, research_output, result
**Returns**: None


## Function: _check_fluff_language

**Parameters**: self, research_output, result
**Returns**: None


## Function: _check_orphaned_claims

**Parameters**: self, research_output, result
**Returns**: None


## Function: _check_citation_coverage

**Parameters**: self, research_output, result
**Returns**: None


## Function: _calculate_depth_score

**Parameters**: self, research_output
**Returns**: float
**Description**: Calculate depth score.



## Function: _has_specific_value

**Parameters**: self, value
**Returns**: bool
**Description**: Has specific value.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Validate research outputs in the repository for integrity violations.

        Scans for research output files and validates them against integrity
        standards including unbound metrics, fluff language, orphaned claims,
        and citation coverage.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes (generate reports)
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of agent names in call chain for cycle detection

        Returns:
            Dict with violations_found, violations_fixed, errors, skipped
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by IntegrityGateExecutorAgent.

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
        



## Usage Examples

### Class Usage

```python
# Using ValidationRejectionReason
validationrejectionreason = ValidationRejectionReason()
```

```python
# Using Violation
violation = Violation()
```

```python
# Using IntegrityGateResult
integritygateresult = IntegrityGateResult()
integritygateresult.add_violation()
```

### Function Usage

```python
# Using validate_research_output
result = validate_research_output(research_output, min_depth_score)
```

```python
# Using __init__
result = __init__(reason, message)
```

```python
# Using __init__
result = __init__(passed, depth_score)
```



---
**Generated**: 2026-03-26T09:39:05.283085
**Type**: api_reference
**Quality**: comprehensive
