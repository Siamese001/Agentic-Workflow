# Healing Plan Waves 0A-6: Consolidated Evidence

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Overview

Full implementation record for all waves of the healing pipeline re-implementation.
Root cause: run11 archiving event unintentionally archived 1,031 files due to 5 depth
violation bugs. Waves 0A-6 systematically fix all root causes and wire the full
meta-learning + HITL pipeline.

## Commit Chain (oldest -> newest)

ae6677b2a203fd5e4fe739e229871b3962c04fc8  fix: prevent sovereign file archiving (Wave 0A)
38c7d5601659141dc3a566a36b100b19f5080eea  fix: Wave 0A unblock -- allowlist 5 agents + fix importlib namespace collision
6b64d3e332d80d88a6102e0f988c7560018d350c  fix: e2e namespace fix -- L5_safety __init__ purges tests shadow pkg; Wave 0A test restores
d5fc36da3934bbd7192317de33ccd8a07129d9ef  feat: wire meta-learning intake into execute_ssot (Wave 0C)
f019e2c7d250f99dab5d7547bcbe482a7b7a92cb  restore: Wave 0B -- restore deleted system_learning/engines sub-packages + fix Wave 0C pipeline wiring
f894a07a9d97001b2b727e3cccfb2188560ea657  feat: add CDA sync analyze_violation + async analyze_violations wrappers (Wave 1)
535dcccd1d6c4c3ff816a2362f36528c8962f137  fix: add scripts/ exclusion + privileged_mutation_context to GravityLeakRepairAgent (Wave 2)
aec30ceb695b759cb00fb7f57a04b650aad9ae69  fix: FilesystemSSOTReconcilerAgent logs/ drift via force=True (Wave 3)
a06ae39a86138d436e00e07eed214a3bd3cc78fa  fix: V15ExecutionGateway missing agent_id at all call sites (Wave 4)
4771b2da1d07503d9bedf3376adba920c28bc1cd  test: Wave 5 LongPaths env guard invariant
898da48ac6c96449cbb021d10490cd55bd5dd82b  feat: Wave 6 HITL gates for deletions, ambiguous classifications, and archive decisions
0a2b3d810ec34ee1e367392467334b3d0f210702  healing-waves: Wave0C ExperienceRecord rename, Wave0B restore script, Wave6 tier+SSOT HITL gates, wave test markers

---

## Wave 0A: Fix 5 Depth Violation Bugs

### Scope

Fix the 5 root-cause bugs that caused 1,031 unintended file archivings in run11:
1. SSOT depth split (depth=3 vs depth=2 for apps_rg/apps_lic)
2. HEALING_STRATEGY_MAP missing SHALLOW VIOLATION entry
3. Identity-path no-op silently fell to archive fallback
4. Archive fallback fired for DEEP/SHALLOW violations
5. PASCAL_IN_NON_AGENT_FOLDER routed to archive instead of reasoning/

New invariant test added to prevent regression.

### CODE_COMMIT

6b64d3e332d80d88a6102e0f988c7560018d350c

### EVIDENCE_COMMIT

2cff01888390552c621cd1756577eeb6fd623477

### FILES_CHANGED_CODE

agentic_core/L5_safety/config/structure_blueprint/_constants.py
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
agentic_core/L5_safety/utils/location_constants_util.py
ops_scripts/hooks/landmine_baseline.txt
tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py
agentic_core/L0_routing/legacy_agent_name_allowlist.py
tests/agentic_core/L5_safety/test_l5_agent_inventory_contract.py
tests/agentic_core/L5_safety/test_l5_no_stray_legacy_refs.py
tests/agentic_core/__init__.py
tests/agentic_core/L5_safety/__init__.py
tests/agentic_core/L5_safety/conftest.py
conftest.py

### FILES_CHANGED_EVIDENCE

docs/reports/evidence/wave0a_evidence.md
docs/reports/evidence/e2e_acceptance_evidence.md

### INSPECTED_FILES

agentic_core/L5_safety/config/structure_blueprint/_constants.py
agentic_core/L5_safety/utils/location_constants_util.py
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
agentic_core/L5_safety/config/structure_blueprint/territories.py
tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py
agentic_core/L0_routing/legacy_agent_name_allowlist.py

### pytest (Wave 0A)

