# API Documentation: _ssot_phases

**Target Audience**: developers, api_users

# _ssot_phases API Documentation

**File**: `_ssot_phases.py`
**Classes**: 2
**Functions**: 36

## Classes

- **RuntimeStateManager**
- **tqdm**

## Functions

- **_get_uwg**
- **_get_heal_result_adapter**
- **assert_no_persistent_write** -> None
- **standard_heal**
- **discover_agents_from_registry** -> list[tuple[str, str]]
- **validate_territory_input** -> tuple[bool, str]
- **execute_phase1_discovery**
- **execute_phase1_discovery_impl**
- **execute_phase2_reconciliation**
- **execute_phase3_validation**
- **execute_phase3_alignment**
- **execute_phase3_alignment_impl**
- **_run_gravity_repair_global**
- **execute_phase4_architectural_validation**
- **execute_phase4_validation_impl**
- **execute_phase5_healing**
- **execute_phase5_healing_impl**
- **execute_phase7_final**
- **execute_phase7_final_impl**
- **__init__**
- **start_mission**
- **update_agent**
- **skip_agent**
- **complete_agent**
- **add_event**
- **finish_mission**
- **save**
- **_emergency_cleanup**
- **update_meta_learning**
- **__init__**
- **__iter__**
- **__next__**
- **__exit__**
- **update**
- **set_description**
- **_w6_hitl_archive_gate**


## Class: RuntimeStateManager

**Description**: Manages live state for dashboard observability.

### Methods

#### __init__
**Parameters**: self, project_root, execution_context

#### start_mission
**Parameters**: self, mission_type, agents_order

#### update_agent
**Parameters**: self, agent_name, layer

#### skip_agent
**Parameters**: self, agent_name, reason
**Description**: Records agent as skipped — confidence gate or HITL rejected execution.

#### complete_agent
**Parameters**: self, agent_name, success, details
**Description**: 
        [HARDENED] Silent Aggregation.
        Records agent completion but suppresses intermediate JSON console dumps.
        

#### add_event
**Parameters**: self, event_type, message

#### finish_mission
**Parameters**: self, status

#### save
**Parameters**: self
**Description**: 
        [HARDENED] Atomic Write Pattern with Permission Lockdown.
        Writes to temp file, sets 600 permissions, then renames.
        Once L0 mutation prohibition fires, latches _persistence_disabled=True
        and becomes a no-op for the remainder of the run.
        

#### _emergency_cleanup
**Parameters**: self
**Description**: Ensure state is finalized even on unhandled exit.

#### update_meta_learning
**Parameters**: self, experience_data
**Description**: [INTEGRATION] Updates cognitive metrics for dashboard.



## Class: tqdm

### Methods

#### __init__
**Parameters**: self

#### __iter__
**Parameters**: self

#### __next__
**Parameters**: self

#### __exit__
**Parameters**: self

#### update
**Parameters**: self, n

#### set_description
**Parameters**: self, s



## Function: _get_uwg



## Function: _get_heal_result_adapter



## Function: assert_no_persistent_write

**Parameters**: layer, operation
**Returns**: None
**Description**: Placeholder — actual enforcement is in UniversalWriteGateway.



## Function: standard_heal

**Parameters**: fn


## Function: discover_agents_from_registry

**Parameters**: project_root, dedupe
**Returns**: list[tuple[str, str]]
**Description**: Hybrid agent discovery: prefer cached JSON, fallback to live scan.



## Function: validate_territory_input

**Parameters**: territory
**Returns**: tuple[bool, str]
**Description**: Validate territory input with comprehensive security checks.



## Function: execute_phase1_discovery

**Parameters**: agents, territory, decision_engine, state_mgr, ctx, repo_root
**Description**: PHASE 1: TERRITORIAL DISCOVERY (Retriable)



## Function: execute_phase1_discovery_impl

**Parameters**: agents, territory, decision_engine, state_mgr, ctx, repo_root
**Description**: PHASE 1: TERRITORIAL DISCOVERY - Implementation with CognitiveDispositionAgent integration



## Function: execute_phase2_reconciliation

**Parameters**: agents, territory, decision_engine, state_mgr, plan, ctx, repo_root
**Description**: 
    PHASE 2: EXECUTE HEALING (HARDENED)
    Critical Path: Modifications occur here. Must strictly adhere to decision engine.
    Enhanced with atomic operations and sovereignty patterns from FileClassificationAgent.
    Returns: Dict conforming to HEAL_RESULT_SCHEMA
    



