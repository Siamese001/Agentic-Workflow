# `apps_underwriting_ai` — ADG Hotspot Report (W0.1)

Generated: `2026-05-25T04:07:58Z`
Snapshot: `adg_indexed_05242026_2005.sqlite`
Severity (Phase B): **LOW (reference impl)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05242026_2005.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 78 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_underwriting_ai/runtime/bindings/__init__.py` | `apps_underwriting_ai/runtime/bindings/__init__.py` | 28 |
| `ADG::Module::apps_underwriting_ai/engines/decision_packet_assembler.py` | `apps_underwriting_ai/engines/decision_packet_assembler.py` | 23 |
| `ADG::Module::apps_underwriting_ai/__main__.py` | `apps_underwriting_ai/__main__.py` | 21 |
| `ADG::Module::apps_underwriting_ai/services/__init__.py` | `apps_underwriting_ai/services/__init__.py` | 18 |
| `ADG::Module::apps_underwriting_ai/runtime/profile_builder.py` | `apps_underwriting_ai/runtime/profile_builder.py` | 15 |
| `ADG::Module::apps_underwriting_ai/runtime/bindings/c0_binding.py` | `apps_underwriting_ai/runtime/bindings/c0_binding.py` | 13 |
| `ADG::Module::apps_underwriting_ai/validators/decision_packet_validator.py` | `apps_underwriting_ai/validators/decision_packet_validator.py` | 11 |
| `ADG::Module::apps_underwriting_ai/tools/run_underwriting.py` | `apps_underwriting_ai/tools/run_underwriting.py` | 11 |
| `ADG::Module::apps_underwriting_ai/parsers/__init__.py` | `apps_underwriting_ai/parsers/__init__.py` | 11 |
| `ADG::Module::apps_underwriting_ai/engines/parsers/__init__.py` | `apps_underwriting_ai/engines/parsers/__init__.py` | 11 |
| `ADG::Module::apps_underwriting_ai/tools/audit_spine_manifest.py` | `apps_underwriting_ai/tools/audit_spine_manifest.py` | 10 |
| `ADG::Module::apps_underwriting_ai/services/rationale_agreement_tracker.py` | `apps_underwriting_ai/services/rationale_agreement_tracker.py` | 10 |
| `ADG::Module::apps_underwriting_ai/integrations/underwriting_llm_firewall.py` | `apps_underwriting_ai/integrations/underwriting_llm_firewall.py` | 10 |
| `ADG::Module::apps_underwriting_ai/engines/risk_scorer.py` | `apps_underwriting_ai/engines/risk_scorer.py` | 9 |
| `ADG::Module::apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 9 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **24**

- `apps_underwriting_ai/engines/__init__.py`
- `apps_underwriting_ai/engines/_legacy/underwriting_engine.py`
- `apps_underwriting_ai/engines/base_underwriting_engine.py`
- `apps_underwriting_ai/engines/decision_packet_assembler.py`
- `apps_underwriting_ai/engines/document_reconciliation_engine.py`
- `apps_underwriting_ai/engines/evidence_register_engine.py`
- `apps_underwriting_ai/engines/feature_derivation_engine.py`
- `apps_underwriting_ai/engines/hop_assemble_decision_engine.py`
- `apps_underwriting_ai/engines/hop_collect_evidence_engine.py`
- `apps_underwriting_ai/engines/hop_derive_features_engine.py`
- `apps_underwriting_ai/engines/hop_initialize_evidence_engine.py`
- `apps_underwriting_ai/engines/hop_reconcile_documents_engine.py`
- `apps_underwriting_ai/engines/judges/__init__.py`
- `apps_underwriting_ai/engines/judges/rationale_quality_judge.py`
- `apps_underwriting_ai/engines/parsers/__init__.py`
- `apps_underwriting_ai/engines/parsers/csv_document_parser.py`
- `apps_underwriting_ai/engines/parsers/document_parser.py`
- `apps_underwriting_ai/engines/parsers/json_document_parser.py`
- `apps_underwriting_ai/engines/parsers/pdf_text_parser.py`
- `apps_underwriting_ai/engines/risk_scorer.py`
- `apps_underwriting_ai/engines/rubric_output_mapper.py`
- `apps_underwriting_ai/engines/underwriting_engine.py`
- `apps_underwriting_ai/reasoning/UnderwritingHopOrchestrator.py`
- `apps_underwriting_ai/reasoning/__init__.py`

