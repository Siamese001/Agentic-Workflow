# `apps_rfp` — ADG Hotspot Report (W0.1)

Generated: `2026-05-25T13:29:39Z`
Snapshot: `adg_indexed_05252026_0849.sqlite`
Severity (Phase B): **MEDIUM-LOW (defensible multi-agent)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05252026_0849.sqlite

## Actionable hotspots (top 5 — deterministic linkage)

Linkage from structured sources only (`gate_results` queue file paths, P-views, `mv_debt_concentration_hotspots`, `refactor_accelerator`). `unknown` = no gate join.

| module_path | linked_gate_ids | violation_refs | impacted_tests_sample | linkage_source | linkage_confidence |
|-------------|-----------------|----------------|----------------------|----------------|-------------------|
| `ADG::Module::apps_rfp/__init__.py` | — | — | — | unknown | missing |
| `apps_rfp/__init__.py` | — | — | — | unknown | missing |
| `ADG::Module::apps_rfp/__main__.py` | — | — | — | unknown | missing |
| `apps_rfp/__main__.py` | — | violations:4589:hygiene:LOW, violations:4590:hygiene:LOW, violations:4591:hygiene:LOW (+7) | — | MV | inferred |
| `ADG::Module::apps_rfp/cert/__init__.py` | — | — | — | unknown | missing |

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
| `ADG::Module::apps_rfp/reasoning/RfpOrchestrator.py` | `apps_rfp/reasoning/RfpOrchestrator.py` | 88 |
| `ADG::Module::apps_rfp/__main__.py` | `apps_rfp/__main__.py` | 82 |
| `ADG::Module::apps_rfp/engines/proposal_assembly_engine.py` | `apps_rfp/engines/proposal_assembly_engine.py` | 75 |
| `ADG::Module::apps_rfp/config/agent_spec_config.py` | `apps_rfp/config/agent_spec_config.py` | 73 |
| `ADG::Module::apps_rfp/reasoning/enterprise_orchestrator.py` | `apps_rfp/reasoning/enterprise_orchestrator.py` | 32 |
| `ADG::Module::apps_rfp/integrations/spine_handoff.py` | `apps_rfp/integrations/spine_handoff.py` | 18 |
| `ADG::Module::apps_rfp/runtime/profile_builder.py` | `apps_rfp/runtime/profile_builder.py` | 16 |
| `ADG::Module::apps_rfp/reasoning/RequirementAnalysisAgent.py` | `apps_rfp/reasoning/RequirementAnalysisAgent.py` | 16 |
| `ADG::Module::apps_rfp/reasoning/ComplianceMappingAgent.py` | `apps_rfp/reasoning/ComplianceMappingAgent.py` | 15 |
| `ADG::Module::apps_rfp/engines/proposal_retrieval_engine.py` | `apps_rfp/engines/proposal_retrieval_engine.py` | 15 |
| `ADG::Module::apps_rfp/engines/base_rfp_engine.py` | `apps_rfp/engines/base_rfp_engine.py` | 15 |
| `ADG::Module::apps_rfp/services/requirement_parser_service.py` | `apps_rfp/services/requirement_parser_service.py` | 14 |
| `ADG::Module::apps_rfp/reasoning/section_orchestrator.py` | `apps_rfp/reasoning/section_orchestrator.py` | 14 |
| `ADG::Module::apps_rfp/integrations/u0_intake_adapter.py` | `apps_rfp/integrations/u0_intake_adapter.py` | 14 |
| `ADG::Module::apps_rfp/engines/rfp_ingestion_engine.py` | `apps_rfp/engines/rfp_ingestion_engine.py` | 13 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **18**

