# Phase 3 Integration Validation Evidence

## Scope

Validate that Phase 1+2 fixes (GravityLeakRepairAgent circuit breaker + RuntimeStateManager persistence latch) produce deterministic, terminating behaviour during both dry-run and full-heal execute_ssot runs.

## CODE_COMMIT

a06039822f30e1982f752b21e8bd542cad816e89

## EVIDENCE_COMMIT

a48b0138a0c6b8a48741978b170f4511c11fc727

## Environment

- Python: `Python 3.12.10`
- git HEAD: `a06039822f30e1982f752b21e8bd542cad816e89`
- LongPaths: `LongPathsEnabled registry value = 0`
- **BYPASS RECORDED: AGENTIC_BYPASS_LONGPATHS_CHECK=1 set because Windows LongPathsEnabled registry value is 0 (not active). This bypass is documented in execute_ssot.py and is the OS-correct workaround for this environment.**

## Pre-Run git status

```
M docs/evidence/phase_execute_ssot_integration_phase3.md
 M tools/run_phase3_integration.py
```

## Overall Result

**PASS: all 4 runs terminated**

## Determinism Check

### dry-run run-1 vs run-2

DIFF: JSON formatting-only; normalized match. Exit codes identical. Termination behavior identical. Normalization: json.loads + json.dumps(sort_keys=True) per line.

### full-heal run-1 vs run-2

DIFF: JSON formatting-only; normalized match (blob-sorted). Exit codes identical. Termination behavior identical. Normalization: raw_decode + deep_sort + sort_keys=True + blob sort.

## Run Outputs


### Run 1: Phase3A dry-run run-1

**argv:** `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --domains --dry-run -v`

**env overrides:**
```
  (none)
```

**exit code:** `0`
**elapsed:** `44.4s`
**timed_out:** `False`

**assertions:**
- OK: terminated in 44.4s (exit 0)
- WARN: 57 MUTATION_PROHIBITED lines (possible spam ? check for loop)
- INFO: no PLAN-ONLY emissions (no L0 gravity targets encountered, or dry-run)
- WARN: 57 MUTATION_PROHIBITED lines ? latch may not be active

**stdout:**
```
{
  "meta": {
    "territory": "prompt_governance",
    "timestamp": "2026-02-22T21:13:21.975171",
    "status": "NON-COMPLIANT",
    "sovereignty_level": "L5"
  },
  "metrics": {
    "confidence_score": 0.396,
    "violation_count": 17,
    "drift_count": 0,
    "errors": 0,
    "violations_fixed": 0
  },
  "governance_log": {
    "decisions": [],
    "files_processed": [
      "C:\\Git\\Agentic-Workflow\\scripts",
      "C:\\Git\\Agentic-Workflow\\.pytest_cache",
      "unknown"
    ],
    "scan_summary": {
      "total_files_scanned": 0,
      "files_with_violations": 3,
      "files_compliant": 0,
      "compliance_rate": 0,
      "file_types": {}
    }
  },
  "unified_violations": [
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\__init__.py', 'reason': 'SHALLOW VIOLATION (agentic_core): depth 1 != 3'}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\__init__.",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L2_execution\\\\types\\\\l2_phase_spec.py', 'reason': \"LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l2_'\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L2_execut",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L2_execution\\\\types\\\\l2_phase_spec_types.py', 'reason': \"LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l2_'\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L2_execut",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\enforcement\\\\rg_execution_safety_enforcer.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\enforcement\\\\rg_execution_safety_enforcer.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\blueprint_hash.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\blueprint_hash.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\cross_layer.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\cross_layer.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\import_graph.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\import_graph.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\leaf_node.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\leaf_node.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\mixin_ast.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\mixin_ast.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\territory_diff.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\territory_diff.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\types.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\types.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\volatile_rules.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\volatile_rules.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\__init__.py', 'reason': \"VOID
... [truncated 191299 chars]
```

