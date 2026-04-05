# Phase 10 Raw Outputs Evidence

## WAVE 10.1 — Mainline (3cd6edf47)

### git --no-pager rev-parse HEAD
```
3cd6edf47b1795ddcd932048953688dd23dd2efe
```

### git --no-pager status --porcelain=v1
```
```

### git --no-pager log --oneline --decorate -n 5
```
3cd6edf47 (HEAD, agentic-v5.4) fix(architecture): scan_directory optional repo_root for test compatibility
32e879a8c guard(architecture): invariant test + ascii-safe guard output
106946dba guard(architecture): baseline-locked module collision no-growth gate
3d9904e9c fix: resolve pre-existing test failures blocking Wave 5
81d9e83eb Revert "wave5: remove deprecated prompt directories after Phase 5 validation"
```

### pytest -q tests/guardian
```
========================================================== test session starts ==========================================================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_test_loop_scope=None, asyncio_default_test_loop_scope=function
collected 1779 items / 1 error

================================================================ ERRORS =================================================================
_________________________________ ERROR collecting tests/guardian/test_v15_artifact_typing_migration.py _________________________________
ImportError while importing test module 'C:\Git\Agentic-Workflow\tests\guardian\test_v15_artifact_typing_migration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\guardian\test_v15_artifact_typing_migration.py:18: in <module>
    from agentic_core.L0_routing.types.v15_artifact_validate import (
E   ModuleNotFoundError: No module named 'agentic_core.L0_routing.types.v15_artifact_validate'

============================================================
GUARDIAN SHIELD: BLOCKING
============================================================
JSON Report: C:\Git\Agentic-Workflow\agentic_core\L0_routing\logs\guardian_report.json
Violations: 0
============================================================
======================================================== GUARDIAN LAYER SUMMARY =========================================================
Guardian tests run: 1779
Passed: 0
Failed: 0
Errors: 1

❌ GUARDIAN STATUS: FAIL
Architectural violations detected. Review failed tests.
===================================================================  ====================================================================
======================================================== short test summary info ========================================================
ERROR tests/guardian/test_v15_artifact_typing_migration.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
=========================================================== 1 error in 0.61s ============================================================
```

### pre-commit run --all-files
```
PS C:\Git\Agentic-Workflow> pre-commit run --all-files
T0: Trailing Whitespace..................................................Passed
T0: End-of-File Fixer....................................................Failed
- hook id: end-of-file-fixer
- exit code: 1
- files were modified by this hook

Fixing artifacts/architecture/module_collision_baseline.json
```

## WAVE 10.2 — Feature Branch (feature/structure-drift-detection-clean)

### git --no-pager rev-parse HEAD
```
d26abe732e26e5bbd4a68b7aadca8429139641b9
```

### git --no-pager status --porcelain=v1
```
```

### git --no-pager log --oneline --decorate -n 10
```
d26abe732 (HEAD -> feature/structure-drift-detection-clean, origin/feature/structure-drift-detection-clean) fix: update golden manifest and test
3c8b4f8e1 feat: structure drift detection system
3cd6edf47 (agentic-v5.4) fix(architecture): scan_directory optional repo_root for test compatibility
32e879a8c guard(architecture): invariant test + ascii-safe guard output
106946dba guard(architecture): baseline-locked module collision no-growth gate
3d9904e9c fix: resolve pre-existing test failures blocking Wave 5
81d9e83eb Revert "wave5: remove deprecated prompt directories after Phase 5 validation"
481469d91 wave5: remove deprecated prompt directories after Phase 5 validation
3a5a8e7c3 (feature/Prompt-SSOT) phase4: finalize SSOT recommendations with deterministic deletion gates
ac031f758 (origin/feature/prompt-modularization, origin/feature/chat-session-20250214, origin/feature/agentic-v5.5-remediation, origin/age
ntic-v5.4, feature/prompt-modularization) Merge branch 'wip/mirror-contract' into agentic-v5.4
```

