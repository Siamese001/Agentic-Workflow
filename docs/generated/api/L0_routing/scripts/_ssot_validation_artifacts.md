# API Documentation: _ssot_validation_artifacts

**Target Audience**: developers, api_users

# _ssot_validation_artifacts API Documentation

**File**: `_ssot_validation_artifacts.py`
**Classes**: 0
**Functions**: 8


## Functions

- **_normalize_finding_id** -> str
- **_write_pre_validation_json** -> None
- **_write_post_validation_json** -> None
- **_write_run_manifest_json** -> None
- **_write_decision_summary_json** -> None
- **_write_artifact_integrity_json** -> None
- **_record_backup_archival_event**
- **_record_healing_action**


## Function: _normalize_finding_id

**Parameters**: finding, validator, index
**Returns**: str
**Description**: Generate normalized finding ID: {validator}:{path}:{rule}:{index}.

    Per hostile audit Section B3: Finding IDs must be normalized and deterministic.
    Per .windsurfrules §1.7: Identical input → identical output.
    



## Function: _write_pre_validation_json

**Parameters**: violations, trace_id, territory, validators_used, output_dir
**Returns**: None
**Description**: Write pre_validation.json before any healing occurs.

    Per hostile audit Section C2: Pre-heal state must be captured in structured artifact.
    Per hostile audit Section B3: Findings must have normalized IDs and validator provenance.
    Per .windsurfrules §2.2: Evidence must be deterministic, ASCII-only.
    



## Function: _write_post_validation_json

**Parameters**: pre_validation_path, phase3_result, trace_id, territory, output_dir
**Returns**: None
**Description**: Write post_validation.json after Phase 3 revalidation.

    Per hostile audit Section C4: Post-heal proof with resolved/residual/regression breakdown.
    Per hostile audit Section B5: Must show resolved, remaining, and newly introduced findings.
    



## Function: _write_run_manifest_json

**Parameters**: trace_id, execution_mode, territories, agents_executed, output_dir
**Returns**: None
**Description**: E6: Write run_manifest.json with run metadata and execution summary.

    Per hostile audit Section E6: run_manifest.json provides high-level run metadata.
    



## Function: _write_decision_summary_json

**Parameters**: trace_id, decisions_made, output_dir
**Returns**: None
**Description**: E6: Write decision_summary.json with routing decision audit trail.

    Per hostile audit Section E6: decision_summary.json provides routing decision audit.
    



## Function: _write_artifact_integrity_json

**Parameters**: trace_id, output_dir
**Returns**: None
**Description**: E7: Write artifact_integrity.json as final step with SHA256 hashes of all artifacts.

    Per hostile audit Section E7: artifact_integrity.json provides cryptographic proof of artifact set.
    



## Function: _record_backup_archival_event

**Parameters**: state_mgr, agent, category, count
**Description**: Record a backup archival event: a violation that required archival instead of direct fix.

    Appends to state_mgr.state["backup_archival_events"] so _fire_meta_learning_intake
    can surface the signal: 'N violations of category X required archival by agent Y'.
    This feeds the system learning pipeline with hard-to-heal violation patterns.
    



## Function: _record_healing_action

**Parameters**: state_mgr, agent, territory, routing_score, routing_tier, model, routing_gate, confidence, fix_summary, outcome, routing_digest, check_id
**Description**: [H2] Record a structured healing action for per-territory JSON and Markdown reports.

    Appends to state_mgr.state["healing_actions"] so Phase 5 can filter by territory
    and emit a healing_log in the detailed_cert JSON.

    Also persists the outcome to the system learning memory bridge (fire-and-forget,
    never raises) so healing patterns accumulate cross-session — same wiring as apps_*.
    



## Usage Examples

### Function Usage

```python
# Using _normalize_finding_id
result = _normalize_finding_id(finding, validator)
```

```python
# Using _write_pre_validation_json
result = _write_pre_validation_json(violations, trace_id)
```

```python
# Using _write_post_validation_json
result = _write_post_validation_json(pre_validation_path, phase3_result)
```



---
**Generated**: 2026-03-26T09:39:03.385036
**Type**: api_reference
**Quality**: comprehensive
