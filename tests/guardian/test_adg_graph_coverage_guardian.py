"""H9 / Guardian integration test — ADG graph coverage.

Asserts all 6 graph types produce minimum evidence and all policies pass.
Plan ref: tests/guardian/test_adg_graph_coverage_guardian.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.adg.extraction.static_scanner import (
    ADGStaticScanner,
    ScanResult,
    run_scanner_self_test,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_adg_graph_coverage_guardian", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_graph_coverage_guardian", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_graph_coverage_guardian", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_graph_coverage_guardian", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_graph_coverage_guardian", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_graph_coverage_guardian", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_graph_coverage_guardian", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_graph_coverage_guardian", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_graph_coverage_guardian", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_graph_coverage_guardian", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_graph_coverage_guardian", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_graph_coverage_guardian", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_graph_coverage_guardian", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_graph_coverage_guardian", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_graph_coverage_guardian", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_graph_coverage_guardian", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_graph_coverage_guardian", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_graph_coverage_guardian", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_graph_coverage_guardian", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_graph_coverage_guardian", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_graph_coverage_guardian", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_graph_coverage_guardian", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_graph_coverage_guardian", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_graph_coverage_guardian", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_graph_coverage_guardian", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_graph_coverage_guardian", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_graph_coverage_guardian", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_graph_coverage_guardian", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_graph_coverage_guardian")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_graph_coverage_guardian", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_graph_coverage_guardian", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_graph_coverage_guardian", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_adg_graph_coverage_guardian", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_graph_coverage_guardian", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_graph_coverage_guardian", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_graph_coverage_guardian", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_adg_graph_coverage_guardian", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_graph_coverage_guardian", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_graph_coverage_guardian", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_graph_coverage_guardian", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_graph_coverage_guardian", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_graph_coverage_guardian", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_graph_coverage_guardian", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_graph_coverage_guardian", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_graph_coverage_guardian", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_graph_coverage_guardian", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_graph_coverage_guardian", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_graph_coverage_guardian", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_graph_coverage_guardian", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_graph_coverage_guardian", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_graph_coverage_guardian", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_graph_coverage_guardian", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_graph_coverage_guardian")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_graph_coverage_guardian", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_graph_coverage_guardian")
# REMOVED: emit_determinism_digest("p0", "test_adg_graph_coverage_guardian")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_graph_coverage_guardian", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_graph_coverage_guardian", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_graph_coverage_guardian", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_graph_coverage_guardian", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_graph_coverage_guardian", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_graph_coverage_guardian", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_graph_coverage_guardian", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_graph_coverage_guardian", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_graph_coverage_guardian", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_graph_coverage_guardian", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_graph_coverage_guardian", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_graph_coverage_guardian", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_graph_coverage_guardian", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_graph_coverage_guardian", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_graph_coverage_guardian", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_graph_coverage_guardian", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_graph_coverage_guardian", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_graph_coverage_guardian", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_graph_coverage_guardian", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_graph_coverage_guardian", "exec_snapshot_link")

_REPO_ROOT = Path(__file__).resolve().parents[2]

# Minimum evidence floors per graph (matches plan A2)
_EVIDENCE_FLOORS = {
    "imports": 500,
    "implements": 100,
    "reads_from": 50,
    "instantiates": 50,
    # GA: behavioral anti-pattern graph (emitted by _AntipatternVisitor)
    "antipattern": 1,
    # GT: test traceability graph
    "covers": 100,
}


@pytest.fixture(scope="module")
def scan_result() -> ScanResult:
    scanner = ADGStaticScanner(repo_root=_REPO_ROOT, include_tests=True)
    return scanner.scan()


class TestScannerSelfTest:
    """S1: Scanner self-test must pass before any graph analysis."""

    def test_self_test_passes(self):
        assert run_scanner_self_test() is True


class TestManifestCompleteness:
    """A1: ScanManifest fields must be populated."""

    def test_scanner_version_set(self, scan_result):
        assert scan_result.manifest.scanner_version == "2.0.0"

    def test_python_ast_version_set(self, scan_result):
        assert scan_result.manifest.python_ast_version != ""

    def test_parsed_modules_nonzero(self, scan_result):
        """A3: Zero-parsed-file check."""
        assert scan_result.manifest.parsed_module_count > 0

    def test_self_test_passed_in_manifest(self, scan_result):
        assert scan_result.manifest.scanner_self_test_passed is True

    def test_tests_included_flag(self, scan_result):
        assert scan_result.manifest.tests_included is True


class TestGraphEvidenceFloors:
    """A2: Minimum evidence floors for all 6 graph types."""

    def test_imports_floor(self, scan_result):
        counts = scan_result.edge_counts_by_relation()
        actual = counts.get("imports", 0)
        assert actual >= _EVIDENCE_FLOORS["imports"], (
            f"imports graph: {actual} edges < floor {_EVIDENCE_FLOORS['imports']}"
        )

    def test_implements_floor(self, scan_result):
        counts = scan_result.edge_counts_by_relation()
        actual = counts.get("implements", 0)
        assert actual >= _EVIDENCE_FLOORS["implements"], (
            f"implements graph: {actual} edges < floor {_EVIDENCE_FLOORS['implements']}"
        )

    def test_reads_from_floor(self, scan_result):
        counts = scan_result.edge_counts_by_relation()
        actual = counts.get("reads_from", 0)
        assert actual >= _EVIDENCE_FLOORS["reads_from"], (
            f"reads_from graph: {actual} edges < floor {_EVIDENCE_FLOORS['reads_from']}"
        )

    def test_instantiates_floor(self, scan_result):
        counts = scan_result.edge_counts_by_relation()
        actual = counts.get("instantiates", 0)
        assert actual >= _EVIDENCE_FLOORS["instantiates"], (
            f"instantiates graph: {actual} edges < floor {_EVIDENCE_FLOORS['instantiates']}"
        )

    def test_antipattern_floor(self, scan_result):
        """GA: _AntipatternVisitor must have found at least one behavioral anti-pattern."""
        counts = scan_result.edge_counts_by_relation()
        actual = counts.get("antipattern", 0)
        assert actual >= _EVIDENCE_FLOORS["antipattern"], (
            f"antipattern graph: {actual} edges < floor {_EVIDENCE_FLOORS['antipattern']}"
        )

    def test_covers_floor(self, scan_result):
        """GT: Test traceability graph must have minimum covers edges."""
        counts = scan_result.edge_counts_by_relation()
        actual = counts.get("covers", 0)
        assert actual >= _EVIDENCE_FLOORS["covers"], (
            f"covers graph: {actual} edges < floor {_EVIDENCE_FLOORS['covers']}"
        )


class TestGraphCoverage:
    """All 6 graph types must be present in a full scan."""

    def test_g1_imports_present(self, scan_result):
        relation_types = {e.relation_type for e in scan_result.edges}
        assert "imports" in relation_types

    def test_g3_implements_present(self, scan_result):
        relation_types = {e.relation_type for e in scan_result.edges}
        assert "implements" in relation_types

    def test_g5_reads_from_present(self, scan_result):
        relation_types = {e.relation_type for e in scan_result.edges}
        assert "reads_from" in relation_types

    def test_g6_instantiates_present(self, scan_result):
        relation_types = {e.relation_type for e in scan_result.edges}
        assert "instantiates" in relation_types

    def test_digest_deterministic(self, scan_result):
        """S7: Digest must be a 64-hex SHA256."""
        assert len(scan_result.digest) == 64
        assert all(c in "0123456789abcdef" for c in scan_result.digest)

    def test_no_cardinality_violations(self, scan_result):
        """S9: No cardinality violations in full scan."""
        assert scan_result.manifest.cardinality_violations == [], (
            f"Cardinality violations: {scan_result.manifest.cardinality_violations}"
        )

    def test_minimum_evidence_passed(self, scan_result):
        """A2: manifest flag must be True."""
        assert scan_result.manifest.minimum_evidence_passed is True


class TestLayerLabelCoverage:
    """H2/S4: No L_UNKNOWN modules after label mapping."""

    def test_unknown_layer_count_zero_or_low(self, scan_result):
        """After H2 mapping, unknown count should be very low (external deps only)."""
        assert scan_result.manifest.unknown_layer_count < 50, (
            f"Too many L_UNKNOWN modules: {scan_result.manifest.unknown_layer_count}"
        )


class TestAntipatternCoverage:
    """GA: Behavioral anti-pattern graph must be populated."""

    def test_antipattern_edges_present(self, scan_result):
        """GA: at least one antipattern edge must be produced in the full repo scan."""
        relation_types = {e.relation_type for e in scan_result.edges}
        assert "antipattern" in relation_types, (
            "No antipattern edges found — _AntipatternVisitor may be broken"
        )

    def test_antipattern_edge_kinds_are_known(self, scan_result):
        """GA: every antipattern edge_kind must be one of the four declared kinds."""
        known_kinds = {
            "silent_exception_swallow",
            "blocking_call_in_async",
            "global_state_mutation",
            "retry_without_backoff",
        }
        bad = [
            e for e in scan_result.edges
            if e.relation_type == "antipattern" and e.edge_kind not in known_kinds
        ]
        assert bad == [], f"Unknown antipattern edge_kinds: {[b.edge_kind for b in bad[:5]]}"

    def test_antipattern_manifest_count_nonzero(self, scan_result):
        """GA: manifest.antipattern_count must be populated."""
        assert scan_result.manifest.antipattern_count > 0, (
            "manifest.antipattern_count is 0 — counting may be broken"
        )

    def test_antipattern_manifest_matches_edge_count(self, scan_result):
        """GA: manifest count must equal actual edge count."""
        actual = sum(1 for e in scan_result.edges if e.relation_type == "antipattern")
        assert scan_result.manifest.antipattern_count == actual, (
            f"manifest.antipattern_count={scan_result.manifest.antipattern_count} "
            f"but actual={actual}"
        )


class TestTestTraceabilityGraph:
    """GT: covers graph must be non-trivial."""

    def test_covers_edges_present(self, scan_result):
        """GT: covers edges must exist (test files import production modules)."""
        relation_types = {e.relation_type for e in scan_result.edges}
        assert "covers" in relation_types, "No covers edges found"

    def test_covers_sources_are_test_modules(self, scan_result):
        """GT: all covers edges must originate from test modules."""
        bad = [
            e for e in scan_result.edges
            if e.relation_type == "covers"
            and not any(ind in e.source_file for ind in ("tests/", "test_", "_test.py"))
        ]
        assert bad == [], (
            f"{len(bad)} covers edges originate from non-test files: "
            f"{[b.source_file for b in bad[:3]]}"
        )

    def test_covers_ratio_reasonable(self, scan_result):
        """GT: test_covers_count must exceed 1% of parsed module count (basic hygiene).

        covers edges point to ADG::Symbol:: targets (imported symbols), not Module nodes.
        We therefore compare manifest.test_covers_count against parsed_module_count.
        """
        covers_count = scan_result.manifest.test_covers_count
        total = scan_result.manifest.parsed_module_count
        if total == 0:
            pytest.skip("No modules parsed")
        ratio = covers_count / total
        assert ratio >= 0.01, (
            f"Too few covers edges relative to module count: "
            f"{covers_count} covers / {total} modules = {ratio:.1%} (need >= 1%)"
        )


class TestPromptSlotGraph:
    """E20: Prompt lifecycle graph — if prompt edges exist they must be well-formed.

    Tests skip gracefully when the repo contains no prompt-slot call sites yet.
    The schema/visitor wiring correctness is covered by unit tests in tests/adg/.
    """

    def test_prompt_slot_to_names_use_canonical_prefix(self, scan_result):
        """E20: generates_prompt to_name must follow ADG::PromptSlot:: prefix."""
        gen_edges = [e for e in scan_result.edges if e.relation_type == "generates_prompt"]
        if not gen_edges:
            pytest.skip("No generates_prompt edges in repo — visitor correctness tested in unit tests")
        bad = [e for e in gen_edges if not e.to_name.startswith("ADG::PromptSlot::")]
        assert bad == [], (
            f"{len(bad)} generates_prompt edges have wrong to_name prefix: "
            f"{[b.to_name for b in bad[:3]]}"
        )

    def test_consumes_prompt_to_names_use_canonical_prefix(self, scan_result):
        """E20: consumes_prompt to_name must follow ADG::PromptTemplate:: prefix."""
        con_edges = [e for e in scan_result.edges if e.relation_type == "consumes_prompt"]
        if not con_edges:
            pytest.skip("No consumes_prompt edges in repo — visitor correctness tested in unit tests")
        bad = [e for e in con_edges if not e.to_name.startswith("ADG::PromptTemplate::")]
        assert bad == [], (
            f"{len(bad)} consumes_prompt edges have wrong to_name prefix: "
            f"{[b.to_name for b in bad[:3]]}"
        )


class TestScannerWiring:
    """S1/A1: Verify that all visitors are wired into the main scan loop."""

    def test_all_graph_types_covered(self, scan_result):
        """Every declared graph type must produce at least one edge."""
        required_relations = {
            "imports",       # G1
            "implements",    # G3
            "reads_from",    # G5
            "instantiates",  # G6
            "violates",      # GV
            "covers",        # GT
            "antipattern",   # GA
        }
        present = {e.relation_type for e in scan_result.edges}
        missing = required_relations - present
        assert missing == set(), (
            f"Missing relation types in full scan: {sorted(missing)}"
        )

    def test_manifest_parse_failure_rate_low(self, scan_result):
        """A3: Parse failure rate must be below 1%."""
        total = scan_result.manifest.parsed_module_count
        failures = scan_result.manifest.syntax_error_count
        if total == 0:
            pytest.skip("No modules parsed")
        rate = failures / total
        assert rate < 0.01, (
            f"Parse failure rate too high: {failures}/{total} = {rate:.1%}"
        )