**stderr:**
```
2026-02-22 21:13:11,150 INFO UnifiedSovereign [PREFLIGHT] Import/symbol check PASSED
2026-02-22 21:13:11,150 INFO UnifiedSovereign [FENCE-SELF-TEST] PASSED: Protected root fence is ACTIVE
2026-02-22 21:13:11,166 INFO agentic_core.L5_safety.reasoning.guardian_decision [L5_GUARDIAN] Decision for CC3AL1-5B4FED78: {'allow': True, 'escalate': False, 'violations': [], 'budget_remaining': 1000000, 'policy_version': '1.0'}
2026-02-22 21:13:11,166 WARNING agentic_core.L0_routing.enforcement.execution_gateway [V15-GW] Successful commit with no mutations detected
2026-02-22 21:13:11,192 WARNING root Windows LongPathsEnabled is NOT active (Set to 1 in Registry) - proceeding in dry-run mode
2026-02-22 21:13:11,192 INFO UnifiedSovereign ?? UNIFIED SOVEREIGN PROTOCOL STARTED
2026-02-22 21:13:11,192 INFO UnifiedSovereign   Mode: AUTONOMOUS
2026-02-22 21:13:11,192 INFO UnifiedSovereign   LLM: DISABLED
2026-02-22 21:13:11,192 INFO UnifiedSovereign   CDA: DISABLED
2026-02-22 21:13:11,192 INFO UnifiedSovereign   HEALING: DRY-RUN
2026-02-22 21:13:11,192 INFO UnifiedSovereign   APPROVAL: AUTO
2026-02-22 21:13:11,409 INFO UnifiedSovereign Total Awareness: Mandatory agent roster registered.
2026-02-22 21:13:11,409 INFO UnifiedSovereign   Agents validated: reconciler, location, hierarchy, arch_governor, gravity_repair, system_architect, file_classification, conversational_repair, cognitive_disposition, root_hygiene
2026-02-22 21:13:11,505 WARNING UnifiedSovereign [PROTECTED-ROOT] forcing dry_run=True for L0_routing
2026-02-22 21:13:11,505 ERROR agentic_core.L0_routing.enforcement.mutation_prohibition MUTATION_PROHIBITION DENY: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 21:13:11,506 CRITICAL UnifiedSovereign [RuntimeStateManager] L0 mutation prohibition active ? runtime state persistence DISABLED for this run (fail-closed). Reason: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 21:13:11,506 INFO UnifiedSovereign 🔍 [PHASE 8] Running integrity check (Scope: ['prompt_governance', 'L5_safety', 'L3_orchestration', 'L2_execution', 'L0_routing'])...
2026-02-22 21:13:13,288 WARNING UnifiedSovereign ⚠?  207 total violations identified.
2026-02-22 21:13:13,288 INFO UnifiedSovereign 🧠 L3 ORCHESTRATOR SUMMONED (via subprocess): Delegating command.
2026-02-22 21:13:13,321 WARNING UnifiedSovereign L3 Orchestrator not found. Falling back to L5 iteration.
2026-02-22 21:13:13,321 INFO UnifiedSovereign
============================================================
2026-02-22 21:13:13,321 INFO UnifiedSovereign 🚀 PROCESSING TERRITORY: prompt_governance
2026-02-22 21:13:13,321 INFO UnifiedSovereign ============================================================
2026-02-22 21:13:13,321 INFO UnifiedSovereign === PHASE 1: DISCOVERY - prompt_governance ===
2026-02-22 21:13:13,321 INFO UnifiedSovereign → Executing FilesystemSSOTReconcilerAgent (L0 - Maintenance)
2026-02-22 21:13:13,322 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Initialized with project_root: C:\Git\Agentic-Workflow
2026-02-22 21:13:13,322 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Archive root: C:\Git\Agentic-Workflow\archives\gatekeeper
2026-02-22 21:13:13,322 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent initialized for C:\Git\Agentic-Workflow
2026-02-22 21:13:13,322 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent: Detecting root-level drift...
2026-02-22 21:13:13,322 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: logs/
2026-02-22 21:13:13,322 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: scripts/
2026-02-22 21:13:13,325 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Duplicate folder: scripts/ at root AND SSOT location
2026-02-22 21:13:13,325 WARNING agentic_core.L5_safety.
... [truncated 506603 chars]
```