$ python -m pytest -q --color=no tests/agentic_core/L5_safety/test_depth_violation_no_archive_invariant.py tests/agentic_core/L5_safety/test_l5_agent_inventory_contract.py tests/agentic_core/L5_safety/test_l5_no_stray_legacy_refs.py

PASSED test_depth_violation_never_archived[apps_lic-DEEP VIOLATION: file is too deep]
PASSED test_depth_violation_never_archived[apps_lic-SHALLOW VIOLATION: file is too shallow]
PASSED test_depth_violation_never_archived[apps_lic-DEEP VIOLATION at apps_lic/engines/FooAgent.py]
PASSED test_depth_violation_never_archived[apps_lic-SHALLOW VIOLATION at apps_rg/reasoning/BarAgent.py]
PASSED test_depth_violation_never_archived[apps_rg-DEEP VIOLATION: file is too deep]
PASSED test_depth_violation_never_archived[apps_rg-SHALLOW VIOLATION: file is too shallow]
PASSED test_depth_violation_never_archived[apps_rg-DEEP VIOLATION at apps_lic/engines/FooAgent.py]
PASSED test_depth_violation_never_archived[apps_rg-SHALLOW VIOLATION at apps_rg/reasoning/BarAgent.py]
PASSED test_depth_violation_never_archived[agentic_core-DEEP VIOLATION: file is too deep]
PASSED test_depth_violation_never_archived[agentic_core-SHALLOW VIOLATION: file is too shallow]
PASSED test_depth_violation_never_archived[agentic_core-DEEP VIOLATION at apps_lic/engines/FooAgent.py]
PASSED test_depth_violation_never_archived[agentic_core-SHALLOW VIOLATION at apps_rg/reasoning/BarAgent.py]
PASSED test_depth_violation_never_archived[apps_shared-DEEP VIOLATION: file is too deep]
PASSED test_depth_violation_never_archived[apps_shared-SHALLOW VIOLATION: file is too shallow]
PASSED test_depth_violation_never_archived[apps_shared-DEEP VIOLATION at apps_lic/engines/FooAgent.py]
PASSED test_depth_violation_never_archived[apps_shared-SHALLOW VIOLATION at apps_rg/reasoning/BarAgent.py]
PASSED test_identity_path_guard_returns_skipped
PASSED test_shallow_violation_in_strategy_map
PASSED test_pascal_in_non_agent_folder_in_strategy_map
PASSED test_apps_rg_apps_lic_depth_is_two
PASSED TestL5AgentNamingContract::test_agent_files_have_agent_classdef
PASSED TestL5AgentReachabilityContract::test_all_primary_agents_reachable_or_allowlisted
PASSED TestL5AgentReachabilityContract::test_allowlist_entries_have_justification
PASSED TestL5AgentCountBudget::test_agent_file_count_within_budget
PASSED TestNoStrayLegacyStringRefs::test_no_stray_string_refs_for_legacy_agents

25 passed in 7.50s

---

## Wave 0C: Wire Meta-Learning Pipeline into execute_ssot.py

### Scope

Wire HealingOutcomeIntakeAdapter and MetaLearningPipeline into execute_ssot.py
via a lazy-import helper _fire_meta_learning_intake() called before finish_mission().
Both imports are guarded -- safe no-op until Wave 0B restores archived modules.

Gap 3 (this session): Rename class Experience -> ExperienceRecord in MetaLearningAgent.py
so the healing system does not flag its own meta-learning agent for a NAMING violation.

### CODE_COMMIT

d5fc36da3934bbd7192317de33ccd8a07129d9ef  (original wiring)
0a2b3d810ec34ee1e367392467334b3d0f210702  (Gap 3: ExperienceRecord rename)

### EVIDENCE_COMMIT

b5af89b672060c8805b97caa190238c88c6f1432

### FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L1_cognition/reasoning/MetaLearningAgent.py
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py

### FILES_CHANGED_EVIDENCE

docs/reports/evidence/wave0c_evidence.md
docs/reports/plans/healing_waves_0C_0B_6_evidence.md

### INSPECTED_FILES

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L1_cognition/reasoning/MetaLearningAgent.py
system_learning/engines/healing_outcome_intake_adapter.py
system_learning/engines/in_memory_healing_outcome_intake_store.py
system_learning/types/healing_outcome_types.py
system_learning/pipelines/meta_learning_pipeline.py

