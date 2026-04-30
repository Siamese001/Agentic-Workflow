# `apps_eval` — ADG Hotspot Report (W0.1)

Generated: `2026-04-29T20:50:39Z`
Snapshot: `adg_indexed_04292026_1606.sqlite`
Severity (Phase B): **MEDIUM (cross-app judge consumer)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_04292026_1606.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 65 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_eval/engines/scenario_runner.py` | `apps_eval/engines/scenario_runner.py` | 114 |
| `ADG::Module::apps_eval/reasoning/EvalOrchestrator.py` | `apps_eval/reasoning/EvalOrchestrator.py` | 90 |
| `ADG::Module::apps_eval/engines/regression_detector.py` | `apps_eval/engines/regression_detector.py` | 83 |
| `ADG::Module::apps_eval/engines/scorecard_engine.py` | `apps_eval/engines/scorecard_engine.py` | 75 |
| `ADG::Module::apps_eval/config/agent_spec_config.py` | `apps_eval/config/agent_spec_config.py` | 74 |
| `ADG::Module::apps_eval/validators/eval_gate_validator.py` | `apps_eval/validators/eval_gate_validator.py` | 72 |
| `ADG::Module::apps_eval/__main__.py` | `apps_eval/__main__.py` | 68 |
| `ADG::Module::apps_eval/reasoning/enterprise_eval_orchestrator.py` | `apps_eval/reasoning/enterprise_eval_orchestrator.py` | 26 |
| `ADG::Module::apps_eval/reasoning/TestDiscoveryAgent.py` | `apps_eval/reasoning/TestDiscoveryAgent.py` | 17 |
| `ADG::Module::apps_eval/engines/hitl_decision_quality_engine.py` | `apps_eval/engines/hitl_decision_quality_engine.py` | 17 |
| `ADG::Module::apps_eval/services/test_discovery_service.py` | `apps_eval/services/test_discovery_service.py` | 16 |
| `ADG::Module::apps_eval/reasoning/ScenarioGenerationAgent.py` | `apps_eval/reasoning/ScenarioGenerationAgent.py` | 16 |
| `ADG::Module::apps_eval/engines/evaluation_retrieval_engine.py` | `apps_eval/engines/evaluation_retrieval_engine.py` | 16 |
| `ADG::Module::apps_eval/reasoning/QualityGateAgent.py` | `apps_eval/reasoning/QualityGateAgent.py` | 15 |
| `ADG::Module::apps_eval/reasoning/evaluation_orchestrator.py` | `apps_eval/reasoning/evaluation_orchestrator.py` | 13 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **16**

- `apps_eval/engines/__init__.py`
- `apps_eval/engines/_taxonomy.py`
- `apps_eval/engines/base_eval_engine.py`
- `apps_eval/engines/evaluation_retrieval_engine.py`
- `apps_eval/engines/hitl_decision_quality_engine.py`
- `apps_eval/engines/regression_detector.py`
- `apps_eval/engines/scenario_runner.py`
- `apps_eval/engines/scorecard_engine.py`
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
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2446, 'ADG::Module::apps_eval/__init__.py', 'L_APP', 'apps_eval/__init__.py', 0, 0, 0, 0.0, 0.0, 2446, 'ADG::Module::apps_eval/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2447, 'ADG::Module::apps_eval/__main__.py', 'L_APP', 'apps_eval/__main__.py', 0, 68, 68, 0.0, 0.0, 2447, 'ADG::Module::apps_eval/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'e6f5f26b593536470ae71fe02dae0745e6168480')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2448, 'ADG::Module::apps_eval/_telemetry.py', 'L_APP', 'apps_eval/_telemetry.py', 0, 5, 5, 0.0, 0.0, 2448, 'ADG::Module::apps_eval/_telemetry.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/_telemetry.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '93e7f6610070029707a3bac99726d476c9fdc56b')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2449, 'ADG::Module::apps_eval/config/__init__.py', 'L_APP', 'apps_eval/config/__init__.py', 0, 3, 3, 0.0, 0.0, 2449, 'ADG::Module::apps_eval/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c02443d64b10702f350632a7eab56c5a5bd4df62')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2450, 'ADG::Module::apps_eval/config/agent_spec_config.py', 'L_APP', 'apps_eval/config/agent_spec_config.py', 0, 74, 74, 0.0, 0.0, 2450, 'ADG::Module::apps_eval/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '910500ba8ef2028f53d1799576b19489869a0675')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2451, 'ADG::Module::apps_eval/config/reasoning_toggles_config.py', 'L_APP', 'apps_eval/config/reasoning_toggles_config.py', 0, 2, 2, 0.0, 0.0, 2451, 'ADG::Module::apps_eval/config/reasoning_toggles_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/reasoning_toggles_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'd2e1b329ca6174dce8bd45883b333c5da27da04c')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2452, 'ADG::Module::apps_eval/engines/__init__.py', 'L_APP', 'apps_eval/engines/__init__.py', 0, 0, 0, 0.0, 0.0, 2452, 'ADG::Module::apps_eval/engines/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2453, 'ADG::Module::apps_eval/engines/_taxonomy.py', 'L_APP', 'apps_eval/engines/_taxonomy.py', 0, 5, 5, 0.0, 0.0, 2453, 'ADG::Module::apps_eval/engines/_taxonomy.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/engines/_taxonomy.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'ff8001119a93ab21a4b948a12582288d1d71de6f')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2454, 'ADG::Module::apps_eval/engines/base_eval_engine.py', 'L_APP', 'apps_eval/engines/base_eval_engine.py', 0, 13, 13, 0.0, 0.0, 2454, 'ADG::Module::apps_eval/engines/base_eval_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/engines/base_eval_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'cf8cbec8d44673c74f9655a0254abbad3d1c86a2')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2455, 'ADG::Module::apps_eval/engines/evaluation_retrieval_engine.py', 'L_APP', 'apps_eval/engines/evaluation_retrieval_engine.py', 0, 16, 16, 0.0, 0.0, 2455, 'ADG::Module::apps_eval/engines/evaluation_retrieval_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/engines/evaluation_retrieval_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'cd5208f877134aaa1ebb73afaf9c6df9ae07b483')

## mv_dependency_cone_risk (top 10 within app)

Rows: 10
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2446, 'ADG::Module::apps_eval/__init__.py', 'L_APP', 'apps_eval/__init__.py', 0, 0, 0, 0, 0.0, 2446, 'ADG::Module::apps_eval/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2447, 'ADG::Module::apps_eval/__main__.py', 'L_APP', 'apps_eval/__main__.py', 0, 0, 0, 0, 0.0, 2447, 'ADG::Module::apps_eval/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'e6f5f26b593536470ae71fe02dae0745e6168480')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2448, 'ADG::Module::apps_eval/_telemetry.py', 'L_APP', 'apps_eval/_telemetry.py', 0, 0, 0, 0, 0.0, 2448, 'ADG::Module::apps_eval/_telemetry.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/_telemetry.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '93e7f6610070029707a3bac99726d476c9fdc56b')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2449, 'ADG::Module::apps_eval/config/__init__.py', 'L_APP', 'apps_eval/config/__init__.py', 0, 0, 0, 0, 0.0, 2449, 'ADG::Module::apps_eval/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c02443d64b10702f350632a7eab56c5a5bd4df62')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2450, 'ADG::Module::apps_eval/config/agent_spec_config.py', 'L_APP', 'apps_eval/config/agent_spec_config.py', 0, 0, 0, 0, 0.0, 2450, 'ADG::Module::apps_eval/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '910500ba8ef2028f53d1799576b19489869a0675')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2451, 'ADG::Module::apps_eval/config/reasoning_toggles_config.py', 'L_APP', 'apps_eval/config/reasoning_toggles_config.py', 0, 0, 0, 0, 0.0, 2451, 'ADG::Module::apps_eval/config/reasoning_toggles_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/config/reasoning_toggles_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'd2e1b329ca6174dce8bd45883b333c5da27da04c')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2452, 'ADG::Module::apps_eval/engines/__init__.py', 'L_APP', 'apps_eval/engines/__init__.py', 0, 0, 0, 0, 0.0, 2452, 'ADG::Module::apps_eval/engines/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2453, 'ADG::Module::apps_eval/engines/_taxonomy.py', 'L_APP', 'apps_eval/engines/_taxonomy.py', 0, 0, 0, 0, 0.0, 2453, 'ADG::Module::apps_eval/engines/_taxonomy.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/engines/_taxonomy.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'ff8001119a93ab21a4b948a12582288d1d71de6f')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2454, 'ADG::Module::apps_eval/engines/base_eval_engine.py', 'L_APP', 'apps_eval/engines/base_eval_engine.py', 0, 0, 0, 0, 0.0, 2454, 'ADG::Module::apps_eval/engines/base_eval_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/engines/base_eval_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'cf8cbec8d44673c74f9655a0254abbad3d1c86a2')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2455, 'ADG::Module::apps_eval/engines/evaluation_retrieval_engine.py', 'L_APP', 'apps_eval/engines/evaluation_retrieval_engine.py', 0, 0, 0, 0, 0.0, 2455, 'ADG::Module::apps_eval/engines/evaluation_retrieval_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_eval/engines/evaluation_retrieval_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'cd5208f877134aaa1ebb73afaf9c6df9ae07b483')

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
  - `apps_eval/engines/scenario_runner.py` (fan-out 114)
  - `apps_eval/reasoning/EvalOrchestrator.py` (fan-out 90)
  - `apps_eval/engines/regression_detector.py` (fan-out 83)
  - `apps_eval/engines/scorecard_engine.py` (fan-out 75)
  - `apps_eval/config/agent_spec_config.py` (fan-out 74)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