- `apps_rfp/engines/base_rfp_engine.py`
- `apps_rfp/engines/hop_proposal_assembly_engine.py`
- `apps_rfp/engines/hop_proposal_retrieval_engine.py`
- `apps_rfp/engines/hop_rfp_ingestion_engine.py`
- `apps_rfp/engines/judges/__init__.py`
- `apps_rfp/engines/judges/win_theme_alignment_judge.py`
- `apps_rfp/engines/proposal_assembly_engine.py`
- `apps_rfp/engines/proposal_retrieval_engine.py`
- `apps_rfp/engines/rfp_ingestion_engine.py`
- `apps_rfp/reasoning/ComplianceMappingAgent.py`
- `apps_rfp/reasoning/RequirementAnalysisAgent.py`
- `apps_rfp/reasoning/RfpHopOrchestrator.py`
- `apps_rfp/reasoning/RfpOrchestrator.py`
- `apps_rfp/reasoning/__init__.py`
- `apps_rfp/reasoning/compliance_validator.py`
- `apps_rfp/reasoning/enterprise_orchestrator.py`
- `apps_rfp/reasoning/requirement_decomposition_agent.py`
- `apps_rfp/reasoning/section_orchestrator.py`

## mv_hotspot_centrality (top 10 within app)

Rows: 10
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3570, 'ADG::Module::apps_rfp/__init__.py', 'L_APP', 'apps_rfp/__init__.py', 0, 2, 2, 0.0, 0.0, 3570, 'ADG::Module::apps_rfp/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '889cb0da36563f06543f83e2449719626ca03562')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3571, 'ADG::Module::apps_rfp/__main__.py', 'L_APP', 'apps_rfp/__main__.py', 0, 82, 82, 0.0, 0.0, 3571, 'ADG::Module::apps_rfp/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '571d6796d1b255f3880635d184143c5d5482d467')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3572, 'ADG::Module::apps_rfp/cert/__init__.py', 'L_APP', 'apps_rfp/cert/__init__.py', 0, 3, 3, 0.0, 0.0, 3572, 'ADG::Module::apps_rfp/cert/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/cert/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '6f80c8ba714b0541f4b84cf3c69370573d596ffe')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3573, 'ADG::Module::apps_rfp/cert/fec_producer.py', 'L_APP', 'apps_rfp/cert/fec_producer.py', 0, 4, 4, 0.0, 0.0, 3573, 'ADG::Module::apps_rfp/cert/fec_producer.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/cert/fec_producer.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '471ba1714be8b3173114e80c9908658091dcb201')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3574, 'ADG::Module::apps_rfp/config/__init__.py', 'L_APP', 'apps_rfp/config/__init__.py', 0, 1, 1, 0.0, 0.0, 3574, 'ADG::Module::apps_rfp/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fc59eec49d4caba3437186fda93b32d705dbd740')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3575, 'ADG::Module::apps_rfp/config/agent_spec_config.py', 'L_APP', 'apps_rfp/config/agent_spec_config.py', 0, 73, 73, 0.0, 0.0, 3575, 'ADG::Module::apps_rfp/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8bd9480b940998bccaadaf9e2102acdad93a6229')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3576, 'ADG::Module::apps_rfp/config/hop_pipeline.py', 'L_APP', 'apps_rfp/config/hop_pipeline.py', 0, 3, 3, 0.0, 0.0, 3576, 'ADG::Module::apps_rfp/config/hop_pipeline.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/hop_pipeline.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '9db9b785ce96e8c856df16976b4003384b6b63e8')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3577, 'ADG::Module::apps_rfp/config/knowledge_base.py', 'L_APP', 'apps_rfp/config/knowledge_base.py', 0, 12, 12, 0.0, 0.0, 3577, 'ADG::Module::apps_rfp/config/knowledge_base.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/knowledge_base.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b9fa25e583cace8dee42e9994e7f4326179a34d5')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3578, 'ADG::Module::apps_rfp/config/reasoning_toggles_config.py', 'L_APP', 'apps_rfp/config/reasoning_toggles_config.py', 0, 2, 2, 0.0, 0.0, 3578, 'ADG::Module::apps_rfp/config/reasoning_toggles_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/reasoning_toggles_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '790fcfab046a1c375d181e97c38c796b950b9c6f')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3579, 'ADG::Module::apps_rfp/engines/base_rfp_engine.py', 'L_APP', 'apps_rfp/engines/base_rfp_engine.py', 0, 15, 15, 0.0, 0.0, 3579, 'ADG::Module::apps_rfp/engines/base_rfp_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/engines/base_rfp_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'e8d996d3925d37e768aad3113d4692abddc4f2ae')

