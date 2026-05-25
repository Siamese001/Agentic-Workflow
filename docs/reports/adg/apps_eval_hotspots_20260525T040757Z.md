# `apps_eval` — ADG Hotspot Report (W0.1)

Generated: `2026-05-25T04:07:57Z`
Snapshot: `adg_indexed_05242026_2005.sqlite`
Severity (Phase B): **MEDIUM (cross-app judge consumer)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05242026_2005.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 76 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_eval/engines/scenario_runner.py` | `apps_eval/engines/scenario_runner.py` | 118 |
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

Total files under `engines/` + `reasoning/`: **27**

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

## mv_hotspot_centrality (top 10 within app)

Rows: 10
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2720, 'ADG::Module::apps_eval/__init__.py', 'L_APP', 'apps_eval/__init__.py', 0, 0, 0, 0.0, 0.0, 2720, 'ADG::Module::apps_eval/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2721, 'ADG::Module::apps_eval/__main__.py', 'L_APP', 'apps_eval/__main__.py', 0, 14, 14, 0.0, 0.0, 2721, 'ADG::Module::apps_eval/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8a64a33aaa28c5e2a18ce5fbe25c4fa2d9f03a05')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2722, 'ADG::Module::apps_eval/_telemetry.py', 'L_APP', 'apps_eval/_telemetry.py', 0, 5, 5, 0.0, 0.0, 2722, 'ADG::Module::apps_eval/_telemetry.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/_telemetry.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '93e7f6610070029707a3bac99726d476c9fdc56b')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2723, 'ADG::Module::apps_eval/cert/__init__.py', 'L_APP', 'apps_eval/cert/__init__.py', 0, 2, 2, 0.0, 0.0, 2723, 'ADG::Module::apps_eval/cert/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/cert/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '237a65b22ff18cb022668a3d07dfa7a95e2c323b')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2724, 'ADG::Module::apps_eval/cert/fec_producer.py', 'L_APP', 'apps_eval/cert/fec_producer.py', 0, 4, 4, 0.0, 0.0, 2724, 'ADG::Module::apps_eval/cert/fec_producer.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/cert/fec_producer.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8561e68593f4ef52d97a35b6869ca153f5d0a1bd')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2725, 'ADG::Module::apps_eval/config/__init__.py', 'L_APP', 'apps_eval/config/__init__.py', 0, 3, 3, 0.0, 0.0, 2725, 'ADG::Module::apps_eval/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c02443d64b10702f350632a7eab56c5a5bd4df62')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2726, 'ADG::Module::apps_eval/config/agent_spec_config.py', 'L_APP', 'apps_eval/config/agent_spec_config.py', 0, 74, 74, 0.0, 0.0, 2726, 'ADG::Module::apps_eval/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '9ac8770f3f933b352ef6d4f5f1307c4e6d455db8')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2727, 'ADG::Module::apps_eval/config/hop_pipeline.py', 'L_APP', 'apps_eval/config/hop_pipeline.py', 0, 3, 3, 0.0, 0.0, 2727, 'ADG::Module::apps_eval/config/hop_pipeline.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/hop_pipeline.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '7e5ce2c25a42bb99c7a8bab725b7b94ac325b243')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2728, 'ADG::Module::apps_eval/config/reasoning_toggles_config.py', 'L_APP', 'apps_eval/config/reasoning_toggles_config.py', 0, 2, 2, 0.0, 0.0, 2728, 'ADG::Module::apps_eval/config/reasoning_toggles_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/reasoning_toggles_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'd2e1b329ca6174dce8bd45883b333c5da27da04c')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2729, 'ADG::Module::apps_eval/contracts/local_eval_evidence.py', 'L_APP', 'apps_eval/contracts/local_eval_evidence.py', 0, 5, 5, 0.0, 0.0, 2729, 'ADG::Module::apps_eval/contracts/local_eval_evidence.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/contracts/local_eval_evidence.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '59bbe918e7a76e6734494f6c657aaea03b0ad375')

## mv_dependency_cone_risk (top 10 within app)

Rows: 10
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2720, 'ADG::Module::apps_eval/__init__.py', 'L_APP', 'apps_eval/__init__.py', 0, 0, 0, 0, 0.0, 2720, 'ADG::Module::apps_eval/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2721, 'ADG::Module::apps_eval/__main__.py', 'L_APP', 'apps_eval/__main__.py', 0, 0, 0, 0, 0.0, 2721, 'ADG::Module::apps_eval/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8a64a33aaa28c5e2a18ce5fbe25c4fa2d9f03a05')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2722, 'ADG::Module::apps_eval/_telemetry.py', 'L_APP', 'apps_eval/_telemetry.py', 0, 0, 0, 0, 0.0, 2722, 'ADG::Module::apps_eval/_telemetry.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/_telemetry.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '93e7f6610070029707a3bac99726d476c9fdc56b')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2723, 'ADG::Module::apps_eval/cert/__init__.py', 'L_APP', 'apps_eval/cert/__init__.py', 0, 0, 0, 0, 0.0, 2723, 'ADG::Module::apps_eval/cert/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/cert/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '237a65b22ff18cb022668a3d07dfa7a95e2c323b')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2724, 'ADG::Module::apps_eval/cert/fec_producer.py', 'L_APP', 'apps_eval/cert/fec_producer.py', 0, 0, 0, 0, 0.0, 2724, 'ADG::Module::apps_eval/cert/fec_producer.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/cert/fec_producer.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8561e68593f4ef52d97a35b6869ca153f5d0a1bd')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2725, 'ADG::Module::apps_eval/config/__init__.py', 'L_APP', 'apps_eval/config/__init__.py', 0, 0, 0, 0, 0.0, 2725, 'ADG::Module::apps_eval/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c02443d64b10702f350632a7eab56c5a5bd4df62')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2726, 'ADG::Module::apps_eval/config/agent_spec_config.py', 'L_APP', 'apps_eval/config/agent_spec_config.py', 0, 0, 0, 0, 0.0, 2726, 'ADG::Module::apps_eval/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '9ac8770f3f933b352ef6d4f5f1307c4e6d455db8')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2727, 'ADG::Module::apps_eval/config/hop_pipeline.py', 'L_APP', 'apps_eval/config/hop_pipeline.py', 0, 0, 0, 0, 0.0, 2727, 'ADG::Module::apps_eval/config/hop_pipeline.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/hop_pipeline.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '7e5ce2c25a42bb99c7a8bab725b7b94ac325b243')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2728, 'ADG::Module::apps_eval/config/reasoning_toggles_config.py', 'L_APP', 'apps_eval/config/reasoning_toggles_config.py', 0, 0, 0, 0, 0.0, 2728, 'ADG::Module::apps_eval/config/reasoning_toggles_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/reasoning_toggles_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'd2e1b329ca6174dce8bd45883b333c5da27da04c')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2729, 'ADG::Module::apps_eval/contracts/local_eval_evidence.py', 'L_APP', 'apps_eval/contracts/local_eval_evidence.py', 0, 0, 0, 0, 0.0, 2729, 'ADG::Module::apps_eval/contracts/local_eval_evidence.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/contracts/local_eval_evidence.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '59bbe918e7a76e6734494f6c657aaea03b0ad375')

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
  - `apps_eval/engines/scenario_runner.py` (fan-out 118)
  - `apps_eval/reasoning/EvalOrchestrator.py` (fan-out 90)
  - `apps_eval/engines/regression_detector.py` (fan-out 84)
  - `apps_eval/engines/scorecard_engine.py` (fan-out 76)
  - `apps_eval/config/agent_spec_config.py` (fan-out 74)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

