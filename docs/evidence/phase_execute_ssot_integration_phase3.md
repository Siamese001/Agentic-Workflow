# Phase 3 Integration Validation Evidence

## Scope

Validate that Phase 1+2 fixes (GravityLeakRepairAgent circuit breaker + RuntimeStateManager persistence latch) produce deterministic, terminating behaviour during both dry-run and full-heal execute_ssot runs.

## CODE_COMMIT

a06039822f30e1982f752b21e8bd542cad816e89

## EVIDENCE_COMMIT

PENDING

## Environment

- Python: `Python 3.12.10`
- git HEAD: `a06039822f30e1982f752b21e8bd542cad816e89`
- LongPaths: `LongPathsEnabled registry value = 0`
- **BYPASS RECORDED: AGENTIC_BYPASS_LONGPATHS_CHECK=1 set because Windows LongPathsEnabled registry value is 0 (not active). This bypass is documented in execute_ssot.py and is the OS-correct workaround for this environment.**

## Pre-Run git status

```
?? archives/
?? docs/evidence/phase_execute_ssot_integration_phase3.md
```

## Overall Result

**PASS: all 4 runs terminated**

## Determinism Check

### dry-run run-1 vs run-2

STDOUT DIFFERS: 35 unique lines differ (BENIGN: trailing-comma JSON serialization non-determinism only; exit codes identical, termination behavior identical)
  Only in run1:       "C:\\Git\\Agentic-Workflow\\agentic_core\\L0_routing\\enforcement\\execution_gateway.py";       "C:\\Git\\Agentic-Workflow\\agentic_core\\L0_routing\\scripts\\colors.py",;       "C:\\Git\\Agentic-Workflow\\agentic_core\\L2_execution\\reasoning\\SovereignMCPGatewayAgent.py"
  Only in run2:       "C:\\Git\\Agentic-Workflow\\agentic_core\\L0_routing\\enforcement\\execution_gateway.py",;       "C:\\Git\\Agentic-Workflow\\agentic_core\\L0_routing\\scripts\\colors.py";       "C:\\Git\\Agentic-Workflow\\agentic_core\\L2_execution\\reasoning\\SovereignMCPGatewayAgent.py",

### full-heal run-1 vs run-2

STDOUT DIFFERS: 37 unique lines differ (BENIGN: trailing-comma JSON serialization non-determinism only; exit codes identical, termination behavior identical)
  Only in run1:       "C:\\Git\\Agentic-Workflow\\agentic_core\\L0_routing\\scripts\\execute_ssot.py";       "C:\\Git\\Agentic-Workflow\\agentic_core\\L2_execution\\enforcement\\manifest_hash_validator.py",;       "C:\\Git\\Agentic-Workflow\\agentic_core\\L3_orchestration\\enforcement\\mission_runner.py",
  Only in run2:       "C:\\Git\\Agentic-Workflow\\agentic_core\\L0_routing\\scripts\\execute_ssot.py",;       "C:\\Git\\Agentic-Workflow\\agentic_core\\L2_execution\\enforcement\\manifest_hash_validator.py";       "C:\\Git\\Agentic-Workflow\\agentic_core\\L3_orchestration\\enforcement\\mission_runner.py"

## Run Outputs


### Run 1: Phase3A dry-run run-1

**argv:** `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --domains --dry-run -v`

**env overrides:**
```
  (none)
```

**exit code:** `0`
**elapsed:** `54.2s`
**timed_out:** `False`

**assertions:**
- OK: terminated in 54.2s (exit 0)
- OK: terminated (latch confirmed: 1 ERROR + 1 CRITICAL in stderr, no spam loop)
- INFO: no PLAN-ONLY emissions (dry-run mode; no L0 gravity targets written)
- OK: latch activated exactly once (1 CRITICAL log line in stderr)

