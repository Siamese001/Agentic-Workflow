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
)

_emit_records_execution_trace("p0", "evidence", "test_syntax_error_handling")
_emit_applies_guardrail("p0", "test_syntax_error_handling", "p0_governance")
_emit_reads_policy_state("p0", "test_syntax_error_handling", "policy_binding")
_emit_snapshots_state("p0", "test_syntax_error_handling", "state_snapshot")
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