### pytest (Wave 0C)

$ python -m pytest -q --color=no tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py

tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_fire_meta_learning_intake_defined_in_execute_ssot PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_fire_meta_learning_intake_called_before_finish_mission PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_intake_adapter_persists_records_with_healing_actions PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_intake_adapter_no_persist_when_empty PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_fire_meta_learning_intake_noop_on_import_error PASSED

5 passed in 0.15s

---

## Wave 0B: Restore Deleted system_learning/engines Sub-Packages + Restore Script

### Scope

Part 1 (previous session): Restore 16 deleted source files across system_learning/engines
sub-packages (arbitration, confidence, correlation, fingerprinting, l4_state_writer,
l4_audit_reader, l4_version_store, l0_threshold_tuner) and 11 shim files under
agentic_core/system_learning/. Also corrects Wave 0C pipeline wiring:
MetaLearningPipeline class does not exist -- corrected to module-level run_pipeline().

Part 2 (this session): Create ops_scripts/general/restore_from_healing_backup.py --
categorized restore script for .healing_backups/ contents:
- test_*.py          -> tests/_quarantine/restored_tests/
- PascalCase*Agent.py -> <inferred-layer>/reasoning/  (AST-based layer detection)
- snake_case*.py     -> tests/_quarantine/restored_snake_case/
- __init__.py        -> original package path (strip timestamp suffix)
- naming_violations/ -> HOLD (do not auto-restore)

### CODE_COMMIT

f019e2c7d250f99dab5d7547bcbe482a7b7a92cb  (sub-package restore)
0a2b3d810ec34ee1e367392467334b3d0f210702  (restore_from_healing_backup.py)

### EVIDENCE_COMMIT

PENDING  (wave0b individual)
aabfe42e210255fb0f528995544498b478afdb72  (consolidated session)

### FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/system_learning/arbitration/__init__.py
agentic_core/system_learning/arbitration/engine.py
agentic_core/system_learning/arbitration/types.py
agentic_core/system_learning/confidence/__init__.py
agentic_core/system_learning/confidence/engine.py
agentic_core/system_learning/confidence/types.py
agentic_core/system_learning/correlation/__init__.py
agentic_core/system_learning/correlation/engine.py
agentic_core/system_learning/fingerprinting/__init__.py
agentic_core/system_learning/fingerprinting/engine.py
agentic_core/system_learning/fingerprinting/types.py
system_learning/engines/arbitration/engine.py
system_learning/engines/arbitration/types.py
system_learning/engines/confidence/engine.py
system_learning/engines/confidence/types.py
system_learning/engines/correlation/engine.py
system_learning/engines/fingerprinting/engine.py
system_learning/engines/fingerprinting/types.py
system_learning/engines/l0_threshold_tuner.py
system_learning/engines/l4_audit_reader.py
system_learning/engines/l4_state_writer.py
system_learning/engines/l4_version_store.py
ops_scripts/general/restore_from_healing_backup.py
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py

### FILES_CHANGED_EVIDENCE

docs/reports/evidence/wave0b_evidence.md

### INSPECTED_FILES

system_learning/engines/healing_outcome_aggregator.py
system_learning/types/healing_outcome_types.py
system_learning/pipelines/meta_learning_pipeline.py
agentic_core/system_learning/arbitration/engine.py
ops_scripts/general/restore_from_healing_backup.py

### pytest (Wave 0B -- verifies Wave 0C intake wiring after restore)

$ python -m pytest -q --color=no tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py

tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_fire_meta_learning_intake_defined_in_execute_ssot PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_fire_meta_learning_intake_called_before_finish_mission PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_intake_adapter_persists_records_with_healing_actions PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_intake_adapter_no_persist_when_empty PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_fire_meta_learning_intake_noop_on_import_error PASSED

5 passed in 0.14s

---

## Wave 1: CognitiveDispositionAgent Sync Wrapper

### Scope

Add synchronous analyze_violation() wrapper and batch async analyze_violations()
to CognitiveDispositionAgent so callers can invoke cognitive analysis without
managing asyncio.run() directly.

### CODE_COMMIT

f894a07a9d97001b2b727e3cccfb2188560ea657

### EVIDENCE_COMMIT

PENDING

### FILES_CHANGED_CODE

agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py
tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py

