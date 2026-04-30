# `apps_research` — ADG Hotspot Report (W0.1)

Generated: `2026-04-29T20:50:39Z`
Snapshot: `adg_indexed_04292026_1606.sqlite`
Severity (Phase B): **LOW**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_04292026_1606.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 57 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_research/reasoning/ResearchOrchestrator.py` | `apps_research/reasoning/ResearchOrchestrator.py` | 89 |
| `ADG::Module::apps_research/engines/research_assembly_engine.py` | `apps_research/engines/research_assembly_engine.py` | 75 |
| `ADG::Module::apps_research/config/agent_spec_config.py` | `apps_research/config/agent_spec_config.py` | 73 |
| `ADG::Module::apps_research/_telemetry.py` | `apps_research/_telemetry.py` | 65 |
| `ADG::Module::apps_research/reasoning/enterprise_research_orchestrator.py` | `apps_research/reasoning/enterprise_research_orchestrator.py` | 25 |
| `ADG::Module::apps_research/reasoning/KnowledgeSynthesisAgent.py` | `apps_research/reasoning/KnowledgeSynthesisAgent.py` | 16 |
| `ADG::Module::apps_research/services/source_discovery_service.py` | `apps_research/services/source_discovery_service.py` | 15 |
| `ADG::Module::apps_research/reasoning/SourceDiscoveryAgent.py` | `apps_research/reasoning/SourceDiscoveryAgent.py` | 15 |
| `ADG::Module::apps_research/integrations/execution_adapter.py` | `apps_research/integrations/execution_adapter.py` | 15 |
| `ADG::Module::apps_research/reasoning/InsightExtractionAgent.py` | `apps_research/reasoning/InsightExtractionAgent.py` | 14 |
| `ADG::Module::apps_research/services/synthesis_engine_service.py` | `apps_research/services/synthesis_engine_service.py` | 13 |
| `ADG::Module::apps_research/reasoning/research_multi_agent.py` | `apps_research/reasoning/research_multi_agent.py` | 13 |
| `ADG::Module::apps_research/engines/research_retrieval_engine.py` | `apps_research/engines/research_retrieval_engine.py` | 13 |
| `ADG::Module::apps_research/engines/base_research_engine.py` | `apps_research/engines/base_research_engine.py` | 13 |
| `ADG::Module::apps_research/config/knowledge_base.py` | `apps_research/config/knowledge_base.py` | 12 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **12**

- `apps_research/engines/__init__.py`
- `apps_research/engines/base_research_engine.py`
- `apps_research/engines/research_assembly_engine.py`
- `apps_research/engines/research_retrieval_engine.py`
- `apps_research/reasoning/InsightExtractionAgent.py`
- `apps_research/reasoning/KnowledgeSynthesisAgent.py`
- `apps_research/reasoning/ResearchOrchestrator.py`
- `apps_research/reasoning/SourceDiscoveryAgent.py`
- `apps_research/reasoning/__init__.py`
- `apps_research/reasoning/enterprise_research_orchestrator.py`
- `apps_research/reasoning/query_decomposition_agent.py`
- `apps_research/reasoning/research_multi_agent.py`

## mv_hotspot_centrality (top 10 within app)

Rows: 10
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2669, 'ADG::Module::apps_research/__init__.py', 'L_APP', 'apps_research/__init__.py', 0, 2, 2, 0.0, 0.0, 2669, 'ADG::Module::apps_research/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '07e9b5e88454a4d657b963e4426c1d48d31f45a8')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2670, 'ADG::Module::apps_research/__main__.py', 'L_APP', 'apps_research/__main__.py', 0, 6, 6, 0.0, 0.0, 2670, 'ADG::Module::apps_research/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'cb4ca8d3156b7c7a7d09a1c59eaa9fb6a0d12e29')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2671, 'ADG::Module::apps_research/_telemetry.py', 'L_APP', 'apps_research/_telemetry.py', 0, 65, 65, 0.0, 0.0, 2671, 'ADG::Module::apps_research/_telemetry.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/_telemetry.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5b1c6cd22edb271311c985eb6795e0e1d556ce0c')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2672, 'ADG::Module::apps_research/config/__init__.py', 'L_APP', 'apps_research/config/__init__.py', 0, 1, 1, 0.0, 0.0, 2672, 'ADG::Module::apps_research/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fc59eec49d4caba3437186fda93b32d705dbd740')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2673, 'ADG::Module::apps_research/config/agent_spec_config.py', 'L_APP', 'apps_research/config/agent_spec_config.py', 0, 73, 73, 0.0, 0.0, 2673, 'ADG::Module::apps_research/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '60a1acce5145f8fe28bc9bb6bba0b51458606264')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2674, 'ADG::Module::apps_research/config/knowledge_base.py', 'L_APP', 'apps_research/config/knowledge_base.py', 0, 12, 12, 0.0, 0.0, 2674, 'ADG::Module::apps_research/config/knowledge_base.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/config/knowledge_base.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '17934dffde61082df38c7d46844542c352a527c7')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2675, 'ADG::Module::apps_research/config/reasoning_toggles_config.py', 'L_APP', 'apps_research/config/reasoning_toggles_config.py', 0, 2, 2, 0.0, 0.0, 2675, 'ADG::Module::apps_research/config/reasoning_toggles_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/config/reasoning_toggles_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b30b2848630654338b37cb816d8fb461822a0fba')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2676, 'ADG::Module::apps_research/engines/__init__.py', 'L_APP', 'apps_research/engines/__init__.py', 0, 0, 0, 0.0, 0.0, 2676, 'ADG::Module::apps_research/engines/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2677, 'ADG::Module::apps_research/engines/base_research_engine.py', 'L_APP', 'apps_research/engines/base_research_engine.py', 0, 13, 13, 0.0, 0.0, 2677, 'ADG::Module::apps_research/engines/base_research_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/engines/base_research_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '9e9714f1d54c56308db0f764486016aff749f587')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2678, 'ADG::Module::apps_research/engines/research_assembly_engine.py', 'L_APP', 'apps_research/engines/research_assembly_engine.py', 0, 75, 75, 0.0, 0.0, 2678, 'ADG::Module::apps_research/engines/research_assembly_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/engines/research_assembly_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '0d5375a9641eab7924b88bda0c69005f6dff53cd')

## mv_dependency_cone_risk (top 10 within app)

Rows: 10
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2669, 'ADG::Module::apps_research/__init__.py', 'L_APP', 'apps_research/__init__.py', 0, 0, 0, 0, 0.0, 2669, 'ADG::Module::apps_research/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '07e9b5e88454a4d657b963e4426c1d48d31f45a8')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2670, 'ADG::Module::apps_research/__main__.py', 'L_APP', 'apps_research/__main__.py', 0, 0, 0, 0, 0.0, 2670, 'ADG::Module::apps_research/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'cb4ca8d3156b7c7a7d09a1c59eaa9fb6a0d12e29')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2671, 'ADG::Module::apps_research/_telemetry.py', 'L_APP', 'apps_research/_telemetry.py', 0, 0, 0, 0, 0.0, 2671, 'ADG::Module::apps_research/_telemetry.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/_telemetry.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5b1c6cd22edb271311c985eb6795e0e1d556ce0c')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2672, 'ADG::Module::apps_research/config/__init__.py', 'L_APP', 'apps_research/config/__init__.py', 0, 0, 0, 0, 0.0, 2672, 'ADG::Module::apps_research/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fc59eec49d4caba3437186fda93b32d705dbd740')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2673, 'ADG::Module::apps_research/config/agent_spec_config.py', 'L_APP', 'apps_research/config/agent_spec_config.py', 0, 0, 0, 0, 0.0, 2673, 'ADG::Module::apps_research/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '60a1acce5145f8fe28bc9bb6bba0b51458606264')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2674, 'ADG::Module::apps_research/config/knowledge_base.py', 'L_APP', 'apps_research/config/knowledge_base.py', 0, 0, 0, 0, 0.0, 2674, 'ADG::Module::apps_research/config/knowledge_base.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/config/knowledge_base.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '17934dffde61082df38c7d46844542c352a527c7')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2675, 'ADG::Module::apps_research/config/reasoning_toggles_config.py', 'L_APP', 'apps_research/config/reasoning_toggles_config.py', 0, 0, 0, 0, 0.0, 2675, 'ADG::Module::apps_research/config/reasoning_toggles_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/config/reasoning_toggles_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b30b2848630654338b37cb816d8fb461822a0fba')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2676, 'ADG::Module::apps_research/engines/__init__.py', 'L_APP', 'apps_research/engines/__init__.py', 0, 0, 0, 0, 0.0, 2676, 'ADG::Module::apps_research/engines/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2677, 'ADG::Module::apps_research/engines/base_research_engine.py', 'L_APP', 'apps_research/engines/base_research_engine.py', 0, 0, 0, 0, 0.0, 2677, 'ADG::Module::apps_research/engines/base_research_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/engines/base_research_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '9e9714f1d54c56308db0f764486016aff749f587')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2678, 'ADG::Module::apps_research/engines/research_assembly_engine.py', 'L_APP', 'apps_research/engines/research_assembly_engine.py', 0, 0, 0, 0, 0.0, 2678, 'ADG::Module::apps_research/engines/research_assembly_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/engines/research_assembly_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '0d5375a9641eab7924b88bda0c69005f6dff53cd')

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
  - `apps_research/reasoning/ResearchOrchestrator.py` (fan-out 89)
  - `apps_research/engines/research_assembly_engine.py` (fan-out 75)
  - `apps_research/config/agent_spec_config.py` (fan-out 73)
  - `apps_research/_telemetry.py` (fan-out 65)
  - `apps_research/reasoning/enterprise_research_orchestrator.py` (fan-out 25)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

