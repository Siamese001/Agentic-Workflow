# Phase 5: Remaining Violation Elimination (Move-Only; No Rule Changes)

## Wave 5.1: Diagnose Exact Failures (NO COMMIT)

### Baseline on HEAD

```text
git rev-parse HEAD: f6254a0f285664542b4785e072e236425c456c73
git status --porcelain=v1: (clean except this evidence file)
```

### pytest -q tests/enforcement/test_folder_purity_invariants.py -vv

```text
9 failed, 7 passed in 0.14s
```

### Failure Analysis

#### 1. reasoning/ (29 files)
Files in reasoning/ that don't match allowed patterns (Agent/Executor/Orchestrator/Inspector/Healer/Guardian):
- apps_rg/reasoning/HardenedanthropicexecutorStrategy.py (Strategy suffix - should be enforcement/)
- apps_rg/reasoning/resume_orchestrator.py (snake_case - should be ResumeOrchestrator.py)
- apps_shared/reasoning/InfrastructureOrchestrator.py (OK - matches Orchestrator)
- apps_shared/reasoning/InfrastructureUpgradesOrchestrator.py (OK - matches Orchestrator)
- apps_shared/reasoning/PilotOrchestrator.py (OK - matches Orchestrator)
- apps_shared/reasoning/batch_refactor_agents.py (snake_case script - should be scripts/)
- apps_shared/reasoning/compare_agent_lists.py (snake_case script - should be scripts/)
- apps_shared/reasoning/coordinate_observability_operations_orchestrator_type.py (snake_case - should be types/)
- apps_shared/reasoning/fix_all_agentic_imports.py (snake_case script - should be scripts/)
- apps_shared/reasoning/l5_autonomous_orchestrator_wrapper.py (snake_case - should be utils/)
- apps_shared/reasoning/orchestrate_observability_planning_orchestrator_type.py (snake_case - should be types/)
- apps_shared/reasoning/AgentRole.py (not Agent suffix - should be types/)
- Plus agentic_core files...

#### 2. validators/ (2 files)
- agentic_core/L5_safety/validators/heal_manifest.py (no _validator suffix)
- agentic_core/L5_safety/validators/heal_registry.py (no _validator suffix)

#### 3. config/ (2 files)
- agentic_core/L5_safety/config/blueprint_compiler.py (no _config suffix)
- agentic_core/L5_safety/config/structure_blueprint/__init__.py (OK - __init__.py)

#### 4. types/ (20 files)
Files without _types/_protocol/Error/Exception suffix - need rename or move

#### 5. utils/ (12 files)
Files without _util/_mixin/_helper suffix - need rename or move

#### 6. enforcement/ (71 files)
Files without _guardrail/_enforcer/_gate/_strategy/Strategy/Adapter/Monitor/Factory/Gateway suffix

#### 7. engines/ (29 files)
Files that don't match allowed patterns

#### 8. tools/ (77 files)
Files that don't match allowed patterns

#### 9. engines/ DISALLOWED (1 file)
- agentic_core/L3_orchestration/engines/DagRuntimeInspectorAgent.py (Agent suffix disallowed in engines/)

### Move Plan Table (Priority: apps_* first, then agentic_core)

| violating_path | target_folder | rationale |
|----------------|---------------|-----------|
| apps_rg/reasoning/HardenedanthropicexecutorStrategy.py | apps_rg/enforcement/ | Strategy suffix -> enforcement |
| apps_rg/reasoning/resume_orchestrator.py | RENAME to ResumeOrchestrator.py | snake_case -> PascalCase Orchestrator |
| apps_shared/reasoning/batch_refactor_agents.py | apps_shared/scripts/ | snake_case script |
| apps_shared/reasoning/compare_agent_lists.py | apps_shared/scripts/ | snake_case script |
| apps_shared/reasoning/fix_all_agentic_imports.py | apps_shared/scripts/ | snake_case script |
| apps_shared/reasoning/coordinate_observability_operations_orchestrator_type.py | apps_shared/types/ | _type suffix |
| apps_shared/reasoning/orchestrate_observability_planning_orchestrator_type.py | apps_shared/types/ | _type suffix |
| apps_shared/reasoning/l5_autonomous_orchestrator_wrapper.py | apps_shared/utils/ | _wrapper suffix |
| apps_shared/reasoning/AgentRole.py | apps_shared/types/ | Role type, not Agent |
| agentic_core/L3_orchestration/engines/DagRuntimeInspectorAgent.py | agentic_core/L3_orchestration/reasoning/ | Agent suffix disallowed in engines |

---

## Wave 5.2: Fix Failures Set #1

(To be appended after execution)

---

## Wave 5.3: Fix Failures Set #2

(To be appended after execution)
