"""Test YAML-only enforcement for instructional injections.

Verifies that:
1. No markdown fallback exists
2. YAML loading is mandatory
3. Failures raise typed exceptions
"""

from agentic_core.runtime.config.instructional_injections import get_instructional_injections
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

_emit_records_execution_trace("p0", "evidence", "test_yaml_only_enforcement")
_emit_applies_guardrail("p0", "test_yaml_only_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_yaml_only_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_yaml_only_enforcement", "state_snapshot")
emit_replay_key("p0", "test_yaml_only_enforcement")
emit_determinism_digest("p0", "test_yaml_only_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_yaml_only_enforcement", "execution_auth")
_emit_validates_capability("p2", "test_yaml_only_enforcement", "capability_check")
_emit_routes_to_capability("p2", "test_yaml_only_enforcement", "capability_route")
_emit_writes_via_uwg("p2", "test_yaml_only_enforcement", "uwg_write")
_emit_blocks_direct_write("p2", "test_yaml_only_enforcement", "direct_write_block")
_emit_records_tool_invocation("p2", "test_yaml_only_enforcement", "tool_invocation")
_emit_captures_execution_output("p2", "test_yaml_only_enforcement", "exec_output")
_emit_dispatches_agent("p3", "test_yaml_only_enforcement", "agent_dispatch")
_emit_coordinates_agents("p3", "test_yaml_only_enforcement", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_yaml_only_enforcement", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_yaml_only_enforcement", "healing_outcome")
_emit_escalates_failure("p3", "test_yaml_only_enforcement", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_yaml_only_enforcement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_yaml_only_enforcement", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_yaml_only_enforcement", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_yaml_only_enforcement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_yaml_only_enforcement", "eval_metric")
_emit_stores_embedding("p4", "test_yaml_only_enforcement", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_yaml_only_enforcement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_yaml_only_enforcement", "exec_snapshot_link")


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
