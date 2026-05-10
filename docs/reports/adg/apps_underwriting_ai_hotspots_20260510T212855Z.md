# `apps_underwriting_ai` — ADG Hotspot Report (W0.1)

Generated: `2026-05-10T21:28:56Z`
Snapshot: `adg_indexed_05102026_1319.sqlite`
Severity (Phase B): **LOW (reference impl)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05102026_1319.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 74 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_underwriting_ai/engines/decision_packet_assembler.py` | `apps_underwriting_ai/engines/decision_packet_assembler.py` | 23 |
| `ADG::Module::apps_underwriting_ai/services/__init__.py` | `apps_underwriting_ai/services/__init__.py` | 18 |
| `ADG::Module::apps_underwriting_ai/__main__.py` | `apps_underwriting_ai/__main__.py` | 13 |
| `ADG::Module::apps_underwriting_ai/validators/decision_packet_validator.py` | `apps_underwriting_ai/validators/decision_packet_validator.py` | 11 |
| `ADG::Module::apps_underwriting_ai/parsers/__init__.py` | `apps_underwriting_ai/parsers/__init__.py` | 11 |
| `ADG::Module::apps_underwriting_ai/engines/parsers/__init__.py` | `apps_underwriting_ai/engines/parsers/__init__.py` | 11 |
| `ADG::Module::apps_underwriting_ai/tools/audit_spine_manifest.py` | `apps_underwriting_ai/tools/audit_spine_manifest.py` | 10 |
| `ADG::Module::apps_underwriting_ai/services/rationale_agreement_tracker.py` | `apps_underwriting_ai/services/rationale_agreement_tracker.py` | 10 |
| `ADG::Module::apps_underwriting_ai/integrations/underwriting_llm_firewall.py` | `apps_underwriting_ai/integrations/underwriting_llm_firewall.py` | 10 |
| `ADG::Module::apps_underwriting_ai/engines/risk_scorer.py` | `apps_underwriting_ai/engines/risk_scorer.py` | 9 |
| `ADG::Module::apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 9 |
| `ADG::Module::apps_underwriting_ai/validators/risk_score_bounds_validator.py` | `apps_underwriting_ai/validators/risk_score_bounds_validator.py` | 8 |
| `ADG::Module::apps_underwriting_ai/types/__init__.py` | `apps_underwriting_ai/types/__init__.py` | 8 |
| `ADG::Module::apps_underwriting_ai/tools/run_underwriting.py` | `apps_underwriting_ai/tools/run_underwriting.py` | 8 |
| `ADG::Module::apps_underwriting_ai/prompt_assembly/underwriting_pa_compiler.py` | `apps_underwriting_ai/prompt_assembly/underwriting_pa_compiler.py` | 8 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **23**

- `apps_underwriting_ai/engines/__init__.py`
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
  - `apps_underwriting_ai/engines/decision_packet_assembler.py` (fan-out 23)
  - `apps_underwriting_ai/services/__init__.py` (fan-out 18)
  - `apps_underwriting_ai/__main__.py` (fan-out 13)
  - `apps_underwriting_ai/validators/decision_packet_validator.py` (fan-out 11)
  - `apps_underwriting_ai/parsers/__init__.py` (fan-out 11)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

