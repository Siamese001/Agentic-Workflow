# P1 Runtime Progress

## Wave 0

- Status: baseline complete
- ADG SQLite: `artifacts/adg/adg_indexed_03152026_2125.sqlite`
- Baseline artifact: `docs/reports/plans/p1_runtime_baseline_03152026_2125.md`
- Target matrix: `docs/reports/plans/p1_target_matrix.md`
- Deficit export: `docs/reports/plans/runtime_gaps/orchestration_governance_deficit.csv`

## Coverage Snapshot (Post Wave 1)

| Relation Type | Baseline | Wave 1 | Delta | Status |
|---|---:|---:|---:|---|
| `routes_to_agent` | 0 | 4 | +4 | LIVE |
| `orchestrates_workflow` | 0 | 33 | +33 | LIVE |
| `dispatches_execution_plan` | 0 | 5 | +5 | LIVE |
| `validates_agent_capability` | 0 | 3 | +3 | LIVE |
| `checks_agent_registry` | 0 | 3 | +3 | LIVE |
| `invokes_eval` | 542 | 542 | 0 | unchanged |
| `applies_guardrail` | 3132 | 3132 | 0 | unchanged |
| `records_execution_trace` | 6556 | 6556 | 0 | unchanged |
| `reads_policy_state` | 4770 | 4770 | 0 | unchanged |

## Wave 1 — Completed

- **ADG SQLite**: `artifacts/adg/adg_indexed_03152026_2137.sqlite`
- **Digest**: `cc92b7f88f05ec5022f88634ffabfbd2159ee62599da0f74949e76bf2bdb36ac`
- **Total edges**: 322,380 (from 6,291 modules)
- **Files edited**: 12 (under 15-module limit)

### Infrastructure changes (3 files)
1. `agentic_core/adg/schema.py` — 5 new RelationType + EdgeKind literals, 5 new frozensets
2. `agentic_core/runtime/lifecycle_trace_contract.py` — 5 new loggers + emitter functions
3. `agentic_core/adg/extraction/static_scanner.py` — `_P1OrchestrationGovernanceVisitor` (G28)

### L3 wiring (9 files)
| Module | Emitters wired |
|---|---|
| `orchestrator_engine.py` | `routes_to_agent`, `orchestrates_workflow` |
| `agent_dispatch_registry.py` | `routes_to_agent`, `dispatches_execution_plan`, `checks_agent_registry` |
| `capability_registry.py` | `validates_agent_capability`, `checks_agent_registry` |
| `deterministic_orchestrator.py` | `routes_to_agent`, `orchestrates_workflow` |
| `rl_coordinator_orchestrator.py` | `orchestrates_workflow` |
| `mission_runner.py` | `dispatches_execution_plan` |
| `autonomous_workflow_engine.py` | `orchestrates_workflow` |
| `orchestration_handoff_contract.py` | `routes_to_agent` |
| `agent_capability_registry.py` | `validates_agent_capability`, `checks_agent_registry` |

### Source files emitting edges (scanner-detected)
- **routes_to_agent** (4): orchestration_handoff_contract, deterministic_orchestrator, orchestrator_engine, agent_dispatch_registry
- **orchestrates_workflow** (33): autonomous_workflow_engine, deterministic_orchestrator, orchestrator_engine, rl_coordinator_orchestrator, execution_orchestrator (L0), + test files
- **dispatches_execution_plan** (5): mission_runner, agent_dispatch_registry, + test files
- **validates_agent_capability** (3): agent_handoff, agent_capability_registry, capability_registry
- **checks_agent_registry** (3): agent_capability_registry, agent_dispatch_registry, capability_registry

## Assessment

- All 5 missing P1 orchestration governance edge families are now **LIVE** with non-zero counts.
- The scanner amplification effect detected additional matching symbols beyond the 9 directly wired modules.
- No existing tests broken (19/19 scanner contract tests pass).
- No orchestration DAG divergence or safety bypass detected.
- Wave 1 is **COMPLETE**. Determine if additional micro-waves are needed for target coverage.
