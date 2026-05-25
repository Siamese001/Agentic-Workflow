# `apps_exec` — ADG Hotspot Report (W0.1)

Generated: `2026-04-29T20:50:39Z`
Snapshot: `adg_indexed_04292026_1606.sqlite`
Severity (Phase B): **MEDIUM**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_04292026_1606.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 61 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_exec/reasoning/ExecOrchestrator.py` | `apps_exec/reasoning/ExecOrchestrator.py` | 91 |
| `ADG::Module::apps_exec/engines/brief_assembly_engine.py` | `apps_exec/engines/brief_assembly_engine.py` | 75 |
| `ADG::Module::apps_exec/config/agent_spec_config.py` | `apps_exec/config/agent_spec_config.py` | 74 |
| `ADG::Module::apps_exec/validators/style_gate_validator.py` | `apps_exec/validators/style_gate_validator.py` | 73 |
| `ADG::Module::apps_exec/engines/capability_extraction_engine.py` | `apps_exec/engines/capability_extraction_engine.py` | 73 |
| `ADG::Module::apps_exec/engines/ingestion_engine.py` | `apps_exec/engines/ingestion_engine.py` | 72 |
| `ADG::Module::apps_exec/__main__.py` | `apps_exec/__main__.py` | 68 |
| `ADG::Module::apps_exec/reasoning/enterprise_brief_orchestrator.py` | `apps_exec/reasoning/enterprise_brief_orchestrator.py` | 26 |
| `ADG::Module::apps_exec/reasoning/SourceIngestionAgent.py` | `apps_exec/reasoning/SourceIngestionAgent.py` | 16 |
| `ADG::Module::apps_exec/services/document_ingestion_service.py` | `apps_exec/services/document_ingestion_service.py` | 15 |
| `ADG::Module::apps_exec/reasoning/BriefAssemblyAgent.py` | `apps_exec/reasoning/BriefAssemblyAgent.py` | 15 |
| `ADG::Module::apps_exec/reasoning/StyleComplianceAgent.py` | `apps_exec/reasoning/StyleComplianceAgent.py` | 14 |
| `ADG::Module::apps_exec/engines/base_exec_engine.py` | `apps_exec/engines/base_exec_engine.py` | 14 |
| `ADG::Module::apps_exec/reasoning/brief_orchestrator.py` | `apps_exec/reasoning/brief_orchestrator.py` | 13 |
| `ADG::Module::apps_exec/engines/brief_retrieval_engine.py` | `apps_exec/engines/brief_retrieval_engine.py` | 13 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **14**

- `apps_exec/engines/__init__.py`
- `apps_exec/engines/base_exec_engine.py`
- `apps_exec/engines/brief_assembly_engine.py`
- `apps_exec/engines/brief_retrieval_engine.py`
- `apps_exec/engines/capability_extraction_engine.py`
- `apps_exec/engines/ingestion_engine.py`
- `apps_exec/reasoning/BriefAssemblyAgent.py`
- `apps_exec/reasoning/ExecOrchestrator.py`
- `apps_exec/reasoning/SourceIngestionAgent.py`
- `apps_exec/reasoning/StyleComplianceAgent.py`
- `apps_exec/reasoning/__init__.py`
- `apps_exec/reasoning/brief_decomposition_agent.py`
- `apps_exec/reasoning/brief_orchestrator.py`
- `apps_exec/reasoning/enterprise_brief_orchestrator.py`

## mv_hotspot_centrality (top 10 within app)

Rows: 10
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2511, 'ADG::Module::apps_exec/__init__.py', 'L_APP', 'apps_exec/__init__.py', 0, 3, 3, 0.0, 0.0, 2511, 'ADG::Module::apps_exec/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '664b5bbb2d7d3c0261d0f917d9129c1e8c49d0e4')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2512, 'ADG::Module::apps_exec/__main__.py', 'L_APP', 'apps_exec/__main__.py', 0, 68, 68, 0.0, 0.0, 2512, 'ADG::Module::apps_exec/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'f318f49c6bee51232919c9b71719299dff608f3d')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2513, 'ADG::Module::apps_exec/_optional_agentic_core.py', 'L_APP', 'apps_exec/_optional_agentic_core.py', 0, 11, 11, 0.0, 0.0, 2513, 'ADG::Module::apps_exec/_optional_agentic_core.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/_optional_agentic_core.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '7f7e77f0d34d37b8e37c23c5cf414a9d1f72f70f')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2514, 'ADG::Module::apps_exec/config/__init__.py', 'L_APP', 'apps_exec/config/__init__.py', 0, 8, 8, 0.0, 0.0, 2514, 'ADG::Module::apps_exec/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b98e2258deb96c361fd8266d7d699a478f50aa1b')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2515, 'ADG::Module::apps_exec/config/agent_spec_config.py', 'L_APP', 'apps_exec/config/agent_spec_config.py', 0, 74, 74, 0.0, 0.0, 2515, 'ADG::Module::apps_exec/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b25803c0023c03c44cc7b499984f31b1d5e76894')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2516, 'ADG::Module::apps_exec/config/knowledge_base.py', 'L_APP', 'apps_exec/config/knowledge_base.py', 0, 4, 4, 0.0, 0.0, 2516, 'ADG::Module::apps_exec/config/knowledge_base.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/config/knowledge_base.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '73eab4885724483ccff25c527bd29a81077c5e56')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2517, 'ADG::Module::apps_exec/config/reasoning_toggles_config.py', 'L_APP', 'apps_exec/config/reasoning_toggles_config.py', 0, 2, 2, 0.0, 0.0, 2517, 'ADG::Module::apps_exec/config/reasoning_toggles_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/config/reasoning_toggles_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'a9e04a8b5b83e295f6d7529786cf8c80efd9cb2c')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2518, 'ADG::Module::apps_exec/engines/__init__.py', 'L_APP', 'apps_exec/engines/__init__.py', 0, 1, 1, 0.0, 0.0, 2518, 'ADG::Module::apps_exec/engines/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fc59eec49d4caba3437186fda93b32d705dbd740')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2519, 'ADG::Module::apps_exec/engines/base_exec_engine.py', 'L_APP', 'apps_exec/engines/base_exec_engine.py', 0, 14, 14, 0.0, 0.0, 2519, 'ADG::Module::apps_exec/engines/base_exec_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/engines/base_exec_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '458af0a4ab7b98eeb18e439c051db60836c74e73')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2520, 'ADG::Module::apps_exec/engines/brief_assembly_engine.py', 'L_APP', 'apps_exec/engines/brief_assembly_engine.py', 0, 75, 75, 0.0, 0.0, 2520, 'ADG::Module::apps_exec/engines/brief_assembly_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/engines/brief_assembly_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '69e6b9b1fb8e7cb008c36f5ef4c0cd4efb4aed20')

## mv_dependency_cone_risk (top 10 within app)

Rows: 10
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2511, 'ADG::Module::apps_exec/__init__.py', 'L_APP', 'apps_exec/__init__.py', 0, 0, 0, 0, 0.0, 2511, 'ADG::Module::apps_exec/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '664b5bbb2d7d3c0261d0f917d9129c1e8c49d0e4')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2512, 'ADG::Module::apps_exec/__main__.py', 'L_APP', 'apps_exec/__main__.py', 0, 0, 0, 0, 0.0, 2512, 'ADG::Module::apps_exec/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'f318f49c6bee51232919c9b71719299dff608f3d')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2513, 'ADG::Module::apps_exec/_optional_agentic_core.py', 'L_APP', 'apps_exec/_optional_agentic_core.py', 0, 0, 0, 0, 0.0, 2513, 'ADG::Module::apps_exec/_optional_agentic_core.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/_optional_agentic_core.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '7f7e77f0d34d37b8e37c23c5cf414a9d1f72f70f')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2514, 'ADG::Module::apps_exec/config/__init__.py', 'L_APP', 'apps_exec/config/__init__.py', 0, 0, 0, 0, 0.0, 2514, 'ADG::Module::apps_exec/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b98e2258deb96c361fd8266d7d699a478f50aa1b')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2515, 'ADG::Module::apps_exec/config/agent_spec_config.py', 'L_APP', 'apps_exec/config/agent_spec_config.py', 0, 0, 0, 0, 0.0, 2515, 'ADG::Module::apps_exec/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b25803c0023c03c44cc7b499984f31b1d5e76894')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2516, 'ADG::Module::apps_exec/config/knowledge_base.py', 'L_APP', 'apps_exec/config/knowledge_base.py', 0, 0, 0, 0, 0.0, 2516, 'ADG::Module::apps_exec/config/knowledge_base.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/config/knowledge_base.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '73eab4885724483ccff25c527bd29a81077c5e56')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2517, 'ADG::Module::apps_exec/config/reasoning_toggles_config.py', 'L_APP', 'apps_exec/config/reasoning_toggles_config.py', 0, 0, 0, 0, 0.0, 2517, 'ADG::Module::apps_exec/config/reasoning_toggles_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/config/reasoning_toggles_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'a9e04a8b5b83e295f6d7529786cf8c80efd9cb2c')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2518, 'ADG::Module::apps_exec/engines/__init__.py', 'L_APP', 'apps_exec/engines/__init__.py', 0, 0, 0, 0, 0.0, 2518, 'ADG::Module::apps_exec/engines/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fc59eec49d4caba3437186fda93b32d705dbd740')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2519, 'ADG::Module::apps_exec/engines/base_exec_engine.py', 'L_APP', 'apps_exec/engines/base_exec_engine.py', 0, 0, 0, 0, 0.0, 2519, 'ADG::Module::apps_exec/engines/base_exec_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/engines/base_exec_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '458af0a4ab7b98eeb18e439c051db60836c74e73')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2520, 'ADG::Module::apps_exec/engines/brief_assembly_engine.py', 'L_APP', 'apps_exec/engines/brief_assembly_engine.py', 0, 0, 0, 0, 0.0, 2520, 'ADG::Module::apps_exec/engines/brief_assembly_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/engines/brief_assembly_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '69e6b9b1fb8e7cb008c36f5ef4c0cd4efb4aed20')

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
  - `apps_exec/reasoning/ExecOrchestrator.py` (fan-out 91)
  - `apps_exec/engines/brief_assembly_engine.py` (fan-out 75)
  - `apps_exec/config/agent_spec_config.py` (fan-out 74)
  - `apps_exec/validators/style_gate_validator.py` (fan-out 73)
  - `apps_exec/engines/capability_extraction_engine.py` (fan-out 73)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

