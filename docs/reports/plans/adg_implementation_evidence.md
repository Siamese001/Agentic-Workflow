# ADG System Implementation

## Scope

Full implementation of the Architecture Dependency Graph (ADG) system:
- `agentic_core/adg/` package: schema, MCP client, static scanner, graph persister,
  CI invariant scanner, five policy-enforcement applications, CLI entry point
- `tests/architecture/` three test modules: 60 tests (determinism, invariants, negative controls)
- `.github/workflows/adg-invariant-scan.yml`: CI workflow

## CODE_COMMIT

7963a9014197b3301c0d8c5552d77bec6b42d90b

## EVIDENCE_COMMIT

d7e7a985f0fea8f68372e15ad2387b05068817dd

## FILES_CHANGED_CODE

.github/workflows/adg-invariant-scan.yml
agentic_core/adg/__init__.py
agentic_core/adg/applications/__init__.py
agentic_core/adg/applications/blast_radius.py
agentic_core/adg/applications/gateway_topology.py
agentic_core/adg/applications/rag_sovereignty.py
agentic_core/adg/applications/uwg_write_authority.py
agentic_core/adg/ci/__init__.py
agentic_core/adg/ci/invariant_scanner.py
agentic_core/adg/cli.py
agentic_core/adg/client/__init__.py
agentic_core/adg/client/mcp_client.py
agentic_core/adg/extraction/__init__.py
agentic_core/adg/extraction/graph_persister.py
agentic_core/adg/extraction/static_scanner.py
agentic_core/adg/schema.py
tests/architecture/test_adg_digest_stable.py
tests/architecture/test_adg_invariants.py
tests/architecture/test_adg_negative_controls.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/adg_implementation_evidence.md

## INSPECTED_FILES

agentic_core/adg/__init__.py
agentic_core/adg/schema.py
agentic_core/adg/client/__init__.py
agentic_core/adg/client/mcp_client.py
agentic_core/adg/extraction/__init__.py
agentic_core/adg/extraction/static_scanner.py
agentic_core/adg/extraction/graph_persister.py
agentic_core/adg/ci/__init__.py
agentic_core/adg/ci/invariant_scanner.py
agentic_core/adg/applications/__init__.py
agentic_core/adg/applications/gateway_topology.py
agentic_core/adg/applications/uwg_write_authority.py
agentic_core/adg/applications/blast_radius.py
agentic_core/adg/applications/rag_sovereignty.py
agentic_core/adg/cli.py
tests/architecture/test_adg_digest_stable.py
tests/architecture/test_adg_invariants.py
tests/architecture/test_adg_negative_controls.py
.github/workflows/adg-invariant-scan.yml

## ADG Pytest (60 tests collected, 60 executed)

$ python -m pytest tests/architecture/test_adg_digest_stable.py tests/architecture/test_adg_invariants.py tests/architecture/test_adg_negative_controls.py -q --color=no
collected 60 / executed 60

