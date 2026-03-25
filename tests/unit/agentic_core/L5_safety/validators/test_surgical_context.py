"""
Tests for SurgicalContext and SurgicalHealerMixin - Phase 0 Infrastructure

Validates the surgical healing infrastructure for Resolution Asymmetry remediation.
"""

import ast
import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.types.surgical_context_types import (
    ASTCoordinate,
    SurgicalContext,
    SurgicalContextBuilder,
    ViolationConstraint,
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

# REMOVED: _emit_emits_metric_event("test_surgical_context", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_surgical_context", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_surgical_context", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_surgical_context", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_surgical_context", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_surgical_context", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_surgical_context", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_surgical_context", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_surgical_context", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_surgical_context", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_surgical_context", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_surgical_context", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_surgical_context", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_surgical_context", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_surgical_context", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_surgical_context", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_surgical_context", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_surgical_context", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_surgical_context", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_surgical_context", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_surgical_context", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_surgical_context", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_surgical_context", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_surgical_context", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_surgical_context", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_surgical_context", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_surgical_context", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_surgical_context", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_surgical_context")
# REMOVED: _emit_applies_guardrail("p0", "test_surgical_context", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_surgical_context", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_surgical_context", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_surgical_context", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_surgical_context", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_surgical_context", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_surgical_context", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_surgical_context", "write_through")
# REMOVED: _emit_writes_through("p1", "test_surgical_context", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_surgical_context", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_surgical_context", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_surgical_context", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_surgical_context", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_surgical_context", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_surgical_context", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_surgical_context", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_surgical_context", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_surgical_context", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_surgical_context", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_surgical_context", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_surgical_context", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_surgical_context", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_surgical_context", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_surgical_context")
# REMOVED: _emit_gated_by_confidence("p1", "test_surgical_context", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_surgical_context")
# REMOVED: emit_determinism_digest("p0", "test_surgical_context")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_surgical_context", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_surgical_context", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_surgical_context", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_surgical_context", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_surgical_context", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_surgical_context", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_surgical_context", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_surgical_context", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_surgical_context", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_surgical_context", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_surgical_context", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_surgical_context", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_surgical_context", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_surgical_context", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_surgical_context", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_surgical_context", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_surgical_context", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_surgical_context", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_surgical_context", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_surgical_context", "exec_snapshot_link")


class TestASTCoordinate:
    """Tests for ASTCoordinate dataclass."""

    def test_create_coordinate(self):
        """Test creating an AST coordinate."""
        coord = ASTCoordinate(
            node_id="func_1",
            node_type="FunctionDef",
            line=10,
            column=0,
            end_line=20,
            end_column=0,
        )
        assert coord.node_id == "func_1"
        assert coord.node_type == "FunctionDef"
        assert coord.line == 10
        assert coord.column == 0
        assert coord.end_line == 20

    def test_coordinate_defaults(self):
        """Test default values for optional fields."""
        coord = ASTCoordinate(
            node_id="test",
            node_type="ClassDef",
            line=1,
            column=0,
        )
        assert coord.end_line is None
        assert coord.end_column is None
        assert coord.parent_id is None
        assert coord.children_ids == []


class TestViolationConstraint:
    """Tests for ViolationConstraint dataclass."""

    def test_create_violation(self):
        """Test creating a violation constraint."""
        violation = ViolationConstraint(
            constraint_type="missing_docstring",
            severity="warning",
            message="Function missing docstring",
            rule_id="DOC001",
            expected_pattern='"""Docstring here."""',
            fix_type="insert",
        )
        assert violation.constraint_type == "missing_docstring"
        assert violation.severity == "warning"
        assert violation.fix_type == "insert"

    def test_violation_defaults(self):
        """Test default values for optional fields."""
        violation = ViolationConstraint(
            constraint_type="test",
            severity="error",
            message="Test message",
        )
        assert violation.rule_id is None
        assert violation.expected_pattern is None
        assert violation.actual_pattern is None
        assert violation.fix_type is None


class TestSurgicalContext:
    """Tests for SurgicalContext dataclass."""

    def test_create_context(self):
        """Test creating a surgical context."""
        source = "def test(): pass"
        tree = ast.parse(source)

        context = SurgicalContext(
            file_path=Path("test.py"),
            file_content=source,
            ast_tree=tree,
            violation_id="v001",
            violations=[],
            target_coordinates=[],
            detector_agent="TestAgent",
            detection_method="test_method",
            detection_timestamp="2026-02-02T17:00:00",
        )
        assert context.file_path == Path("test.py")
        assert context.violation_id == "v001"
        assert context.detector_agent == "TestAgent"

    def test_get_nodes_by_type(self):
        """Test getting nodes by type."""
        source = """
def func1(): pass
def func2(): pass
class MyClass: pass
"""
        tree = ast.parse(source)
        context = SurgicalContext(
            file_path=Path("test.py"),
            file_content=source,
            ast_tree=tree,
            violation_id="v001",
            violations=[],
            target_coordinates=[],
            detector_agent="TestAgent",
            detection_method="test",
            detection_timestamp="2026-02-02T17:00:00",
        )

        func_nodes = context.get_nodes_by_type("FunctionDef")
        class_nodes = context.get_nodes_by_type("ClassDef")

        assert len(func_nodes) == 2
        assert len(class_nodes) == 1

    def test_get_line_range(self):
        """Test getting line range for coordinate."""
        coord = ASTCoordinate(
            node_id="test",
            node_type="FunctionDef",
            line=5,
            column=0,
            end_line=10,
        )

        source = "def test(): pass"
        tree = ast.parse(source)
        context = SurgicalContext(
            file_path=Path("test.py"),
            file_content=source,
            ast_tree=tree,
            violation_id="v001",
            violations=[],
            target_coordinates=[],
            detector_agent="TestAgent",
            detection_method="test",
            detection_timestamp="2026-02-02T17:00:00",
        )

        start, end = context.get_line_range(coord)
        assert start == 5
        assert end == 10


class TestSurgicalContextBuilder:
    """Tests for SurgicalContextBuilder."""

    def test_builder_creates_context(self):
        """Test that builder creates a valid context."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("def test_func(): pass\n")
            temp_path = Path(f.name)

        try:
            builder = SurgicalContextBuilder(temp_path, "TestAgent", "test_method")

            violations = [
                {
                    "constraint_type": "missing_docstring",
                    "severity": "warning",
                    "message": "Missing docstring",
                    "fix_type": "insert",
                },
            ]

            tree = ast.parse(temp_path.read_text())
            target_nodes = [tree.body[0]]  # The function def

            context = builder.build_context(
                violation_id="v001",
                violations=violations,
                target_nodes=target_nodes,
            )

            assert context is not None
            assert context.violation_id == "v001"
            assert len(context.violations) == 1
            assert context.detector_agent == "TestAgent"
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