## mv_hotspot_centrality (top 10 within app)

Rows: 10
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4023, 'ADG::Module::apps_underwriting_ai/__init__.py', 'L_APP', 'apps_underwriting_ai/__init__.py', 0, 6, 6, 0.0, 0.0, 4023, 'ADG::Module::apps_underwriting_ai/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8a6206d7bf1383784c51dcd50b6c390c88f4aacf')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4024, 'ADG::Module::apps_underwriting_ai/__main__.py', 'L_APP', 'apps_underwriting_ai/__main__.py', 0, 21, 21, 0.0, 0.0, 4024, 'ADG::Module::apps_underwriting_ai/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '974b1145e898fe056c3b7532445eb4d433094238')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4025, 'ADG::Module::apps_underwriting_ai/airlocks/_otel_spans.py', 'L_APP', 'apps_underwriting_ai/airlocks/_otel_spans.py', 0, 5, 5, 0.0, 0.0, 4025, 'ADG::Module::apps_underwriting_ai/airlocks/_otel_spans.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/airlocks/_otel_spans.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'abae24299ded132eb3c4476b948c4fe3b62cae98')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4026, 'ADG::Module::apps_underwriting_ai/cert/__init__.py', 'L_APP', 'apps_underwriting_ai/cert/__init__.py', 0, 3, 3, 0.0, 0.0, 4026, 'ADG::Module::apps_underwriting_ai/cert/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/cert/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5cc832534776cb5ae283fe52a50261be54f79834')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4027, 'ADG::Module::apps_underwriting_ai/cert/fec_producer.py', 'L_APP', 'apps_underwriting_ai/cert/fec_producer.py', 0, 7, 7, 0.0, 0.0, 4027, 'ADG::Module::apps_underwriting_ai/cert/fec_producer.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/cert/fec_producer.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '379a0861ea75a04445314d6b6acbb277162b9527')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4028, 'ADG::Module::apps_underwriting_ai/config/__init__.py', 'L_APP', 'apps_underwriting_ai/config/__init__.py', 0, 1, 1, 0.0, 0.0, 4028, 'ADG::Module::apps_underwriting_ai/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b9e593aaa6b63803986af29f66cfd506f5b30051')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4029, 'ADG::Module::apps_underwriting_ai/config/agent_spec_config.py', 'L_APP', 'apps_underwriting_ai/config/agent_spec_config.py', 0, 8, 8, 0.0, 0.0, 4029, 'ADG::Module::apps_underwriting_ai/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c16d130c624164336b5cefd1d0d13ff5bce7f9cb')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4030, 'ADG::Module::apps_underwriting_ai/config/hop_pipeline.py', 'L_APP', 'apps_underwriting_ai/config/hop_pipeline.py', 0, 3, 3, 0.0, 0.0, 4030, 'ADG::Module::apps_underwriting_ai/config/hop_pipeline.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/hop_pipeline.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fa0557b019f204551ef9b459b0ff2cbeb53fbeb8')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4031, 'ADG::Module::apps_underwriting_ai/engines/__init__.py', 'L_APP', 'apps_underwriting_ai/engines/__init__.py', 0, 3, 3, 0.0, 0.0, 4031, 'ADG::Module::apps_underwriting_ai/engines/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '28d5939fbda5b77a2477997e9dcf195aee416e83')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4032, 'ADG::Module::apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 'L_APP', 'apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 0, 8, 8, 0.0, 0.0, 4032, 'ADG::Module::apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '0047fc621fa07448a9993e4b3d3fa036f9670307')

