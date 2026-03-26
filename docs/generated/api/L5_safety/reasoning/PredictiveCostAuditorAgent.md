# API Documentation: PredictiveCostAuditorAgent

**Target Audience**: developers, api_users

# PredictiveCostAuditorAgent API Documentation

**File**: `PredictiveCostAuditorAgent.py`
**Classes**: 4
**Functions**: 14

## Classes

- **HealingMetrics**
- **FileAudit**
- **CostReport**
- **PredictiveCostAuditorAgent** (inherits from SovereignBaseAgent, SubAtomicAgent)

## Functions

- **get_cost_auditor** -> PredictiveCostAuditor
- **__init__** -> None
- **_load_healing_history** -> Any
- **_audit_files** -> Any
- **_audit_single_file** -> FileAudit
- **_generate_recommendation** -> str
- **_generate_cost_report** -> CostReport
- **_generate_global_recommendations** -> list[str]
- **_display_report** -> Any
- **get_thermal_map** -> dict[str, str]
- **get_fission_candidates** -> list[str]
- **generate_daily_mission_report** -> str
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]


## Class: HealingMetrics

**Description**: Metrics for a single healing attempt.



## Class: FileAudit

**Description**: Audit record for a single file.



## Class: CostReport

**Description**: Comprehensive cost report.



## Class: PredictiveCostAuditorAgent

**Description**: 
    The Efficiency Guard - Predictive Cost Auditor

    Monitors economic ROI of swarm healing efforts.
    Provides thermal map of repository identifying technical debt hotspots.

    Thresholds:
    - Healing Sink: >3 attempts without success
    - Critical Sink: >$5 in tokens without success
    - Fission Candidate: >$10 total tokens spent

    Provides:
    - Daily Mission Report
    - Go/No-Go signals for pipeline
    - Atomic Fission recommendations
    - Cost optimization strategies
    

**Inherits from**: SovereignBaseAgent, SubAtomicAgent

### Methods

#### __init__
**Parameters**: self, ctx
**Returns**: None
**Description**: 
        Initialize Predictive Cost Auditor.

        Args:
            ctx: ValidationContext
        

#### _load_healing_history
**Parameters**: self
**Returns**: Any
**Description**: Load healing history from context.

#### _audit_files
**Parameters**: self
**Returns**: Any
**Description**: Audit each file for cost efficiency.

#### _audit_single_file
**Parameters**: self, file_path, metrics_list
**Returns**: FileAudit
**Description**: Audit a single file.

#### _generate_recommendation
**Parameters**: self, file_path, attempts, cost_usd, success_rate, Severity
**Returns**: str
**Description**: Generate Recommendation for file.

#### _generate_cost_report
**Parameters**: self
**Returns**: CostReport
**Description**: Generate comprehensive cost report.

#### _generate_global_recommendations
**Parameters**: self, healing_sinks, efficiency_score, cost_usd
**Returns**: list[str]
**Description**: Generate global recommendations.

#### _display_report
**Parameters**: self, report
**Returns**: Any
**Description**: Display cost report.

#### get_thermal_map
**Parameters**: self
**Returns**: dict[str, str]
**Description**: 
        Generate thermal map of repository.

        Returns:
            Dictionary mapping file paths to thermal status
            (cold, warm, hot, critical)
        

#### get_fission_candidates
**Parameters**: self
**Returns**: list[str]
**Description**: Get list of files that should undergo Atomic Fission.

#### generate_daily_mission_report
**Parameters**: self
**Returns**: str
**Description**: Generate daily mission report.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        Cost Audit Healing - Generates thermal maps and efficiency reports.
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by PredictiveCostAuditorAgent.

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
        



## Function: get_cost_auditor

**Parameters**: ctx
**Returns**: PredictiveCostAuditor
**Description**: Get or create global Cost Auditor instance.



## Function: __init__

**Parameters**: self, ctx
**Returns**: None
**Description**: 
        Initialize Predictive Cost Auditor.

        Args:
            ctx: ValidationContext
        



## Function: _load_healing_history

**Parameters**: self
**Returns**: Any
**Description**: Load healing history from context.



## Function: _audit_files

**Parameters**: self
**Returns**: Any
**Description**: Audit each file for cost efficiency.



## Function: _audit_single_file

**Parameters**: self, file_path, metrics_list
**Returns**: FileAudit
**Description**: Audit a single file.



## Function: _generate_recommendation

**Parameters**: self, file_path, attempts, cost_usd, success_rate, Severity
**Returns**: str
**Description**: Generate Recommendation for file.



## Function: _generate_cost_report

**Parameters**: self
**Returns**: CostReport
**Description**: Generate comprehensive cost report.



## Function: _generate_global_recommendations

**Parameters**: self, healing_sinks, efficiency_score, cost_usd
**Returns**: list[str]
**Description**: Generate global recommendations.



## Function: _display_report

**Parameters**: self, report
**Returns**: Any
**Description**: Display cost report.



## Function: get_thermal_map

**Parameters**: self
**Returns**: dict[str, str]
**Description**: 
        Generate thermal map of repository.

        Returns:
            Dictionary mapping file paths to thermal status
            (cold, warm, hot, critical)
        



## Function: get_fission_candidates

**Parameters**: self
**Returns**: list[str]
**Description**: Get list of files that should undergo Atomic Fission.



## Function: generate_daily_mission_report

**Parameters**: self
**Returns**: str
**Description**: Generate daily mission report.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        Cost Audit Healing - Generates thermal maps and efficiency reports.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by PredictiveCostAuditorAgent.

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
# Using HealingMetrics
healingmetrics = HealingMetrics()
```

```python
# Using FileAudit
fileaudit = FileAudit()
```

```python
# Using CostReport
costreport = CostReport()
```

### Function Usage

```python
# Using get_cost_auditor
result = get_cost_auditor(ctx)
```

```python
# Using __init__
result = __init__(ctx)
```

```python
# Using _load_healing_history
result = _load_healing_history()
```



---
**Generated**: 2026-03-26T09:39:05.354665
**Type**: api_reference
**Quality**: comprehensive
