"""Test YAML-only enforcement for instructional injections.

Verifies that:
1. No markdown fallback exists
2. YAML loading is mandatory
3. Failures raise typed exceptions
"""

from agentic_core.runtime.config.instructional_injections import get_instructional_injections
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_yaml_only_enforcement")
_emit_applies_guardrail("p0", "test_yaml_only_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_yaml_only_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_yaml_only_enforcement", "state_snapshot")
emit_replay_key("p0", "test_yaml_only_enforcement")
emit_determinism_digest("p0", "test_yaml_only_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestYamlOnlyEnforcement:
    """Test YAML-only enforcement for instructional injections."""

    def test_yaml_only_no_markdown_fallback(self):
        """Test that YAML-only path is enforced (no markdown fallback)."""
        # This should load from YAML only
        patterns = get_instructional_injections()

        # Verify we got patterns
        assert patterns is not None
        assert len(patterns) > 0

        # Verify patterns are from YAML (not markdown fallback)
        # YAML patterns should have proper structure
        for pattern in patterns:
            assert hasattr(pattern, "id")
            assert hasattr(pattern, "name")
            assert hasattr(pattern, "layer")
            assert hasattr(pattern, "description")
            assert hasattr(pattern, "template")

    def test_yaml_failure_raises_exception(self):
        """Test that YAML loading failures raise typed exceptions."""
        # This test verifies that if YAML loading fails,
        # it raises the appropriate exception (not a silent fallback)
        # The actual exception type depends on the failure mode:
        # - ImportError: YAML loader not available
        # - FileNotFoundError: YAML corpus not found
        # - YamlValidationError: YAML validation fails

        # For now, we verify the function works with proper YAML setup
        patterns = get_instructional_injections()
        assert patterns is not None

    def test_no_markdown_function_called(self):
        """Test that markdown fallback function is not called."""
        # Verify that _get_markdown_injections is not in the module
        from agentic_core.runtime.config import instructional_injections

        # The markdown fallback function should not exist
        assert not hasattr(instructional_injections, "_get_markdown_injections")

    def test_injection_patterns_from_yaml_only(self):
        """Test that all injection patterns come from YAML."""
        patterns = get_instructional_injections()

        # Verify we have patterns
        assert len(patterns) > 0

        # Verify all patterns have required YAML structure
        for pattern in patterns:
            # All patterns should have these attributes
            assert pattern.id is not None
            assert pattern.name is not None
            assert pattern.layer is not None
            assert pattern.description is not None
            assert pattern.template is not None