## mv_dependency_cone_risk (top 10 within app)

Rows: 10
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4023, 'ADG::Module::apps_underwriting_ai/__init__.py', 'L_APP', 'apps_underwriting_ai/__init__.py', 0, 0, 0, 0, 0.0, 4023, 'ADG::Module::apps_underwriting_ai/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8a6206d7bf1383784c51dcd50b6c390c88f4aacf')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4024, 'ADG::Module::apps_underwriting_ai/__main__.py', 'L_APP', 'apps_underwriting_ai/__main__.py', 0, 0, 0, 0, 0.0, 4024, 'ADG::Module::apps_underwriting_ai/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '974b1145e898fe056c3b7532445eb4d433094238')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4025, 'ADG::Module::apps_underwriting_ai/airlocks/_otel_spans.py', 'L_APP', 'apps_underwriting_ai/airlocks/_otel_spans.py', 0, 0, 0, 0, 0.0, 4025, 'ADG::Module::apps_underwriting_ai/airlocks/_otel_spans.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/airlocks/_otel_spans.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'abae24299ded132eb3c4476b948c4fe3b62cae98')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4026, 'ADG::Module::apps_underwriting_ai/cert/__init__.py', 'L_APP', 'apps_underwriting_ai/cert/__init__.py', 0, 0, 0, 0, 0.0, 4026, 'ADG::Module::apps_underwriting_ai/cert/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/cert/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5cc832534776cb5ae283fe52a50261be54f79834')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4027, 'ADG::Module::apps_underwriting_ai/cert/fec_producer.py', 'L_APP', 'apps_underwriting_ai/cert/fec_producer.py', 0, 0, 0, 0, 0.0, 4027, 'ADG::Module::apps_underwriting_ai/cert/fec_producer.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/cert/fec_producer.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '379a0861ea75a04445314d6b6acbb277162b9527')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4028, 'ADG::Module::apps_underwriting_ai/config/__init__.py', 'L_APP', 'apps_underwriting_ai/config/__init__.py', 0, 0, 0, 0, 0.0, 4028, 'ADG::Module::apps_underwriting_ai/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b9e593aaa6b63803986af29f66cfd506f5b30051')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4029, 'ADG::Module::apps_underwriting_ai/config/agent_spec_config.py', 'L_APP', 'apps_underwriting_ai/config/agent_spec_config.py', 0, 0, 0, 0, 0.0, 4029, 'ADG::Module::apps_underwriting_ai/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c16d130c624164336b5cefd1d0d13ff5bce7f9cb')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4030, 'ADG::Module::apps_underwriting_ai/config/hop_pipeline.py', 'L_APP', 'apps_underwriting_ai/config/hop_pipeline.py', 0, 0, 0, 0, 0.0, 4030, 'ADG::Module::apps_underwriting_ai/config/hop_pipeline.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/hop_pipeline.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fa0557b019f204551ef9b459b0ff2cbeb53fbeb8')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4031, 'ADG::Module::apps_underwriting_ai/engines/__init__.py', 'L_APP', 'apps_underwriting_ai/engines/__init__.py', 0, 0, 0, 0, 0.0, 4031, 'ADG::Module::apps_underwriting_ai/engines/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '28d5939fbda5b77a2477997e9dcf195aee416e83')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 4032, 'ADG::Module::apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 'L_APP', 'apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 0, 0, 0, 0, 0.0, 4032, 'ADG::Module::apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '0047fc621fa07448a9993e4b3d3fa036f9670307')

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
  - `apps_underwriting_ai/runtime/bindings/__init__.py` (fan-out 28)
  - `apps_underwriting_ai/engines/decision_packet_assembler.py` (fan-out 23)
  - `apps_underwriting_ai/__main__.py` (fan-out 21)
  - `apps_underwriting_ai/services/__init__.py` (fan-out 18)
  - `apps_underwriting_ai/runtime/profile_builder.py` (fan-out 15)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

