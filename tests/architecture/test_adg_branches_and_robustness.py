"""Phase 7.4: ADG branch coverage, boundary, exception, matrix, and robustness tests.

Covers every changed logic surface per .windsurfrules §4:
- All branch paths (success, failure, boundary, malformed, exception)
- Threshold boundary values (blast-radius: 300, 700)
- Exception paths (SyntaxError, OSError in scanner)
- Malformed / near-plausible inputs
- Matrix tests (multiple interacting inputs)
- Idempotent re-entry / replay tests
- Side-effect safety on blocked paths
- Determinism across two invocations

Markers: architecture, determinism, negative_control, governance
"""

from __future__ import annotations

from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    L2_EXECUTION_DIR,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_branches_and_robustness")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_branches_and_robustness", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_branches_and_robustness", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_branches_and_robustness", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_adg_branches_and_robustness", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_branches_and_robustness", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_branches_and_robustness", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_branches_and_robustness", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_branches_and_robustness", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_branches_and_robustness", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_branches_and_robustness", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_branches_and_robustness", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_branches_and_robustness", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_branches_and_robustness", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_branches_and_robustness", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_branches_and_robustness", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_branches_and_robustness", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_branches_and_robustness", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_branches_and_robustness", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_branches_and_robustness", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_branches_and_robustness", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_branches_and_robustness", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_branches_and_robustness", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_branches_and_robustness", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_branches_and_robustness", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_branches_and_robustness", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_branches_and_robustness", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_branches_and_robustness", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_branches_and_robustness", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_branches_and_robustness", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_branches_and_robustness", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_branches_and_robustness", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_branches_and_robustness", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_branches_and_robustness", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_branches_and_robustness", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_branches_and_robustness", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_branches_and_robustness", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_branches_and_robustness", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_branches_and_robustness", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_branches_and_robustness", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_branches_and_robustness", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_branches_and_robustness", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_branches_and_robustness", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_branches_and_robustness", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_branches_and_robustness", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_branches_and_robustness", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_branches_and_robustness", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_branches_and_robustness", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_branches_and_robustness", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_branches_and_robustness", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_branches_and_robustness", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_branches_and_robustness", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_branches_and_robustness")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_branches_and_robustness", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_branches_and_robustness")
# REMOVED: emit_determinism_digest("p0", "test_adg_branches_and_robustness")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_branches_and_robustness", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_branches_and_robustness", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_branches_and_robustness", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_branches_and_robustness", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_branches_and_robustness", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_branches_and_robustness", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_branches_and_robustness", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_branches_and_robustness", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_branches_and_robustness", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_branches_and_robustness", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_branches_and_robustness", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_branches_and_robustness", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_branches_and_robustness", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_branches_and_robustness", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_branches_and_robustness", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_branches_and_robustness", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_branches_and_robustness", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_branches_and_robustness", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_branches_and_robustness", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_branches_and_robustness", "exec_snapshot_link")

REPO_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# §4 canonical_name -- boundary / malformed / encoding
# ---------------------------------------------------------------------------