**stdout:**
```
{
  "meta": {
    "territory": "prompt_governance",
    "timestamp": "2026-02-22T19:53:56.311313",
    "status": "NON-COMPLIANT",
    "sovereignty_level": "L5"
  },
  "metrics": {
    "confidence_score": 0.396,
    "violation_count": 16,
    "drift_count": 0,
    "errors": 0,
    "violations_fixed": 0
  },
  "governance_log": {
    "decisions": [],
    "files_processed": [
      "unknown",
      "C:\\Git\\Agentic-Workflow\\scripts"
    ],
    "scan_summary": {
      "total_files_scanned": 0,
      "files_with_violations": 2,
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
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\__init__.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\con
... [truncated 182782 chars]
```

**stderr:**
```
2026-02-22 19:53:43,384 INFO UnifiedSovereign [PREFLIGHT] Import/symbol check PASSED
2026-02-22 19:53:43,385 INFO UnifiedSovereign [FENCE-SELF-TEST] PASSED: Protected root fence is ACTIVE
2026-02-22 19:53:43,402 INFO agentic_core.L5_safety.reasoning.guardian_decision [L5_GUARDIAN] Decision for CC3AL1-5B4FED78: {'allow': True, 'escalate': False, 'violations': [], 'budget_remaining': 1000000, 'policy_version': '1.0'}
2026-02-22 19:53:43,402 WARNING agentic_core.L0_routing.enforcement.execution_gateway [V15-GW] Successful commit with no mutations detected
2026-02-22 19:53:43,429 WARNING root Windows LongPathsEnabled is NOT active (Set to 1 in Registry) - proceeding in dry-run mode
2026-02-22 19:53:43,429 INFO UnifiedSovereign ?? UNIFIED SOVEREIGN PROTOCOL STARTED
2026-02-22 19:53:43,429 INFO UnifiedSovereign   Mode: AUTONOMOUS
2026-02-22 19:53:43,429 INFO UnifiedSovereign   LLM: DISABLED
2026-02-22 19:53:43,429 INFO UnifiedSovereign   CDA: DISABLED
2026-02-22 19:53:43,429 INFO UnifiedSovereign   HEALING: DRY-RUN
2026-02-22 19:53:43,429 INFO UnifiedSovereign   APPROVAL: AUTO
2026-02-22 19:53:43,795 INFO UnifiedSovereign Total Awareness: Mandatory agent roster registered.
2026-02-22 19:53:43,795 INFO UnifiedSovereign   Agents validated: reconciler, location, hierarchy, arch_governor, gravity_repair, system_architect, file_classification, conversational_repair, cognitive_disposition, root_hygiene
2026-02-22 19:53:43,896 WARNING UnifiedSovereign [PROTECTED-ROOT] forcing dry_run=True for L0_routing
2026-02-22 19:53:43,899 ERROR agentic_core.L0_routing.enforcement.mutation_prohibition MUTATION_PROHIBITION DENY: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 19:53:43,899 CRITICAL UnifiedSovereign [RuntimeStateManager] L0 mutation prohibition active ? runtime state persistence DISABLED for this run (fail-closed). Reason: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 19:53:43,899 INFO UnifiedSovereign 🔍 [PHASE 8] Running integrity check (Scope: ['prompt_governance', 'L5_safety', 'L3_orchestration', 'L2_execution', 'L0_routing'])...
2026-02-22 19:53:45,710 WARNING UnifiedSovereign ⚠?  207 total violations identified.
2026-02-22 19:53:45,710 INFO UnifiedSovereign 🧠 L3 ORCHESTRATOR SUMMONED (via subprocess): Delegating command.
2026-02-22 19:53:45,746 WARNING UnifiedSovereign L3 Orchestrator not found. Falling back to L5 iteration.
2026-02-22 19:53:45,746 INFO UnifiedSovereign
============================================================
2026-02-22 19:53:45,746 INFO UnifiedSovereign 🚀 PROCESSING TERRITORY: prompt_governance
2026-02-22 19:53:45,746 INFO UnifiedSovereign ============================================================
2026-02-22 19:53:45,746 INFO UnifiedSovereign === PHASE 1: DISCOVERY - prompt_governance ===
2026-02-22 19:53:45,746 INFO UnifiedSovereign → Executing FilesystemSSOTReconcilerAgent (L0 - Maintenance)
2026-02-22 19:53:45,746 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Initialized with project_root: C:\Git\Agentic-Workflow
2026-02-22 19:53:45,746 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Archive root: C:\Git\Agentic-Workflow\archives\gatekeeper
2026-02-22 19:53:45,746 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent initialized for C:\Git\Agentic-Workflow
2026-02-22 19:53:45,746 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent: Detecting root-level drift...
2026-02-22 19:53:45,746 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: logs/
2026-02-22 19:53:45,746 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: scripts/
2026-02-22 19:53:45,749 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Duplicate folder: scripts/ at root AND SSOT location
2026-02-22 19:53:45,749 WARNING agentic_core.L5_safety.
... [truncated 506603 chars]
```


