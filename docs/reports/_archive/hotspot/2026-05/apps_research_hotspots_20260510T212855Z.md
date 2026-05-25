# `apps_research` — ADG Hotspot Report (W0.1)

Generated: `2026-05-10T21:28:56Z`
Snapshot: `adg_indexed_05102026_1319.sqlite`
Severity (Phase B): **LOW**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05102026_1319.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 88 |

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
| `ADG::Module::apps_research/engines/company_brief_engine.py` | `apps_research/engines/company_brief_engine.py` | 38 |
| `ADG::Module::apps_research/reasoning/enterprise_research_orchestrator.py` | `apps_research/reasoning/enterprise_research_orchestrator.py` | 25 |
| `ADG::Module::apps_research/integrations/research_c0_adapter.py` | `apps_research/integrations/research_c0_adapter.py` | 23 |
| `ADG::Module::apps_research/__main__.py` | `apps_research/__main__.py` | 22 |
| `ADG::Module::apps_research/integrations/research_brief_uwg_writer.py` | `apps_research/integrations/research_brief_uwg_writer.py` | 21 |
| `ADG::Module::apps_research/integrations/spine_handoff.py` | `apps_research/integrations/spine_handoff.py` | 18 |
| `ADG::Module::apps_research/integrations/research_l2_step_adapters.py` | `apps_research/integrations/research_l2_step_adapters.py` | 17 |
| `ADG::Module::apps_research/integrations/execution_adapter.py` | `apps_research/integrations/execution_adapter.py` | 17 |
| `ADG::Module::apps_research/reasoning/KnowledgeSynthesisAgent.py` | `apps_research/reasoning/KnowledgeSynthesisAgent.py` | 16 |
| `ADG::Module::apps_research/integrations/governed_research_run.py` | `apps_research/integrations/governed_research_run.py` | 16 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **19**

- `apps_research/engines/__init__.py`
- `apps_research/engines/base_research_engine.py`
- `apps_research/engines/company_brief_engine.py`
- `apps_research/engines/judges/__init__.py`
- `apps_research/engines/judges/citation_quality_judge.py`
- `apps_research/engines/judges/coverage_depth_judge.py`
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
  - `apps_research/reasoning/ResearchOrchestrator.py` (fan-out 89)
  - `apps_research/engines/research_assembly_engine.py` (fan-out 77)
  - `apps_research/config/agent_spec_config.py` (fan-out 73)
  - `apps_research/services/telemetry.py` (fan-out 65)
  - `apps_research/_telemetry.py` (fan-out 65)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

