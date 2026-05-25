# `apps_eval` — ADG Hotspot Report (W0.1)

Generated: `2026-05-10T21:28:55Z`
Snapshot: `adg_indexed_05102026_1319.sqlite`
Severity (Phase B): **MEDIUM (cross-app judge consumer)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05102026_1319.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 84 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_eval/engines/scenario_runner.py` | `apps_eval/engines/scenario_runner.py` | 120 |
| `ADG::Module::apps_eval/reasoning/EvalOrchestrator.py` | `apps_eval/reasoning/EvalOrchestrator.py` | 90 |
| `ADG::Module::apps_eval/engines/regression_detector.py` | `apps_eval/engines/regression_detector.py` | 84 |
| `ADG::Module::apps_eval/engines/scorecard_engine.py` | `apps_eval/engines/scorecard_engine.py` | 76 |
| `ADG::Module::apps_eval/config/agent_spec_config.py` | `apps_eval/config/agent_spec_config.py` | 74 |
| `ADG::Module::apps_eval/validators/eval_gate_validator.py` | `apps_eval/validators/eval_gate_validator.py` | 72 |
| `ADG::Module::apps_eval/engines/narrative_judge_scorer.py` | `apps_eval/engines/narrative_judge_scorer.py` | 29 |
| `ADG::Module::apps_eval/reasoning/enterprise_eval_orchestrator.py` | `apps_eval/reasoning/enterprise_eval_orchestrator.py` | 26 |
| `ADG::Module::apps_eval/engines/hitl_decision_quality_engine.py` | `apps_eval/engines/hitl_decision_quality_engine.py` | 19 |
| `ADG::Module::apps_eval/reasoning/TestDiscoveryAgent.py` | `apps_eval/reasoning/TestDiscoveryAgent.py` | 17 |
| `ADG::Module::apps_eval/integrations/eval_ingress.py` | `apps_eval/integrations/eval_ingress.py` | 17 |
| `ADG::Module::apps_eval/engines/evaluation_retrieval_engine.py` | `apps_eval/engines/evaluation_retrieval_engine.py` | 17 |
| `ADG::Module::apps_eval/services/test_discovery_service.py` | `apps_eval/services/test_discovery_service.py` | 16 |
| `ADG::Module::apps_eval/reasoning/ScenarioGenerationAgent.py` | `apps_eval/reasoning/ScenarioGenerationAgent.py` | 16 |
| `ADG::Module::apps_eval/reasoning/QualityGateAgent.py` | `apps_eval/reasoning/QualityGateAgent.py` | 15 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **28**

- `apps_eval/engines/__init__.py`
- `apps_eval/engines/_taxonomy.py`
- `apps_eval/engines/base_eval_engine.py`
- `apps_eval/engines/eval_heal.py`
- `apps_eval/engines/eval_prep.py`
- `apps_eval/engines/eval_seal.py`
- `apps_eval/engines/eval_valid.py`
- `apps_eval/engines/evaluation_retrieval_engine.py`
- `apps_eval/engines/hitl_decision_quality_engine.py`
- `apps_eval/engines/hop_evaluation_retrieval_engine.py`
- `apps_eval/engines/hop_hitl_decision_quality_engine.py`
- `apps_eval/engines/hop_narrative_judge_engine.py`
- `apps_eval/engines/hop_regression_detector_engine.py`
- `apps_eval/engines/hop_scenario_runner_engine.py`
- `apps_eval/engines/hop_scorecard_engine.py`
- `apps_eval/engines/narrative_judge_scorer.py`
- `apps_eval/engines/regression_detector.py`
- `apps_eval/engines/scenario_runner.py`
- `apps_eval/engines/scorecard_engine.py`
- `apps_eval/reasoning/EvalHopOrchestrator.py`
- `apps_eval/reasoning/EvalOrchestrator.py`
- `apps_eval/reasoning/QualityGateAgent.py`
- `apps_eval/reasoning/ScenarioGenerationAgent.py`
- `apps_eval/reasoning/TestDiscoveryAgent.py`
- `apps_eval/reasoning/__init__.py`
- `apps_eval/reasoning/criteria_decomposition_agent.py`
- `apps_eval/reasoning/enterprise_eval_orchestrator.py`
- `apps_eval/reasoning/evaluation_orchestrator.py`

## mv_hotspot_centrality

_view not present in this snapshot_

## mv_dependency_cone_risk

_view not present in this snapshot_

## mv_chokepoint_bridges

_view not present in this snapshot_

## v_p0_apps_direct_infra (P0 violation — apps directly importing infra)

Rows: 1
- ('__error__', 'no such column: source_file')

## SC/AP Violations (top 30 by severity)

Rows: 1

| Severity | Kind | File | Line | Message |
|---|---|---|---:|---|

## Recommendations (derived)

- **Broadest reachers (most likely to consolidate):**
  - `apps_eval/engines/scenario_runner.py` (fan-out 120)
  - `apps_eval/reasoning/EvalOrchestrator.py` (fan-out 90)
  - `apps_eval/engines/regression_detector.py` (fan-out 84)
  - `apps_eval/engines/scorecard_engine.py` (fan-out 76)
  - `apps_eval/config/agent_spec_config.py` (fan-out 74)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

