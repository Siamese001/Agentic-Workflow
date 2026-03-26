# API Documentation: _ssot_reporting

**Target Audience**: developers, api_users

# _ssot_reporting API Documentation

**File**: `_ssot_reporting.py`
**Classes**: 0
**Functions**: 17


## Functions

- **assert_no_persistent_write** -> None
- **save_comprehensive_reports**
- **save_aggregate_report** -> 'Path | None'
- **_collect_llm_call_trace** -> dict
- **_collect_blocker_scan** -> list
- **_build_coverage_proof** -> dict
- **_build_calibration_proof** -> dict
- **_write_mandatory_json_output** -> None
- **_write_heal_run_complete** -> dict
- **_write_failure_forensics** -> None
- **_print_healing_heatmap** -> None
- **_print_meta_learning_summary** -> None
- **_print_run_manifest** -> int
- **_print_executive_summary** -> None
- **_lookup_outcome** -> str
- **_bar** -> str
- **_json_serialise**


## Function: assert_no_persistent_write

**Parameters**: layer, operation
**Returns**: None
**Description**: Placeholder — actual enforcement is in UniversalWriteGateway.



## Function: save_comprehensive_reports

**Parameters**: territory, detailed_cert, markdown_summary, files_affected, project_root
**Description**: Save detailed JSON manifest and Markdown summary to persistent files.



## Function: save_aggregate_report

**Parameters**: targets, project_root
**Returns**: 'Path | None'
**Description**: Merge all per-territory compliance reports into compliance_report_AGGREGATE.json.



## Function: _collect_llm_call_trace

**Parameters**: state_mgr, decision_engine
**Returns**: dict
**Description**: Extract LLM invocation proof from healing_actions and decision records.



## Function: _collect_blocker_scan

**Parameters**: state_mgr
**Returns**: list
**Description**: Extract blocked agent records with timestamps and blocker taxonomy.



## Function: _build_coverage_proof

**Parameters**: state_mgr, decision_engine
**Returns**: dict
**Description**: Build agent coverage proof: expected vs executed vs skipped.



## Function: _build_calibration_proof

**Parameters**: state_mgr, decision_engine
**Returns**: dict
**Description**: Compute per-tier confidence calibration error.



## Function: _write_mandatory_json_output

**Parameters**: state_mgr, decision_engine
**Returns**: None
**Description**: Write mandatory heal_run_output.json to logs/compliance_reports/.



## Function: _write_heal_run_complete

**Parameters**: state_mgr, decision_engine
**Returns**: dict
**Description**: Write authoritative heal_run_complete.json with prove-it evidence.



## Function: _write_failure_forensics

**Parameters**: state_mgr, decision_engine
**Returns**: None
**Description**: Write failure_forensics.json — detailed drill-down for failed/blocked/misrouted agents.



## Function: _print_healing_heatmap

**Parameters**: state_mgr, decision_engine
**Returns**: None
**Description**: Print a per-agent healing count heatmap at end of every run.



## Function: _print_meta_learning_summary

**Parameters**: state_mgr, decision_engine
**Returns**: None
**Description**: Print meta-learning bus additions summary.



## Function: _print_run_manifest

**Parameters**: state_mgr, targets
**Returns**: int
**Description**: Print a complete agent/phase execution manifest and return the number of gaps.



## Function: _print_executive_summary

**Parameters**: complete_output
**Returns**: None
**Description**: Print the mandatory high-signal pass/fail executive summary table.



## Function: _lookup_outcome

**Parameters**: agent_key
**Returns**: str


## Function: _bar

**Parameters**: n
**Returns**: str


## Function: _json_serialise

**Parameters**: obj


## Usage Examples

### Function Usage

```python
# Using assert_no_persistent_write
result = assert_no_persistent_write(layer, operation)
```

```python
# Using save_comprehensive_reports
result = save_comprehensive_reports(territory, detailed_cert)
```

```python
# Using save_aggregate_report
result = save_aggregate_report(targets, project_root)
```



---
**Generated**: 2026-03-26T09:39:03.364957
**Type**: api_reference
**Quality**: comprehensive
