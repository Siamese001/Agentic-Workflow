# `apps_rfp` — ADG Hotspot Report (W0.1)

Generated: `2026-05-10T21:28:56Z`
Snapshot: `adg_indexed_05102026_1319.sqlite`
Severity (Phase B): **MEDIUM-LOW (defensible multi-agent)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05102026_1319.sqlite

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
| `ADG::Module::apps_rfp/reasoning/RfpOrchestrator.py` | `apps_rfp/reasoning/RfpOrchestrator.py` | 88 |
| `ADG::Module::apps_rfp/__main__.py` | `apps_rfp/__main__.py` | 80 |
| `ADG::Module::apps_rfp/engines/proposal_assembly_engine.py` | `apps_rfp/engines/proposal_assembly_engine.py` | 75 |
| `ADG::Module::apps_rfp/config/agent_spec_config.py` | `apps_rfp/config/agent_spec_config.py` | 73 |
| `ADG::Module::apps_rfp/reasoning/enterprise_orchestrator.py` | `apps_rfp/reasoning/enterprise_orchestrator.py` | 32 |
| `ADG::Module::apps_rfp/integrations/spine_handoff.py` | `apps_rfp/integrations/spine_handoff.py` | 18 |
| `ADG::Module::apps_rfp/reasoning/RequirementAnalysisAgent.py` | `apps_rfp/reasoning/RequirementAnalysisAgent.py` | 16 |
| `ADG::Module::apps_rfp/reasoning/ComplianceMappingAgent.py` | `apps_rfp/reasoning/ComplianceMappingAgent.py` | 15 |
| `ADG::Module::apps_rfp/engines/proposal_retrieval_engine.py` | `apps_rfp/engines/proposal_retrieval_engine.py` | 15 |
| `ADG::Module::apps_rfp/engines/base_rfp_engine.py` | `apps_rfp/engines/base_rfp_engine.py` | 15 |
| `ADG::Module::apps_rfp/services/requirement_parser_service.py` | `apps_rfp/services/requirement_parser_service.py` | 14 |
| `ADG::Module::apps_rfp/reasoning/section_orchestrator.py` | `apps_rfp/reasoning/section_orchestrator.py` | 14 |
| `ADG::Module::apps_rfp/engines/rfp_ingestion_engine.py` | `apps_rfp/engines/rfp_ingestion_engine.py` | 13 |
| `ADG::Module::apps_rfp/services/compliance_checker_service.py` | `apps_rfp/services/compliance_checker_service.py` | 12 |
| `ADG::Module::apps_rfp/reasoning/compliance_validator.py` | `apps_rfp/reasoning/compliance_validator.py` | 12 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **19**

- `apps_rfp/engines/__init__.py`
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
  - `apps_rfp/reasoning/RfpOrchestrator.py` (fan-out 88)
  - `apps_rfp/__main__.py` (fan-out 80)
  - `apps_rfp/engines/proposal_assembly_engine.py` (fan-out 75)
  - `apps_rfp/config/agent_spec_config.py` (fan-out 73)
  - `apps_rfp/reasoning/enterprise_orchestrator.py` (fan-out 32)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