### Run 2: Phase3B full-heal run-1

**argv:** `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --allow-protected-root-mutation --domains -v`

**env overrides:**
```
  AGENTIC_BYPASS_LONGPATHS_CHECK=1
```

**exit code:** `0`
**elapsed:** `43.9s`
**timed_out:** `False`

**assertions:**
- OK: terminated in 43.9s (exit 0)
- WARN: 57 MUTATION_PROHIBITED lines (possible spam ? check for loop)
- OK: 50 PLAN-ONLY emission(s) found ? L0 files not mutated
- WARN: 57 MUTATION_PROHIBITED lines ? latch may not be active

**stdout:**
```

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\__init__.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\__init__.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L2_execution\types\l2_phase_spec.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\l2_phase_spec.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L2_execution\types\l2_phase_spec_types.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\l2_phase_spec_types.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\rg_execution_safety_enforcer.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\rg_execution_safety_enforcer.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\blueprint_hash.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\blueprint_hash.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\cross_layer.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\cross_layer.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\import_graph.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\import_graph.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\leaf_node.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\leaf_node.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\mixin_ast.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\mixin_ast.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\territory_diff.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\territory_diff.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\types.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\types.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\volatile_rules.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\volatile_rules.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\__init__.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\__init__.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L6_observability\golden_evaluation\resume_quality_evaluator.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\resume_quality_evaluator.py
  Reason:      Reorganizing structure
======================================================================
[WARNING] Windows LongPathsEnabled is NOT set to 1.
  [PLAN] RENAME noxfile.py -> noxfile_util.py
  [PLAN] RENAME py.py -> py_util.py
  [PLAN] RENAME typing_extensions.py -> typing_extensions_config.py
  [PLAN] RENAME _virtualenv.py -> virtualenv.py
  [PLAN] RENAME test_cases.py -> Case.py
  [PLAN
... [truncated 198304 chars]
```