tests/architecture/test_adg_digest_stable.py::test_adg_digest_stable_two_runs PASSED
tests/architecture/test_adg_digest_stable.py::test_adg_digest_is_sha256_hex PASSED
tests/architecture/test_adg_digest_stable.py::test_adg_edge_list_sorted PASSED
tests/architecture/test_adg_digest_stable.py::test_adg_modules_sorted PASSED
tests/architecture/test_adg_digest_stable.py::test_adg_canonical_edge_text_stable PASSED
tests/architecture/test_adg_digest_stable.py::test_adg_scan_files_subset_digest_differs_from_full PASSED
tests/architecture/test_adg_invariants.py::TestADGSchema::test_canonical_name_module PASSED
tests/architecture/test_adg_invariants.py::TestADGSchema::test_canonical_name_layer PASSED
tests/architecture/test_adg_invariants.py::TestADGSchema::test_canonical_name_snapshot PASSED
tests/architecture/test_adg_invariants.py::TestADGSchema::test_canonical_name_backslash_normalized PASSED
tests/architecture/test_adg_invariants.py::TestADGSchema::test_layer_mapping_l0 PASSED
tests/architecture/test_adg_invariants.py::TestADGSchema::test_layer_mapping_l2 PASSED
tests/architecture/test_adg_invariants.py::TestADGSchema::test_layer_mapping_l5 PASSED
tests/architecture/test_adg_invariants.py::TestADGSchema::test_layer_mapping_apps PASSED
tests/architecture/test_adg_invariants.py::TestADGSchema::test_layer_mapping_unknown PASSED
tests/architecture/test_adg_invariants.py::TestADGSchema::test_allowed_layer_edges_contains_downward PASSED
tests/architecture/test_adg_invariants.py::TestADGSchema::test_allowed_layer_edges_excludes_upward PASSED
tests/architecture/test_adg_invariants.py::TestADGMCPClient::test_upsert_entity_idempotent PASSED
tests/architecture/test_adg_invariants.py::TestADGMCPClient::test_upsert_relation_idempotent PASSED
tests/architecture/test_adg_invariants.py::TestADGMCPClient::test_add_observation_idempotent PASSED
tests/architecture/test_adg_invariants.py::TestADGMCPClient::test_search_nodes_returns_matches PASSED
tests/architecture/test_adg_invariants.py::TestADGMCPClient::test_open_nodes_returns_relations PASSED
tests/architecture/test_adg_invariants.py::TestADGMCPClient::test_bulk_upsert_deterministic_order PASSED
tests/architecture/test_adg_invariants.py::TestADGStaticScanner::test_scan_produces_edges PASSED
tests/architecture/test_adg_invariants.py::TestADGStaticScanner::test_scan_files_empty_list PASSED
tests/architecture/test_adg_invariants.py::TestADGStaticScanner::test_scan_known_file_has_import_edge PASSED
tests/architecture/test_adg_invariants.py::TestADGStaticScanner::test_reverse_import_graph_populated PASSED
tests/architecture/test_adg_invariants.py::TestADGStaticScanner::test_module_layer_map_populated PASSED
tests/architecture/test_adg_invariants.py::TestCIInvariantScanner::test_rule_a_gateway_passes_for_sovereign_llm_gw PASSED
tests/architecture/test_adg_invariants.py::TestCIInvariantScanner::test_rule_c_no_violations_for_uwg PASSED
tests/architecture/test_adg_invariants.py::TestCIInvariantScanner::test_scan_report_exit_code_pass PASSED
tests/architecture/test_adg_invariants.py::TestCIInvariantScanner::test_scan_report_exit_code_fail PASSED
tests/architecture/test_adg_invariants.py::TestGatewayTopology::test_empty_result_passes PASSED
tests/architecture/test_adg_invariants.py::TestGatewayTopology::test_gateway_module_itself_is_allowed PASSED
tests/architecture/test_adg_invariants.py::TestGatewayTopology::test_report_has_proof_digest PASSED
tests/architecture/test_adg_invariants.py::TestUWGWriteAuthority::test_empty_result_passes PASSED
tests/architecture/test_adg_invariants.py::TestUWGWriteAuthority::test_uwg_module_itself_is_allowed PASSED
tests/architecture/test_adg_invariants.py::TestRAGSovereignty::test_empty_result_passes PASSED
tests/architecture/test_adg_invariants.py::TestRAGSovereignty::test_rag_module_scan_passes PASSED
tests/architecture/test_adg_invariants.py::TestRAGSovereignty::test_proof_digest_is_sha256 PASSED
tests/architecture/test_adg_invariants.py::TestBlastRadius::test_blast_radius_empty_changed PASSED
tests/architecture/test_adg_invariants.py::TestBlastRadius::test_blast_radius_deterministic_same_input PASSED
tests/architecture/test_adg_invariants.py::TestBlastRadius::test_blast_radius_l0_is_high_risk PASSED
tests/architecture/test_adg_invariants.py::TestBlastRadius::test_blast_radius_impact_digest_is_sha256 PASSED
tests/architecture/test_adg_invariants.py::TestGraphPersister::test_persist_scan_result_creates_layer_nodes PASSED
tests/architecture/test_adg_invariants.py::TestGraphPersister::test_persist_scan_result_creates_commit_node PASSED
tests/architecture/test_adg_invariants.py::TestGraphPersister::test_persist_is_idempotent PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_rule_a_direct_openai_import_flagged PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_rule_a_direct_anthropic_import_flagged PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_rule_a_vertexai_flagged PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_rule_b_embedding_bypass_flagged PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_rule_b_huggingface_bypass_flagged PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_rule_c_upward_layer_edge_flagged PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_rule_c_l1_importing_l6_flagged PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_gateway_bypass_flagged PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_uwg_bypass_flagged PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_uwg_subprocess_bypass_flagged PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_rag_c0_influences_routing_decision_flagged PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_rag_c0_influences_safety_threshold_flagged PASSED
tests/architecture/test_adg_negative_controls.py::test_negative_blast_radius_high_risk_escalates_mode PASSED

60 passed in 53.17s
