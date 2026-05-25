# `apps_underwriting_ai` — ADG Hotspot Report (W0.1)

Generated: `2026-04-29T20:50:39Z`
Snapshot: `adg_indexed_04292026_1606.sqlite`
Severity (Phase B): **LOW (reference impl)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_04292026_1606.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_UNKNOWN | 75 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_underwriting_ai/types/__init__.py` | `apps_underwriting_ai/types/__init__.py` | 43 |
| `ADG::Module::apps_underwriting_ai/engines/underwriting_engine.py` | `apps_underwriting_ai/engines/underwriting_engine.py` | 35 |
| `ADG::Module::apps_underwriting_ai/ingestion/json_mapper.py` | `apps_underwriting_ai/ingestion/json_mapper.py` | 24 |
| `ADG::Module::apps_underwriting_ai/engines/feature_derivation_engine.py` | `apps_underwriting_ai/engines/feature_derivation_engine.py` | 18 |
| `ADG::Module::apps_underwriting_ai/tests/test_underwriting_engine.py` | `apps_underwriting_ai/tests/test_underwriting_engine.py` | 17 |
| `ADG::Module::apps_underwriting_ai/ingestion/intake_router.py` | `apps_underwriting_ai/ingestion/intake_router.py` | 15 |
| `ADG::Module::apps_underwriting_ai/types/underwriting_request_types.py` | `apps_underwriting_ai/types/underwriting_request_types.py` | 14 |
| `ADG::Module::apps_underwriting_ai/tests/test_document_completeness_validator.py` | `apps_underwriting_ai/tests/test_document_completeness_validator.py` | 14 |
| `ADG::Module::apps_underwriting_ai/integrations/governed_uw_exception.py` | `apps_underwriting_ai/integrations/governed_uw_exception.py` | 13 |
| `ADG::Module::apps_underwriting_ai/engines/decision_packet_assembler.py` | `apps_underwriting_ai/engines/decision_packet_assembler.py` | 13 |
| `ADG::Module::apps_underwriting_ai/validators/document_completeness_validator.py` | `apps_underwriting_ai/validators/document_completeness_validator.py` | 12 |
| `ADG::Module::apps_underwriting_ai/ingestion/document_ingestion.py` | `apps_underwriting_ai/ingestion/document_ingestion.py` | 12 |
| `ADG::Module::apps_underwriting_ai/ingestion/csv_mapper.py` | `apps_underwriting_ai/ingestion/csv_mapper.py` | 12 |
| `ADG::Module::apps_underwriting_ai/validators/stale_data_validator.py` | `apps_underwriting_ai/validators/stale_data_validator.py` | 11 |
| `ADG::Module::apps_underwriting_ai/engines/document_reconciliation_engine.py` | `apps_underwriting_ai/engines/document_reconciliation_engine.py` | 11 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **14**

- `apps_underwriting_ai/engines/__init__.py`
- `apps_underwriting_ai/engines/decision_packet_assembler.py`
- `apps_underwriting_ai/engines/document_reconciliation_engine.py`
- `apps_underwriting_ai/engines/evidence_register_engine.py`
- `apps_underwriting_ai/engines/feature_derivation_engine.py`
- `apps_underwriting_ai/engines/underwriting_engine.py`
- `apps_underwriting_ai/reasoning/__init__.py`
- `apps_underwriting_ai/reasoning/condition_recommender.py`
- `apps_underwriting_ai/reasoning/counter_offer_recommender.py`
- `apps_underwriting_ai/reasoning/covenant_recommender.py`
- `apps_underwriting_ai/reasoning/exception_summarizer.py`
- `apps_underwriting_ai/reasoning/feature_interpreter.py`
- `apps_underwriting_ai/reasoning/human_escalation_selector.py`
- `apps_underwriting_ai/reasoning/risk_hypothesis_builder.py`

## mv_hotspot_centrality (top 10 within app)

Rows: 10
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3150, 'ADG::Module::apps_underwriting_ai/__init__.py', 'L_UNKNOWN', 'apps_underwriting_ai/__init__.py', 0, 1, 1, 0.0, 0.0, 3150, 'ADG::Module::apps_underwriting_ai/__init__.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '386acf5af6da8d601d241e0307cdff798a156d5a')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3151, 'ADG::Module::apps_underwriting_ai/config/__init__.py', 'L_UNKNOWN', 'apps_underwriting_ai/config/__init__.py', 0, 0, 0, 0.0, 0.0, 3151, 'ADG::Module::apps_underwriting_ai/config/__init__.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3152, 'ADG::Module::apps_underwriting_ai/config/agent_spec_config.py', 'L_UNKNOWN', 'apps_underwriting_ai/config/agent_spec_config.py', 0, 3, 3, 0.0, 0.0, 3152, 'ADG::Module::apps_underwriting_ai/config/agent_spec_config.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b0f08b72ad835a5a6eee3b9addcc2c23007b24b3')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3153, 'ADG::Module::apps_underwriting_ai/engines/__init__.py', 'L_UNKNOWN', 'apps_underwriting_ai/engines/__init__.py', 0, 8, 8, 0.0, 0.0, 3153, 'ADG::Module::apps_underwriting_ai/engines/__init__.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '24de3be9548caecd5a9d458af6fd47d41f2d43fc')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3154, 'ADG::Module::apps_underwriting_ai/engines/decision_packet_assembler.py', 'L_UNKNOWN', 'apps_underwriting_ai/engines/decision_packet_assembler.py', 0, 13, 13, 0.0, 0.0, 3154, 'ADG::Module::apps_underwriting_ai/engines/decision_packet_assembler.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/decision_packet_assembler.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '3da6984357267f2ed60da05db8f6a923a21098a8')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3155, 'ADG::Module::apps_underwriting_ai/engines/document_reconciliation_engine.py', 'L_UNKNOWN', 'apps_underwriting_ai/engines/document_reconciliation_engine.py', 0, 11, 11, 0.0, 0.0, 3155, 'ADG::Module::apps_underwriting_ai/engines/document_reconciliation_engine.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/document_reconciliation_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '2d5921d6463ccaef9689d3ab3f65c3c7a6be9bd4')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3156, 'ADG::Module::apps_underwriting_ai/engines/evidence_register_engine.py', 'L_UNKNOWN', 'apps_underwriting_ai/engines/evidence_register_engine.py', 0, 8, 8, 0.0, 0.0, 3156, 'ADG::Module::apps_underwriting_ai/engines/evidence_register_engine.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/evidence_register_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5e7a275bb89b26d78edca05555cd6dd95668e430')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3157, 'ADG::Module::apps_underwriting_ai/engines/feature_derivation_engine.py', 'L_UNKNOWN', 'apps_underwriting_ai/engines/feature_derivation_engine.py', 0, 18, 18, 0.0, 0.0, 3157, 'ADG::Module::apps_underwriting_ai/engines/feature_derivation_engine.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/feature_derivation_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '595d718c7a468420ebd3cfad31b86f1483c1fb75')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3158, 'ADG::Module::apps_underwriting_ai/engines/underwriting_engine.py', 'L_UNKNOWN', 'apps_underwriting_ai/engines/underwriting_engine.py', 0, 35, 35, 0.0, 0.0, 3158, 'ADG::Module::apps_underwriting_ai/engines/underwriting_engine.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/underwriting_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '2077d57523e7f2e286e2221439f01d982912256c')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3159, 'ADG::Module::apps_underwriting_ai/ingestion/__init__.py', 'L_UNKNOWN', 'apps_underwriting_ai/ingestion/__init__.py', 0, 10, 10, 0.0, 0.0, 3159, 'ADG::Module::apps_underwriting_ai/ingestion/__init__.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/ingestion/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c2a9480360c981d5b533d96d9aab0fad6b40da2a')

## mv_dependency_cone_risk (top 10 within app)

Rows: 10
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3150, 'ADG::Module::apps_underwriting_ai/__init__.py', 'L_UNKNOWN', 'apps_underwriting_ai/__init__.py', 0, 0, 0, 0, 0.0, 3150, 'ADG::Module::apps_underwriting_ai/__init__.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '386acf5af6da8d601d241e0307cdff798a156d5a')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3151, 'ADG::Module::apps_underwriting_ai/config/__init__.py', 'L_UNKNOWN', 'apps_underwriting_ai/config/__init__.py', 0, 0, 0, 0, 0.0, 3151, 'ADG::Module::apps_underwriting_ai/config/__init__.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3152, 'ADG::Module::apps_underwriting_ai/config/agent_spec_config.py', 'L_UNKNOWN', 'apps_underwriting_ai/config/agent_spec_config.py', 0, 0, 0, 0, 0.0, 3152, 'ADG::Module::apps_underwriting_ai/config/agent_spec_config.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'b0f08b72ad835a5a6eee3b9addcc2c23007b24b3')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3153, 'ADG::Module::apps_underwriting_ai/engines/__init__.py', 'L_UNKNOWN', 'apps_underwriting_ai/engines/__init__.py', 0, 0, 0, 0, 0.0, 3153, 'ADG::Module::apps_underwriting_ai/engines/__init__.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '24de3be9548caecd5a9d458af6fd47d41f2d43fc')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3154, 'ADG::Module::apps_underwriting_ai/engines/decision_packet_assembler.py', 'L_UNKNOWN', 'apps_underwriting_ai/engines/decision_packet_assembler.py', 0, 0, 0, 0, 0.0, 3154, 'ADG::Module::apps_underwriting_ai/engines/decision_packet_assembler.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/decision_packet_assembler.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '3da6984357267f2ed60da05db8f6a923a21098a8')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3155, 'ADG::Module::apps_underwriting_ai/engines/document_reconciliation_engine.py', 'L_UNKNOWN', 'apps_underwriting_ai/engines/document_reconciliation_engine.py', 0, 0, 0, 0, 0.0, 3155, 'ADG::Module::apps_underwriting_ai/engines/document_reconciliation_engine.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/document_reconciliation_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '2d5921d6463ccaef9689d3ab3f65c3c7a6be9bd4')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3156, 'ADG::Module::apps_underwriting_ai/engines/evidence_register_engine.py', 'L_UNKNOWN', 'apps_underwriting_ai/engines/evidence_register_engine.py', 0, 0, 0, 0, 0.0, 3156, 'ADG::Module::apps_underwriting_ai/engines/evidence_register_engine.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/evidence_register_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5e7a275bb89b26d78edca05555cd6dd95668e430')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3157, 'ADG::Module::apps_underwriting_ai/engines/feature_derivation_engine.py', 'L_UNKNOWN', 'apps_underwriting_ai/engines/feature_derivation_engine.py', 0, 0, 0, 0, 0.0, 3157, 'ADG::Module::apps_underwriting_ai/engines/feature_derivation_engine.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/feature_derivation_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '595d718c7a468420ebd3cfad31b86f1483c1fb75')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3158, 'ADG::Module::apps_underwriting_ai/engines/underwriting_engine.py', 'L_UNKNOWN', 'apps_underwriting_ai/engines/underwriting_engine.py', 0, 0, 0, 0, 0.0, 3158, 'ADG::Module::apps_underwriting_ai/engines/underwriting_engine.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/engines/underwriting_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '2077d57523e7f2e286e2221439f01d982912256c')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 3159, 'ADG::Module::apps_underwriting_ai/ingestion/__init__.py', 'L_UNKNOWN', 'apps_underwriting_ai/ingestion/__init__.py', 0, 0, 0, 0, 0.0, 3159, 'ADG::Module::apps_underwriting_ai/ingestion/__init__.py', 'module', 'L_UNKNOWN', 'repo_module', 'HIGH', 'apps_underwriting_ai/ingestion/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c2a9480360c981d5b533d96d9aab0fad6b40da2a')

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
  - `apps_underwriting_ai/types/__init__.py` (fan-out 43)
  - `apps_underwriting_ai/engines/underwriting_engine.py` (fan-out 35)
  - `apps_underwriting_ai/ingestion/json_mapper.py` (fan-out 24)
  - `apps_underwriting_ai/engines/feature_derivation_engine.py` (fan-out 18)
  - `apps_underwriting_ai/tests/test_underwriting_engine.py` (fan-out 17)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

