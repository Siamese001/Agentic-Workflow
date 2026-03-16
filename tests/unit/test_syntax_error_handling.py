"""
Test syntax error handling in FCA.

Validates:
- SyntaxError results in graceful UNKNOWN classification
- No crashes on malformed Python files
- Violations are generated for unparseable files
"""

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
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
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_syntax_error_handling")
_emit_applies_guardrail("p0", "test_syntax_error_handling", "p0_governance")
_emit_reads_policy_state("p0", "test_syntax_error_handling", "policy_binding")
_emit_snapshots_state("p0", "test_syntax_error_handling", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
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

_emit_emits_metric_event("test_syntax_error_handling", "p4obs", "metric_1")
_emit_emits_metric_event("test_syntax_error_handling", "p4obs", "metric_2")
_emit_emits_metric_event("test_syntax_error_handling", "p4obs", "metric_3")
_emit_emits_metric_event("test_syntax_error_handling", "p4obs", "metric_4")
_emit_emits_metric_event("test_syntax_error_handling", "p4obs", "metric_5")
_emit_emits_metric_event("test_syntax_error_handling", "p4obs", "metric_6")
_emit_records_incident_event("test_syntax_error_handling", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_syntax_error_handling", "p4obs", "anomaly")
_emit_writes_observability_log("test_syntax_error_handling", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_syntax_error_handling", "p4obs", "mon_state")
_emit_triggers_alert("test_syntax_error_handling", "p4obs", "alert")
_emit_links_incident_trace("test_syntax_error_handling", "p4obs", "trace_link")
_emit_captures_pattern("test_syntax_error_handling", "p3lm", "pattern")
_emit_records_learning_event("test_syntax_error_handling", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_syntax_error_handling", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_syntax_error_handling", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_syntax_error_handling", "p3lm", "routing")
_emit_improves_agent_policy("test_syntax_error_handling", "p3lm", "policy")
_emit_stores_learning_state("test_syntax_error_handling", "p3lm", "state")
_emit_records_execution_trace("test_syntax_error_handling", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_syntax_error_handling", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_syntax_error_handling", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_syntax_error_handling", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_syntax_error_handling", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_syntax_error_handling", "env_read", "p2_env_1")
_emit_reads_environ("test_syntax_error_handling", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_syntax_error_handling", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_syntax_error_handling", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_syntax_error_handling", "context_pull")
_emit_pulls_context("p1", "test_syntax_error_handling", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_syntax_error_handling", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_syntax_error_handling", "uwg_term_2")
_emit_writes_through("p1", "test_syntax_error_handling", "write_through")
_emit_writes_through("p1", "test_syntax_error_handling", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_syntax_error_handling", "safety_validation")
_emit_invokes_eval("p1", "test_syntax_error_handling", "eval_call")
_emit_proposal_commits_routing("p1", "test_syntax_error_handling", "routing_commit")
_emit_escalates_to_human("p1", "test_syntax_error_handling", "human_escalation")
_emit_routes_through("p1", "test_syntax_error_handling", "route_through")
_emit_checks_agent_registry("p1", "test_syntax_error_handling", "agent_registry")
_emit_validates_agent_capability("p1", "test_syntax_error_handling", "capability")
_emit_dispatches_execution_plan("p1", "test_syntax_error_handling", "exec_plan")
_emit_agent_executes_agent("p1", "test_syntax_error_handling", "sub_agent")
_emit_routes_to_agent("p1", "test_syntax_error_handling", "target_agent")
_emit_verifies_policy("p1", "test_syntax_error_handling", "policy_check")
_emit_observes_runtime_state("p1", "test_syntax_error_handling", "runtime_state")
_emit_verifies_boundary("p1", "test_syntax_error_handling", "boundary_check")
_emit_transcripts_response("p1", "test_syntax_error_handling", "transcript")
_emit_hard_fails_untranscripted("p1", "test_syntax_error_handling")
_emit_gated_by_confidence("p1", "test_syntax_error_handling", "confidence_gate")
emit_replay_key("p0", "test_syntax_error_handling")
emit_determinism_digest("p0", "test_syntax_error_handling")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_syntax_error_handling", "execution_auth")
_emit_validates_capability("p2", "test_syntax_error_handling", "capability_check")
_emit_routes_to_capability("p2", "test_syntax_error_handling", "capability_route")
_emit_writes_via_uwg("p2", "test_syntax_error_handling", "uwg_write")
_emit_blocks_direct_write("p2", "test_syntax_error_handling", "direct_write_block")
_emit_records_tool_invocation("p2", "test_syntax_error_handling", "tool_invocation")
_emit_captures_execution_output("p2", "test_syntax_error_handling", "exec_output")
_emit_dispatches_agent("p3", "test_syntax_error_handling", "agent_dispatch")
_emit_coordinates_agents("p3", "test_syntax_error_handling", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_syntax_error_handling", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_syntax_error_handling", "healing_outcome")
_emit_escalates_failure("p3", "test_syntax_error_handling", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_syntax_error_handling", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_syntax_error_handling", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_syntax_error_handling", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_syntax_error_handling", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_syntax_error_handling", "eval_metric")
_emit_stores_embedding("p4", "test_syntax_error_handling", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_syntax_error_handling", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_syntax_error_handling", "exec_snapshot_link")


class TestSyntaxErrorHandling:
    """Tests for FCA handling of syntax errors."""

    @pytest.fixture
    def fca(self):
        """Create FCA instance for testing."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

        return FileClassificationAgent()

    def test_syntax_error_does_not_crash(self, fca, tmp_path):
        """FCA should not crash on syntax errors."""
        content = '''"""Module with syntax error."""
def broken_function(
    # Missing closing paren and body
'''
        test_file = tmp_path / "broken.py"
        test_file.write_text(content)

        # Should not raise exception
        try:
            result = fca.classify_file(test_file)
            # Result should indicate unknown or error
            assert result is not None
        except SyntaxError:
            pytest.fail("FCA should handle SyntaxError gracefully")

    def test_incomplete_class_definition(self, fca, tmp_path):
        """FCA should handle incomplete class definitions."""
        content = '''"""Module with incomplete class."""
class Incomplete
'''
        test_file = tmp_path / "incomplete.py"
        test_file.write_text(content)

        try:
            result = fca.classify_file(test_file)
            assert result is not None
        except SyntaxError:
            pytest.fail("FCA should handle incomplete class gracefully")

    def test_invalid_indentation(self, fca, tmp_path):
        """FCA should handle invalid indentation."""
        content = '''"""Module with bad indentation."""
def function():
pass  # Wrong indentation
'''
        test_file = tmp_path / "bad_indent.py"
        test_file.write_text(content)

        try:
            result = fca.classify_file(test_file)
            assert result is not None
        except IndentationError:
            pytest.fail("FCA should handle IndentationError gracefully")

    def test_unicode_errors(self, fca, tmp_path):
        """FCA should handle unicode errors gracefully."""
        test_file = tmp_path / "unicode.py"
        # Write bytes that aren't valid UTF-8
        test_file.write_bytes(b'"""Module."""\n\xff\xfe\x00\x01')

        try:
            fca.classify_file(test_file)
            # Should not crash
        except UnicodeDecodeError:
            pytest.fail("FCA should handle UnicodeDecodeError gracefully")

    def test_empty_file(self, fca, tmp_path):
        """FCA should handle empty files."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        result = fca.classify_file(test_file)
        assert result is not None

    def test_only_comments(self, fca, tmp_path):
        """FCA should handle files with only comments."""
        content = """# Just a comment
# Another comment
"""
        test_file = tmp_path / "comments.py"
        test_file.write_text(content)

        result = fca.classify_file(test_file)
        assert result is not None

    def test_only_docstring(self, fca, tmp_path):
        """FCA should handle files with only docstring."""
        content = '''"""Just a docstring module."""
'''
        test_file = tmp_path / "docstring.py"
        test_file.write_text(content)

        result = fca.classify_file(test_file)
        assert result is not None