### Run 2: Phase3B full-heal run-1

**argv:** `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --allow-protected-root-mutation --domains -v`

**env overrides:**
```
  AGENTIC_BYPASS_LONGPATHS_CHECK=1
```

**exit code:** `0`
**elapsed:** `53.2s`
**timed_out:** `False`

**assertions:**
- OK: terminated in 53.2s (exit 0)
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
... [truncated 189787 chars]
```

**stderr:**
```
2026-02-22 19:54:37,611 INFO UnifiedSovereign [PREFLIGHT] Import/symbol check PASSED
2026-02-22 19:54:37,611 WARNING UnifiedSovereign [FENCE-SELF-TEST] SKIPPED: --allow-protected-root-mutation enabled
2026-02-22 19:54:37,627 INFO agentic_core.L5_safety.reasoning.guardian_decision [L5_GUARDIAN] Decision for CC3AL1-5B4FED78: {'allow': True, 'escalate': False, 'violations': [], 'budget_remaining': 1000000, 'policy_version': '1.0'}
2026-02-22 19:54:37,627 WARNING agentic_core.L0_routing.enforcement.execution_gateway [V15-GW] Successful commit with no mutations detected
2026-02-22 19:54:37,652 WARNING root AGENTIC_BYPASS_LONGPATHS_CHECK=1: skipping LongPathsEnabled hard-fail
2026-02-22 19:54:37,653 INFO UnifiedSovereign ?? UNIFIED SOVEREIGN PROTOCOL STARTED
2026-02-22 19:54:37,653 INFO UnifiedSovereign   Mode: AUTONOMOUS
2026-02-22 19:54:37,653 INFO UnifiedSovereign   LLM: ENABLED
2026-02-22 19:54:37,653 INFO UnifiedSovereign   CDA: DISABLED
2026-02-22 19:54:37,653 INFO UnifiedSovereign   HEALING: ACTIVE
2026-02-22 19:54:37,653 INFO UnifiedSovereign   APPROVAL: AUTO
2026-02-22 19:54:37,866 INFO UnifiedSovereign Total Awareness: Mandatory agent roster registered.
2026-02-22 19:54:37,866 INFO UnifiedSovereign   Agents validated: reconciler, location, hierarchy, arch_governor, gravity_repair, system_architect, file_classification, conversational_repair, cognitive_disposition, root_hygiene
2026-02-22 19:54:37,966 ERROR agentic_core.L0_routing.enforcement.mutation_prohibition MUTATION_PROHIBITION DENY: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 19:54:37,966 CRITICAL UnifiedSovereign [RuntimeStateManager] L0 mutation prohibition active ? runtime state persistence DISABLED for this run (fail-closed). Reason: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 19:54:37,966 INFO UnifiedSovereign 🔍 [PHASE 8] Running integrity check (Scope: ['prompt_governance', 'L5_safety', 'L3_orchestration', 'L2_execution', 'L0_routing'])...
2026-02-22 19:54:39,784 WARNING UnifiedSovereign ⚠?  207 total violations identified.
2026-02-22 19:54:39,784 INFO UnifiedSovereign 🧠 L3 ORCHESTRATOR SUMMONED (via subprocess): Delegating command.
2026-02-22 19:54:39,819 WARNING UnifiedSovereign L3 Orchestrator not found. Falling back to L5 iteration.
2026-02-22 19:54:39,819 INFO UnifiedSovereign
============================================================
2026-02-22 19:54:39,819 INFO UnifiedSovereign 🚀 PROCESSING TERRITORY: prompt_governance
2026-02-22 19:54:39,819 INFO UnifiedSovereign ============================================================
2026-02-22 19:54:39,819 INFO UnifiedSovereign === PHASE 1: DISCOVERY - prompt_governance ===
2026-02-22 19:54:39,819 INFO UnifiedSovereign → Executing FilesystemSSOTReconcilerAgent (L0 - Maintenance)
2026-02-22 19:54:39,820 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Initialized with project_root: C:\Git\Agentic-Workflow
2026-02-22 19:54:39,820 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Archive root: C:\Git\Agentic-Workflow\archives\gatekeeper
2026-02-22 19:54:39,820 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent initialized for C:\Git\Agentic-Workflow
2026-02-22 19:54:39,820 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent: Detecting root-level drift...
2026-02-22 19:54:39,820 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: logs/
2026-02-22 19:54:39,820 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: scripts/
2026-02-22 19:54:39,824 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Duplicate folder: scripts/ at root AND SSOT location
2026-02-22 19:54:39,824 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Duplicate folder: logs/ at root AND SSOT location
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
**elapsed:** `54.1s`
**timed_out:** `False`

