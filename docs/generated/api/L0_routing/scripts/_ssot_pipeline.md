# API Documentation: _ssot_pipeline

**Target Audience**: developers, api_users

# _ssot_pipeline API Documentation

**File**: `_ssot_pipeline.py`
**Classes**: 1
**Functions**: 10

## Classes

- **_ScanCtx**

## Functions

- **get_execution_plan** -> list[dict]
- **_emit_pipeline_digest** -> str
- **run_pipeline** -> 'dict[str, object]'
- **print_execution_plan** -> None
- **resolve_agent_subset** -> list[str]
- **list_available_agents** -> list
- **_emit_adg_pre_run_artifact** -> None
- **_build_ssot_territory_targets** -> list[str]
- **_compute_pipeline_digest** -> str
- **try_summon_orchestrator** -> 'tuple[bool, Any]'


## Class: _ScanCtx



## Function: get_execution_plan

**Returns**: list[dict]
**Description**: Return the deterministic, ordered execution plan.



## Function: _emit_pipeline_digest

**Parameters**: adapters, territory, ctx
**Returns**: str
**Description**: Compute and print the deterministic pipeline digest (once per run).



## Function: run_pipeline

**Parameters**: adapters, territory, decision_engine, state_mgr, ctx
**Returns**: 'dict[str, object]'
**Description**: Unified pipeline loop replacing the five bespoke execute_phase*_impl functions.

    Governance invariants enforced:
    - Digest emitted exactly once per call via _emit_pipeline_digest.
    - pre_commit and validate receive scan_ctx (heal=False) structurally.
    - update_agent is never called for execute/heal when gated or fatal.
    - All four subphase slots are always present in AgentRunResult.subphases.
    - Exception in any subphase -> fatal=True -> remaining subphases skipped.
    - Confidence gate fires immediately after validate, before any execute call.

    Returns dict mapping agent_id -> AgentRunResult.
    



## Function: print_execution_plan

**Parameters**: arbitrate_plan, ptc_plan
**Returns**: None
**Description**: Print stable, sorted execution plan to stdout.



## Function: resolve_agent_subset

**Parameters**: requested
**Returns**: list[str]
**Description**: Resolve requested agent keys to a closed set including dependencies.

    Raises ValueError on unknown keys.
    Deterministic ordering: sorted alphabetically after closure.
    



## Function: list_available_agents

**Parameters**: project_root, dedupe
**Returns**: list
**Description**: Alias for discover_agents_from_registry (backward compat).



## Function: _emit_adg_pre_run_artifact

**Parameters**: repo_root
**Returns**: None
**Description**: Emit artifacts/adg/execution_impact_<timestamp>.json before main execution.

    Gracefully degrades: if ADG is unavailable, writes a minimal artifact with
    adg_available=false. Never raises — must not block main execution.
    



## Function: _build_ssot_territory_targets

**Parameters**: project_root
**Returns**: list[str]
**Description**: Derive the canonical territory target list from SOVEREIGN_TERRITORIES SSOT.



## Function: _compute_pipeline_digest

**Parameters**: targets
**Returns**: str
**Description**: Compute a stable determinism digest for the pipeline run.



## Function: try_summon_orchestrator

**Parameters**: project_root, targets, execute
**Returns**: 'tuple[bool, Any]'
**Description**: Attempt L3 Orchestrator execution. Returns (success, results).



## Usage Examples

### Class Usage

```python
# Using _ScanCtx
_scanctx = _ScanCtx()
```

### Function Usage

```python
# Using get_execution_plan
result = get_execution_plan()
```

```python
# Using _emit_pipeline_digest
result = _emit_pipeline_digest(adapters, territory)
```

```python
# Using run_pipeline
result = run_pipeline(adapters, territory)
```



---
**Generated**: 2026-03-26T09:39:03.345674
**Type**: api_reference
**Quality**: comprehensive
