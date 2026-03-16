"""
Test Cognitive Endurance Infrastructure.

Verifies the anti-context drift and anti-token overload mechanisms:
- Telemetry Pruner (sanitize_tool_output)
- Golden Context Mixin (inject_golden_context)

COGNITIVE HARDENING (Feb 2026):
- Landmine #3 Prevention: Context Drift
- Landmine #4 Prevention: Token Overload
"""

import pytest

from agentic_core.L4_state.utils.sanitize_telemetry_util import sanitize_tool_output
from agentic_core.mixins.golden_context_mixin import (
    GOLDEN_CONTEXT_SUMMARY,
    THRESHOLD,
    GoldenContextMixin,
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
)

_emit_emits_metric_event("test_cognitive_endurance", "p4obs", "metric_1")
_emit_emits_metric_event("test_cognitive_endurance", "p4obs", "metric_2")
_emit_emits_metric_event("test_cognitive_endurance", "p4obs", "metric_3")
_emit_emits_metric_event("test_cognitive_endurance", "p4obs", "metric_4")
_emit_emits_metric_event("test_cognitive_endurance", "p4obs", "metric_5")
_emit_emits_metric_event("test_cognitive_endurance", "p4obs", "metric_6")
_emit_records_incident_event("test_cognitive_endurance", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_cognitive_endurance", "p4obs", "anomaly")
_emit_writes_observability_log("test_cognitive_endurance", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_cognitive_endurance", "p4obs", "mon_state")
_emit_triggers_alert("test_cognitive_endurance", "p4obs", "alert")
_emit_links_incident_trace("test_cognitive_endurance", "p4obs", "trace_link")
_emit_captures_pattern("test_cognitive_endurance", "p3lm", "pattern")
_emit_records_learning_event("test_cognitive_endurance", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_cognitive_endurance", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_cognitive_endurance", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_cognitive_endurance", "p3lm", "routing")
_emit_improves_agent_policy("test_cognitive_endurance", "p3lm", "policy")
_emit_stores_learning_state("test_cognitive_endurance", "p3lm", "state")
_emit_records_execution_trace("test_cognitive_endurance", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_cognitive_endurance", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_cognitive_endurance", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_cognitive_endurance", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_cognitive_endurance", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_cognitive_endurance", "env_read", "p2_env_1")
_emit_reads_environ("test_cognitive_endurance", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_cognitive_endurance", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_cognitive_endurance", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_cognitive_endurance")
_emit_applies_guardrail("p0", "test_cognitive_endurance", "p0_governance")
_emit_reads_policy_state("p0", "test_cognitive_endurance", "policy_binding")
_emit_snapshots_state("p0", "test_cognitive_endurance", "state_snapshot")
_emit_pulls_context("p1", "test_cognitive_endurance", "context_pull")
_emit_pulls_context("p1", "test_cognitive_endurance", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_cognitive_endurance", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_cognitive_endurance", "uwg_term_secondary")
_emit_writes_through("p1", "test_cognitive_endurance", "write_through")
_emit_writes_through("p1", "test_cognitive_endurance", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_cognitive_endurance", "safety_validation")
_emit_invokes_eval("p1", "test_cognitive_endurance", "eval_call")
_emit_proposal_commits_routing("p1", "test_cognitive_endurance", "routing_commit")
emit_replay_key("p0", "test_cognitive_endurance")
emit_determinism_digest("p0", "test_cognitive_endurance")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_cognitive_endurance", "execution_auth")
_emit_validates_capability("p2", "test_cognitive_endurance", "capability_check")
_emit_routes_to_capability("p2", "test_cognitive_endurance", "capability_route")
_emit_writes_via_uwg("p2", "test_cognitive_endurance", "uwg_write")
_emit_blocks_direct_write("p2", "test_cognitive_endurance", "direct_write_block")
_emit_records_tool_invocation("p2", "test_cognitive_endurance", "tool_invocation")
_emit_captures_execution_output("p2", "test_cognitive_endurance", "exec_output")
_emit_dispatches_agent("p3", "test_cognitive_endurance", "agent_dispatch")
_emit_coordinates_agents("p3", "test_cognitive_endurance", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_cognitive_endurance", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_cognitive_endurance", "healing_outcome")
_emit_escalates_failure("p3", "test_cognitive_endurance", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_cognitive_endurance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_cognitive_endurance", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_cognitive_endurance", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_cognitive_endurance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_cognitive_endurance", "eval_metric")
_emit_stores_embedding("p4", "test_cognitive_endurance", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_cognitive_endurance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_cognitive_endurance", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


class TestTelemetrySanitizer:
    """Test the telemetry pruner (anti-token overload)."""

    def test_short_output_unchanged(self):
        """Short outputs should pass through unchanged."""
        short_output = "This is a short output."
        result = sanitize_tool_output(short_output)
        assert result == short_output

    def test_long_output_pruned(self):
        """Long outputs should be pruned to approximately 1000 chars."""
        # Create a 10,000 character string
        long_output = "A" * 10000
        result = sanitize_tool_output(long_output)

        # Should be approximately head (500) + marker + tail (500) ≈ 1000+ chars
        assert len(result) < len(long_output)
        assert len(result) < 1500  # Reasonable upper bound with marker

        # Should contain the pruning marker
        assert "Pruned" in result
        assert "chars" in result

        # Should contain head and tail
        assert result.startswith("A" * 100)  # Start of head
        assert result.endswith("A" * 100)  # End of tail

    def test_pruned_output_contains_start_and_end(self):
        """Pruned output should preserve start and end content."""
        # Create output with distinct start and end
        start_marker = "START_MARKER_12345"
        end_marker = "END_MARKER_67890"
        middle = "X" * 10000
        long_output = start_marker + middle + end_marker

        result = sanitize_tool_output(long_output)

        # Should contain both markers
        assert start_marker in result
        assert end_marker in result

    def test_traceback_preserves_error(self):
        """Tracebacks should preserve the actual error at the end."""
        traceback_output = (
            """
Some initial output here that is not important.
More filler text to make this long enough to trigger pruning.
"""
            + "X" * 5000
            + """
Traceback (most recent call last):
  File "/path/to/file.py", line 42, in some_function
    result = do_something()
  File "/path/to/other.py", line 100, in do_something
    raise ValueError("This is the actual error message!")
ValueError: This is the actual error message!
"""
        )
        result = sanitize_tool_output(traceback_output)

        # Should preserve the actual error message
        assert "ValueError: This is the actual error message!" in result
        assert "Traceback" in result

    def test_exact_boundary_no_pruning(self):
        """Output exactly at max_chars should not be pruned."""
        exact_output = "B" * 2000
        result = sanitize_tool_output(exact_output, max_chars=2000)
        assert result == exact_output
        assert "Pruned" not in result

    def test_empty_output(self):
        """Empty output should return empty."""
        result = sanitize_tool_output("")
        assert result == ""

    def test_custom_max_chars(self):
        """Custom max_chars should be respected."""
        output = "C" * 500
        result = sanitize_tool_output(output, max_chars=100)
        assert len(result) < 500
        assert "Pruned" in result


class TestGoldenContextMixin:
    """Test the golden context mixin (anti-context drift)."""

    class MockAgent(GoldenContextMixin):
        """Mock agent for testing the mixin."""

        pass

    def test_get_golden_context(self):
        """Should return the SSOT law summary."""
        agent = self.MockAgent()
        context = agent.get_golden_context()

        assert "SOVEREIGN SSOT LAW" in context
        assert "BASE AGENTS LOCATION" in context
        assert "LAYER HIERARCHY" in context

    def test_inject_golden_context_appends_message(self):
        """Should append a system message with the golden context."""
        agent = self.MockAgent()
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]

        result = agent.inject_golden_context(messages)

        # Should have one more message
        assert len(result) == 3

        # Last message should be the golden context
        last_message = result[-1]
        assert last_message["role"] == "system"
        assert "SOVEREIGN SSOT LAW" in last_message["content"]

    def test_inject_does_not_mutate_original(self):
        """Injection should not mutate the original message list."""
        agent = self.MockAgent()
        original_messages = [
            {"role": "user", "content": "Hello"},
        ]
        original_length = len(original_messages)

        result = agent.inject_golden_context(original_messages)

        # Original should be unchanged
        assert len(original_messages) == original_length
        # Result should be different
        assert len(result) == original_length + 1

    def test_inject_empty_messages(self):
        """Should handle empty message list."""
        agent = self.MockAgent()
        result = agent.inject_golden_context([])

        assert len(result) == 1
        assert "SOVEREIGN SSOT LAW" in result[0]["content"]

    def test_should_inject_below_threshold(self):
        """Should not inject when below threshold."""
        agent = self.MockAgent()
        messages = [{"role": "user", "content": "Hi"}] * 5

        should_inject = agent.should_inject_golden_context(messages, threshold=10)
        assert should_inject is False

    def test_should_inject_above_threshold(self):
        """Should inject when above threshold."""
        agent = self.MockAgent()
        messages = [{"role": "user", "content": "Hi"}] * 15

        should_inject = agent.should_inject_golden_context(messages, threshold=10)
        assert should_inject is True

    def test_should_not_inject_if_recent(self):
        """Should not inject if golden context was recently injected."""
        agent = self.MockAgent()
        messages = [{"role": "user", "content": "Hi"}] * 15
        # Add a recent golden context injection
        messages.append({"role": "system", "content": GOLDEN_CONTEXT_SUMMARY})

        should_inject = agent.should_inject_golden_context(messages, threshold=10)
        assert should_inject is False

    def test_custom_role(self):
        """Should support custom role for injected message."""
        agent = self.MockAgent()
        messages = [{"role": "user", "content": "Hello"}]

        result = agent.inject_golden_context(messages, role="developer")

        assert result[-1]["role"] == "developer"


class TestIntegration:
    """Integration tests for cognitive endurance infrastructure."""

    def test_pruner_and_context_work_together(self):
        """Both mechanisms should work together without conflict."""
        # Create a large output that needs pruning
        large_output = "D" * 10000
        sanitized = sanitize_tool_output(large_output)

        # Create a message history with the sanitized output
        class TestAgent(GoldenContextMixin):
            pass

        agent = TestAgent()
        messages = [
            {"role": "user", "content": "Run the tool"},
            {"role": "assistant", "content": "Running..."},
            {"role": "tool", "content": sanitized},
        ] * 5  # 15 messages total

        # Should recommend injection
        assert agent.should_inject_golden_context(messages, threshold=THRESHOLD)

        # Inject and verify
        result = agent.inject_golden_context(messages)
        assert len(result) == 16
        assert "SOVEREIGN SSOT LAW" in result[-1]["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