**stderr:**
```
2026-02-22 21:13:55,516 INFO UnifiedSovereign [PREFLIGHT] Import/symbol check PASSED
2026-02-22 21:13:55,516 WARNING UnifiedSovereign [FENCE-SELF-TEST] SKIPPED: --allow-protected-root-mutation enabled
2026-02-22 21:13:55,532 INFO agentic_core.L5_safety.reasoning.guardian_decision [L5_GUARDIAN] Decision for CC3AL1-5B4FED78: {'allow': True, 'escalate': False, 'violations': [], 'budget_remaining': 1000000, 'policy_version': '1.0'}
2026-02-22 21:13:55,532 WARNING agentic_core.L0_routing.enforcement.execution_gateway [V15-GW] Successful commit with no mutations detected
2026-02-22 21:13:55,555 WARNING root AGENTIC_BYPASS_LONGPATHS_CHECK=1: skipping LongPathsEnabled hard-fail
2026-02-22 21:13:55,556 INFO UnifiedSovereign ?? UNIFIED SOVEREIGN PROTOCOL STARTED
2026-02-22 21:13:55,556 INFO UnifiedSovereign   Mode: AUTONOMOUS
2026-02-22 21:13:55,556 INFO UnifiedSovereign   LLM: ENABLED
2026-02-22 21:13:55,556 INFO UnifiedSovereign   CDA: DISABLED
2026-02-22 21:13:55,556 INFO UnifiedSovereign   HEALING: ACTIVE
2026-02-22 21:13:55,556 INFO UnifiedSovereign   APPROVAL: AUTO
2026-02-22 21:13:55,763 INFO UnifiedSovereign Total Awareness: Mandatory agent roster registered.
2026-02-22 21:13:55,763 INFO UnifiedSovereign   Agents validated: reconciler, location, hierarchy, arch_governor, gravity_repair, system_architect, file_classification, conversational_repair, cognitive_disposition, root_hygiene
2026-02-22 21:13:55,862 ERROR agentic_core.L0_routing.enforcement.mutation_prohibition MUTATION_PROHIBITION DENY: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 21:13:55,862 CRITICAL UnifiedSovereign [RuntimeStateManager] L0 mutation prohibition active ? runtime state persistence DISABLED for this run (fail-closed). Reason: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 21:13:55,862 INFO UnifiedSovereign 🔍 [PHASE 8] Running integrity check (Scope: ['prompt_governance', 'L5_safety', 'L3_orchestration', 'L2_execution', 'L0_routing'])...
2026-02-22 21:13:57,610 WARNING UnifiedSovereign ⚠?  207 total violations identified.
2026-02-22 21:13:57,610 INFO UnifiedSovereign 🧠 L3 ORCHESTRATOR SUMMONED (via subprocess): Delegating command.
2026-02-22 21:13:57,643 WARNING UnifiedSovereign L3 Orchestrator not found. Falling back to L5 iteration.
2026-02-22 21:13:57,643 INFO UnifiedSovereign
============================================================
2026-02-22 21:13:57,643 INFO UnifiedSovereign 🚀 PROCESSING TERRITORY: prompt_governance
2026-02-22 21:13:57,643 INFO UnifiedSovereign ============================================================
2026-02-22 21:13:57,643 INFO UnifiedSovereign === PHASE 1: DISCOVERY - prompt_governance ===
2026-02-22 21:13:57,643 INFO UnifiedSovereign → Executing FilesystemSSOTReconcilerAgent (L0 - Maintenance)
2026-02-22 21:13:57,643 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Initialized with project_root: C:\Git\Agentic-Workflow
2026-02-22 21:13:57,644 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Archive root: C:\Git\Agentic-Workflow\archives\gatekeeper
2026-02-22 21:13:57,644 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent initialized for C:\Git\Agentic-Workflow
2026-02-22 21:13:57,644 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent: Detecting root-level drift...
2026-02-22 21:13:57,644 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: logs/
2026-02-22 21:13:57,644 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: scripts/
2026-02-22 21:13:57,647 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Duplicate folder: scripts/ at root AND SSOT location
2026-02-22 21:13:57,647 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Duplicate folder: logs/ at root AND SSOT location
2026-02-22
... [truncated 526576 chars]
```


### Run 3: Phase3A dry-run run-2

**argv:** `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --domains --dry-run -v`

**env overrides:**
```
  (none)
```

**exit code:** `0`
**elapsed:** `44.2s`
**timed_out:** `False`

**assertions:**
- OK: terminated in 44.2s (exit 0)
- WARN: 57 MUTATION_PROHIBITED lines (possible spam ? check for loop)
- INFO: no PLAN-ONLY emissions (no L0 gravity targets encountered, or dry-run)
- WARN: 57 MUTATION_PROHIBITED lines ? latch may not be active

**stdout:**
```
{
  "meta": {
    "territory": "prompt_governance",
    "timestamp": "2026-02-22T21:14:50.143180",
    "status": "NON-COMPLIANT",
    "sovereignty_level": "L5"
  },
  "metrics": {
    "confidence_score": 0.396,
    "violation_count": 17,
    "drift_count": 0,
    "errors": 0,
    "violations_fixed": 0
  },
  "governance_log": {
    "decisions": [],
    "files_processed": [
      "unknown",
      "C:\\Git\\Agentic-Workflow\\scripts",
      "C:\\Git\\Agentic-Workflow\\.pytest_cache"
    ],
    "scan_summary": {
      "total_files_scanned": 0,
      "files_with_violations": 3,
      "files_compliant": 0,
      "compliance_rate": 0,
      "file_types": {}
    }
  },
  "unified_violations": [
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\__init__.py', 'reason': 'SHALLOW VIOLATION (agentic_core): depth 1 != 3'}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\__init__.",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L2_execution\\\\types\\\\l2_phase_spec.py', 'reason': \"LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l2_'\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L2_execut",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L2_execution\\\\types\\\\l2_phase_spec_types.py', 'reason': \"LAYER PREFIX VIOLATION: Filename has forbidden prefix 'l2_'\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L2_execut",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\enforcement\\\\rg_execution_safety_enforcer.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\enforcement\\\\rg_execution_safety_enforcer.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\blueprint_hash.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\blueprint_hash.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\cross_layer.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\cross_layer.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\import_graph.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\import_graph.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\leaf_node.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\leaf_node.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\mixin_ast.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\mixin_ast.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\territory_diff.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\territory_diff.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\types.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\types.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\volatile_rules.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\volatile_rules.py' not in sovereign territory\"}",
      "severity": "medium",
      "recommended_action": "Fix location/naming issue: {'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety",
      "llm_triggered": false,
      "confidence": 0.792
    },
    {
      "type": "LOCATION",
      "source": "LocationAgent",
      "file": "unknown",
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\__init__.py', 'reason': \"VOID
... [truncated 191299 chars]
```

