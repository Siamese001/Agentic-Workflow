# `apps_underwriting_ai` — ADG Hotspot Report (W0.1)

Generated: `2026-05-25T13:29:39Z`
Snapshot: `adg_indexed_05252026_0849.sqlite`
Severity (Phase B): **LOW (reference impl)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05252026_0849.sqlite

## Actionable hotspots (top 5 — deterministic linkage)

Linkage from structured sources only (`gate_results` queue file paths, P-views, `mv_debt_concentration_hotspots`, `refactor_accelerator`). `unknown` = no gate join.

| module_path | linked_gate_ids | violation_refs | impacted_tests_sample | linkage_source | linkage_confidence |
|-------------|-----------------|----------------|----------------------|----------------|-------------------|
| `ADG::Module::apps_underwriting_ai/__init__.py` | — | — | — | unknown | missing |
| `apps_underwriting_ai/__init__.py` | — | — | — | unknown | missing |
| `ADG::Module::apps_underwriting_ai/__main__.py` | — | — | — | unknown | missing |
| `apps_underwriting_ai/__main__.py` | — | violations:6254:hygiene:LOW, violations:6255:hygiene:LOW, violations:6256:hygiene:LOW (+3) | — | MV | inferred |
| `ADG::Module::apps_underwriting_ai/airlocks/_otel_spans.py` | — | — | — | unknown | missing |

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
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4351, 'ADG::Module::apps_underwriting_ai/__init__.py', 'L_APP', 'apps_underwriting_ai/__init__.py', 0, 6, 6, 0.0, 0.0, 4351, 'ADG::Module::apps_underwriting_ai/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8a6206d7bf1383784c51dcd50b6c390c88f4aacf')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4352, 'ADG::Module::apps_underwriting_ai/__main__.py', 'L_APP', 'apps_underwriting_ai/__main__.py', 0, 21, 21, 0.0, 0.0, 4352, 'ADG::Module::apps_underwriting_ai/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '974b1145e898fe056c3b7532445eb4d433094238')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4353, 'ADG::Module::apps_underwriting_ai/airlocks/_otel_spans.py', 'L_APP', 'apps_underwriting_ai/airlocks/_otel_spans.py', 0, 5, 5, 0.0, 0.0, 4353, 'ADG::Module::apps_underwriting_ai/airlocks/_otel_spans.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/airlocks/_otel_spans.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'abae24299ded132eb3c4476b948c4fe3b62cae98')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4354, 'ADG::Module::apps_underwriting_ai/cert/__init__.py', 'L_APP', 'apps_underwriting_ai/cert/__init__.py', 0, 3, 3, 0.0, 0.0, 4354, 'ADG::Module::apps_underwriting_ai/cert/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/cert/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5cc832534776cb5ae283fe52a50261be54f79834')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4355, 'ADG::Module::apps_underwriting_ai/cert/fec_producer.py', 'L_APP', 'apps_underwriting_ai/cert/fec_producer.py', 0, 7, 7, 0.0, 0.0, 4355, 'ADG::Module::apps_underwriting_ai/cert/fec_producer.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/cert/fec_producer.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '379a0861ea75a04445314d6b6acbb277162b9527')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4356, 'ADG::Module::apps_underwriting_ai/config/__init__.py', 'L_APP', 'apps_underwriting_ai/config/__init__.py', 0, 1, 1, 0.0, 0.0, 4356, 'ADG::Module::apps_underwriting_ai/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b9e593aaa6b63803986af29f66cfd506f5b30051')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4357, 'ADG::Module::apps_underwriting_ai/config/agent_spec_config.py', 'L_APP', 'apps_underwriting_ai/config/agent_spec_config.py', 0, 8, 8, 0.0, 0.0, 4357, 'ADG::Module::apps_underwriting_ai/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c16d130c624164336b5cefd1d0d13ff5bce7f9cb')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4358, 'ADG::Module::apps_underwriting_ai/config/hop_pipeline.py', 'L_APP', 'apps_underwriting_ai/config/hop_pipeline.py', 0, 3, 3, 0.0, 0.0, 4358, 'ADG::Module::apps_underwriting_ai/config/hop_pipeline.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/hop_pipeline.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fa0557b019f204551ef9b459b0ff2cbeb53fbeb8')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4359, 'ADG::Module::apps_underwriting_ai/engines/__init__.py', 'L_APP', 'apps_underwriting_ai/engines/__init__.py', 0, 3, 3, 0.0, 0.0, 4359, 'ADG::Module::apps_underwriting_ai/engines/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '28d5939fbda5b77a2477997e9dcf195aee416e83')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4360, 'ADG::Module::apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 'L_APP', 'apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 0, 8, 8, 0.0, 0.0, 4360, 'ADG::Module::apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '0047fc621fa07448a9993e4b3d3fa036f9670307')

## mv_dependency_cone_risk (top 10 within app)

