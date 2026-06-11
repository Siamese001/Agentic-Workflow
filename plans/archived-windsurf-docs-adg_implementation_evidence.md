---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg_implementation_evidence.md'
original_relative_path: 'adg_implementation_evidence.md'
source_sha256: 4bf41ccca5c16dd84fc60c24b94e1604c4a6bb8b3c92cdaf7a42891353d919d2
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG System Implementation

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Scope

Full implementation of the Architecture Dependency Graph (ADG) system:
- `agentic_core/adg/` package: schema, MCP client, static scanner, graph persister,
  CI invariant scanner, five policy-enforcement applications, CLI entry point
- `tests/architecture/` four test modules: 153 tests
  (determinism, invariants, negative controls, branch+robustness)
- `.github/workflows/adg-invariant-scan.yml`: CI workflow
- `tools/evidence/run_adg_evidence.py`: evidence runner (this file)

## CODE_COMMIT

c4b1cd32fdc5fff92f274701b00f257e6442a1a6

## EVIDENCE_COMMIT

1ca3bd24e5d14c95f01fbf9e409c29eb1afad792

## FILES_CHANGED_CODE

tests/architecture/test_adg_branches_and_robustness.py
tools/evidence/run_adg_evidence.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/adg_implementation_evidence.md

## INSPECTED_FILES

.github/workflows/adg-invariant-scan.yml
.windsurfrules
agentic_core/L2_execution/UniversalWriteGateway.py
agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
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
pytest.ini
tests/architecture/test_adg_branches_and_robustness.py
tests/architecture/test_adg_digest_stable.py
tests/architecture/test_adg_invariants.py
tests/architecture/test_adg_negative_controls.py
tools/evidence/run_adg_evidence.py

## ADG Pytest (153 tests collected, 153 executed)

$ -m pytest tests/architecture/test_adg_digest_stable.py tests/architecture/test_adg_invariants.py tests/architecture/test_adg_negative_controls.py tests/architecture/test_adg_branches_and_robustness.py -q --color=no

============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 153 items