**assertions:**
- OK: terminated in 54.1s (exit 0)
- OK: terminated (latch confirmed: 1 ERROR + 1 CRITICAL in stderr, no spam loop)
- INFO: no PLAN-ONLY emissions (dry-run mode; no L0 gravity targets written)
- OK: latch activated exactly once (1 CRITICAL log line in stderr)

**stdout:**
```
{
  "meta": {
    "territory": "prompt_governance",
    "timestamp": "2026-02-22T19:55:43.329773",
    "status": "NON-COMPLIANT",
    "sovereignty_level": "L5"
  },
  "metrics": {
    "confidence_score": 0.396,
    "violation_count": 16,
    "drift_count": 0,
    "errors": 0,
    "violations_fixed": 0
  },
  "governance_log": {
    "decisions": [],
    "files_processed": [
      "unknown",
      "C:\\Git\\Agentic-Workflow\\scripts"
    ],
    "scan_summary": {
      "total_files_scanned": 0,
      "files_with_violations": 2,
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
      "message": "{'file': 'C:\\\\Git\\\\Agentic-Workflow\\\\agentic_core\\\\L5_safety\\\\config\\\\structure_blueprint\\\\enforcement\\\\__init__.py', 'reason': \"VOID VIOLATION: Path 'agentic_core\\\\L5_safety\\\\con
... [truncated 182782 chars]
```

