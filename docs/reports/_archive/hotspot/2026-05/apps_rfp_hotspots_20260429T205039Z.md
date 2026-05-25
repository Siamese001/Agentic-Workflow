# `apps_rfp` — ADG Hotspot Report (W0.1)

Generated: `2026-04-29T20:50:39Z`
Snapshot: `adg_indexed_04292026_1606.sqlite`
Severity (Phase B): **MEDIUM-LOW (defensible multi-agent)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_04292026_1606.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 58 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_rfp/reasoning/RfpOrchestrator.py` | `apps_rfp/reasoning/RfpOrchestrator.py` | 88 |
| `ADG::Module::apps_rfp/engines/proposal_assembly_engine.py` | `apps_rfp/engines/proposal_assembly_engine.py` | 74 |
| `ADG::Module::apps_rfp/config/agent_spec_config.py` | `apps_rfp/config/agent_spec_config.py` | 73 |
| `ADG::Module::apps_rfp/__main__.py` | `apps_rfp/__main__.py` | 68 |
| `ADG::Module::apps_rfp/reasoning/enterprise_orchestrator.py` | `apps_rfp/reasoning/enterprise_orchestrator.py` | 32 |
| `ADG::Module::apps_rfp/reasoning/RequirementAnalysisAgent.py` | `apps_rfp/reasoning/RequirementAnalysisAgent.py` | 16 |
| `ADG::Module::apps_rfp/_compat/lifecycle_trace.py` | `apps_rfp/_compat/lifecycle_trace.py` | 16 |
| `ADG::Module::apps_rfp/reasoning/ComplianceMappingAgent.py` | `apps_rfp/reasoning/ComplianceMappingAgent.py` | 15 |
| `ADG::Module::apps_rfp/services/requirement_parser_service.py` | `apps_rfp/services/requirement_parser_service.py` | 14 |
| `ADG::Module::apps_rfp/reasoning/section_orchestrator.py` | `apps_rfp/reasoning/section_orchestrator.py` | 14 |
| `ADG::Module::apps_rfp/engines/proposal_retrieval_engine.py` | `apps_rfp/engines/proposal_retrieval_engine.py` | 14 |
| `ADG::Module::apps_rfp/engines/base_rfp_engine.py` | `apps_rfp/engines/base_rfp_engine.py` | 13 |
| `ADG::Module::apps_rfp/services/compliance_checker_service.py` | `apps_rfp/services/compliance_checker_service.py` | 12 |
| `ADG::Module::apps_rfp/reasoning/compliance_validator.py` | `apps_rfp/reasoning/compliance_validator.py` | 12 |
| `ADG::Module::apps_rfp/engines/rfp_ingestion_engine.py` | `apps_rfp/engines/rfp_ingestion_engine.py` | 12 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **13**

- `apps_rfp/engines/__init__.py`
- `apps_rfp/engines/base_rfp_engine.py`
- `apps_rfp/engines/proposal_assembly_engine.py`
- `apps_rfp/engines/proposal_retrieval_engine.py`
- `apps_rfp/engines/rfp_ingestion_engine.py`
- `apps_rfp/reasoning/ComplianceMappingAgent.py`
- `apps_rfp/reasoning/RequirementAnalysisAgent.py`
- `apps_rfp/reasoning/RfpOrchestrator.py`
- `apps_rfp/reasoning/__init__.py`
- `apps_rfp/reasoning/compliance_validator.py`
- `apps_rfp/reasoning/enterprise_orchestrator.py`
- `apps_rfp/reasoning/requirement_decomposition_agent.py`
- `apps_rfp/reasoning/section_orchestrator.py`

## mv_hotspot_centrality (top 10 within app)

Rows: 10
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2726, 'ADG::Module::apps_rfp/__init__.py', 'L_APP', 'apps_rfp/__init__.py', 0, 2, 2, 0.0, 0.0, 2726, 'ADG::Module::apps_rfp/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '889cb0da36563f06543f83e2449719626ca03562')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2727, 'ADG::Module::apps_rfp/__main__.py', 'L_APP', 'apps_rfp/__main__.py', 0, 68, 68, 0.0, 0.0, 2727, 'ADG::Module::apps_rfp/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'a226570c408e5a271fd9dc5d791f30c3c4bc3ff3')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2728, 'ADG::Module::apps_rfp/_compat/__init__.py', 'L_APP', 'apps_rfp/_compat/__init__.py', 0, 0, 0, 0.0, 0.0, 2728, 'ADG::Module::apps_rfp/_compat/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/_compat/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2729, 'ADG::Module::apps_rfp/_compat/lifecycle_trace.py', 'L_APP', 'apps_rfp/_compat/lifecycle_trace.py', 0, 16, 16, 0.0, 0.0, 2729, 'ADG::Module::apps_rfp/_compat/lifecycle_trace.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/_compat/lifecycle_trace.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '0cef92a0de5d5603826af99ca91b462c71772484')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2730, 'ADG::Module::apps_rfp/config/__init__.py', 'L_APP', 'apps_rfp/config/__init__.py', 0, 1, 1, 0.0, 0.0, 2730, 'ADG::Module::apps_rfp/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fc59eec49d4caba3437186fda93b32d705dbd740')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2731, 'ADG::Module::apps_rfp/config/agent_spec_config.py', 'L_APP', 'apps_rfp/config/agent_spec_config.py', 0, 73, 73, 0.0, 0.0, 2731, 'ADG::Module::apps_rfp/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '421a95e77510eca85a116a557bedcde8f6dfd368')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2732, 'ADG::Module::apps_rfp/config/knowledge_base.py', 'L_APP', 'apps_rfp/config/knowledge_base.py', 0, 12, 12, 0.0, 0.0, 2732, 'ADG::Module::apps_rfp/config/knowledge_base.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/knowledge_base.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b9fa25e583cace8dee42e9994e7f4326179a34d5')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2733, 'ADG::Module::apps_rfp/config/reasoning_toggles_config.py', 'L_APP', 'apps_rfp/config/reasoning_toggles_config.py', 0, 2, 2, 0.0, 0.0, 2733, 'ADG::Module::apps_rfp/config/reasoning_toggles_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/reasoning_toggles_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '790fcfab046a1c375d181e97c38c796b950b9c6f')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2734, 'ADG::Module::apps_rfp/engines/__init__.py', 'L_APP', 'apps_rfp/engines/__init__.py', 0, 0, 0, 0.0, 0.0, 2734, 'ADG::Module::apps_rfp/engines/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2735, 'ADG::Module::apps_rfp/engines/base_rfp_engine.py', 'L_APP', 'apps_rfp/engines/base_rfp_engine.py', 0, 13, 13, 0.0, 0.0, 2735, 'ADG::Module::apps_rfp/engines/base_rfp_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/engines/base_rfp_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '311570076d5e6b3d154ba4c6f7296256c041baa2')

## mv_dependency_cone_risk (top 10 within app)

Rows: 10
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2726, 'ADG::Module::apps_rfp/__init__.py', 'L_APP', 'apps_rfp/__init__.py', 0, 0, 0, 0, 0.0, 2726, 'ADG::Module::apps_rfp/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '889cb0da36563f06543f83e2449719626ca03562')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2727, 'ADG::Module::apps_rfp/__main__.py', 'L_APP', 'apps_rfp/__main__.py', 0, 0, 0, 0, 0.0, 2727, 'ADG::Module::apps_rfp/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'a226570c408e5a271fd9dc5d791f30c3c4bc3ff3')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2728, 'ADG::Module::apps_rfp/_compat/__init__.py', 'L_APP', 'apps_rfp/_compat/__init__.py', 0, 0, 0, 0, 0.0, 2728, 'ADG::Module::apps_rfp/_compat/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/_compat/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2729, 'ADG::Module::apps_rfp/_compat/lifecycle_trace.py', 'L_APP', 'apps_rfp/_compat/lifecycle_trace.py', 0, 0, 0, 0, 0.0, 2729, 'ADG::Module::apps_rfp/_compat/lifecycle_trace.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/_compat/lifecycle_trace.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '0cef92a0de5d5603826af99ca91b462c71772484')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2730, 'ADG::Module::apps_rfp/config/__init__.py', 'L_APP', 'apps_rfp/config/__init__.py', 0, 0, 0, 0, 0.0, 2730, 'ADG::Module::apps_rfp/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fc59eec49d4caba3437186fda93b32d705dbd740')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2731, 'ADG::Module::apps_rfp/config/agent_spec_config.py', 'L_APP', 'apps_rfp/config/agent_spec_config.py', 0, 0, 0, 0, 0.0, 2731, 'ADG::Module::apps_rfp/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '421a95e77510eca85a116a557bedcde8f6dfd368')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2732, 'ADG::Module::apps_rfp/config/knowledge_base.py', 'L_APP', 'apps_rfp/config/knowledge_base.py', 0, 0, 0, 0, 0.0, 2732, 'ADG::Module::apps_rfp/config/knowledge_base.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/knowledge_base.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b9fa25e583cace8dee42e9994e7f4326179a34d5')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2733, 'ADG::Module::apps_rfp/config/reasoning_toggles_config.py', 'L_APP', 'apps_rfp/config/reasoning_toggles_config.py', 0, 0, 0, 0, 0.0, 2733, 'ADG::Module::apps_rfp/config/reasoning_toggles_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/reasoning_toggles_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '790fcfab046a1c375d181e97c38c796b950b9c6f')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2734, 'ADG::Module::apps_rfp/engines/__init__.py', 'L_APP', 'apps_rfp/engines/__init__.py', 0, 0, 0, 0, 0.0, 2734, 'ADG::Module::apps_rfp/engines/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2735, 'ADG::Module::apps_rfp/engines/base_rfp_engine.py', 'L_APP', 'apps_rfp/engines/base_rfp_engine.py', 0, 0, 0, 0, 0.0, 2735, 'ADG::Module::apps_rfp/engines/base_rfp_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/engines/base_rfp_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '311570076d5e6b3d154ba4c6f7296256c041baa2')

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
  - `apps_rfp/reasoning/RfpOrchestrator.py` (fan-out 88)
  - `apps_rfp/engines/proposal_assembly_engine.py` (fan-out 74)
  - `apps_rfp/config/agent_spec_config.py` (fan-out 73)
  - `apps_rfp/__main__.py` (fan-out 68)
  - `apps_rfp/reasoning/enterprise_orchestrator.py` (fan-out 32)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