tests/architecture/test_adg_digest_stable.py::test_adg_digest_stable_two_runs PASSED [  0%]
tests/architecture/test_adg_digest_stable.py::test_adg_digest_is_sha256_hex PASSED [  1%]
tests/architecture/test_adg_digest_stable.py::test_adg_edge_list_sorted PASSED [  1%]
tests/architecture/test_adg_digest_stable.py::test_adg_modules_sorted PASSED [  2%]
tests/architecture/test_adg_digest_stable.py::test_adg_canonical_edge_text_stable PASSED [  3%]
tests/architecture/test_adg_digest_stable.py::test_adg_scan_files_subset_digest_differs_from_full PASSED [  3%]
tests/architecture/test_adg_invariants.py::TestADGSchema::test_canonical_name_module PASSED [  4%]
tests/architecture/test_adg_invariants.py::TestADGSchema::test_canonical_name_layer PASSED [  5%]
tests/architecture/test_adg_invariants.py::TestADGSchema::test_canonical_name_snapshot PASSED [  5%]
tests/architecture/test_adg_invariants.py::TestADGSchema::test_canonical_name_backslash_normalized PASSED [  6%]
tests/architecture/test_adg_invariants.py::TestADGSchema::test_layer_mapping_l0 PASSED [  7%]
tests/architecture/test_adg_invariants.py::TestADGSchema::test_layer_mapping_l2 PASSED [  7%]
tests/architecture/test_adg_invariants.py::TestADGSchema::test_layer_mapping_l5 PASSED [  8%]
tests/architecture/test_adg_invariants.py::TestADGSchema::test_layer_mapping_apps PASSED [  9%]
tests/architecture/test_adg_invariants.py::TestADGSchema::test_layer_mapping_unknown PASSED [  9%]
tests/architecture/test_adg_invariants.py::TestADGSchema::test_allowed_layer_edges_contains_downward PASSED [ 10%]
tests/architecture/test_adg_invariants.py::TestADGSchema::test_allowed_layer_edges_excludes_upward PASSED [ 11%]
tests/architecture/test_adg_invariants.py::TestADGMCPClient::test_upsert_entity_idempotent PASSED [ 11%]
tests/architecture/test_adg_invariants.py::TestADGMCPClient::test_upsert_relation_idempotent PASSED [ 12%]
tests/architecture/test_adg_invariants.py::TestADGMCPClient::test_add_observation_idempotent PASSED [ 13%]
tests/architecture/test_adg_invariants.py::TestADGMCPClient::test_search_nodes_returns_matches PASSED [ 13%]
tests/architecture/test_adg_invariants.py::TestADGMCPClient::test_open_nodes_returns_relations PASSED [ 14%]
tests/architecture/test_adg_invariants.py::TestADGMCPClient::test_bulk_upsert_deterministic_order PASSED [ 15%]
tests/architecture/test_adg_invariants.py::TestADGStaticScanner::test_scan_produces_edges PASSED [ 15%]
tests/architecture/test_adg_invariants.py::TestADGStaticScanner::test_scan_files_empty_list PASSED [ 16%]
tests/architecture/test_adg_invariants.py::TestADGStaticScanner::test_scan_known_file_has_import_edge PASSED [ 16%]
tests/architecture/test_adg_invariants.py::TestADGStaticScanner::test_reverse_import_graph_populated PASSED [ 17%]
tests/architecture/test_adg_invariants.py::TestADGStaticScanner::test_module_layer_map_populated PASSED [ 18%]
tests/architecture/test_adg_invariants.py::TestCIInvariantScanner::test_rule_a_gateway_passes_for_sovereign_llm_gw PASSED [ 18%]
tests/architecture/test_adg_invariants.py::TestCIInvariantScanner::test_rule_c_no_violations_for_uwg PASSED [ 19%]
tests/architecture/test_adg_invariants.py::TestCIInvariantScanner::test_scan_report_exit_code_pass PASSED [ 20%]
tests/architecture/test_adg_invariants.py::TestCIInvariantScanner::test_scan_report_exit_code_fail PASSED [ 20%]
tests/architecture/test_adg_invariants.py::TestGatewayTopology::test_empty_result_passes PASSED [ 21%]
tests/architecture/test_adg_invariants.py::TestGatewayTopology::test_gateway_module_itself_is_allowed PASSED [ 22%]
tests/architecture/test_adg_invariants.py::TestGatewayTopology::test_report_has_proof_digest PASSED [ 22%]
tests/architecture/test_adg_invariants.py::TestUWGWriteAuthority::test_empty_result_passes PASSED [ 23%]
tests/architecture/test_adg_invariants.py::TestUWGWriteAuthority::test_uwg_module_itself_is_allowed PASSED [ 24%]
tests/architecture/test_adg_invariants.py::TestRAGSovereignty::test_empty_result_passes PASSED [ 24%]
tests/architecture/test_adg_invariants.py::TestRAGSovereignty::test_rag_module_scan_passes PASSED [ 25%]
tests/architecture/test_adg_invariants.py::TestRAGSovereignty::test_proof_digest_is_sha256 PASSED [ 26%]
tests/architecture/test_adg_invariants.py::TestBlastRadius::test_blast_radius_empty_changed PASSED [ 26%]
tests/architecture/test_adg_invariants.py::TestBlastRadius::test_blast_radius_deterministic_same_input PASSED [ 27%]
tests/architecture/test_adg_invariants.py::TestBlastRadius::test_blast_radius_l0_is_high_risk PASSED [ 28%]
tests/architecture/test_adg_invariants.py::TestBlastRadius::test_blast_radius_impact_digest_is_sha256 PASSED [ 28%]
tests/architecture/test_adg_invariants.py::TestGraphPersister::test_persist_scan_result_creates_layer_nodes PASSED [ 29%]
tests/architecture/test_adg_invariants.py::TestGraphPersister::test_persist_scan_result_creates_commit_node PASSED [ 30%]
tests/architecture/test_adg_invariants.py::TestGraphPersister::test_persist_is_idempotent PASSED [ 30%]
tests/architecture/test_adg_negative_controls.py::test_negative_rule_a_direct_openai_import_flagged PASSED [ 31%]
tests/architecture/test_adg_negative_controls.py::test_negative_rule_a_direct_anthropic_import_flagged PASSED [ 32%]
tests/architecture/test_adg_negative_controls.py::test_negative_rule_a_vertexai_flagged PASSED [ 32%]
tests/architecture/test_adg_negative_controls.py::test_negative_rule_b_embedding_bypass_flagged PASSED [ 33%]
tests/architecture/test_adg_negative_controls.py::test_negative_rule_b_huggingface_bypass_flagged PASSED [ 33%]
tests/architecture/test_adg_negative_controls.py::test_negative_rule_c_upward_layer_edge_flagged PASSED [ 34%]
tests/architecture/test_adg_negative_controls.py::test_negative_rule_c_l1_importing_l6_flagged PASSED [ 35%]
tests/architecture/test_adg_negative_controls.py::test_negative_gateway_bypass_flagged PASSED [ 35%]
tests/architecture/test_adg_negative_controls.py::test_negative_uwg_bypass_flagged PASSED [ 36%]
tests/architecture/test_adg_negative_controls.py::test_negative_uwg_subprocess_bypass_flagged PASSED [ 37%]
tests/architecture/test_adg_negative_controls.py::test_negative_rag_c0_influences_routing_decision_flagged PASSED [ 37%]
tests/architecture/test_adg_negative_controls.py::test_negative_rag_c0_influences_safety_threshold_flagged PASSED [ 38%]
tests/architecture/test_adg_negative_controls.py::test_negative_blast_radius_high_risk_escalates_mode PASSED [ 39%]
tests/architecture/test_adg_branches_and_robustness.py::TestCanonicalNameBranches::test_single_part PASSED [ 39%]
tests/architecture/test_adg_branches_and_robustness.py::TestCanonicalNameBranches::test_multi_part PASSED [ 40%]
tests/architecture/test_adg_branches_and_robustness.py::TestCanonicalNameBranches::test_backslash_in_single_part PASSED [ 41%]
tests/architecture/test_adg_branches_and_robustness.py::TestCanonicalNameBranches::test_backslash_in_multi_part PASSED [ 41%]
tests/architecture/test_adg_branches_and_robustness.py::TestCanonicalNameBranches::test_empty_part_preserved PASSED [ 42%]
tests/architecture/test_adg_branches_and_robustness.py::TestCanonicalNameBranches::test_forward_slash_unchanged PASSED [ 43%]
tests/architecture/test_adg_branches_and_robustness.py::TestCanonicalNameBranches::test_namespace_prefix_correct PASSED [ 43%]
tests/architecture/test_adg_branches_and_robustness.py::TestCanonicalNameBranches::test_two_calls_same_input_identical PASSED [ 44%]
tests/architecture/test_adg_branches_and_robustness.py::TestModulePathToLayerBranches::test_each_layer_prefix_maps_correctly PASSED [ 45%]
tests/architecture/test_adg_branches_and_robustness.py::TestModulePathToLayerBranches::test_unknown_prefix_returns_l_unknown PASSED [ 45%]
tests/architecture/test_adg_branches_and_robustness.py::TestModulePathToLayerBranches::test_backslash_path_normalized PASSED [ 46%]
tests/architecture/test_adg_branches_and_robustness.py::TestModulePathToLayerBranches::test_empty_path_returns_l_unknown PASSED [ 47%]
tests/architecture/test_adg_branches_and_robustness.py::TestModulePathToLayerBranches::test_longer_prefix_wins_over_shorter PASSED [ 47%]
tests/architecture/test_adg_branches_and_robustness.py::TestModulePathToLayerBranches::test_determinism_two_calls PASSED [ 48%]
tests/architecture/test_adg_branches_and_robustness.py::TestStaticScannerExceptionPaths::test_syntax_error_file_skipped_no_crash PASSED [ 49%]
tests/architecture/test_adg_branches_and_robustness.py::TestStaticScannerExceptionPaths::test_syntax_error_file_produces_no_edges PASSED [ 49%]
tests/architecture/test_adg_branches_and_robustness.py::TestStaticScannerExceptionPaths::test_oserror_file_produces_no_edges PASSED [ 50%]
tests/architecture/test_adg_branches_and_robustness.py::TestStaticScannerExceptionPaths::test_unicode_decode_file_handled PASSED [ 50%]
tests/architecture/test_adg_branches_and_robustness.py::TestStaticScannerExceptionPaths::test_empty_file_produces_no_edges PASSED [ 51%]
tests/architecture/test_adg_branches_and_robustness.py::TestStaticScannerExceptionPaths::test_comment_only_file_produces_no_edges PASSED [ 52%]
tests/architecture/test_adg_branches_and_robustness.py::TestStaticScannerMalformedInputs::test_scan_files_nonexistent_path_skipped PASSED [ 52%]
tests/architecture/test_adg_branches_and_robustness.py::TestStaticScannerMalformedInputs::test_scan_files_non_py_extension_skipped PASSED [ 53%]
tests/architecture/test_adg_branches_and_robustness.py::TestStaticScannerMalformedInputs::test_scan_files_duplicate_entries_deduped PASSED [ 54%]
tests/architecture/test_adg_branches_and_robustness.py::TestStaticScannerMalformedInputs::test_repo_relative_normalizes_backslash PASSED [ 54%]
tests/architecture/test_adg_branches_and_robustness.py::TestStaticScannerMalformedInputs::test_edge_dataclass_ordering_stable PASSED [ 55%]
tests/architecture/test_adg_branches_and_robustness.py::TestStaticScannerMalformedInputs::test_edge_dataclass_equal PASSED [ 56%]
tests/architecture/test_adg_branches_and_robustness.py::TestScanResultDigestBranches::test_empty_edges_digest_stable PASSED [ 56%]
tests/architecture/test_adg_branches_and_robustness.py::TestScanResultDigestBranches::test_different_edges_different_digest PASSED [ 57%]
tests/architecture/test_adg_branches_and_robustness.py::TestScanResultDigestBranches::test_edge_order_does_not_change_digest PASSED [ 58%]
tests/architecture/test_adg_branches_and_robustness.py::TestScanResultDigestBranches::test_commit_sha_does_not_affect_digest PASSED [ 58%]
tests/architecture/test_adg_branches_and_robustness.py::TestScanResultDigestBranches::test_canonical_edge_text_pipe_separated PASSED [ 59%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_weight_zero_is_normal PASSED [ 60%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_boundary_exactly_restricted_threshold PASSED [ 60%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_boundary_exactly_human_review_threshold PASSED [ 61%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_route_mode_normal_below_300 PASSED [ 62%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_route_mode_restricted_at_300 PASSED [ 62%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_route_mode_restricted_at_301 PASSED [ 63%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_route_mode_restricted_at_699 PASSED [ 64%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_route_mode_human_review_at_700 PASSED [ 64%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_route_mode_human_review_at_701 PASSED [ 65%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_impact_digest_changes_with_different_changed_files PASSED [ 66%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_l0_weight_is_100 PASSED [ 66%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_l2_weight_is_90 PASSED [ 67%]
tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_l5_weight_is_85 PASSED [ 67%]
tests/architecture/test_adg_branches_and_robustness.py::TestInvariantScannerBranches::test_rule_a_skips_l_unknown_modules PASSED [ 68%]
tests/architecture/test_adg_branches_and_robustness.py::TestInvariantScannerBranches::test_rule_b_edge_kind_not_embedding_skipped PASSED [ 69%]
tests/architecture/test_adg_branches_and_robustness.py::TestInvariantScannerBranches::test_rule_c_same_layer_not_flagged PASSED [ 69%]
tests/architecture/test_adg_branches_and_robustness.py::TestInvariantScannerBranches::test_rule_c_downward_l6_to_l0_not_flagged PASSED [ 70%]
tests/architecture/test_adg_branches_and_robustness.py::TestInvariantScannerBranches::test_rule_c_l_app_to_any_layer_not_flagged PASSED [ 71%]
tests/architecture/test_adg_branches_and_robustness.py::TestInvariantScannerBranches::test_empty_scan_result_no_violations PASSED [ 71%]
tests/architecture/test_adg_branches_and_robustness.py::TestInvariantScannerBranches::test_violation_format_no_crash PASSED [ 72%]
tests/architecture/test_adg_branches_and_robustness.py::TestInvariantScannerBranches::test_scan_report_print_summary_pass PASSED [ 73%]
tests/architecture/test_adg_branches_and_robustness.py::TestInvariantScannerBranches::test_scan_report_print_summary_fail PASSED [ 73%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_upsert_entity_none_observations PASSED [ 74%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_upsert_entity_empty_observations PASSED [ 75%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_upsert_entity_duplicate_observations_deduped PASSED [ 75%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_add_observation_nonexistent_entity_creates_it PASSED [ 76%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_search_nodes_empty_store_returns_empty PASSED [ 77%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_search_nodes_no_match_returns_empty PASSED [ 77%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_open_nodes_nonexistent_returns_empty PASSED [ 78%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_read_graph_empty PASSED [ 79%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_read_graph_sorted PASSED [ 79%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_triple_upsert_entity_stays_single PASSED [ 80%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_triple_upsert_relation_stays_single PASSED [ 81%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_bulk_upsert_empty_list PASSED [ 81%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_bulk_upsert_relations_empty_list PASSED [ 82%]
tests/architecture/test_adg_branches_and_robustness.py::TestADGMCPClientRobustness::test_observations_accumulated_across_upserts PASSED [ 83%]
tests/architecture/test_adg_branches_and_robustness.py::TestInvariantScannerMatrix::test_matrix_rule_a_invokes_provider_not_imports PASSED [ 83%]
tests/architecture/test_adg_branches_and_robustness.py::TestInvariantScannerMatrix::test_matrix_rule_c_all_upward_pairs_flagged PASSED [ 84%]
tests/architecture/test_adg_branches_and_robustness.py::TestInvariantScannerMatrix::test_matrix_rule_a_all_provider_sdk_symbols PASSED [ 84%]
tests/architecture/test_adg_branches_and_robustness.py::TestGatewayTopologyBranches::test_bypass_violation_does_not_persist_to_client PASSED [ 85%]
tests/architecture/test_adg_branches_and_robustness.py::TestGatewayTopologyBranches::test_empty_scan_no_client_call_needed PASSED [ 86%]
tests/architecture/test_adg_branches_and_robustness.py::TestGatewayTopologyBranches::test_proof_digest_is_sha256_hex PASSED [ 86%]
tests/architecture/test_adg_branches_and_robustness.py::TestUWGWriteAuthorityBranches::test_tests_module_is_allowed PASSED [ 87%]
tests/architecture/test_adg_branches_and_robustness.py::TestUWGWriteAuthorityBranches::test_ops_scripts_module_is_allowed PASSED [ 88%]
tests/architecture/test_adg_branches_and_robustness.py::TestUWGWriteAuthorityBranches::test_non_write_edge_kind_not_flagged PASSED [ 88%]
tests/architecture/test_adg_branches_and_robustness.py::TestUWGWriteAuthorityBranches::test_uwg_violation_persisted_to_client PASSED [ 89%]
tests/architecture/test_adg_branches_and_robustness.py::TestUWGWriteAuthorityBranches::test_violation_classify_filesystem_write PASSED [ 90%]
tests/architecture/test_adg_branches_and_robustness.py::TestUWGWriteAuthorityBranches::test_violation_classify_subprocess PASSED [ 90%]
tests/architecture/test_adg_branches_and_robustness.py::TestGraphPersisterBranches::test_persist_empty_result_no_crash PASSED [ 91%]
tests/architecture/test_adg_branches_and_robustness.py::TestGraphPersisterBranches::test_persist_no_commit_sha_no_commit_node PASSED [ 92%]
tests/architecture/test_adg_branches_and_robustness.py::TestGraphPersisterBranches::test_persist_with_commit_sha_creates_snapshot PASSED [ 92%]
tests/architecture/test_adg_branches_and_robustness.py::TestGraphPersisterBranches::test_persist_three_times_idempotent PASSED [ 93%]
tests/architecture/test_adg_branches_and_robustness.py::TestRAGSovereigntyBranches::test_no_extra_edges_no_violations PASSED [ 94%]
tests/architecture/test_adg_branches_and_robustness.py::TestRAGSovereigntyBranches::test_extra_edges_empty_list_no_violations PASSED [ 94%]
tests/architecture/test_adg_branches_and_robustness.py::TestRAGSovereigntyBranches::test_extra_edges_non_influences_relation_not_flagged PASSED [ 95%]
tests/architecture/test_adg_branches_and_robustness.py::TestRAGSovereigntyBranches::test_extra_edges_influences_non_decision_node_not_flagged PASSED [ 96%]
tests/architecture/test_adg_branches_and_robustness.py::TestRAGSovereigntyBranches::test_all_three_decision_nodes_are_flagged PASSED [ 96%]
tests/architecture/test_adg_branches_and_robustness.py::TestRAGSovereigntyBranches::test_snapshot_digest_changes_when_violations_change PASSED [ 97%]
tests/architecture/test_adg_branches_and_robustness.py::TestCLIBranches::test_cli_no_command_exits_1 PASSED [ 98%]
tests/architecture/test_adg_branches_and_robustness.py::TestCLIBranches::test_cli_scan_exits_0_or_1 PASSED [ 98%]
tests/architecture/test_adg_branches_and_robustness.py::TestCLIBranches::test_cli_blast_radius_exits_0 PASSED [ 99%]
tests/architecture/test_adg_branches_and_robustness.py::TestCLIBranches::test_cli_scan_diff_mode_no_crash PASSED [100%]

============================ slowest 10 durations =============================
6.44s call     tests/architecture/test_adg_digest_stable.py::test_adg_digest_stable_two_runs
3.33s call     tests/architecture/test_adg_branches_and_robustness.py::TestCLIBranches::test_cli_blast_radius_exits_0
3.29s call     tests/architecture/test_adg_invariants.py::TestADGStaticScanner::test_scan_produces_edges
3.27s call     tests/architecture/test_adg_invariants.py::TestADGStaticScanner::test_reverse_import_graph_populated
3.26s call     tests/architecture/test_adg_digest_stable.py::test_adg_scan_files_subset_digest_differs_from_full
3.25s call     tests/architecture/test_adg_digest_stable.py::test_adg_canonical_edge_text_stable
3.25s call     tests/architecture/test_adg_invariants.py::TestBlastRadius::test_blast_radius_l0_is_high_risk
3.24s call     tests/architecture/test_adg_invariants.py::TestBlastRadius::test_blast_radius_deterministic_same_input
3.23s call     tests/architecture/test_adg_digest_stable.py::test_adg_modules_sorted
3.23s call     tests/architecture/test_adg_branches_and_robustness.py::TestBlastRadiusThresholdBoundary::test_impact_digest_changes_with_different_changed_files
============================ 153 passed in 55.15s =============================

collected 153 / executed 153

## ROBUSTNESS_MATRIX

### surface: canonical_name
- ingress: schema.canonical_name(entity_type, *parts)
- success: test_single_part, test_multi_part, test_forward_slash_unchanged
- edge: test_backslash_in_single_part, test_backslash_in_multi_part, test_empty_part_preserved
- failure: (no failure path -- pure function, no exception contract)
- recovery: n/a
- determinism: test_two_calls_same_input_identical
- side-effect-safety: no side effects

### surface: module_path_to_layer
- ingress: schema.module_path_to_layer(rel_path)
- success: test_each_layer_prefix_maps_correctly
- edge: test_unknown_prefix_returns_l_unknown, test_empty_path_returns_l_unknown, test_backslash_path_normalized
- failure: test_unknown_prefix_returns_l_unknown
- recovery: n/a
- determinism: test_determinism_two_calls
- side-effect-safety: no side effects

### surface: _scan_file (exception paths)
- ingress: static_scanner._scan_file(filepath, repo_root)
- success: test_scan_known_file_has_import_edge
- edge: test_empty_file_produces_no_edges, test_comment_only_file_produces_no_edges
- failure: test_syntax_error_file_produces_no_edges, test_oserror_file_produces_no_edges, test_unicode_decode_file_handled
- recovery: silently returns [] (fail-open per scanner contract)
- determinism: test_adg_digest_stable_two_runs
- side-effect-safety: no writes

### surface: ScanResult.compute_digest
- ingress: ScanResult.compute_digest()
- success: test_empty_edges_digest_stable, test_different_edges_different_digest
- edge: test_edge_order_does_not_change_digest, test_commit_sha_does_not_affect_digest
- failure: (no failure path)
- determinism: test_adg_digest_stable_two_runs, test_edge_order_does_not_change_digest
- side-effect-safety: sets self.digest only

### surface: blast_radius thresholds
- ingress: compute_blast_radius(changed_files, result, commit_sha)
- success: test_blast_radius_empty_changed, test_blast_radius_l0_is_high_risk
- edge: test_route_mode_normal_below_300, test_route_mode_restricted_at_300, test_route_mode_restricted_at_301
- edge: test_route_mode_restricted_at_699, test_route_mode_human_review_at_700, test_route_mode_human_review_at_701
- failure: (no exception path)
- determinism: test_blast_radius_deterministic_same_input, test_impact_digest_changes_with_different_changed_files
- side-effect-safety: no writes when client=None

### surface: InvariantScanner rules A/B/C
- ingress: InvariantScanner.scan(result)
- success: test_empty_scan_result_no_violations, test_rule_a_gateway_passes_for_sovereign_llm_gw
- edge: test_rule_b_edge_kind_not_embedding_skipped, test_rule_c_same_layer_not_flagged, test_rule_c_downward_l6_to_l0_not_flagged
- failure: test_negative_rule_a_direct_openai_import_flagged, test_negative_rule_b_embedding_bypass_flagged, test_negative_rule_c_upward_layer_edge_flagged
- matrix: test_matrix_rule_a_invokes_provider_not_imports, test_matrix_rule_c_all_upward_pairs_flagged, test_matrix_rule_a_all_provider_sdk_symbols
- determinism: test_adg_digest_stable_two_runs
- side-effect-safety: no writes

### surface: ADGMCPClient idempotency
- ingress: upsert_entity, upsert_relation, add_observation, bulk_upsert_*
- success: test_upsert_entity_idempotent, test_upsert_relation_idempotent
- edge: test_upsert_entity_none_observations, test_upsert_entity_empty_observations, test_upsert_entity_duplicate_observations_deduped
- failure: test_search_nodes_empty_store_returns_empty, test_open_nodes_nonexistent_returns_empty
- recovery: test_add_observation_nonexistent_entity_creates_it
- determinism: test_bulk_upsert_deterministic_order, test_read_graph_sorted
- side-effect-safety: triple_upsert_entity_stays_single, triple_upsert_relation_stays_single

### surface: gateway_topology no-bypass
- ingress: check_gateway_topology(result, client)
- success: test_empty_result_passes, test_gateway_module_itself_is_allowed
- failure: test_negative_gateway_bypass_flagged
- side-effect-safety: test_bypass_violation_does_not_persist_to_client (proof node created, violation flagged)
- determinism: test_proof_digest_is_sha256_hex

### surface: uwg_write_authority
- ingress: check_uwg_write_authority(result, client)
- success: test_empty_result_passes, test_uwg_module_itself_is_allowed
- edge: test_tests_module_is_allowed, test_ops_scripts_module_is_allowed, test_non_write_edge_kind_not_flagged
- failure: test_negative_uwg_bypass_flagged, test_negative_uwg_subprocess_bypass_flagged
- side-effect-safety: test_uwg_violation_persisted_to_client

### surface: rag_sovereignty
- ingress: check_rag_sovereignty(result, extra_edges)
- success: test_empty_result_passes, test_rag_module_scan_passes
- edge: test_extra_edges_non_influences_relation_not_flagged, test_extra_edges_influences_non_decision_node_not_flagged
- failure: test_negative_rag_c0_influences_routing_decision_flagged, test_negative_rag_c0_influences_safety_threshold_flagged
- matrix: test_all_three_decision_nodes_are_flagged
- determinism: test_snapshot_digest_changes_when_violations_change

## DEFECT_MODEL

- **off-by-one**: blast-radius thresholds 300/700 tested at boundary-1, boundary, boundary+1
- **guard omission**: RULE_A/B/C each have a negative control proving the guard fires
- **broad-except masking**: _scan_file SyntaxError/OSError caught and tested; result is [] not crash
- **stale cache reuse**: digest is recomputed from sorted edge list each call (no cache); two-run test proves stability
- **unsigned side-effect**: UWG and gateway topology proofs tested: blocked path produces no mutation before proof write
- **hidden fallback**: gateway allowlist tested; SovereignLLMGateway passes, all others fail
- **order instability**: edge sort order tested; inserting in different order produces same digest
- **replay drift**: commit_sha excluded from digest computation; two different commit_sha produce same digest
- **duplicate mutation**: triple upsert tests prove idempotency for entities, relations, observations
- **partial-write leak**: empty observations, None observations, and duplicate observations all tested

## NO_VERIFY_BYPASS_JUSTIFICATION

--no-verify was used for code commit 7963a9014197b3301c0d8c5552d77bec6b42d90b.
Pre-commit guardian hook (T4: check_anti_patterns.py) scans the entire repo and
reported 80+ pre-existing violations in LocationHealerAgent.py, SafetyInspectorAgent.py,
StructureEnforcerAgent.py, and other files NOT touched by this phase.
Per ss6 exemption: pre-commit fails on repo-wide unrelated violations not touched by the change.
The ADG source files themselves pass all pre-commit hooks (T0-T2b lint/format).
Follow-on remediation: existing anti-pattern violations in LocationHealerAgent,
SafetyInspectorAgent, StructureEnforcerAgent should be addressed in a dedicated phase.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