## mv_dependency_cone_risk (top 10 within app)

Rows: 10
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3570, 'ADG::Module::apps_rfp/__init__.py', 'L_APP', 'apps_rfp/__init__.py', 0, 0, 0, 0, 0.0, 3570, 'ADG::Module::apps_rfp/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '889cb0da36563f06543f83e2449719626ca03562')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3571, 'ADG::Module::apps_rfp/__main__.py', 'L_APP', 'apps_rfp/__main__.py', 0, 0, 0, 0, 0.0, 3571, 'ADG::Module::apps_rfp/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '571d6796d1b255f3880635d184143c5d5482d467')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3572, 'ADG::Module::apps_rfp/cert/__init__.py', 'L_APP', 'apps_rfp/cert/__init__.py', 0, 0, 0, 0, 0.0, 3572, 'ADG::Module::apps_rfp/cert/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/cert/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '6f80c8ba714b0541f4b84cf3c69370573d596ffe')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3573, 'ADG::Module::apps_rfp/cert/fec_producer.py', 'L_APP', 'apps_rfp/cert/fec_producer.py', 0, 0, 0, 0, 0.0, 3573, 'ADG::Module::apps_rfp/cert/fec_producer.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/cert/fec_producer.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '471ba1714be8b3173114e80c9908658091dcb201')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3574, 'ADG::Module::apps_rfp/config/__init__.py', 'L_APP', 'apps_rfp/config/__init__.py', 0, 0, 0, 0, 0.0, 3574, 'ADG::Module::apps_rfp/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fc59eec49d4caba3437186fda93b32d705dbd740')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3575, 'ADG::Module::apps_rfp/config/agent_spec_config.py', 'L_APP', 'apps_rfp/config/agent_spec_config.py', 0, 0, 0, 0, 0.0, 3575, 'ADG::Module::apps_rfp/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8bd9480b940998bccaadaf9e2102acdad93a6229')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3576, 'ADG::Module::apps_rfp/config/hop_pipeline.py', 'L_APP', 'apps_rfp/config/hop_pipeline.py', 0, 0, 0, 0, 0.0, 3576, 'ADG::Module::apps_rfp/config/hop_pipeline.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/hop_pipeline.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '9db9b785ce96e8c856df16976b4003384b6b63e8')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3577, 'ADG::Module::apps_rfp/config/knowledge_base.py', 'L_APP', 'apps_rfp/config/knowledge_base.py', 0, 0, 0, 0, 0.0, 3577, 'ADG::Module::apps_rfp/config/knowledge_base.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/knowledge_base.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b9fa25e583cace8dee42e9994e7f4326179a34d5')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3578, 'ADG::Module::apps_rfp/config/reasoning_toggles_config.py', 'L_APP', 'apps_rfp/config/reasoning_toggles_config.py', 0, 0, 0, 0, 0.0, 3578, 'ADG::Module::apps_rfp/config/reasoning_toggles_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/config/reasoning_toggles_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '790fcfab046a1c375d181e97c38c796b950b9c6f')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3579, 'ADG::Module::apps_rfp/engines/base_rfp_engine.py', 'L_APP', 'apps_rfp/engines/base_rfp_engine.py', 0, 0, 0, 0, 0.0, 3579, 'ADG::Module::apps_rfp/engines/base_rfp_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_rfp/engines/base_rfp_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'e8d996d3925d37e768aad3113d4692abddc4f2ae')