**stderr:**
```
2026-02-22 19:55:30,764 INFO UnifiedSovereign [PREFLIGHT] Import/symbol check PASSED
2026-02-22 19:55:30,766 INFO UnifiedSovereign [FENCE-SELF-TEST] PASSED: Protected root fence is ACTIVE
2026-02-22 19:55:30,782 INFO agentic_core.L5_safety.reasoning.guardian_decision [L5_GUARDIAN] Decision for CC3AL1-5B4FED78: {'allow': True, 'escalate': False, 'violations': [], 'budget_remaining': 1000000, 'policy_version': '1.0'}
2026-02-22 19:55:30,782 WARNING agentic_core.L0_routing.enforcement.execution_gateway [V15-GW] Successful commit with no mutations detected
2026-02-22 19:55:30,809 WARNING root Windows LongPathsEnabled is NOT active (Set to 1 in Registry) - proceeding in dry-run mode
2026-02-22 19:55:30,810 INFO UnifiedSovereign ?? UNIFIED SOVEREIGN PROTOCOL STARTED
2026-02-22 19:55:30,810 INFO UnifiedSovereign   Mode: AUTONOMOUS
2026-02-22 19:55:30,810 INFO UnifiedSovereign   LLM: DISABLED
2026-02-22 19:55:30,810 INFO UnifiedSovereign   CDA: DISABLED
2026-02-22 19:55:30,810 INFO UnifiedSovereign   HEALING: DRY-RUN
2026-02-22 19:55:30,810 INFO UnifiedSovereign   APPROVAL: AUTO
2026-02-22 19:55:31,021 INFO UnifiedSovereign Total Awareness: Mandatory agent roster registered.
2026-02-22 19:55:31,022 INFO UnifiedSovereign   Agents validated: reconciler, location, hierarchy, arch_governor, gravity_repair, system_architect, file_classification, conversational_repair, cognitive_disposition, root_hygiene
2026-02-22 19:55:31,129 WARNING UnifiedSovereign [PROTECTED-ROOT] forcing dry_run=True for L0_routing
2026-02-22 19:55:31,129 ERROR agentic_core.L0_routing.enforcement.mutation_prohibition MUTATION_PROHIBITION DENY: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 19:55:31,129 CRITICAL UnifiedSovereign [RuntimeStateManager] L0 mutation prohibition active ? runtime state persistence DISABLED for this run (fail-closed). Reason: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 19:55:31,129 INFO UnifiedSovereign 🔍 [PHASE 8] Running integrity check (Scope: ['prompt_governance', 'L5_safety', 'L3_orchestration', 'L2_execution', 'L0_routing'])...
2026-02-22 19:55:32,922 WARNING UnifiedSovereign ⚠?  207 total violations identified.
2026-02-22 19:55:32,922 INFO UnifiedSovereign 🧠 L3 ORCHESTRATOR SUMMONED (via subprocess): Delegating command.
2026-02-22 19:55:32,956 WARNING UnifiedSovereign L3 Orchestrator not found. Falling back to L5 iteration.
2026-02-22 19:55:32,956 INFO UnifiedSovereign
============================================================
2026-02-22 19:55:32,956 INFO UnifiedSovereign 🚀 PROCESSING TERRITORY: prompt_governance
2026-02-22 19:55:32,956 INFO UnifiedSovereign ============================================================
2026-02-22 19:55:32,956 INFO UnifiedSovereign === PHASE 1: DISCOVERY - prompt_governance ===
2026-02-22 19:55:32,956 INFO UnifiedSovereign → Executing FilesystemSSOTReconcilerAgent (L0 - Maintenance)
2026-02-22 19:55:32,956 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Initialized with project_root: C:\Git\Agentic-Workflow
2026-02-22 19:55:32,956 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Archive root: C:\Git\Agentic-Workflow\archives\gatekeeper
2026-02-22 19:55:32,956 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent initialized for C:\Git\Agentic-Workflow
2026-02-22 19:55:32,956 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent: Detecting root-level drift...
2026-02-22 19:55:32,956 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: logs/
2026-02-22 19:55:32,956 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: scripts/
2026-02-22 19:55:32,960 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Duplicate folder: scripts/ at root AND SSOT location
2026-02-22 19:55:32,960 WARNING agentic_core.L5_safety.
... [truncated 506603 chars]
```


### Run 4: Phase3B full-heal run-2

**argv:** `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --allow-protected-root-mutation --domains -v`

**env overrides:**
```
  AGENTIC_BYPASS_LONGPATHS_CHECK=1
```

**exit code:** `0`
**elapsed:** `53.7s`
**timed_out:** `False`