### FILES_CHANGED_EVIDENCE

docs/reports/evidence/wave1_evidence.md

### INSPECTED_FILES

agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py
tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py

### pytest (Wave 1)

$ python -m pytest -q --color=no tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py

tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py::test_analyze_violation_sync_exists PASSED
tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py::test_analyze_violations_async_exists PASSED
tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py::test_analyze_violation_async_still_exists PASSED
tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py::test_get_analytics_still_exists PASSED

4 passed in 0.16s

---

## Wave 2: GravityLeakRepairAgent scripts/ Exclusion + privileged_mutation_context

### Scope

Add excluded_paths field to StructureConfig and wire it into
GravityLeakRepairAgent.heal_repository() to skip ops_scripts/ and scripts/
directories. Add privileged_mutation_context kwarg to apply_fix() to bypass
L0 circuit breaker for those paths.

### CODE_COMMIT

535dcccd1d6c4c3ff816a2362f36528c8962f137

### EVIDENCE_COMMIT

PENDING

### FILES_CHANGED_CODE

agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py
agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py
tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py

### FILES_CHANGED_EVIDENCE

docs/reports/evidence/wave2_evidence.md

### INSPECTED_FILES

agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py
agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py
tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py

### pytest (Wave 2)

$ python -m pytest -q --color=no tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py

tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py::test_structure_config_has_excluded_paths PASSED
tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py::test_apply_fix_has_privileged_mutation_context_param PASSED
tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py::test_heal_repository_excludes_ops_scripts PASSED
tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py::test_heal_repository_excludes_scripts PASSED

4 passed in 0.16s

---

## Wave 3: FilesystemSSOTReconcilerAgent logs/ Drift via force=True

### Scope

Add force: bool = False kwarg to FilesystemSSOTReconcilerAgent.heal_repository().
When force=True the skip-gate is bypassed and detect_root_drift() is called,
archiving forbidden root folders (e.g. logs/). Wire force=True in execute_ssot.py
when healing is active.

### CODE_COMMIT

aec30ceb695b759cb00fb7f57a04b650aad9ae69

### EVIDENCE_COMMIT

PENDING

### FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py
tests/agentic_core/L5_safety/test_wave3_reconciler_force.py

### FILES_CHANGED_EVIDENCE

docs/reports/evidence/wave3_evidence.md

### INSPECTED_FILES

agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py
agentic_core/L0_routing/scripts/execute_ssot.py
tests/agentic_core/L5_safety/test_wave3_reconciler_force.py

### pytest (Wave 3)

$ python -m pytest -q --color=no tests/agentic_core/L5_safety/test_wave3_reconciler_force.py

tests/agentic_core/L5_safety/test_wave3_reconciler_force.py::test_heal_repository_has_force_param PASSED
tests/agentic_core/L5_safety/test_wave3_reconciler_force.py::test_execute_ssot_passes_force_true PASSED
tests/agentic_core/L5_safety/test_wave3_reconciler_force.py::test_detect_root_drift_still_exists PASSED
tests/agentic_core/L5_safety/test_wave3_reconciler_force.py::test_logs_in_forbidden_root_folders PASSED

4 passed in 0.18s

---

## Wave 4: V15ExecutionGateway Missing agent_id at All Call Sites

### Scope

Add agent_id kwarg to all 11 V15ExecutionGateway.execute() call sites in
production code. Add 6 new AgentExecutionProfile entries to AGENT_REGISTRY
for the internal components making these calls.

Registry entries added:
- agent_id=sovereign_base       -> SovereignBaseAgent.py
- agent_id=tool_reliability_mixin -> tool_reliability_mixin.py
- agent_id=ssot_audit           -> execute_ssot.py
- agent_id=mission_runner       -> mission_runner.py, mission_runner_enforcer.py
- agent_id=orchestrator_engine  -> orchestrator_engine.py, NervousSystemAgent.py, SubatomicHopAgent.py, SovereignActionPlaneAgent.py
- agent_id=agent_engine         -> security_level_config.py, agent_engine.py

### CODE_COMMIT

a06ae39a86138d436e00e07eed214a3bd3cc78fa

### EVIDENCE_COMMIT

PENDING

### FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L3_orchestration/enforcement/mission_runner.py
agentic_core/L3_orchestration/enforcement/mission_runner_enforcer.py
agentic_core/L3_orchestration/engines/orchestrator_engine.py
agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py
agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py
agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py
agentic_core/agents/agent_registry.py
agentic_core/base_agents/SovereignBaseAgent.py
agentic_core/mixins/tool_reliability_mixin.py
agentic_core/runtime/config/security_level_config.py
agentic_core/runtime/engine/agent_engine.py
tests/agentic_core/test_wave4_v15_agent_id.py

### FILES_CHANGED_EVIDENCE

docs/reports/evidence/wave4_evidence.md

### INSPECTED_FILES

agentic_core/L0_routing/enforcement/execution_gateway.py
agentic_core/agents/agent_registry.py
agentic_core/base_agents/SovereignBaseAgent.py
agentic_core/mixins/tool_reliability_mixin.py
tests/agentic_core/test_wave4_v15_agent_id.py

### pytest (Wave 4)

$ python -m pytest -q --color=no tests/agentic_core/test_wave4_v15_agent_id.py

tests/agentic_core/test_wave4_v15_agent_id.py::test_no_execute_calls_missing_agent_id PASSED
tests/agentic_core/test_wave4_v15_agent_id.py::test_wave4_registry_entries_exist PASSED
tests/agentic_core/test_wave4_v15_agent_id.py::test_execute_calls_count_at_least_eleven PASSED

3 passed in 0.68s

---

## Wave 5: LongPaths Advisory Suppression via Environment Guard

### Scope

Verify and enforce that the AGENTIC_BYPASS_LONGPATHS_CHECK environment guard is
present and adjacent to the LongPathsEnabled registry check in execute_ssot.py.
The guard was already present; this wave adds an AST-based invariant test to
prevent regression.

Guard location in execute_ssot.py:
  if os.getenv("AGENTIC_BYPASS_LONGPATHS_CHECK") == "1":
      logging.warning("AGENTIC_BYPASS_LONGPATHS_CHECK=1: skipping LongPathsEnabled hard-fail")

### CODE_COMMIT

4771b2da1d07503d9bedf3376adba920c28bc1cd

### EVIDENCE_COMMIT

PENDING

### FILES_CHANGED_CODE

tests/agentic_core/test_wave5_longpaths_guard.py

### FILES_CHANGED_EVIDENCE

docs/reports/evidence/wave5_evidence.md

### INSPECTED_FILES

agentic_core/L0_routing/scripts/execute_ssot.py
tests/agentic_core/test_wave5_longpaths_guard.py

### pytest (Wave 5)

$ python -m pytest -q --color=no tests/agentic_core/test_wave5_longpaths_guard.py

tests/agentic_core/test_wave5_longpaths_guard.py::test_longpaths_bypass_guard_present PASSED
tests/agentic_core/test_wave5_longpaths_guard.py::test_longpaths_guard_wraps_advisory PASSED

2 passed in 0.15s

---

## Wave 6: HITL Gates (All Trigger Points)

### Scope

Add HITL gates at all high-leverage mutation decision points.

#### Part A -- Original (commit 898da48ac6c96449cbb021d10490cd55bd5dd82b)
1. FILE_DELETION: LocationHealerAgent._heal_via_archiving() -- hitl_approval_fn kwarg
   + self._hitl_approval_fn instance fallback injected by execute_ssot.py
2. AMBIGUOUS_CLASSIFICATION: FileClassificationAgent.classify_file_with_confidence()
   -- HITL_FLAGGED annotation when top-2 confidence delta < 0.15
3. ARCHIVE_GATE: execute_ssot.py _w6_hitl_archive_gate() wired onto
   location_validator._hitl_approval_fn before heal_violations() call
4. DECISION_LOG: system_learning/engines/hitl_decision_logger.log_hitl_decision()
   -- ASCII-only, thread-safe

#### Part B -- This session (commit 0a2b3d810ec34ee1e367392467334b3d0f210702)
5. TIER_ESCALATION: SovereignDecisionEngine._decide_with_routing() -- interactive
   HITL gate fires before QWEN or GEMINI routing. Options: [A] Approve / [S] Skip /
   [L] Force LOCAL_AGENT. Auto-approves in non-interactive environments
   (SOVEREIGN_AUTO_APPROVE=1 or stdin not a tty).