## Function: execute_phase3_validation

**Parameters**: agents, territory, original_violations, dry_run, repo_root
**Description**: 
    PHASE 3: POST-MORTEM VALIDATION

    Verifies that 'fixed' files now pass AST and SSOT checks.
    Does NOT blindly trust the agent's 'success' return value.
    



## Function: execute_phase3_alignment

**Parameters**: agents, territory, decision_engine, state_mgr, ctx, repo_root
**Description**: PHASE 3: STRUCTURAL ALIGNMENT (Retriable)



## Function: execute_phase3_alignment_impl

**Parameters**: agents, territory, decision_engine, state_mgr, ctx, repo_root
**Description**: PHASE 3: STRUCTURAL ALIGNMENT - Implementation



## Function: _run_gravity_repair_global

**Parameters**: agents, state_mgr, ctx, repo_root
**Description**: Run GravityLeakRepairAgent once globally — gravity (layer inversions) is repo-wide.



## Function: execute_phase4_architectural_validation

**Parameters**: agents, territory, state_mgr, ctx, repo_root
**Description**: PHASE 4: ARCHITECTURAL VALIDATION (Retriable)



## Function: execute_phase4_validation_impl

**Parameters**: agents, territory, state_mgr, ctx, repo_root
**Description**: PHASE 4: ARCHITECTURAL VALIDATION - Implementation



## Function: execute_phase5_healing

**Parameters**: agents, territory, gov_report, decision_engine, state_mgr, ctx, repo_root
**Description**: PHASE 5: HEALING (Retriable)



## Function: execute_phase5_healing_impl

**Parameters**: agents, territory, gov_report, decision_engine, state_mgr, ctx, repo_root
**Description**: PHASE 5: HEALING - Implementation



## Function: execute_phase7_final

**Parameters**: agents, territory, state_mgr, decision_engine, repo_root
**Description**: PHASE 7: CERTIFICATION (Retriable)



## Function: execute_phase7_final_impl

**Parameters**: agents, territory, state_mgr, decision_engine, repo_root
**Description**: PHASE 7: CERTIFICATION - Implementation with Silent Aggregation



## Function: __init__

**Parameters**: self, project_root, execution_context


## Function: start_mission

**Parameters**: self, mission_type, agents_order


## Function: update_agent

**Parameters**: self, agent_name, layer


## Function: skip_agent

**Parameters**: self, agent_name, reason
**Description**: Records agent as skipped — confidence gate or HITL rejected execution.



## Function: complete_agent

**Parameters**: self, agent_name, success, details
**Description**: 
        [HARDENED] Silent Aggregation.
        Records agent completion but suppresses intermediate JSON console dumps.
        



## Function: add_event

**Parameters**: self, event_type, message


## Function: finish_mission

**Parameters**: self, status


## Function: save

**Parameters**: self
**Description**: 
        [HARDENED] Atomic Write Pattern with Permission Lockdown.
        Writes to temp file, sets 600 permissions, then renames.
        Once L0 mutation prohibition fires, latches _persistence_disabled=True
        and becomes a no-op for the remainder of the run.
        



## Function: _emergency_cleanup

**Parameters**: self
**Description**: Ensure state is finalized even on unhandled exit.



## Function: update_meta_learning

**Parameters**: self, experience_data
**Description**: [INTEGRATION] Updates cognitive metrics for dashboard.



## Function: __init__

**Parameters**: self


## Function: __iter__

**Parameters**: self


## Function: __next__

**Parameters**: self


## Function: __exit__

**Parameters**: self


## Function: update

**Parameters**: self, n


## Function: set_description

**Parameters**: self, s


## Function: _w6_hitl_archive_gate

**Parameters**: file_path, msg


## Usage Examples

### Class Usage

```python
# Using RuntimeStateManager
runtimestatemanager = RuntimeStateManager()
runtimestatemanager.start_mission()
runtimestatemanager.update_agent()
```

```python
# Using tqdm
tqdm = tqdm()
tqdm.update()
tqdm.set_description()
```

### Function Usage

```python
# Using _get_uwg
result = _get_uwg()
```

```python
# Using _get_heal_result_adapter
result = _get_heal_result_adapter()
```

```python
# Using assert_no_persistent_write
result = assert_no_persistent_write(layer, operation)
```



---
**Generated**: 2026-03-26T09:39:03.339504
**Type**: api_reference
**Quality**: comprehensive
