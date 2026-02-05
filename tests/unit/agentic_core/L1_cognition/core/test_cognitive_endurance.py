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

from agentic_core.L1_cognition.memory.golden_context_mixin import (
    GOLDEN_CONTEXT_SUMMARY,
    GoldenContextMixin,
)
from agentic_core.L4_state.utils.telemetry_sanitizer import sanitize_tool_output


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
        assert agent.should_inject_golden_context(messages, threshold=10)

        # Inject and verify
        result = agent.inject_golden_context(messages)
        assert len(result) == 16
        assert "SOVEREIGN SSOT LAW" in result[-1]["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