**stderr:**
```
2026-02-22 21:14:39,425 INFO UnifiedSovereign [PREFLIGHT] Import/symbol check PASSED
2026-02-22 21:14:39,426 INFO UnifiedSovereign [FENCE-SELF-TEST] PASSED: Protected root fence is ACTIVE
2026-02-22 21:14:39,441 INFO agentic_core.L5_safety.reasoning.guardian_decision [L5_GUARDIAN] Decision for CC3AL1-5B4FED78: {'allow': True, 'escalate': False, 'violations': [], 'budget_remaining': 1000000, 'policy_version': '1.0'}
2026-02-22 21:14:39,442 WARNING agentic_core.L0_routing.enforcement.execution_gateway [V15-GW] Successful commit with no mutations detected
2026-02-22 21:14:39,464 WARNING root Windows LongPathsEnabled is NOT active (Set to 1 in Registry) - proceeding in dry-run mode
2026-02-22 21:14:39,466 INFO UnifiedSovereign ?? UNIFIED SOVEREIGN PROTOCOL STARTED
2026-02-22 21:14:39,466 INFO UnifiedSovereign   Mode: AUTONOMOUS
2026-02-22 21:14:39,466 INFO UnifiedSovereign   LLM: DISABLED
2026-02-22 21:14:39,466 INFO UnifiedSovereign   CDA: DISABLED
2026-02-22 21:14:39,466 INFO UnifiedSovereign   HEALING: DRY-RUN
2026-02-22 21:14:39,466 INFO UnifiedSovereign   APPROVAL: AUTO
2026-02-22 21:14:39,671 INFO UnifiedSovereign Total Awareness: Mandatory agent roster registered.
2026-02-22 21:14:39,671 INFO UnifiedSovereign   Agents validated: reconciler, location, hierarchy, arch_governor, gravity_repair, system_architect, file_classification, conversational_repair, cognitive_disposition, root_hygiene
2026-02-22 21:14:39,768 WARNING UnifiedSovereign [PROTECTED-ROOT] forcing dry_run=True for L0_routing
2026-02-22 21:14:39,768 ERROR agentic_core.L0_routing.enforcement.mutation_prohibition MUTATION_PROHIBITION DENY: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 21:14:39,768 CRITICAL UnifiedSovereign [RuntimeStateManager] L0 mutation prohibition active ? runtime state persistence DISABLED for this run (fail-closed). Reason: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 21:14:39,769 INFO UnifiedSovereign 🔍 [PHASE 8] Running integrity check (Scope: ['prompt_governance', 'L5_safety', 'L3_orchestration', 'L2_execution', 'L0_routing'])...
2026-02-22 21:14:41,509 WARNING UnifiedSovereign ⚠?  207 total violations identified.
2026-02-22 21:14:41,509 INFO UnifiedSovereign 🧠 L3 ORCHESTRATOR SUMMONED (via subprocess): Delegating command.
2026-02-22 21:14:41,540 WARNING UnifiedSovereign L3 Orchestrator not found. Falling back to L5 iteration.
2026-02-22 21:14:41,542 INFO UnifiedSovereign
============================================================
2026-02-22 21:14:41,542 INFO UnifiedSovereign 🚀 PROCESSING TERRITORY: prompt_governance
2026-02-22 21:14:41,542 INFO UnifiedSovereign ============================================================
2026-02-22 21:14:41,542 INFO UnifiedSovereign === PHASE 1: DISCOVERY - prompt_governance ===
2026-02-22 21:14:41,542 INFO UnifiedSovereign → Executing FilesystemSSOTReconcilerAgent (L0 - Maintenance)
2026-02-22 21:14:41,542 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Initialized with project_root: C:\Git\Agentic-Workflow
2026-02-22 21:14:41,542 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Archive root: C:\Git\Agentic-Workflow\archives\gatekeeper
2026-02-22 21:14:41,542 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent initialized for C:\Git\Agentic-Workflow
2026-02-22 21:14:41,542 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent: Detecting root-level drift...
2026-02-22 21:14:41,543 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: logs/
2026-02-22 21:14:41,543 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: scripts/
2026-02-22 21:14:41,545 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Duplicate folder: scripts/ at root AND SSOT location
2026-02-22 21:14:41,546 WARNING agentic_core.L5_safety.
... [truncated 506603 chars]
```