### git --no-pager diff --name-status 3cd6edf47..HEAD
```
M       agentic_core/L2_execution/enforcement/capability_chokepoint.py
M       agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py
M       agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py
M       agentic_core/L2_execution/reasoning/ToolsmithAgent.py
M       agentic_core/L3_orchestration/engines/orchestrator_engine.py
M       agentic_core/L3_orchestration/engines/recursive_orchestrator.py
M       agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py
M       agentic_core/L3_orchestration/reasoning/CoverageAgent.py
M       agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py
M       agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py
M       agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py
M       agentic_core/L3_orchestration/reasoning/StateManagementAgent.py
M       agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py
M       agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py
M       agentic_core/L3_orchestration/types/recursive_orchestration_types.py
M       agentic_core/L4_state/memory/sovereign_semantic_cache.py
M       agentic_core/L4_state/reasoning/CheckpointManagerAgent.py
M       agentic_core/L4_state/reasoning/GravityStateAgent.py
M       agentic_core/L4_state/reasoning/RedisSovereignAgent.py
M       agentic_core/L5_safety/enforcement/input_validation_guardrail.py
M       agentic_core/L5_safety/enforcement/secure_error_handler_enforcer.py
M       agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py
M       agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py
M       agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py
M       agentic_core/L5_safety/reasoning/BootstrapAgent.py
M       agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py
M       agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py
M       agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py
M       agentic_core/L5_safety/reasoning/CostGovernorAgent.py
M       agentic_core/L5_safety/reasoning/DependencyPruningAgent.py
M       agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py
M       agentic_core/L5_safety/reasoning/FileClassificationAgent.py
M       agentic_core/L5_safety/reasoning/GitHygieneAgent.py
M       agentic_core/L5_safety/reasoning/HierarchyAgent.py
M       agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py
M       agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py
M       agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py
M       agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py
M       agentic_core/L5_safety/reasoning/RedSentinelAgent.py
M       agentic_core/L5_safety/reasoning/RedTeamAgent.py
M       agentic_core/L5_safety/reasoning/RegressionOracleAgent.py
M       agentic_core/L5_safety/reasoning/RootHygieneAgent.py
M       agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py
M       agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py
M       agentic_core/L5_safety/utils/code_tool_runner_core_util.py
A       agentic_core/L5_safety/validators/structure_drift_manifest.py
M       agentic_core/base_agents/L0MaintenanceBase.py
M       agentic_core/base_agents/L3OrchestrationBase.py
M       agentic_core/knowledge/document_loaders/csv_loader.py
M       agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py
M       agentic_core/prompt_governance/core/prompt_assembler.py
M       artifacts/architecture/module_collision_baseline.json
A       artifacts/structure/structure_manifest.json
A       artifacts/structure/structure_manifest.sha256
A       docs/reports/plans/sdk-mcp-gap-analysis-b9e42c.md
A       ops_scripts/ci/structure_drift_validator.py
M       tests/architecture/test_module_collision_guard.py
M       tests/guardian/test_capability_chokepoint.py
M       tests/guardian/test_healer_pipe_order_enforcement.py
A       tests/guardian/test_structure_drift.py
M       tests/guardian/test_v15_artifact_typing_migration.py
M       tests/unit/agentic_core/L2_execution/enforcement/test_gateway_output_injection_scan.py
M       tests/unit_min_deps/test_base_agents_purity_contract.py
M       tests/unit_min_deps/test_import_boundary_contract.py
M       tests/unit_min_deps/test_leaf_domain_contract.py
```

### pre-commit run --all-files
```
PS C:\Git\Agentic-Workflow> pre-commit run --all-files
T0: Trailing Whitespace..................................................Failed
- hook id: trailing-whitespace
- exit code: 1
- files were modified by this hook

Fixing docs/reports/plans/sdk-mcp-gap-analysis-b9e42c.md
Fixing tests/guardian/test_structure_drift.py
```

### python -m ops_scripts.ci.structure_drift_validator
```
PASS: Structure manifest matches golden
  hash=13c21fd32163f345790663eb7e4b299bef0e1dff4b6ede8e47287e111439abeb
```

### pytest -q tests/guardian/test_structure_drift.py
```
========================================================== test session starts ==========================================================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_test_loop_scope=None, asyncio_default_test_loop_scope=function
collected 4 items

tests/guardian/test_structure_drift.py::test_manifest_determinism PASSED                                                           [ 25%]
tests/guardian/test_structure_drift.py::test_drift_detection_in_temp_repo PASSED                                                   [ 50%]
tests/guardian/test_structure_drift.py::test_update_gate_enforcement PASSED                                                        [ 75%]
tests/guardian/test_structure_drift.py::test_structure_drift_validator_integration PASSED                                          [100%]

============================================================
GUARDIAN SHIELD: PASS
============================================================
JSON Report: C:\Git\Agentic-Workflow\agentic_core\L0_routing\logs\guardian_report.json
Violations: 0
============================================================

======================================================== GUARDIAN LAYER SUMMARY =========================================================
Guardian tests run: 4
Passed: 4
Failed: 0
Errors: 0

✅ GUARDIAN STATUS: PASS
All architectural integrity checks passed.
===================================================================  ====================================================================
========================================================= slowest 10 durations ==========================================================
1.56s call     tests/guardian/test_structure_drift.py::test_manifest_determinism
1.55s call     tests/guardian/test_structure_drift.py::test_structure_drift_validator_integration
0.80s call     tests/guardian/test_structure_drift.py::test_update_gate_enforcement

(7 durations < 0.005s hidden.  Use -vv to show these durations.)
=========================================================== 4 passed in 3.96s ============================================================
```