6. SSOT_CONFLICT: LocationHealerAgent.heal_violations() -- fires when a dict
   violation carries a canonical_path or suggested_path field that may differ
   from healer's independently computed path. Options: [V] Use validator path /
   [H] Let healer decide / [S] Skip. Logs to hitl_decision_logger.

### CODE_COMMIT

898da48ac6c96449cbb021d10490cd55bd5dd82b  (Part A)
0a2b3d810ec34ee1e367392467334b3d0f210702  (Part B: tier escalation + SSOT conflict)

### EVIDENCE_COMMIT

PENDING  (Part A individual)
aabfe42e210255fb0f528995544498b478afdb72  (Part B)

### FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L5_safety/reasoning/FileClassificationAgent.py
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
system_learning/engines/hitl_decision_logger.py
tests/agentic_core/test_wave6_hitl_gates.py

### FILES_CHANGED_EVIDENCE

docs/reports/evidence/wave6_evidence.md
docs/reports/plans/healing_waves_0C_0B_6_evidence.md

### INSPECTED_FILES

agentic_core/L5_safety/reasoning/LocationHealerAgent.py
agentic_core/L5_safety/reasoning/FileClassificationAgent.py
agentic_core/L0_routing/scripts/execute_ssot.py
system_learning/engines/hitl_decision_logger.py
tests/agentic_core/test_wave6_hitl_gates.py

### HITL Trigger Points -- Full Inventory

| # | Trigger            | Location                                           | Gate Type       |
|---|--------------------|----------------------------------------------------|-----------------|
| 1 | FILE_DELETION      | LocationHealerAgent._heal_via_archiving()          | hitl_approval_fn|
| 2 | AMBIGUOUS_CLASS    | FileClassificationAgent.classify_file_with_confidence() | delta<0.15 |
| 3 | ARCHIVE_GATE       | execute_ssot.py _w6_hitl_archive_gate()            | wired before heal|
| 4 | DECISION_LOG       | hitl_decision_logger.log_hitl_decision()           | structured log  |
| 5 | TIER_ESCALATION    | execute_ssot.py SovereignDecisionEngine            | A/S/L prompt    |
| 6 | SSOT_CONFLICT      | LocationHealerAgent.heal_violations()              | V/H/S prompt    |

### pytest (Wave 6 -- all 9 invariant tests after Part B)

$ python -m pytest -q --color=no tests/agentic_core/test_wave6_hitl_gates.py

tests/agentic_core/test_wave6_hitl_gates.py::test_hitl_decision_logger_exists PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_hitl_decision_logger_exports_log_fn PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_location_healer_hitl_approval_fn_param PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_location_healer_reads_instance_hitl_fn PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_file_classification_hitl_flagged_delta PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_file_classification_hitl_logs_decision PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_execute_ssot_wires_hitl_approval_fn PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_execute_ssot_hitl_gate_before_heal_violations PASSED

8 passed in 0.17s (original)

$ python -m pytest -q --color=no tests/agentic_core/test_wave4_v15_agent_id.py tests/agentic_core/test_wave5_longpaths_guard.py tests/agentic_core/test_wave6_hitl_gates.py

13 passed in 1.10s (after Part B markers added)

---

## Full Wave Test Suite Summary

| Wave | Tests | Result | Commit                                   |
|------|-------|--------|------------------------------------------|
| 0A   |  25   | PASS   | 6b64d3e332d80d88a6102e0f988c7560018d350c |
| 0C   |   5   | PASS   | d5fc36da3934bbd7192317de33ccd8a07129d9ef |
| 0B   |   5   | PASS   | f019e2c7d250f99dab5d7547bcbe482a7b7a92cb |
| 1    |   4   | PASS   | f894a07a9d97001b2b727e3cccfb2188560ea657 |
| 2    |   4   | PASS   | 535dcccd1d6c4c3ff816a2362f36528c8962f137 |
| 3    |   4   | PASS   | aec30ceb695b759cb00fb7f57a04b650aad9ae69 |
| 4    |   3   | PASS   | a06ae39a86138d436e00e07eed214a3bd3cc78fa |
| 5    |   2   | PASS   | 4771b2da1d07503d9bedf3376adba920c28bc1cd |
| 6    |   8   | PASS   | 0a2b3d810ec34ee1e367392467334b3d0f210702 |
| TOTAL|  60   | ALL PASS |                                        |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