Rows: 10
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4351, 'ADG::Module::apps_underwriting_ai/__init__.py', 'L_APP', 'apps_underwriting_ai/__init__.py', 0, 0, 0, 0, 0.0, 4351, 'ADG::Module::apps_underwriting_ai/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8a6206d7bf1383784c51dcd50b6c390c88f4aacf')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4352, 'ADG::Module::apps_underwriting_ai/__main__.py', 'L_APP', 'apps_underwriting_ai/__main__.py', 0, 0, 0, 0, 0.0, 4352, 'ADG::Module::apps_underwriting_ai/__main__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/__main__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '974b1145e898fe056c3b7532445eb4d433094238')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4353, 'ADG::Module::apps_underwriting_ai/airlocks/_otel_spans.py', 'L_APP', 'apps_underwriting_ai/airlocks/_otel_spans.py', 0, 0, 0, 0, 0.0, 4353, 'ADG::Module::apps_underwriting_ai/airlocks/_otel_spans.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/airlocks/_otel_spans.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'abae24299ded132eb3c4476b948c4fe3b62cae98')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4354, 'ADG::Module::apps_underwriting_ai/cert/__init__.py', 'L_APP', 'apps_underwriting_ai/cert/__init__.py', 0, 0, 0, 0, 0.0, 4354, 'ADG::Module::apps_underwriting_ai/cert/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/cert/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5cc832534776cb5ae283fe52a50261be54f79834')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4355, 'ADG::Module::apps_underwriting_ai/cert/fec_producer.py', 'L_APP', 'apps_underwriting_ai/cert/fec_producer.py', 0, 0, 0, 0, 0.0, 4355, 'ADG::Module::apps_underwriting_ai/cert/fec_producer.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/cert/fec_producer.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '379a0861ea75a04445314d6b6acbb277162b9527')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4356, 'ADG::Module::apps_underwriting_ai/config/__init__.py', 'L_APP', 'apps_underwriting_ai/config/__init__.py', 0, 0, 0, 0, 0.0, 4356, 'ADG::Module::apps_underwriting_ai/config/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b9e593aaa6b63803986af29f66cfd506f5b30051')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4357, 'ADG::Module::apps_underwriting_ai/config/agent_spec_config.py', 'L_APP', 'apps_underwriting_ai/config/agent_spec_config.py', 0, 0, 0, 0, 0.0, 4357, 'ADG::Module::apps_underwriting_ai/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c16d130c624164336b5cefd1d0d13ff5bce7f9cb')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4358, 'ADG::Module::apps_underwriting_ai/config/hop_pipeline.py', 'L_APP', 'apps_underwriting_ai/config/hop_pipeline.py', 0, 0, 0, 0, 0.0, 4358, 'ADG::Module::apps_underwriting_ai/config/hop_pipeline.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/hop_pipeline.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'fa0557b019f204551ef9b459b0ff2cbeb53fbeb8')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4359, 'ADG::Module::apps_underwriting_ai/engines/__init__.py', 'L_APP', 'apps_underwriting_ai/engines/__init__.py', 0, 0, 0, 0, 0.0, 4359, 'ADG::Module::apps_underwriting_ai/engines/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '28d5939fbda5b77a2477997e9dcf195aee416e83')
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 4360, 'ADG::Module::apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 'L_APP', 'apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 0, 0, 0, 0, 0.0, 4360, 'ADG::Module::apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/_legacy/underwriting_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '0047fc621fa07448a9993e4b3d3fa036f9670307')

## mv_chokepoint_bridges

_view not present in this snapshot_

## v_p0_apps_direct_infra (P0 violation — apps directly importing infra)

Rows: 1
- ('__error__', 'no such column: source_file')

## SC/AP Violations (top 30 by severity)

Rows: 30

| Severity | Class | File | Line | Category |
|---|---|---|---:|---|
| LOW | hygiene | `apps_underwriting_ai/__main__.py` | 123 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/__main__.py` | 275 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/__main__.py` | 66 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/__main__.py` | 111 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/__main__.py` | 181 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/__main__.py` | 123 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/cert/fec_producer.py` | 213 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/cert/fec_producer.py` | 242 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/cert/fec_producer.py` | 247 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/cert/fec_producer.py` | 249 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/decision_packet_assembler.py` | 343 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/decision_packet_assembler.py` | 369 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/decision_packet_assembler.py` | 552 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/decision_packet_assembler.py` | 486 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/decision_packet_assembler.py` | 488 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 528 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 145 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 176 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 347 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 353 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 365 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 366 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 379 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 403 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 404 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 406 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 528 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 501 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/parsers/document_parser.py` | 122 | antipattern |
| LOW | hygiene | `apps_underwriting_ai/engines/parsers/pdf_text_parser.py` | 48 | antipattern |

See [adg_action_dispatch_playbook.md](../../docs/reports/cursor/adg_action_dispatch_playbook.md) and latest `artifacts/adg/adg_action_queue_*.json` for FIX-first triage.

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