### Run 4: Phase3B full-heal run-2

**argv:** `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --allow-protected-root-mutation --domains -v`

**env overrides:**
```
  AGENTIC_BYPASS_LONGPATHS_CHECK=1
```

**exit code:** `0`
**elapsed:** `44.0s`
**timed_out:** `False`

**assertions:**
- OK: terminated in 44.0s (exit 0)
- WARN: 57 MUTATION_PROHIBITED lines (possible spam ? check for loop)
- OK: 50 PLAN-ONLY emission(s) found ? L0 files not mutated
- WARN: 57 MUTATION_PROHIBITED lines ? latch may not be active

**stdout:**
```

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\__init__.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\__init__.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L2_execution\types\l2_phase_spec.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\l2_phase_spec.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L2_execution\types\l2_phase_spec_types.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\l2_phase_spec_types.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\rg_execution_safety_enforcer.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\rg_execution_safety_enforcer.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\blueprint_hash.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\blueprint_hash.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\cross_layer.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\cross_layer.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\import_graph.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\import_graph.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\leaf_node.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\leaf_node.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\mixin_ast.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\mixin_ast.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\territory_diff.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\territory_diff.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\types.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\types.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\volatile_rules.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\volatile_rules.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\enforcement\__init__.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\__init__.py
  Reason:      Reorganizing structure
======================================================================

======================================================================
🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED
======================================================================
  Operation:   MOVE
  Requester:   LocationHealerAgent
  Source:      C:\Git\Agentic-Workflow\agentic_core\L6_observability\golden_evaluation\resume_quality_evaluator.py
  Destination: C:\Git\Agentic-Workflow\.healing_backups\location_violations\resume_quality_evaluator.py
  Reason:      Reorganizing structure
======================================================================
[WARNING] Windows LongPathsEnabled is NOT set to 1.
  [PLAN] RENAME noxfile.py -> noxfile_util.py
  [PLAN] RENAME py.py -> py_util.py
  [PLAN] RENAME typing_extensions.py -> typing_extensions_config.py
  [PLAN] RENAME _virtualenv.py -> virtualenv.py
  [PLAN] RENAME test_cases.py -> Case.py
  [PLAN
... [truncated 198304 chars]
```

