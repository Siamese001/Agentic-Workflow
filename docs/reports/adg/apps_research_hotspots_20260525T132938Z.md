# `apps_research` — ADG Hotspot Report (W0.1)

Generated: `2026-05-25T13:29:39Z`
Snapshot: `adg_indexed_05252026_0849.sqlite`
Severity (Phase B): **LOW**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05252026_0849.sqlite

## Actionable hotspots (top 5 — deterministic linkage)

Linkage from structured sources only (`gate_results` queue file paths, P-views, `mv_debt_concentration_hotspots`, `refactor_accelerator`). `unknown` = no gate join.

| module_path | linked_gate_ids | violation_refs | impacted_tests_sample | linkage_source | linkage_confidence |
|-------------|-----------------|----------------|----------------------|----------------|-------------------|
| `ADG::Module::apps_research/__init__.py` | — | — | — | unknown | missing |
| `apps_research/__init__.py` | — | — | — | unknown | missing |
| `ADG::Module::apps_research/__main__.py` | — | — | — | unknown | missing |
| `apps_research/__main__.py` | — | violations:4484:hygiene:LOW, violations:4485:hygiene:LOW, violations:4486:hygiene:LOW (+6) | — | MV | inferred |
| `ADG::Module::apps_research/_telemetry.py` | — | — | — | unknown | missing |

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 95 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_research/reasoning/ResearchOrchestrator.py` | `apps_research/reasoning/ResearchOrchestrator.py` | 89 |
| `ADG::Module::apps_research/engines/research_assembly_engine.py` | `apps_research/engines/research_assembly_engine.py` | 77 |
| `ADG::Module::apps_research/config/agent_spec_config.py` | `apps_research/config/agent_spec_config.py` | 73 |
| `ADG::Module::apps_research/services/telemetry.py` | `apps_research/services/telemetry.py` | 65 |
| `ADG::Module::apps_research/_telemetry.py` | `apps_research/_telemetry.py` | 65 |
| `ADG::Module::apps_research/engines/company_brief_engine.py` | `apps_research/engines/company_brief_engine.py` | 39 |
| `ADG::Module::apps_research/engines/judges/__init__.py` | `apps_research/engines/judges/__init__.py` | 32 |
| `ADG::Module::apps_research/reasoning/enterprise_research_orchestrator.py` | `apps_research/reasoning/enterprise_research_orchestrator.py` | 25 |
| `ADG::Module::apps_research/integrations/research_c0_adapter.py` | `apps_research/integrations/research_c0_adapter.py` | 23 |
| `ADG::Module::apps_research/__main__.py` | `apps_research/__main__.py` | 23 |
| `ADG::Module::apps_research/runtime/profile_builder_adapter.py` | `apps_research/runtime/profile_builder_adapter.py` | 22 |
| `ADG::Module::apps_research/integrations/research_brief_uwg_writer.py` | `apps_research/integrations/research_brief_uwg_writer.py` | 21 |
| `ADG::Module::apps_research/runtime/u0/binding.py` | `apps_research/runtime/u0/binding.py` | 20 |
| `ADG::Module::apps_research/integrations/spine_handoff.py` | `apps_research/integrations/spine_handoff.py` | 18 |
| `ADG::Module::apps_research/integrations/research_l2_step_adapters.py` | `apps_research/integrations/research_l2_step_adapters.py` | 17 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **26**

- `apps_research/engines/base_research_engine.py`
- `apps_research/engines/company_brief_engine.py`
- `apps_research/engines/integration/chroma_research_store.py`
- `apps_research/engines/judges/__init__.py`
- `apps_research/engines/judges/base.py`
- `apps_research/engines/judges/briefing_injection_judge.py`
- `apps_research/engines/judges/cache_compatibility_judge.py`
- `apps_research/engines/judges/citation_quality_judge.py`
- `apps_research/engines/judges/claim_support_judge.py`
- `apps_research/engines/judges/contradiction_resolution_judge.py`
- `apps_research/engines/judges/coverage_depth_judge.py`
- `apps_research/engines/judges/downstream_relevance_judge.py`
- `apps_research/engines/judges/source_authority_judge.py`
- `apps_research/engines/query_decomposer.py`
- `apps_research/engines/research_assembly_engine.py`
- `apps_research/engines/research_retrieval_engine.py`
- `apps_research/engines/role_profile_engine.py`
- `apps_research/reasoning/InsightExtractionAgent.py`
- `apps_research/reasoning/KnowledgeSynthesisAgent.py`
- `apps_research/reasoning/ResearchHopOrchestrator.py`
- `apps_research/reasoning/ResearchOrchestrator.py`
- `apps_research/reasoning/SourceDiscoveryAgent.py`
- `apps_research/reasoning/__init__.py`
- `apps_research/reasoning/enterprise_research_orchestrator.py`
- `apps_research/reasoning/query_decomposition_agent.py`
- `apps_research/reasoning/research_multi_agent.py`

## mv_hotspot_centrality (top 10 within app)

Rows: 10
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3475, 'ADG::Module::apps_research/__init__.py', 'L_APP', 'apps_research/__init__.py', 0, 2, 2, 0.0, 0.0, 3475, 'ADG::Module::apps_research/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '07e9b5e88454a4d657b963e4426c1d48d31f45a8')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3476, 'ADG::Module::apps_research/__main__.py', 'L_APP', 'apps_research/__main__.py', 0, 23, 23, 0.0, 0.0, 3476, 'ADG::Module::apps_research/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c50a069a9ba0f9fc2a30261032beb0a4325d0b3c')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3477, 'ADG::Module::apps_research/_telemetry.py', 'L_APP', 'apps_research/_telemetry.py', 0, 65, 65, 0.0, 0.0, 3477, 'ADG::Module::apps_research/_telemetry.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/_telemetry.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5b1c6cd22edb271311c985eb6795e0e1d556ce0c')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3478, 'ADG::Module::apps_research/airlocks/__init__.py', 'L_APP', 'apps_research/airlocks/__init__.py', 0, 3, 3, 0.0, 0.0, 3478, 'ADG::Module::apps_research/airlocks/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/airlocks/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8a3fc2eff993d5c50581030166767a10d721a2db')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3479, 'ADG::Module::apps_research/airlocks/_otel_spans.py', 'L_APP', 'apps_research/airlocks/_otel_spans.py', 0, 5, 5, 0.0, 0.0, 3479, 'ADG::Module::apps_research/airlocks/_otel_spans.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/airlocks/_otel_spans.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'dbc1049e22aab1c8ec8572a61f88cf7336ed4765')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3480, 'ADG::Module::apps_research/airlocks/research_query.py', 'L_APP', 'apps_research/airlocks/research_query.py', 0, 8, 8, 0.0, 0.0, 3480, 'ADG::Module::apps_research/airlocks/research_query.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/airlocks/research_query.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '226530c86c27819c5d1c8346d4c3f55cb246a22e')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3481, 'ADG::Module::apps_research/cert/__init__.py', 'L_APP', 'apps_research/cert/__init__.py', 0, 3, 3, 0.0, 0.0, 3481, 'ADG::Module::apps_research/cert/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/cert/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5039857f259b1d4805585023201a6268cda3d625')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3482, 'ADG::Module::apps_research/cert/fec_producer.py', 'L_APP', 'apps_research/cert/fec_producer.py', 0, 4, 4, 0.0, 0.0, 3482, 'ADG::Module::apps_research/cert/fec_producer.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/cert/fec_producer.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'e54784c43f0d5c275e48193e3fcbd45f02b16b60')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3483, 'ADG::Module::apps_research/config/__init__.py', 'L_APP', 'apps_research/config/__init__.py', 0, 1, 1, 0.0, 0.0, 3483, 'ADG::Module::apps_research/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fc59eec49d4caba3437186fda93b32d705dbd740')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3484, 'ADG::Module::apps_research/config/agent_spec_config.py', 'L_APP', 'apps_research/config/agent_spec_config.py', 0, 73, 73, 0.0, 0.0, 3484, 'ADG::Module::apps_research/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '60a1acce5145f8fe28bc9bb6bba0b51458606264')

## mv_dependency_cone_risk (top 10 within app)

Rows: 10
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3475, 'ADG::Module::apps_research/__init__.py', 'L_APP', 'apps_research/__init__.py', 0, 0, 0, 0, 0.0, 3475, 'ADG::Module::apps_research/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '07e9b5e88454a4d657b963e4426c1d48d31f45a8')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3476, 'ADG::Module::apps_research/__main__.py', 'L_APP', 'apps_research/__main__.py', 0, 0, 0, 0, 0.0, 3476, 'ADG::Module::apps_research/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c50a069a9ba0f9fc2a30261032beb0a4325d0b3c')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3477, 'ADG::Module::apps_research/_telemetry.py', 'L_APP', 'apps_research/_telemetry.py', 0, 0, 0, 0, 0.0, 3477, 'ADG::Module::apps_research/_telemetry.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/_telemetry.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5b1c6cd22edb271311c985eb6795e0e1d556ce0c')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3478, 'ADG::Module::apps_research/airlocks/__init__.py', 'L_APP', 'apps_research/airlocks/__init__.py', 0, 0, 0, 0, 0.0, 3478, 'ADG::Module::apps_research/airlocks/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/airlocks/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8a3fc2eff993d5c50581030166767a10d721a2db')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3479, 'ADG::Module::apps_research/airlocks/_otel_spans.py', 'L_APP', 'apps_research/airlocks/_otel_spans.py', 0, 0, 0, 0, 0.0, 3479, 'ADG::Module::apps_research/airlocks/_otel_spans.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/airlocks/_otel_spans.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'dbc1049e22aab1c8ec8572a61f88cf7336ed4765')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3480, 'ADG::Module::apps_research/airlocks/research_query.py', 'L_APP', 'apps_research/airlocks/research_query.py', 0, 0, 0, 0, 0.0, 3480, 'ADG::Module::apps_research/airlocks/research_query.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/airlocks/research_query.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '226530c86c27819c5d1c8346d4c3f55cb246a22e')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3481, 'ADG::Module::apps_research/cert/__init__.py', 'L_APP', 'apps_research/cert/__init__.py', 0, 0, 0, 0, 0.0, 3481, 'ADG::Module::apps_research/cert/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/cert/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5039857f259b1d4805585023201a6268cda3d625')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3482, 'ADG::Module::apps_research/cert/fec_producer.py', 'L_APP', 'apps_research/cert/fec_producer.py', 0, 0, 0, 0, 0.0, 3482, 'ADG::Module::apps_research/cert/fec_producer.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/cert/fec_producer.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'e54784c43f0d5c275e48193e3fcbd45f02b16b60')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3483, 'ADG::Module::apps_research/config/__init__.py', 'L_APP', 'apps_research/config/__init__.py', 0, 0, 0, 0, 0.0, 3483, 'ADG::Module::apps_research/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fc59eec49d4caba3437186fda93b32d705dbd740')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3484, 'ADG::Module::apps_research/config/agent_spec_config.py', 'L_APP', 'apps_research/config/agent_spec_config.py', 0, 0, 0, 0, 0.0, 3484, 'ADG::Module::apps_research/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_research/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '60a1acce5145f8fe28bc9bb6bba0b51458606264')

## mv_chokepoint_bridges

_view not present in this snapshot_

## v_p0_apps_direct_infra (P0 violation — apps directly importing infra)

Rows: 1
- ('__error__', 'no such column: source_file')

## SC/AP Violations (top 30 by severity)

Rows: 30

| Severity | Class | File | Line | Category |
|---|---|---|---:|---|
| CRITICAL | hygiene | `apps_research/integrations/execution_adapter.py` | 184 | violates |
| LOW | hygiene | `apps_research/__main__.py` | 221 | antipattern |
| LOW | hygiene | `apps_research/__main__.py` | 238 | antipattern |
| LOW | hygiene | `apps_research/__main__.py` | 278 | antipattern |
| LOW | hygiene | `apps_research/__main__.py` | 317 | antipattern |
| LOW | hygiene | `apps_research/__main__.py` | 317 | antipattern |
| LOW | hygiene | `apps_research/__main__.py` | 17 | antipattern |
| LOW | hygiene | `apps_research/__main__.py` | 238 | antipattern |
| LOW | hygiene | `apps_research/__main__.py` | 305 | antipattern |
| LOW | hygiene | `apps_research/__main__.py` | 278 | antipattern |
| LOW | hygiene | `apps_research/cert/fec_producer.py` | 62 | antipattern |
| LOW | hygiene | `apps_research/cert/fec_producer.py` | 67 | antipattern |
| LOW | hygiene | `apps_research/config/agent_spec_config.py` | 318 | antipattern |
| LOW | hygiene | `apps_research/config/agent_spec_config.py` | 323 | antipattern |
| LOW | hygiene | `apps_research/config/agent_spec_config.py` | 320 | antipattern |
| LOW | hygiene | `apps_research/engines/base_research_engine.py` | 75 | antipattern |
| LOW | hygiene | `apps_research/engines/base_research_engine.py` | 83 | antipattern |
| LOW | hygiene | `apps_research/engines/base_research_engine.py` | 68 | antipattern |
| LOW | hygiene | `apps_research/engines/base_research_engine.py` | 84 | antipattern |
| LOW | hygiene | `apps_research/engines/company_brief_engine.py` | 169 | antipattern |
| LOW | hygiene | `apps_research/engines/company_brief_engine.py` | 552 | antipattern |
| LOW | hygiene | `apps_research/engines/company_brief_engine.py` | 557 | antipattern |
| LOW | hygiene | `apps_research/engines/company_brief_engine.py` | 739 | antipattern |
| LOW | hygiene | `apps_research/engines/company_brief_engine.py` | 784 | antipattern |
| LOW | hygiene | `apps_research/engines/company_brief_engine.py` | 911 | antipattern |
| LOW | hygiene | `apps_research/engines/company_brief_engine.py` | 646 | antipattern |
| LOW | hygiene | `apps_research/engines/company_brief_engine.py` | 66 | antipattern |
| LOW | hygiene | `apps_research/engines/company_brief_engine.py` | 407 | antipattern |
| LOW | hygiene | `apps_research/engines/company_brief_engine.py` | 525 | antipattern |
| LOW | hygiene | `apps_research/engines/company_brief_engine.py` | 539 | antipattern |

See [adg_action_dispatch_playbook.md](../../docs/reports/cursor/adg_action_dispatch_playbook.md) and latest `artifacts/adg/adg_action_queue_*.json` for FIX-first triage.

## Recommendations (derived)

- **Broadest reachers (most likely to consolidate):**
  - `apps_research/reasoning/ResearchOrchestrator.py` (fan-out 89)
  - `apps_research/engines/research_assembly_engine.py` (fan-out 77)
  - `apps_research/config/agent_spec_config.py` (fan-out 73)
  - `apps_research/services/telemetry.py` (fan-out 65)
  - `apps_research/_telemetry.py` (fan-out 65)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