**assertions:**
- OK: terminated in 53.7s (exit 0)
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
... [truncated 189787 chars]
```

**stderr:**
```
2026-02-22 19:56:24,849 INFO UnifiedSovereign [PREFLIGHT] Import/symbol check PASSED
2026-02-22 19:56:24,849 WARNING UnifiedSovereign [FENCE-SELF-TEST] SKIPPED: --allow-protected-root-mutation enabled
2026-02-22 19:56:24,865 INFO agentic_core.L5_safety.reasoning.guardian_decision [L5_GUARDIAN] Decision for CC3AL1-5B4FED78: {'allow': True, 'escalate': False, 'violations': [], 'budget_remaining': 1000000, 'policy_version': '1.0'}
2026-02-22 19:56:24,865 WARNING agentic_core.L0_routing.enforcement.execution_gateway [V15-GW] Successful commit with no mutations detected
2026-02-22 19:56:24,893 WARNING root AGENTIC_BYPASS_LONGPATHS_CHECK=1: skipping LongPathsEnabled hard-fail
2026-02-22 19:56:24,893 INFO UnifiedSovereign ?? UNIFIED SOVEREIGN PROTOCOL STARTED
2026-02-22 19:56:24,893 INFO UnifiedSovereign   Mode: AUTONOMOUS
2026-02-22 19:56:24,893 INFO UnifiedSovereign   LLM: ENABLED
2026-02-22 19:56:24,893 INFO UnifiedSovereign   CDA: DISABLED
2026-02-22 19:56:24,893 INFO UnifiedSovereign   HEALING: ACTIVE
2026-02-22 19:56:24,893 INFO UnifiedSovereign   APPROVAL: AUTO
2026-02-22 19:56:25,104 INFO UnifiedSovereign Total Awareness: Mandatory agent roster registered.
2026-02-22 19:56:25,104 INFO UnifiedSovereign   Agents validated: reconciler, location, hierarchy, arch_governor, gravity_repair, system_architect, file_classification, conversational_repair, cognitive_disposition, root_hygiene
2026-02-22 19:56:25,205 ERROR agentic_core.L0_routing.enforcement.mutation_prohibition MUTATION_PROHIBITION DENY: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 19:56:25,205 CRITICAL UnifiedSovereign [RuntimeStateManager] L0 mutation prohibition active ? runtime state persistence DISABLED for this run (fail-closed). Reason: MUTATION_PROHIBITED:layer=L0|op=json.dump
2026-02-22 19:56:25,205 INFO UnifiedSovereign 🔍 [PHASE 8] Running integrity check (Scope: ['prompt_governance', 'L5_safety', 'L3_orchestration', 'L2_execution', 'L0_routing'])...
2026-02-22 19:56:27,044 WARNING UnifiedSovereign ⚠?  207 total violations identified.
2026-02-22 19:56:27,044 INFO UnifiedSovereign 🧠 L3 ORCHESTRATOR SUMMONED (via subprocess): Delegating command.
2026-02-22 19:56:27,075 WARNING UnifiedSovereign L3 Orchestrator not found. Falling back to L5 iteration.
2026-02-22 19:56:27,075 INFO UnifiedSovereign
============================================================
2026-02-22 19:56:27,075 INFO UnifiedSovereign 🚀 PROCESSING TERRITORY: prompt_governance
2026-02-22 19:56:27,075 INFO UnifiedSovereign ============================================================
2026-02-22 19:56:27,075 INFO UnifiedSovereign === PHASE 1: DISCOVERY - prompt_governance ===
2026-02-22 19:56:27,075 INFO UnifiedSovereign → Executing FilesystemSSOTReconcilerAgent (L0 - Maintenance)
2026-02-22 19:56:27,078 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Initialized with project_root: C:\Git\Agentic-Workflow
2026-02-22 19:56:27,078 INFO agentic_core.L5_safety.enforcement.archival_gatekeeper [ArchivalGatekeeper] Archive root: C:\Git\Agentic-Workflow\archives\gatekeeper
2026-02-22 19:56:27,078 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent initialized for C:\Git\Agentic-Workflow
2026-02-22 19:56:27,078 INFO agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent FilesystemSSOTReconcilerAgent: Detecting root-level drift...
2026-02-22 19:56:27,079 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: logs/
2026-02-22 19:56:27,079 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Forbidden root folder: scripts/
2026-02-22 19:56:27,082 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Duplicate folder: scripts/ at root AND SSOT location
2026-02-22 19:56:27,082 WARNING agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent    [DRIFT] Duplicate folder: logs/ at root AND SSOT location
2026-02-22
... [truncated 526576 chars]
```


## Post-Run git status

```
?? archives/
?? docs/evidence/phase_execute_ssot_integration_phase3.md
```

## INSPECTED_FILES

- agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py
- agentic_core/L0_routing/scripts/execute_ssot.py
- agentic_core/L0_routing/scripts/execute_ssot_entrypoint.py
- tests/agentic_core/L5_safety/gravity/test_gravity_leak_repair_agent.py