**stderr:**
```
2026-02-22 21:15:23,631 INFO UnifiedSovereign [PREFLIGHT] Import/symbol check PASSED
2026-02-22 21:15:23,631 WARNING UnifiedSovereign [FENCE-SELF-TEST] SKIPPED: --allow-protected-root-mutation enabled
2026-02-22 21:15:23,646 INFO agentic_core.L5_safety.reasoning.guardian_decision [L5_GUARDIAN] Decision for CC3AL1-5B4FED78: {'allow': True, 'escalate': False, 'violations': [], 'budget_remaining': 1000000, 'policy_version': '1.0'}
2026-02-22 21:15:23,646 WARNING agentic_core.L0_routing.enforcement.execution_gateway [V15-GW] Successful commit with no mutations detected
2026-02-22 21:15:23,674 WARNING root AGENTIC_BYPASS_LONGPATHS_CHECK=1: skipping LongPathsEnabled hard-fail
2026-02-22 21:15:23,674 INFO UnifiedSovereign ?? UNIFIED SOVEREIGN PROTOCOL STARTED
2026-02-22 21:15:23,675 INFO UnifiedSovereign   Mode: AUTONOMOUS
2026-02-22 21:15:23,675 INFO UnifiedSovereign   LLM: ENABLED
2026-02-22 21:15:23,675 INFO UnifiedSovereign   CDA: DISABLED
2026-02-22 21:15:23,675 INFO UnifiedSovereign   HEALING: ACTIVE
2026-02-22 21:15:23,675 INFO UnifiedSovereign   APPROVAL: AUTO
2026-02-22 21:15:23,881 INFO UnifiedSovereign Total Awareness: Mandatory agent roster registered.
2026-02-22 21:15:23,881 INFO UnifiedSovereign   Agents validated: reconciler, location, hierarchy, arch_governor, gravity_repair, system_architect, file_classification, conversational_repair, cognitive_disposition, root_hygiene
2026-02-22 21:15:23,981 ERROR agentic_core.L0_routing.enforcement.mutation_prohibition MUTATION_PROHIBITION DENY: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 21:15:23,981 CRITICAL UnifiedSovereign [RuntimeStateManager] L0 mutation prohibition active ? runtime state persistence DISABLED for this run (fail-closed). Reason: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 21:15:23,981 INFO UnifiedSovereign 🔍 [PHASE 8] Running integrity check (Scope: ['prompt_governance', 'L5_safety', 'L3_orchestration', 'L2_execution', 'L0_routing'])...
2026-02-22 21:15:25,726 WARNING UnifiedSovereign ⚠?  207 total violations identified.
2026-02-22 21:15:25,726 INFO UnifiedSovereign 🧠 L3 ORCHESTRATOR SUMMONED (via subprocess): Delegating command.
2026-02-22 21:15:25,758 WARNING UnifiedSovereign L3 Orchestrator not found. Falling back to L5 iteration.
2026-02-22 21:15:25,758 INFO UnifiedSovereign
============================================================
2026-02-22 21:15:25,758 INFO UnifiedSovereign 🚀 PROCESSING TERRITORY: prompt_governance
2026-02-22 21:15:25,758 INFO UnifiedSovereign ============================================================
2026-02-22 21:15:25,758 INFO UnifiedSovereign === PHASE 1: DISCOVERY - prompt_governance ===
2026-02-22 21:15:25,758 INFO UnifiedSovereign → Executing FilesystemSSOTReconcilerAgent (L0 - Maintenance)
2026-02-22 21:15:25,760 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Initialized with project_root: C:\Git\Agentic-Workflow
2026-02-22 21:15:25,760 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Archive root: C:\Git\Agentic-Workflow\archives\gatekeeper
2026-02-22 21:15:25,760 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent initialized for C:\Git\Agentic-Workflow
2026-02-22 21:15:25,760 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent: Detecting root-level drift...
2026-02-22 21:15:25,760 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: logs/
2026-02-22 21:15:25,760 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: scripts/
2026-02-22 21:15:25,764 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Duplicate folder: scripts/ at root AND SSOT location
2026-02-22 21:15:25,764 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Duplicate folder: logs/ at root AND SSOT location
2026-02-22
... [truncated 526576 chars]
```


## Post-Run git status

```
M docs/evidence/phase_execute_ssot_integration_phase3.md
 M tools/run_phase3_integration.py
```

## INSPECTED_FILES

- agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py
- agentic_core/L0_routing/scripts/execute_ssot.py
- agentic_core/L0_routing/scripts/execute_ssot_entrypoint.py
- tests/agentic_core/L5_safety/gravity/test_gravity_leak_repair_agent.py