## mv_chokepoint_bridges

_view not present in this snapshot_

## v_p0_apps_direct_infra (P0 violation — apps directly importing infra)

Rows: 1
- ('__error__', 'no such column: source_file')

## SC/AP Violations (top 30 by severity)

Rows: 28

| Severity | Class | File | Line | Category |
|---|---|---|---:|---|
| LOW | hygiene | `apps_rfp/__main__.py` | 184 | antipattern |
| LOW | hygiene | `apps_rfp/__main__.py` | 264 | antipattern |
| LOW | hygiene | `apps_rfp/__main__.py` | 308 | antipattern |
| LOW | hygiene | `apps_rfp/__main__.py` | 339 | antipattern |
| LOW | hygiene | `apps_rfp/__main__.py` | 370 | antipattern |
| LOW | hygiene | `apps_rfp/__main__.py` | 184 | antipattern |
| LOW | hygiene | `apps_rfp/__main__.py` | 370 | antipattern |
| LOW | hygiene | `apps_rfp/__main__.py` | 264 | antipattern |
| LOW | hygiene | `apps_rfp/__main__.py` | 358 | antipattern |
| LOW | hygiene | `apps_rfp/__main__.py` | 308 | antipattern |
| LOW | hygiene | `apps_rfp/cert/fec_producer.py` | 62 | antipattern |
| LOW | hygiene | `apps_rfp/cert/fec_producer.py` | 67 | antipattern |
| LOW | hygiene | `apps_rfp/config/agent_spec_config.py` | 361 | antipattern |
| LOW | hygiene | `apps_rfp/config/agent_spec_config.py` | 366 | antipattern |
| LOW | hygiene | `apps_rfp/config/agent_spec_config.py` | 363 | antipattern |
| LOW | hygiene | `apps_rfp/engines/base_rfp_engine.py` | 66 | antipattern |
| LOW | hygiene | `apps_rfp/engines/base_rfp_engine.py` | 74 | antipattern |
| LOW | hygiene | `apps_rfp/engines/base_rfp_engine.py` | 59 | antipattern |
| LOW | hygiene | `apps_rfp/engines/base_rfp_engine.py` | 75 | antipattern |
| LOW | hygiene | `apps_rfp/engines/rfp_ingestion_engine.py` | 356 | antipattern |
| LOW | hygiene | `apps_rfp/reasoning/RfpHopOrchestrator.py` | 30 | antipattern |
| LOW | hygiene | `apps_rfp/reasoning/RfpOrchestrator.py` | 228 | antipattern |
| LOW | hygiene | `apps_rfp/runtime/bindings/exit_binding.py` | 75 | antipattern |
| LOW | hygiene | `apps_rfp/runtime/bindings/exit_binding.py` | 77 | antipattern |
| LOW | hygiene | `apps_rfp/runtime/bindings/exit_binding.py` | 79 | antipattern |
| LOW | hygiene | `apps_rfp/scripts/run_rfp.py` | 75 | antipattern |
| LOW | hygiene | `apps_rfp/services/__init__.py` | 32 | antipattern |
| LOW | hygiene | `apps_rfp/tools/rfp_dry_run_tool.py` | 32 | antipattern |

See [adg_action_dispatch_playbook.md](../../docs/reports/cursor/adg_action_dispatch_playbook.md) and latest `artifacts/adg/adg_action_queue_*.json` for FIX-first triage.

## Recommendations (derived)

- **Broadest reachers (most likely to consolidate):**
  - `apps_rfp/reasoning/RfpOrchestrator.py` (fan-out 88)
  - `apps_rfp/__main__.py` (fan-out 82)
  - `apps_rfp/engines/proposal_assembly_engine.py` (fan-out 75)
  - `apps_rfp/config/agent_spec_config.py` (fan-out 73)
  - `apps_rfp/reasoning/enterprise_orchestrator.py` (fan-out 32)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