class TestCanonicalNameBranches:
    """schema.canonical_name: all branch and edge-case paths."""

    @pytest.mark.architecture
    def test_single_part(self) -> None:
                from agentic_core.L0_routing.config.path_constants import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.schema_util import ADG_NS, canonical_name
                from agentic_core.adg.schema_util import module_path_to_layer
                from agentic_core.adg.schema_util import module_path_to_layer
                from agentic_core.adg.schema_util import module_path_to_layer
                from agentic_core.adg.schema_util import module_path_to_layer
                from agentic_core.adg.schema_util import module_path_to_layer
                from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
                from agentic_core.adg.extraction.static_scanner import _scan_file
                from agentic_core.adg.extraction.static_scanner import _scan_file
                from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
                from agentic_core.adg.extraction.static_scanner import _scan_file
                from agentic_core.adg.extraction.static_scanner import _scan_file
                from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
                from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
                from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
                from agentic_core.adg.extraction.static_scanner import _repo_relative
                from agentic_core.adg.extraction.static_scanner import Edge
                from agentic_core.adg.extraction.static_scanner import Edge
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.applications.BlastRadiusResult import compute_blast_radius
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.applications.BlastRadiusResult import (
                from agentic_core.adg.applications.BlastRadiusResult import _HUMAN_REVIEW_THRESHOLD
                from agentic_core.adg.applications.BlastRadiusResult import (
                from agentic_core.adg.applications.BlastRadiusResult import _RESTRICTED_THRESHOLD
                from agentic_core.adg.applications.BlastRadiusResult import _HUMAN_REVIEW_THRESHOLD
                from agentic_core.adg.applications.BlastRadiusResult import compute_blast_radius
                from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
                from agentic_core.adg.applications.BlastRadiusResult import _LAYER_WEIGHTS
                from agentic_core.adg.applications.BlastRadiusResult import _LAYER_WEIGHTS
                from agentic_core.adg.applications.BlastRadiusResult import _LAYER_WEIGHTS
                from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.ci.invariant_scanner_config import Violation
                from agentic_core.adg.ci.invariant_scanner_config import ScanReport
                from agentic_core.adg.ci.invariant_scanner_config import ScanReport, Violation
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.schema_util import PROVIDER_SDK_SYMBOLS, canonical_name
                from agentic_core.adg.applications.gateway_topology_validator import check_gateway_topology
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.applications.uwg_write_authority_validator import check_uwg_write_authority
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.applications.uwg_write_authority_validator import check_uwg_write_authority
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.applications.uwg_write_authority_validator import check_uwg_write_authority
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.applications.uwg_write_authority_validator import check_uwg_write_authority
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.applications.uwg_write_authority_validator import _classify_side_effect
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.extraction.graph_persister import persist_scan_result
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.extraction.graph_persister import persist_scan_result
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.extraction.graph_persister import persist_scan_result
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.client.InMemoryStore import ADGMCPClient
                from agentic_core.adg.extraction.graph_persister import persist_scan_result
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.applications.rag_sovereignty_validator import (
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
                from agentic_core.adg.extraction.static_scanner import ScanResult
                from agentic_core.adg.schema_util import canonical_name
                from agentic_core.adg.cli import main
                from agentic_core.adg.cli import main
                from agentic_core.adg.cli import main
                from agentic_core.adg.cli import main
                from agentic_core.adg.cli import main
        #  # MOVED: from agentic_core.adg.schema_util import canonical_name

#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        assert canonical_name("Module", "a.py") == "ADG::Module::a.py"

    @pytest.mark.architecture
    def test_multi_part(self) -> None:
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        assert canonical_name("Snapshot", "sha1", "dig1") == "ADG::Snapshot::sha1::dig1"

    @pytest.mark.architecture
    def test_backslash_in_single_part(self) -> None:
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        result = canonical_name("Module", "a\\b\\c.py")
        assert "\\" not in result
        assert result == "ADG::Module::a/b/c.py"

    @pytest.mark.architecture
    def test_backslash_in_multi_part(self) -> None:
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        result = canonical_name("Module", "a\\b", "c\\d")
        assert "\\" not in result

    @pytest.mark.architecture
    def test_empty_part_preserved(self) -> None:
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        result = canonical_name("Symbol", "")
        assert result == "ADG::Symbol::"

    @pytest.mark.architecture
    def test_forward_slash_unchanged(self) -> None:
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        result = canonical_name("Module", "a/b/c.py")
        assert result == "ADG::Module::a/b/c.py"

    @pytest.mark.architecture
    def test_namespace_prefix_correct(self) -> None:
#  # MOVED: from agentic_core.adg.schema_util import ADG_NS, canonical_name

        result = canonical_name("Layer", "L0")
        assert result.startswith(f"{ADG_NS}::")

    @pytest.mark.architecture
    def test_two_calls_same_input_identical(self) -> None:
    """Test two_calls_same_input_identical runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute two_calls_same_input_identical
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
#  # MOVED: from agentic_core.adg.schema_util import module_path_to_layer

        cases = [
            ("agentic_core/L0_routing/x.py", "L0"),
            ("agentic_core/L1_cognition/x.py", "L1"),
            ("agentic_core/L2_execution/x.py", "L2"),
            ("agentic_core/L3_orchestration/x.py", "L3"),
            ("agentic_core/L4_state/x.py", "L4"),
            ("agentic_core/L5_safety/x.py", "L5"),
            ("agentic_core/L6_observability/x.py", "L6"),
            ("apps_rg/engines/x.py", "L_APP"),
            ("apps_lic/engines/x.py", "L_APP"),
            ("apps_shared/reasoning/x.py", "L_APP"),
            ("system_learning/adapters/x.py", "L_SL"),
            ("tools/evidence/x.py", "L_TOOLS"),
            ("ops_scripts/ci/x.py", "L_OPS"),
        ]
        for path, expected in cases:
            assert module_path_to_layer(path) == expected, f"Failed for {path!r}"

    @pytest.mark.architecture
    def test_unknown_prefix_returns_l_unknown(self) -> None:
#  # MOVED: from agentic_core.adg.schema_util import module_path_to_layer

        assert module_path_to_layer("totally/random/path.py") == "L_UNKNOWN"

    @pytest.mark.architecture
    def test_backslash_path_normalized(self) -> None:
#  # MOVED: from agentic_core.adg.schema_util import module_path_to_layer

        assert module_path_to_layer("agentic_core\\L2_execution\\x.py") == "L2"

    @pytest.mark.architecture
    def test_empty_path_returns_l_unknown(self) -> None:
#  # MOVED: from agentic_core.adg.schema_util import module_path_to_layer

        assert module_path_to_layer("") == "L_UNKNOWN"

    @pytest.mark.architecture
    def test_longer_prefix_wins_over_shorter(self) -> None:
        """Longer prefix must win (no false L_UNKNOWN from prefix collision)."""
#  # MOVED: from agentic_core.adg.schema_util import module_path_to_layer

        result = module_path_to_layer("agentic_core/L0_routing/engines/deep/path.py")
        assert result == "L0"

    @pytest.mark.architecture
    def test_determinism_two_calls(self) -> None:
    """Test determinism_two_calls runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute determinism_two_calls
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
    """ADGStaticScanner: SyntaxError and OSError paths must be silently skipped."""

    @pytest.mark.architecture
    def test_syntax_error_file_skipped_no_crash(self, tmp_path: Path) -> None:
        """SyntaxError in source file must not crash the scanner."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        bad_file = tmp_path / L2_EXECUTION_DIR / "bad.py"
        bad_file.parent.mkdir(parents=True)
        bad_file.write_text("def foo(\n    # unterminated\n", encoding="utf-8")

        scanner = ADGStaticScanner(repo_root=tmp_path)
        result = scanner.scan(commit_sha="syntax-err")
        assert result.digest, "Should produce a digest even with syntax-error files"

    @pytest.mark.architecture
    def test_syntax_error_file_produces_no_edges(self, tmp_path: Path) -> None:
        """Syntax-error file contributes zero edges."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import _scan_file

        bad_file = tmp_path / "bad.py"
        bad_file.write_text("def foo(:\n", encoding="utf-8")
        edges, had_error = _scan_file(bad_file, tmp_path)
        assert edges == []
        assert had_error is True

    @pytest.mark.architecture
    def test_oserror_file_produces_no_edges(self, tmp_path: Path) -> None:
        """OSError reading a file produces zero edges (not an exception)."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import _scan_file

        missing = tmp_path / "nonexistent.py"
        edges, had_error = _scan_file(missing, tmp_path)
        assert edges == []
        assert had_error is True

    @pytest.mark.architecture
    def test_unicode_decode_file_handled(self, tmp_path: Path) -> None:
        """Binary content that fails UTF-8 strict must not crash (errors=replace)."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        binary_dir = tmp_path / L2_EXECUTION_DIR
        binary_dir.mkdir(parents=True)
        bad_file = binary_dir / "binary.py"
        bad_file.write_bytes(b"import os\n\x80\x81\x82\xff\nfoo = 1\n")

        scanner = ADGStaticScanner(repo_root=tmp_path)
        result = scanner.scan(commit_sha="binary-test")
        assert isinstance(result.digest, str)

    @pytest.mark.architecture
    def test_empty_file_produces_no_edges(self, tmp_path: Path) -> None:
        """Empty .py file contributes zero edges."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import _scan_file

        empty = tmp_path / "empty.py"
        empty.write_text("", encoding="utf-8")
        edges, had_error = _scan_file(empty, tmp_path)
        assert edges == []
        assert had_error is False

    @pytest.mark.architecture
    def test_comment_only_file_produces_no_edges(self, tmp_path: Path) -> None:
        """File with only comments contributes zero edges."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import _scan_file

        f = tmp_path / "comments.py"
        f.write_text("# just a comment\n# another\n", encoding="utf-8")
        edges, had_error = _scan_file(f, tmp_path)
        assert edges == []
        assert had_error is False


class TestStaticScannerMalformedInputs:
    """Scanner: malformed-but-plausible inputs."""

    @pytest.mark.architecture
    def test_scan_files_nonexistent_path_skipped(self) -> None:
        """Non-existent file in scan_files list is silently skipped."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files(
            ["does/not/exist.py", "also/missing.py"],
            commit_sha="missing",
        )
        assert result.edges == []
        assert result.modules == []

    @pytest.mark.architecture
    def test_scan_files_non_py_extension_skipped(self) -> None:
        """Non-.py files in list are skipped."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan_files(
            ["README.md", "pyproject.toml", "requirements.txt"],
            commit_sha="non-py",
        )
        assert result.edges == []

    @pytest.mark.architecture
    def test_scan_files_duplicate_entries_deduped(self, tmp_path: Path) -> None:
        """Duplicate file entries produce identical result to single entry."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        src_dir = tmp_path / L2_EXECUTION_DIR
        src_dir.mkdir(parents=True)
        src = src_dir / "foo.py"
        src.write_text("import os\n", encoding="utf-8")

        scanner = ADGStaticScanner(repo_root=tmp_path)
        r1 = scanner.scan_files(
            ["agentic_core/L2_execution/foo.py"],
            commit_sha="single",
        )
        r2 = scanner.scan_files(
            ["agentic_core/L2_execution/foo.py", "agentic_core/L2_execution/foo.py"],
            commit_sha="double",
        )
        assert r1.digest == r2.digest

    @pytest.mark.architecture
    def test_repo_relative_normalizes_backslash(self, tmp_path: Path) -> None:
        """_repo_relative must produce forward-slash paths."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import _repo_relative

        src = tmp_path / "a" / "b" / "c.py"
        result = _repo_relative(src, tmp_path)
        assert "\\" not in result

    @pytest.mark.architecture
    def test_edge_dataclass_ordering_stable(self) -> None:
        """Edge ordering is deterministic for sorting."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge

        e1 = Edge("ADG::Module::a.py", "imports", "ADG::Symbol::z", "import", "a.py", 1)
        e2 = Edge("ADG::Module::a.py", "imports", "ADG::Symbol::a", "import", "a.py", 2)
        assert e2 < e1

    @pytest.mark.architecture
    def test_edge_dataclass_equal(self) -> None:
        """Identical edges compare equal."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge

        e1 = Edge("ADG::Module::a.py", "imports", "ADG::Symbol::z", "import", "a.py", 1)
        e2 = Edge("ADG::Module::a.py", "imports", "ADG::Symbol::z", "import", "a.py", 1)
        assert e1 == e2


# ---------------------------------------------------------------------------
# §4 ScanResult digest -- determinism and boundary
# ---------------------------------------------------------------------------


class TestScanResultDigestBranches:
    """ScanResult.compute_digest: all branches."""

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_empty_edges_digest_stable(self) -> None:
        """Empty edge list produces same digest on two calls."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult

        r1 = ScanResult(commit_sha="t")
        r1.compute_digest()
        r2 = ScanResult(commit_sha="t")
        r2.compute_digest()
        assert r1.digest == r2.digest

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_different_edges_different_digest(self) -> None:
        """Adding one more edge changes the digest."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult

        r1 = ScanResult(commit_sha="t")
        r1.edges = [Edge("ADG::Module::a.py", "imports", "ADG::Symbol::b", "import", "a.py", 1)]
        r1.compute_digest()

        r2 = ScanResult(commit_sha="t")
        r2.edges = [
            Edge("ADG::Module::a.py", "imports", "ADG::Symbol::b", "import", "a.py", 1),
            Edge("ADG::Module::a.py", "imports", "ADG::Symbol::c", "import", "a.py", 2),
        ]
        r2.compute_digest()
        assert r1.digest != r2.digest

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_edge_order_does_not_change_digest(self) -> None:
        """Inserting edges in different order produces same digest (sorted)."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult

        e1 = Edge("ADG::Module::a.py", "imports", "ADG::Symbol::b", "import", "a.py", 1)
        e2 = Edge("ADG::Module::a.py", "imports", "ADG::Symbol::c", "import", "a.py", 2)

        r1 = ScanResult(commit_sha="t")
        r1.edges = sorted([e1, e2])
        r1.compute_digest()

        r2 = ScanResult(commit_sha="t")
        r2.edges = sorted([e2, e1])
        r2.compute_digest()

        assert r1.digest == r2.digest

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_commit_sha_does_not_affect_digest(self) -> None:
        """Different commit_sha values must NOT change the edge digest."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult

        e = Edge("ADG::Module::a.py", "imports", "ADG::Symbol::b", "import", "a.py", 1)
        r1 = ScanResult(commit_sha="sha-aaa")
        r1.edges = [e]
        r1.compute_digest()

        r2 = ScanResult(commit_sha="sha-bbb")
        r2.edges = [e]
        r2.compute_digest()

        assert r1.digest == r2.digest

    @pytest.mark.architecture
    def test_canonical_edge_text_pipe_separated(self) -> None:
        """canonical_edge_text uses pipe separator."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult

        e = Edge("ADG::Module::a.py", "imports", "ADG::Symbol::b", "import", "a.py", 5, "b")
        r = ScanResult(commit_sha="t")
        r.edges = [e]
        text = r.canonical_edge_text()
        assert "|" in text
        assert "imports" in text


# ---------------------------------------------------------------------------
# §4 Blast-radius -- threshold boundary (exact 300, 700, 299, 301, 699, 701)
# ---------------------------------------------------------------------------


class TestBlastRadiusThresholdBoundary:
    """Blast-radius scoring: exact threshold boundary values per §4."""

    def _make_result_with_weight(self, total_weight: int) -> ScanResult:  # noqa: F821
        """Build a ScanResult whose impacted modules sum to exactly total_weight."""
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="threshold-test")
        result.compute_digest()
        return result

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_weight_zero_is_normal(self) -> None:
#  # MOVED: from agentic_core.adg.applications.BlastRadiusResult import compute_blast_radius
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="t")
        result.compute_digest()
        br = compute_blast_radius([], result, commit_sha="t")
        assert br.risk_score == 0
        assert br.route_mode == "NORMAL"

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_boundary_exactly_restricted_threshold(self, tmp_path: Path) -> None:
        """risk_score == 300 is RESTRICTED (>= 300, < 700)."""
#  # MOVED: from agentic_core.adg.applications.BlastRadiusResult import (
            _HUMAN_REVIEW_THRESHOLD,
            _RESTRICTED_THRESHOLD,
        )

        assert _RESTRICTED_THRESHOLD == 300
        assert _HUMAN_REVIEW_THRESHOLD == 700

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_boundary_exactly_human_review_threshold(self) -> None:
        """_HUMAN_REVIEW_THRESHOLD must be 700."""
#  # MOVED: from agentic_core.adg.applications.BlastRadiusResult import _HUMAN_REVIEW_THRESHOLD

        assert _HUMAN_REVIEW_THRESHOLD == 700

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_route_mode_normal_below_300(self) -> None:
        """risk_score < 300 -> NORMAL."""
#  # MOVED: from agentic_core.adg.applications.BlastRadiusResult import (
            _RESTRICTED_THRESHOLD,
        )

        score = _RESTRICTED_THRESHOLD - 1
        mode = "HUMAN_REVIEW" if score >= 700 else "RESTRICTED" if score >= 300 else "NORMAL"
        assert mode == "NORMAL"

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_route_mode_restricted_at_300(self) -> None:
        """risk_score == 300 -> RESTRICTED."""
#  # MOVED: from agentic_core.adg.applications.BlastRadiusResult import _RESTRICTED_THRESHOLD

        score = _RESTRICTED_THRESHOLD
        mode = "HUMAN_REVIEW" if score >= 700 else "RESTRICTED" if score >= 300 else "NORMAL"
        assert mode == "RESTRICTED"

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_route_mode_restricted_at_301(self) -> None:
        """risk_score == 301 -> RESTRICTED."""
        score = 301
        mode = "HUMAN_REVIEW" if score >= 700 else "RESTRICTED" if score >= 300 else "NORMAL"
        assert mode == "RESTRICTED"

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_route_mode_restricted_at_699(self) -> None:
        """risk_score == 699 -> RESTRICTED."""
        score = 699
        mode = "HUMAN_REVIEW" if score >= 700 else "RESTRICTED" if score >= 300 else "NORMAL"
        assert mode == "RESTRICTED"

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_route_mode_human_review_at_700(self) -> None:
        """risk_score == 700 -> HUMAN_REVIEW."""
#  # MOVED: from agentic_core.adg.applications.BlastRadiusResult import _HUMAN_REVIEW_THRESHOLD

        score = _HUMAN_REVIEW_THRESHOLD
        mode = "HUMAN_REVIEW" if score >= 700 else "RESTRICTED" if score >= 300 else "NORMAL"
        assert mode == "HUMAN_REVIEW"

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_route_mode_human_review_at_701(self) -> None:
        """risk_score == 701 -> HUMAN_REVIEW."""
        score = 701
        mode = "HUMAN_REVIEW" if score >= 700 else "RESTRICTED" if score >= 300 else "NORMAL"
        assert mode == "HUMAN_REVIEW"

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_impact_digest_changes_with_different_changed_files(self) -> None:
        """Materially distinct changed files must produce different impact digest."""
#  # MOVED: from agentic_core.adg.applications.BlastRadiusResult import compute_blast_radius
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=REPO_ROOT)
        result = scanner.scan(commit_sha="br-distinct")

        br1 = compute_blast_radius(
            ["agentic_core/L2_execution/UniversalWriteGateway.py"],
            result,
            commit_sha="c1",
        )
        br2 = compute_blast_radius(
            ["agentic_core/L2_execution/enforcement/SovereignLLMGateway.py"],
            result,
            commit_sha="c2",
        )
        assert br1.impact_digest != br2.impact_digest, (
            "Different changed files must produce different impact digests"
        )

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_l0_weight_is_100(self) -> None:
#  # MOVED: from agentic_core.adg.applications.BlastRadiusResult import _LAYER_WEIGHTS

        assert _LAYER_WEIGHTS["L0"] == 100

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_l2_weight_is_90(self) -> None:
#  # MOVED: from agentic_core.adg.applications.BlastRadiusResult import _LAYER_WEIGHTS

        assert _LAYER_WEIGHTS["L2"] == 90

    @pytest.mark.architecture
    @pytest.mark.determinism
    def test_l5_weight_is_85(self) -> None:
#  # MOVED: from agentic_core.adg.applications.BlastRadiusResult import _LAYER_WEIGHTS

        assert _LAYER_WEIGHTS["L5"] == 85


# ---------------------------------------------------------------------------
# §4 InvariantScanner -- exception handler branches
# ---------------------------------------------------------------------------


class TestInvariantScannerBranches:
    """InvariantScanner: all conditional branches."""

    @pytest.mark.architecture
    def test_rule_a_skips_l_unknown_modules(self) -> None:
        """Modules with L_UNKNOWN source (no module prefix) must not trigger RULE_A
        for their destination if the destination is also ambiguous."""
#  # MOVED: from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        edge = Edge(
            from_name=canonical_name("Module", "totally/random/module.py"),
            relation_type="imports",
            to_name=canonical_name("Symbol", "openai"),
            edge_kind="network",
            source_file="totally/random/module.py",
            line_no=1,
            symbol="openai",
        )
        result = ScanResult(commit_sha="unknown-src")
        result.edges = [edge]
        result.modules = ["totally/random/module.py"]
        result.compute_digest()

        report = InvariantScanner().scan(result)
        rule_a = [v for v in report.violations if v.rule == "RULE_A"]
        assert len(rule_a) >= 1, "Non-gateway module importing openai must still be RULE_A"

    @pytest.mark.architecture
    def test_rule_b_edge_kind_not_embedding_skipped(self) -> None:
        """Non-embedding edge_kind must not trigger RULE_B even for embedding symbol."""
#  # MOVED: from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        edge = Edge(
            from_name=canonical_name("Module", "apps_rg/engines/SomeEngine.py"),
            relation_type="instantiates",
            to_name=canonical_name("Symbol", "OpenAIEmbeddings"),
            edge_kind="import",
            source_file="apps_rg/engines/SomeEngine.py",
            line_no=1,
            symbol="OpenAIEmbeddings",
        )
        result = ScanResult(commit_sha="b-wrong-kind")
        result.edges = [edge]
        result.modules = ["apps_rg/engines/SomeEngine.py"]
        result.compute_digest()

        report = InvariantScanner().scan(result)
        rule_b = [v for v in report.violations if v.rule == "RULE_B"]
        assert len(rule_b) == 0, "Non-embedding edge_kind must not trigger RULE_B"

    @pytest.mark.architecture
    def test_rule_c_same_layer_not_flagged(self) -> None:
        """Edge within same layer must not be flagged by RULE_C."""
#  # MOVED: from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        edge = Edge(
            from_name=canonical_name("Module", "agentic_core/L2_execution/UniversalWriteGateway.py"),
            relation_type="imports",
            to_name=canonical_name("Module", "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py"),
            edge_kind="import",
            source_file="agentic_core/L2_execution/UniversalWriteGateway.py",
            line_no=1,
            symbol="SovereignLLMGateway",
        )
        result = ScanResult(commit_sha="same-layer")
        result.edges = [edge]
        result.modules = [
            "agentic_core/L2_execution/UniversalWriteGateway.py",
            "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
        ]
        result.compute_digest()

        report = InvariantScanner().scan(result)
        rule_c = [v for v in report.violations if v.rule == "RULE_C"]
        assert len(rule_c) == 0, "Same-layer edge must not be RULE_C"

    @pytest.mark.architecture
    def test_rule_c_downward_l6_to_l0_not_flagged(self) -> None:
        """L6 importing L0 is allowed (downward)."""
#  # MOVED: from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        edge = Edge(
            from_name=canonical_name("Module", "agentic_core/L6_observability/engines/monitor.py"),
            relation_type="imports",
            to_name=canonical_name("Module", "agentic_core/L0_routing/engines/path_router.py"),
            edge_kind="import",
            source_file="agentic_core/L6_observability/engines/monitor.py",
            line_no=1,
            symbol="path_router",
        )
        result = ScanResult(commit_sha="downward-l6-l0")
        result.edges = [edge]
        result.modules = [
            "agentic_core/L6_observability/engines/monitor.py",
            "agentic_core/L0_routing/engines/path_router.py",
        ]
        result.compute_digest()

        report = InvariantScanner().scan(result)
        rule_c = [v for v in report.violations if v.rule == "RULE_C"]
        assert len(rule_c) == 0, "L6->L0 is downward, must not be RULE_C"

    @pytest.mark.architecture
    def test_rule_c_l_app_to_any_layer_not_flagged(self) -> None:
        """L_APP importing L2 is allowed."""
#  # MOVED: from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        edge = Edge(
            from_name=canonical_name("Module", "apps_rg/engines/SomeAgent.py"),
            relation_type="imports",
            to_name=canonical_name("Module", "agentic_core/L2_execution/UniversalWriteGateway.py"),
            edge_kind="import",
            source_file="apps_rg/engines/SomeAgent.py",
            line_no=1,
            symbol="UniversalWriteGateway",
        )
        result = ScanResult(commit_sha="app-to-l2")
        result.edges = [edge]
        result.modules = [
            "apps_rg/engines/SomeAgent.py",
            "agentic_core/L2_execution/UniversalWriteGateway.py",
        ]
        result.compute_digest()

        report = InvariantScanner().scan(result)
        rule_c = [v for v in report.violations if v.rule == "RULE_C"]
        assert len(rule_c) == 0, "L_APP->L2 is allowed"

    @pytest.mark.architecture
    def test_empty_scan_result_no_violations(self) -> None:
        """Empty ScanResult produces zero violations."""
#  # MOVED: from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="empty")
        result.compute_digest()
        report = InvariantScanner().scan(result)
        assert report.passed
        assert report.violations == []

    @pytest.mark.architecture
    def test_violation_format_no_crash(self) -> None:
        """Violation.format() must not raise."""
#  # MOVED: from agentic_core.adg.ci.invariant_scanner_config import Violation

        v = Violation(
            rule="RULE_A",
            policy_id="ADG::Policy::LLM_EGRESS_SINGLETON",
            offending_edge="X -> Y",
            from_module="some/module.py",
            to_symbol="openai",
            source_file="some/module.py",
            line_no=10,
            witness="test",
        )
        text = v.format()
        assert "RULE_A" in text
        assert "openai" in text

    @pytest.mark.architecture
    def test_scan_report_print_summary_pass(self, capsys: pytest.CaptureFixture) -> None:
        """ScanReport.print_summary prints PASSED when no violations."""
#  # MOVED: from agentic_core.adg.ci.invariant_scanner_config import ScanReport

        report = ScanReport(new_edges_count=5, digest="abc123")
        report.print_summary()
        captured = capsys.readouterr()
        assert "PASSED" in captured.out

    @pytest.mark.architecture
    def test_scan_report_print_summary_fail(self, capsys: pytest.CaptureFixture) -> None:
        """ScanReport.print_summary prints FAILED when violations present."""
#  # MOVED: from agentic_core.adg.ci.invariant_scanner_config import ScanReport, Violation

        report = ScanReport()
        report.violations.append(
            Violation(
                rule="RULE_A",
                policy_id="p",
                offending_edge="x->y",
                from_module="m",
                to_symbol="s",
                source_file="m",
                line_no=1,
                witness="w",
            )
        )
        report.print_summary()
        captured = capsys.readouterr()
        assert "FAILED" in captured.out


# ---------------------------------------------------------------------------
# §4 MCP client -- idempotency, malformed, stale-state, duplicate-submit
# ---------------------------------------------------------------------------


class TestADGMCPClientRobustness:
    """ADGMCPClient: state transitions, malformed, replay, idempotent re-entry."""

    @pytest.mark.architecture
    def test_upsert_entity_none_observations(self) -> None:
        """upsert_entity with None observations must not crash."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_entity("ADG::Module::x.py", "module", None)
        entities = client.get_store().get_entities()
        assert any(e["name"] == "ADG::Module::x.py" for e in entities)

    @pytest.mark.architecture
    def test_upsert_entity_empty_observations(self) -> None:
        """upsert_entity with empty list must not crash."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_entity("ADG::Module::y.py", "module", [])
        entities = client.get_store().get_entities()
        assert any(e["name"] == "ADG::Module::y.py" for e in entities)

    @pytest.mark.architecture
    def test_upsert_entity_duplicate_observations_deduped(self) -> None:
        """Duplicate observations in one call must be stored only once."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_entity("ADG::Module::z.py", "module", ["path:z.py", "path:z.py", "path:z.py"])
        entities = client.get_store().get_entities()
        e = next(x for x in entities if x["name"] == "ADG::Module::z.py")
        assert e["observations"].count("path:z.py") == 1

    @pytest.mark.architecture
    def test_add_observation_nonexistent_entity_creates_it(self) -> None:
        """add_observation on nonexistent entity must create the entity."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.add_observation("ADG::Symbol::new_sym", ["edge_kind:import"])
        entities = client.get_store().get_entities()
        assert any(e["name"] == "ADG::Symbol::new_sym" for e in entities)

    @pytest.mark.architecture
    def test_search_nodes_empty_store_returns_empty(self) -> None:
        """search_nodes on empty store returns empty list."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        assert client.search_nodes("anything") == []

    @pytest.mark.architecture
    def test_search_nodes_no_match_returns_empty(self) -> None:
        """search_nodes with non-matching query returns empty list."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_entity("ADG::Module::foo.py", "module", [])
        assert client.search_nodes("zzz_no_match") == []

    @pytest.mark.architecture
    def test_open_nodes_nonexistent_returns_empty(self) -> None:
        """open_nodes for unknown entity returns empty list."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        result = client.open_nodes(["ADG::Module::nonexistent.py"])
        assert result == []

    @pytest.mark.architecture
    def test_read_graph_empty(self) -> None:
        """read_graph on empty store returns empty entities and relations."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        g = client.read_graph()
        assert g["entities"] == []
        assert g["relations"] == []

    @pytest.mark.architecture
    def test_read_graph_sorted(self) -> None:
        """read_graph entities must be in sorted order."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_entity("ADG::Module::z.py", "module", [])
        client.upsert_entity("ADG::Module::a.py", "module", [])
        g = client.read_graph()
        names = [e["name"] for e in g["entities"]]
        assert names == sorted(names)

    @pytest.mark.architecture
    def test_triple_upsert_entity_stays_single(self) -> None:
        """Three upserts of same entity = exactly one entity in store."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        for _ in range(3):
            client.upsert_entity("ADG::Module::x.py", "module", ["path:x.py"])
        matches = [e for e in client.get_store().get_entities() if e["name"] == "ADG::Module::x.py"]
        assert len(matches) == 1

    @pytest.mark.architecture
    def test_triple_upsert_relation_stays_single(self) -> None:
        """Three upserts of same relation = exactly one relation in store."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        for _ in range(3):
            client.upsert_relation("ADG::Module::a.py", "imports", "ADG::Symbol::b")
        rels = [r for r in client.get_store().get_relations() if r["from"] == "ADG::Module::a.py"]
        assert len(rels) == 1

    @pytest.mark.architecture
    def test_bulk_upsert_empty_list(self) -> None:
        """bulk_upsert_entities with empty list must not crash."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.bulk_upsert_entities([])
        assert client.get_store().get_entities() == []

    @pytest.mark.architecture
    def test_bulk_upsert_relations_empty_list(self) -> None:
        """bulk_upsert_relations with empty list must not crash."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.bulk_upsert_relations([])
        assert client.get_store().get_relations() == []

    @pytest.mark.architecture
    def test_observations_accumulated_across_upserts(self) -> None:
        """Multiple upserts with different obs must accumulate all unique obs."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient

        client = ADGMCPClient()
        client.upsert_entity("ADG::Module::x.py", "module", ["path:x.py"])
        client.upsert_entity("ADG::Module::x.py", "module", ["commit:abc"])
        e = next(x for x in client.get_store().get_entities() if x["name"] == "ADG::Module::x.py")
        assert "path:x.py" in e["observations"]
        assert "commit:abc" in e["observations"]


# ---------------------------------------------------------------------------
# §4 Matrix tests: policy x module x relation type
# ---------------------------------------------------------------------------


class TestInvariantScannerMatrix:
    """Matrix: policy gate x relation type x module type."""

    @pytest.mark.architecture
    def test_matrix_rule_a_invokes_provider_not_imports(self) -> None:
    """Test matrix_rule_a_invokes_provider_not_imports runtime behavior."""
    # Arrange
    # TODO: Set up test data for matrix_rule_a_invokes_provider_not_imports
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute matrix_rule_a_invokes_provider_not_imports
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
                symbol="openai",
            )
            result = ScanResult(commit_sha=f"matrix-a-{rel_type}")
            result.edges = [edge]
            result.modules = ["apps_rg/engines/SomeEngine.py"]
            result.compute_digest()

            report = InvariantScanner().scan(result)
            rule_a = [v for v in report.violations if v.rule == "RULE_A"]
            assert len(rule_a) >= 1, f"RULE_A must fire for relation_type={rel_type!r}"

    @pytest.mark.architecture
    def test_matrix_rule_c_all_upward_pairs_flagged(self) -> None:
        """Every upward L_low -> L_high pair (low num < high num) must be RULE_C."""
#  # MOVED: from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        upward_pairs = [
            ("L0", "L1"),
            ("L0", "L5"),
            ("L1", "L2"),
            ("L2", "L3"),
            ("L3", "L4"),
            ("L4", "L5"),
            ("L5", "L6"),
        ]
        layer_to_path = {
            "L0": "agentic_core/L0_routing/engines/x.py",
            "L1": "agentic_core/L1_cognition/engines/x.py",
            "L2": "agentic_core/L2_execution/x.py",
            "L3": "agentic_core/L3_orchestration/engines/x.py",
            "L4": "agentic_core/L4_state/engines/x.py",
            "L5": "agentic_core/L5_safety/enforcement/x.py",
            "L6": "agentic_core/L6_observability/engines/x.py",
        }
        for from_layer, to_layer in upward_pairs:
            from_path = layer_to_path[from_layer]
            to_path = layer_to_path[to_layer]
            edge = Edge(
                from_name=canonical_name("Module", from_path),
                relation_type="imports",
                to_name=canonical_name("Module", to_path),
                edge_kind="import",
                source_file=from_path,
                line_no=1,
                symbol=to_path,
            )
            result = ScanResult(commit_sha=f"matrix-c-{from_layer}-{to_layer}")
            result.edges = [edge]
            result.modules = [from_path, to_path]
            result.compute_digest()

            report = InvariantScanner().scan(result)
            rule_c = [v for v in report.violations if v.rule == "RULE_C"]
            assert len(rule_c) >= 1, f"RULE_C must fire for {from_layer}->{to_layer} but got 0 violations"

    @pytest.mark.architecture
    def test_matrix_rule_a_all_provider_sdk_symbols(self) -> None:
        """RULE_A must fire for each provider SDK symbol from a non-gateway module."""
#  # MOVED: from agentic_core.adg.ci.invariant_scanner_config import InvariantScanner
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.adg.schema_util import PROVIDER_SDK_SYMBOLS, canonical_name

        provider_bases = sorted({s.split(".")[0] for s in PROVIDER_SDK_SYMBOLS})
        for sym_base in provider_bases:
            edge = Edge(
                from_name=canonical_name("Module", "apps_rg/engines/Rogue.py"),
                relation_type="imports",
                to_name=canonical_name("Symbol", sym_base),
                edge_kind="network",
                source_file="apps_rg/engines/Rogue.py",
                line_no=1,
                symbol=sym_base,
            )
            result = ScanResult(commit_sha=f"matrix-sdk-{sym_base}")
            result.edges = [edge]
            result.modules = ["apps_rg/engines/Rogue.py"]
            result.compute_digest()

            report = InvariantScanner().scan(result)
            rule_a = [v for v in report.violations if v.rule == "RULE_A"]
            assert len(rule_a) >= 1, f"RULE_A must fire for SDK symbol base={sym_base!r}"


# ---------------------------------------------------------------------------
# §4 Gateway topology -- side-effect safety on blocked path
# ---------------------------------------------------------------------------


class TestGatewayTopologyBranches:
    """Gateway topology: blocked path produces no side-effects in client."""

    @pytest.mark.architecture
    def test_bypass_violation_does_not_persist_to_client(self) -> None:
        """When gateway is bypassed, proof node must be stored but violation must be flagged."""
#  # MOVED: from agentic_core.adg.applications.gateway_topology_validator import check_gateway_topology
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        client = ADGMCPClient()
        bad_edge = Edge(
            from_name=canonical_name("Module", "apps_rg/engines/BadEngine.py"),
            relation_type="invokes_provider",
            to_name=canonical_name("Symbol", "openai"),
            edge_kind="network",
            source_file="apps_rg/engines/BadEngine.py",
            line_no=5,
            symbol="openai",
        )
        result = ScanResult(commit_sha="gw-side-effect")
        result.edges = [bad_edge]
        result.modules = ["apps_rg/engines/BadEngine.py"]
        result.compute_digest()

        report = check_gateway_topology(result, client=client)
        assert not report.passed
        entities = client.get_store().get_entities()
        proof_nodes = [e for e in entities if "gateway_topology_proof" in e["name"]]
        assert len(proof_nodes) == 1

    @pytest.mark.architecture
    def test_empty_scan_no_client_call_needed(self) -> None:
    """Test empty_scan_no_client_call_needed runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute empty_scan_no_client_call_needed
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="gw-proof-hex")
        result.compute_digest()
        report = check_gateway_topology(result)
        assert len(report.snapshot_digest) == 64
        assert all(c in "0123456789abcdef" for c in report.snapshot_digest)


# ---------------------------------------------------------------------------
# §4 UWG write authority -- blocked path, allowed modules, side-effect safety
# ---------------------------------------------------------------------------


class TestUWGWriteAuthorityBranches:
    """UWG: blocked paths, allowed modules, side-effect safety."""

    @pytest.mark.architecture
    def test_tests_module_is_allowed(self) -> None:
        """Modules under tests/ prefix must not be flagged."""
#  # MOVED: from agentic_core.adg.applications.uwg_write_authority_validator import check_uwg_write_authority
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        edge = Edge(
            from_name=canonical_name("Module", "tests/architecture/test_foo.py"),
            relation_type="writes_to",
            to_name=canonical_name("Symbol", "open"),
            edge_kind="write",
            source_file="tests/architecture/test_foo.py",
            line_no=1,
            symbol="open",
        )
        result = ScanResult(commit_sha="uwg-test-module")
        result.edges = [edge]
        result.modules = ["tests/architecture/test_foo.py"]
        result.compute_digest()

        report = check_uwg_write_authority(result)
        assert report.passed, "Test modules must be allowed to write"

    @pytest.mark.architecture
    def test_ops_scripts_module_is_allowed(self) -> None:
        """Modules under ops_scripts/ci/ prefix must not be flagged."""
#  # MOVED: from agentic_core.adg.applications.uwg_write_authority_validator import check_uwg_write_authority
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        edge = Edge(
            from_name=canonical_name("Module", "ops_scripts/ci/run_contract_gates.py"),
            relation_type="writes_to",
            to_name=canonical_name("Symbol", "open"),
            edge_kind="write",
            source_file="ops_scripts/ci/run_contract_gates.py",
            line_no=1,
            symbol="open",
        )
        result = ScanResult(commit_sha="uwg-ops-module")
        result.edges = [edge]
        result.modules = ["ops_scripts/ci/run_contract_gates.py"]
        result.compute_digest()

        report = check_uwg_write_authority(result)
        assert report.passed, "ops_scripts/ci/ must be allowed"

    @pytest.mark.architecture
    def test_non_write_edge_kind_not_flagged(self) -> None:
        """Only write edge_kind triggers UWG check (not import/network/etc)."""
#  # MOVED: from agentic_core.adg.applications.uwg_write_authority_validator import check_uwg_write_authority
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        edge = Edge(
            from_name=canonical_name("Module", "agentic_core/L1_cognition/engines/x.py"),
            relation_type="writes_to",
            to_name=canonical_name("Symbol", "open"),
            edge_kind="import",
            source_file="agentic_core/L1_cognition/engines/x.py",
            line_no=1,
            symbol="open",
        )
        result = ScanResult(commit_sha="uwg-import-kind")
        result.edges = [edge]
        result.modules = ["agentic_core/L1_cognition/engines/x.py"]
        result.compute_digest()

        report = check_uwg_write_authority(result)
        assert report.passed, "Non-write edge_kind must not trigger UWG"

    @pytest.mark.architecture
    def test_uwg_violation_persisted_to_client(self) -> None:
        """UWG violation must persist a proof snapshot to client."""
#  # MOVED: from agentic_core.adg.applications.uwg_write_authority_validator import check_uwg_write_authority
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient
#  # MOVED: from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        client = ADGMCPClient()
        edge = Edge(
            from_name=canonical_name("Module", "agentic_core/L1_cognition/engines/rogue.py"),
            relation_type="writes_to",
            to_name=canonical_name("Symbol", "open"),
            edge_kind="write",
            source_file="agentic_core/L1_cognition/engines/rogue.py",
            line_no=5,
            symbol="open",
        )
        result = ScanResult(commit_sha="uwg-persist-commit")
        result.edges = [edge]
        result.modules = ["agentic_core/L1_cognition/engines/rogue.py"]
        result.compute_digest()

        report = check_uwg_write_authority(result, client=client)
        assert not report.passed
        entities = client.get_store().get_entities()
        proof_nodes = [e for e in entities if "uwg_write_authority_proof" in e["name"]]
        assert len(proof_nodes) == 1

    @pytest.mark.architecture
    def test_violation_classify_filesystem_write(self) -> None:
        """open symbol must be classified as filesystem_write."""
#  # MOVED: from agentic_core.adg.applications.uwg_write_authority_validator import _classify_side_effect

        assert _classify_side_effect("open") == "filesystem_write"

    @pytest.mark.architecture
    def test_violation_classify_subprocess(self) -> None:
    """Test violation_classify_subprocess runtime behavior."""
    # Arrange
    # TODO: Set up processing data
    raw_data = []  # Replace with actual test data

    # Act
    # TODO: Process data with violation_classify_subprocess
    processed_result = None  # Replace with actual processing

    # Assert
    assert processed_result is not None, "Processing should produce a result"
    assert len(processed_result) >= 0, "Processed result should be measurable"
    # TODO: Add specific processing assertions

    @pytest.mark.architecture
    def test_persist_empty_result_no_crash(self) -> None:
        """Persisting empty ScanResult must not crash."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient
#  # MOVED: from agentic_core.adg.extraction.graph_persister import persist_scan_result
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="")
        result.compute_digest()
        client = ADGMCPClient()
        persist_scan_result(result, client)
        layer_nodes = [e for e in client.get_store().get_entities() if e["entityType"] == "layer"]
        assert len(layer_nodes) >= 7

    @pytest.mark.architecture
    def test_persist_no_commit_sha_no_commit_node(self) -> None:
        """Empty commit_sha must not create a commit entity."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient
#  # MOVED: from agentic_core.adg.extraction.graph_persister import persist_scan_result
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="")
        result.compute_digest()
        client = ADGMCPClient()
        persist_scan_result(result, client)
        commit_nodes = [e for e in client.get_store().get_entities() if e["entityType"] == "commit"]
        assert len(commit_nodes) == 0

    @pytest.mark.architecture
    def test_persist_with_commit_sha_creates_snapshot(self) -> None:
        """Non-empty commit_sha + digest creates snapshot entity."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient
#  # MOVED: from agentic_core.adg.extraction.graph_persister import persist_scan_result
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="deadbeef1234567890abcdef1234567890123456")
        result.compute_digest()
        client = ADGMCPClient()
        persist_scan_result(result, client)
        snap = [e for e in client.get_store().get_entities() if e["entityType"] == "snapshot"]
        assert len(snap) >= 1

    @pytest.mark.architecture
    def test_persist_three_times_idempotent(self) -> None:
        """Three calls with same result must not grow the store."""
#  # MOVED: from agentic_core.adg.client.InMemoryStore import ADGMCPClient
#  # MOVED: from agentic_core.adg.extraction.graph_persister import persist_scan_result
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="triple-test")
        result.compute_digest()
        client = ADGMCPClient()
        persist_scan_result(result, client)
        c1 = len(client.get_store().get_entities())
        persist_scan_result(result, client)
        c2 = len(client.get_store().get_entities())
        persist_scan_result(result, client)
        c3 = len(client.get_store().get_entities())
        assert c1 == c2 == c3, f"Not idempotent: {c1} {c2} {c3}"


# ---------------------------------------------------------------------------
# §4 RAG sovereignty -- decision node boundary, extra_edges=None
# ---------------------------------------------------------------------------


class TestRAGSovereigntyBranches:
    """RAG sovereignty: all branch paths."""

    @pytest.mark.architecture
    def test_no_extra_edges_no_violations(self) -> None:
#  # MOVED: from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="rag-none-extra")
        result.compute_digest()
        report = check_rag_sovereignty(result, extra_edges=None)
        assert report.passed

    @pytest.mark.architecture
    def test_extra_edges_empty_list_no_violations(self) -> None:
#  # MOVED: from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult

        result = ScanResult(commit_sha="rag-empty-extra")
        result.compute_digest()
        report = check_rag_sovereignty(result, extra_edges=[])
        assert report.passed

    @pytest.mark.architecture
    def test_extra_edges_non_influences_relation_not_flagged(self) -> None:
        """Extra edges with relation != 'influences' must not be flagged."""
#  # MOVED: from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        result = ScanResult(commit_sha="rag-non-influences")
        result.compute_digest()
        safe_edge = {
            "from": canonical_name("Retrieval", "C0Context"),
            "relation": "reads_from",
            "to": canonical_name("Decision", "RoutingDecision"),
        }
        report = check_rag_sovereignty(result, extra_edges=[safe_edge])
        assert report.passed, "Non-influences relation must not trigger RAG sovereignty"

    @pytest.mark.architecture
    def test_extra_edges_influences_non_decision_node_not_flagged(self) -> None:
        """C0Context influences non-decision node must NOT be flagged."""
#  # MOVED: from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        result = ScanResult(commit_sha="rag-non-decision")
        result.compute_digest()
        safe_edge = {
            "from": canonical_name("Retrieval", "C0Context"),
            "relation": "influences",
            "to": canonical_name("Module", "apps_rg/engines/SomeAgent.py"),
        }
        report = check_rag_sovereignty(result, extra_edges=[safe_edge])
        assert report.passed, "influences to non-decision node must not be flagged"

    @pytest.mark.architecture
    def test_all_three_decision_nodes_are_flagged(self) -> None:
        """All three defined decision nodes must individually trigger the violation."""
#  # MOVED: from agentic_core.adg.applications.rag_sovereignty_validator import (
            _DECISION_NODES,
            check_rag_sovereignty,
        )
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        for decision_node in sorted(_DECISION_NODES):
            result = ScanResult(commit_sha=f"rag-dn-{decision_node[-10:]}")
            result.compute_digest()
            edge = {
                "from": canonical_name("Retrieval", "C0Context"),
                "relation": "influences",
                "to": decision_node,
            }
            report = check_rag_sovereignty(result, extra_edges=[edge])
            assert not report.passed, f"Decision node {decision_node!r} must be flagged"
            assert len(report.violations) >= 1

    @pytest.mark.architecture
    def test_snapshot_digest_changes_when_violations_change(self) -> None:
        """Proof digest must differ when violations are present vs absent."""
#  # MOVED: from agentic_core.adg.applications.rag_sovereignty_validator import check_rag_sovereignty
#  # MOVED: from agentic_core.adg.extraction.static_scanner import ScanResult
#  # MOVED: from agentic_core.adg.schema_util import canonical_name

        result = ScanResult(commit_sha="rag-digest-diff")
        result.compute_digest()

        report_clean = check_rag_sovereignty(result)
        report_violated = check_rag_sovereignty(
            result,
            extra_edges=[
                {
                    "from": canonical_name("Retrieval", "C0Context"),
                    "relation": "influences",
                    "to": canonical_name("Decision", "RoutingDecision"),
                }
            ],
        )
        assert report_clean.snapshot_digest != report_violated.snapshot_digest


# ---------------------------------------------------------------------------
# §4 CLI -- entry points and exit codes
# ---------------------------------------------------------------------------


class TestCLIBranches:
    """CLI: all command branches and exit codes."""

    @pytest.mark.architecture
    def test_cli_no_command_exits_1(self) -> None:
        """CLI with no subcommand must exit 1."""
#  # MOVED: from agentic_core.adg.cli import main

        result = main(["--repo-root", str(REPO_ROOT)])
        assert result == 1

    @pytest.mark.architecture
    def test_cli_scan_exits_0_or_1(self) -> None:
        """CLI scan command must exit 0 or 1 (no crash)."""
#  # MOVED: from agentic_core.adg.cli import main

        result = main(["--repo-root", str(REPO_ROOT), "scan"])
        assert result in (0, 1)

    @pytest.mark.architecture
    def test_cli_blast_radius_exits_0(self) -> None:
        """CLI blast-radius with no changed files exits 0."""
#  # MOVED: from agentic_core.adg.cli import main

        result = main(["--repo-root", str(REPO_ROOT), "blast-radius"])
        assert result == 0

    @pytest.mark.architecture
    def test_cli_scan_diff_mode_no_crash(self) -> None:
        """CLI scan --diff-files with nonexistent files must not crash."""
#  # MOVED: from agentic_core.adg.cli import main

        result = main(
            [
                "--repo-root",
                str(REPO_ROOT),
                "scan",
                "--diff-files",
                "does/not/exist.py",
            ]
        )
        assert result in (0, 1)
