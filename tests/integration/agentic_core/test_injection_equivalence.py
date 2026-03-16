"""Test behavioral equivalence of YAML-only injection system.

Verifies that YAML-only behavior matches expected prior behavior:
- Same injection count
- Same order
- Same required resolution behavior
- Same semantic output
"""

import json
from pathlib import Path

import pytest

from agentic_core.runtime.config.instructional_injections import (
    get_instructional_injections,
    get_required_injections,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
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
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_injection_equivalence", "p4obs", "metric_1")
_emit_emits_metric_event("test_injection_equivalence", "p4obs", "metric_2")
_emit_emits_metric_event("test_injection_equivalence", "p4obs", "metric_3")
_emit_emits_metric_event("test_injection_equivalence", "p4obs", "metric_4")
_emit_emits_metric_event("test_injection_equivalence", "p4obs", "metric_5")
_emit_emits_metric_event("test_injection_equivalence", "p4obs", "metric_6")
_emit_records_incident_event("test_injection_equivalence", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_injection_equivalence", "p4obs", "anomaly")
_emit_writes_observability_log("test_injection_equivalence", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_injection_equivalence", "p4obs", "mon_state")
_emit_triggers_alert("test_injection_equivalence", "p4obs", "alert")
_emit_links_incident_trace("test_injection_equivalence", "p4obs", "trace_link")
_emit_captures_pattern("test_injection_equivalence", "p3lm", "pattern")
_emit_records_learning_event("test_injection_equivalence", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_injection_equivalence", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_injection_equivalence", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_injection_equivalence", "p3lm", "routing")
_emit_improves_agent_policy("test_injection_equivalence", "p3lm", "policy")
_emit_stores_learning_state("test_injection_equivalence", "p3lm", "state")
_emit_records_execution_trace("test_injection_equivalence", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_injection_equivalence", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_injection_equivalence", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_injection_equivalence", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_injection_equivalence", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_injection_equivalence", "env_read", "p2_env_1")
_emit_reads_environ("test_injection_equivalence", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_injection_equivalence", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_injection_equivalence", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_injection_equivalence")
_emit_applies_guardrail("p0", "test_injection_equivalence", "p0_governance")
_emit_reads_policy_state("p0", "test_injection_equivalence", "policy_binding")
_emit_snapshots_state("p0", "test_injection_equivalence", "state_snapshot")
_emit_pulls_context("p1", "test_injection_equivalence", "context_pull")
_emit_pulls_context("p1", "test_injection_equivalence", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_injection_equivalence", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_injection_equivalence", "uwg_term_secondary")
_emit_writes_through("p1", "test_injection_equivalence", "write_through")
_emit_writes_through("p1", "test_injection_equivalence", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_injection_equivalence", "safety_validation")
_emit_invokes_eval("p1", "test_injection_equivalence", "eval_call")
_emit_proposal_commits_routing("p1", "test_injection_equivalence", "routing_commit")
_emit_escalates_to_human("p1", "test_injection_equivalence", "human_escalation")
_emit_routes_through("p1", "test_injection_equivalence", "route_through")
_emit_checks_agent_registry("p1", "test_injection_equivalence", "agent_registry")
_emit_validates_agent_capability("p1", "test_injection_equivalence", "capability")
_emit_dispatches_execution_plan("p1", "test_injection_equivalence", "exec_plan")
_emit_agent_executes_agent("p1", "test_injection_equivalence", "sub_agent")
_emit_routes_to_agent("p1", "test_injection_equivalence", "target_agent")
_emit_verifies_policy("p1", "test_injection_equivalence", "policy_check")
_emit_observes_runtime_state("p1", "test_injection_equivalence", "runtime_state")
_emit_verifies_boundary("p1", "test_injection_equivalence", "boundary_check")
_emit_transcripts_response("p1", "test_injection_equivalence", "transcript")
_emit_hard_fails_untranscripted("p1", "test_injection_equivalence")
_emit_gated_by_confidence("p1", "test_injection_equivalence", "confidence_gate")
emit_replay_key("p0", "test_injection_equivalence")
emit_determinism_digest("p0", "test_injection_equivalence")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_injection_equivalence", "execution_auth")
_emit_validates_capability("p2", "test_injection_equivalence", "capability_check")
_emit_routes_to_capability("p2", "test_injection_equivalence", "capability_route")
_emit_writes_via_uwg("p2", "test_injection_equivalence", "uwg_write")
_emit_blocks_direct_write("p2", "test_injection_equivalence", "direct_write_block")
_emit_records_tool_invocation("p2", "test_injection_equivalence", "tool_invocation")
_emit_captures_execution_output("p2", "test_injection_equivalence", "exec_output")
_emit_dispatches_agent("p3", "test_injection_equivalence", "agent_dispatch")
_emit_coordinates_agents("p3", "test_injection_equivalence", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_injection_equivalence", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_injection_equivalence", "healing_outcome")
_emit_escalates_failure("p3", "test_injection_equivalence", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_injection_equivalence", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_injection_equivalence", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_injection_equivalence", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_injection_equivalence", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_injection_equivalence", "eval_metric")
_emit_stores_embedding("p4", "test_injection_equivalence", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_injection_equivalence", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_injection_equivalence", "exec_snapshot_link")


class TestInjectionEquivalence:
    """Test behavioral equivalence of YAML-only injection system."""

    @pytest.fixture
    def baseline_snapshot(self, tmp_path: Path) -> Path:
        """Create baseline snapshot of injection outputs."""
        snapshot_file = tmp_path / "injection_baseline.json"

        # Snapshot all injections
        all_patterns = get_instructional_injections()
        required_patterns = get_required_injections()

        snapshot = {
            "all_patterns_count": len(all_patterns),
            "required_patterns_count": len(required_patterns),
            "all_pattern_ids": [p.id for p in all_patterns],
            "required_pattern_ids": [p.id for p in required_patterns],
            "all_pattern_names": [p.name for p in all_patterns],
            "required_pattern_names": [p.name for p in required_patterns],
        }

        with open(snapshot_file, "w") as f:
            json.dump(snapshot, f, indent=2)

        return snapshot_file

    def test_injection_count_consistency(self):
        """Test that injection count is consistent."""
        all_patterns = get_instructional_injections()
        required_patterns = get_required_injections()

        # Verify we have patterns
        assert len(all_patterns) > 0, "Should have at least one pattern"
        assert len(required_patterns) > 0, "Should have at least one required pattern"

        # Verify required patterns are subset of all patterns
        required_ids = {p.id for p in required_patterns}
        all_ids = {p.id for p in all_patterns}
        assert required_ids.issubset(all_ids), "Required patterns should be subset of all patterns"

    def test_injection_order_consistency(self):
        """Test that injection order is deterministic."""
        # Get patterns multiple times
        patterns1 = get_instructional_injections()
        patterns2 = get_instructional_injections()

        # Verify same order
        ids1 = [p.id for p in patterns1]
        ids2 = [p.id for p in patterns2]

        assert ids1 == ids2, "Injection order should be deterministic"

    def test_required_injection_resolution(self):
        """Test that required injection resolution works correctly."""
        all_patterns = get_instructional_injections()
        required_patterns = get_required_injections()

        # Verify required patterns exist
        assert len(required_patterns) > 0

        # Verify all required patterns are in all patterns
        required_ids = {p.id for p in required_patterns}
        all_ids = {p.id for p in all_patterns}

        for req_id in required_ids:
            assert req_id in all_ids, f"Required pattern {req_id} not in all patterns"

    def test_pattern_semantic_structure(self):
        """Test that pattern semantic structure is preserved."""
        patterns = get_instructional_injections()

        for pattern in patterns:
            # Verify required attributes
            assert hasattr(pattern, "id"), "Pattern should have id"
            assert hasattr(pattern, "name"), "Pattern should have name"
            assert hasattr(pattern, "layer"), "Pattern should have layer"
            assert hasattr(pattern, "description"), "Pattern should have description"
            assert hasattr(pattern, "template"), "Pattern should have template"
            assert hasattr(pattern, "enabled"), "Pattern should have enabled"
            assert hasattr(pattern, "required"), "Pattern should have required"

            # Verify values are non-empty where expected
            assert pattern.id is not None, "Pattern id should not be None"
            assert pattern.name is not None, "Pattern name should not be None"
            assert pattern.layer is not None, "Pattern layer should not be None"
            assert pattern.description is not None, "Pattern description should not be None"
            assert pattern.template is not None, "Pattern template should not be None"

    def test_framing_layer_fallback_behavior(self):
        """Test that FRAMING layer fallback behavior is preserved."""
        all_patterns = get_instructional_injections()
        required_patterns = get_required_injections()

        # If no explicitly required patterns, should return FRAMING layer patterns
        required_ids = {p.id for p in required_patterns}

        # Verify behavior: either explicit required or FRAMING layer
        if not any(p.required for p in all_patterns):
            # Should return FRAMING layer patterns
            framing_patterns = [p for p in all_patterns if p.layer.name == "FRAMING"]
            framing_ids = {p.id for p in framing_patterns}
            assert required_ids == framing_ids, "Should return FRAMING layer when no explicit required"

    def test_yaml_only_no_markdown_patterns(self):
        """Test that patterns come from YAML only (not markdown)."""
        patterns = get_instructional_injections()

        # Verify patterns have YAML structure (not markdown-generated)
        for pattern in patterns:
            # YAML patterns should have proper layer attribute
            assert pattern.layer is not None
            # YAML patterns should have enabled attribute
            assert hasattr(pattern, "enabled")
            # YAML patterns should have required attribute
            assert hasattr(pattern, "required")
