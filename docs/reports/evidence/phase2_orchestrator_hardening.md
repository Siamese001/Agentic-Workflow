# Phase 2: Orchestrator Hardening — Evidence

## BRANCH_BASELINE

```text
Branch: file_classification_enhancements
Commit: f5e533eaa5adcf0a04d4d533434538fdaec53b0e
Status: clean (tracked files)
Last commit: f5e533eaa Phase 1: ENFORCER/SEAM FCA classification + tests
```

## FCA_ORCHESTRATOR_AUDIT

### rg -n "_detect_orchestrator_patterns|ORCHESTRATOR" FileClassificationAgent.py

```text
186:  "ORCHESTRATOR": 0,              — stats violations
225:  "ORCHESTRATOR": ["engines", "reasoning"],  — app_territory_map
742:  Orchestrators: ...               — summary logging
776:  6. ORCHESTRATOR                  — docstring priority
978:  is_orchestrator = self._detect_orchestrator_patterns(...)
1019: # 6. ORCHESTRATOR: Specialized agent type
1020: if is_orchestrator: return "ORCHESTRATOR"
1186: def _detect_orchestrator_patterns(self, tree, path, content, primary_name)
1212-1218: orchestrator_name_patterns list
1222-1246: orchestrator_behavior_signals list
1249: behavior_signal_count
1260-1265: stage_functions detection
1268-1273: pipeline_methods detection
1281-1304: decision logic (L3 check, multi-stage, pipeline, router override)
```

### rg -n "L3_orchestration|orchestration" FileClassificationAgent.py

```text
1277: # 2. If in L3_orchestration/ with orchestrator patterns
1282: is_in_l3 = "L3_orchestration" in path.parts
2043: *Manager with workflow/dag/pipeline/orchestrat signals -> L3_orchestration
2071: return "L3_orchestration"
2192: "L3_orchestration": ("workflow", "dag", "pipeline", ...)
```

**Finding:** FCA has _detect_orchestrator_patterns() at line 1186 with name+behavior detection.
Missing: inheritance signal, broader tokens, multi-class coordinator, relaxed threshold,
invariant validation, layer alignment reporting.

## KERNEL_ORCHESTRATOR_AUDIT

### rg -n "Coordinator|Orchestrator|is_orchestrator" classification_kernel.py

```text
264: is_orchestrator = any(p in primary_name for p in ("Orchestrator", "Coordinator", "Pipeline"))
287-288: top_tier_signals ORCHESTRATOR
320-322: PRIORITY 9: ORCHESTRATOR return
434: is_agent_or_orchestrator()
448: classify_file_standalone(path) in ("AGENT", "ORCHESTRATOR")
```

**Finding:** Kernel detects orchestrator by name only (Orchestrator/Coordinator/Pipeline in primary_name).
Missing: base-class inheritance signal.

## IMPLEMENTATION_DELTA

### Changed files

```text
 classification_kernel.py              |   10 +
 FileClassificationAgent.py            |  210 +++++++++++++++---
 classification.py (blueprint)         |    4 +
 test_phase2_orchestrator_hardening.py |  320 +++++++++++++++++++++++++
 phase2_orchestrator_hardening.md      |  new
```

### classification_kernel.py

- Added base-class detection assist: if any base in {Coordinator, Orchestrator, WorkflowCoordinator, L3OrchestrationBase} then is_orchestrator = True

### FileClassificationAgent.py

- **Wave 2A** — Hardened _detect_orchestrator_patterns():
  - Strong inheritance signal (WorkflowCoordinator, Coordinator, L3OrchestrationBase, IOrchestratorProtocol)
  - Multi-class coordinator detection (>=3 ClassDef ending with Coordinator)
  - Broadened behavior tokens (+8: run_stages, execute_workflow, run_phases, dispatch_to_agents, agent_roster, mission_context, run_all_guardians, run_healers)
  - Relaxed threshold for exact suffix match (Orchestrator/Coordinator + >=1 behavior token)
- **Wave 2B** — _validate_orchestrator_invariants():
  - Role coordination: >=2 distinct role buckets from imports/string refs
  - Mutation hard fail: open("w"), write_text, shutil.move, os.remove, etc. => ENGINE
  - Mutation soft warn: subprocess.run, apply_*, commit_* => remain ORCHESTRATOR
  - Thin wrapper: <=3 funcs AND <=50 LOC AND <=5 calls => ENGINE
  - Insufficient roles: <2 role buckets => ENGINE
- **Wave 2C** — _validate_orchestrator_layer_alignment():
  - Flags ORCHESTRATOR outside L3_orchestration/
  - Exceptions: apps_*, L5_safety/runners, knowledge/, *_enforcer.py
- **Wave 2F** — Stats bookkeeping:
  - ORCHESTRATOR_INVARIANT_FAIL: {mutation_hard, mutation_soft, thin_wrapper, insufficient_roles}
  - ORCHESTRATOR_LAYER_MISALIGNMENT: int
- classify_file() hook: ORCHESTRATOR return now runs invariant validation + layer alignment

### classification.py (blueprint)

- CLASSIFICATION_SUFFIX_PATTERNS: _orchestrator.py, _coordinator.py => ORCHESTRATOR
- SUFFIX_TO_FOLDER: Coordinator.py => engines
- KNOWN_ARCHITECTURAL_SUFFIXES: _coordinator

## TEST_OUTPUT

### pytest -q (Phase 2 + Phase 1 regression)

```text
19 passed in 0.36s
```

Test breakdown (6 Phase 2 tests):
- test_inherits_workflow_coordinator — WorkflowCoordinator => ORCHESTRATOR
- test_thin_wrapper_downgraded_to_engine — <=3 funcs, <=50 LOC => ENGINE + thin_wrapper stat
- test_hard_mutation_downgraded_to_engine — open("w") => ENGINE + mutation_hard stat
- test_soft_mutation_remains_orchestrator — subprocess.run => ORCHESTRATOR + mutation_soft stat
- test_orchestrator_under_l2_flags_misalignment — ORCHESTRATOR under L2 => misalignment stat
- test_mini_slice — 3 files: valid orchestrator, thin wrapper, hard mutation

Phase 1 regression: 13/13 passed (0 regressions)

## COMMIT

```text
Commit: ae4a586b6
Branch: file_classification_enhancements
Parent: 00af00b00 (Phase 1)
Files:
  agentic_core/L5_safety/config/structure_blueprint/classification.py
  agentic_core/L5_safety/core_kernel/classification_kernel.py
  agentic_core/L5_safety/reasoning/FileClassificationAgent.py
  artifacts/evidence/phase2_orchestrator_hardening.md
  ops_scripts/hooks/import_dep_baseline.txt
  ops_scripts/hooks/landmine_baseline.txt
  tests/unit/file_classification_agent/test_phase2_orchestrator_hardening.py
```

## CONVERGE_CONFIDENCE

**converge_confidence: 90%**

Rationale:
- Orchestrator detection hardened with inheritance, broader tokens, multi-class, relaxed threshold
- Invariant validation implemented with tiered mutation checks
- Layer alignment reporting implemented (report-only)
- 6/6 Phase 2 tests pass, 13/13 Phase 1 tests pass (0 regressions)
- Blueprint wiring complete
- No Phase 3 router work performed
- Deductions: -5% invariant validation not yet exercised in real repo scan, -5% no end-to-end layer alignment test with apps_* exception
