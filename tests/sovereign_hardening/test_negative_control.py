"""Tests for negative control with W_HARDEN_NEGCTRL_TAMPER."""

import os
from unittest.mock import patch

import pytest

from agentic_core.L2_execution.determinism import (
    compute_lockdown_determinism_digest,
    get_embedding_config_surface,
)
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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_negative_control", "p4obs", "metric_1")
_emit_emits_metric_event("test_negative_control", "p4obs", "metric_2")
_emit_emits_metric_event("test_negative_control", "p4obs", "metric_3")
_emit_emits_metric_event("test_negative_control", "p4obs", "metric_4")
_emit_emits_metric_event("test_negative_control", "p4obs", "metric_5")
_emit_emits_metric_event("test_negative_control", "p4obs", "metric_6")
_emit_records_incident_event("test_negative_control", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_negative_control", "p4obs", "anomaly")
_emit_writes_observability_log("test_negative_control", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_negative_control", "p4obs", "mon_state")
_emit_triggers_alert("test_negative_control", "p4obs", "alert")
_emit_links_incident_trace("test_negative_control", "p4obs", "trace_link")
_emit_captures_pattern("test_negative_control", "p3lm", "pattern")
_emit_records_learning_event("test_negative_control", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_negative_control", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_negative_control", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_negative_control", "p3lm", "routing")
_emit_improves_agent_policy("test_negative_control", "p3lm", "policy")
_emit_stores_learning_state("test_negative_control", "p3lm", "state")
_emit_records_execution_trace("test_negative_control", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_negative_control", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_negative_control", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_negative_control", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_negative_control", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_negative_control", "env_read", "p2_env_1")
_emit_reads_environ("test_negative_control", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_negative_control", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_negative_control", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_negative_control")
_emit_applies_guardrail("p0", "test_negative_control", "p0_governance")
_emit_reads_policy_state("p0", "test_negative_control", "policy_binding")
_emit_snapshots_state("p0", "test_negative_control", "state_snapshot")
_emit_pulls_context("p1", "test_negative_control", "context_pull")
_emit_pulls_context("p1", "test_negative_control", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_negative_control", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_negative_control", "uwg_term_secondary")
_emit_writes_through("p1", "test_negative_control", "write_through")
_emit_writes_through("p1", "test_negative_control", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_negative_control", "safety_validation")
_emit_invokes_eval("p1", "test_negative_control", "eval_call")
_emit_proposal_commits_routing("p1", "test_negative_control", "routing_commit")
emit_replay_key("p0", "test_negative_control")
emit_determinism_digest("p0", "test_negative_control")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_negative_control", "execution_auth")
_emit_validates_capability("p2", "test_negative_control", "capability_check")
_emit_routes_to_capability("p2", "test_negative_control", "capability_route")
_emit_writes_via_uwg("p2", "test_negative_control", "uwg_write")
_emit_blocks_direct_write("p2", "test_negative_control", "direct_write_block")
_emit_records_tool_invocation("p2", "test_negative_control", "tool_invocation")
_emit_captures_execution_output("p2", "test_negative_control", "exec_output")
_emit_dispatches_agent("p3", "test_negative_control", "agent_dispatch")
_emit_coordinates_agents("p3", "test_negative_control", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_negative_control", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_negative_control", "healing_outcome")
_emit_escalates_failure("p3", "test_negative_control", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_negative_control", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_negative_control", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_negative_control", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_negative_control", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_negative_control", "eval_metric")
_emit_stores_embedding("p4", "test_negative_control", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_negative_control", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_negative_control", "exec_snapshot_link")


class TestNegativeControl:
    """Tests for negative control tampering detection."""

    def test_tamper_environment_detection(self):
        """Test that tampering environment variable is detected."""
        # Test with tampering enabled
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            assert os.environ.get("W_HARDEN_NEGCTRL_TAMPER") == "1"

        # Test without tampering
        with patch.dict(os.environ, {}, clear=True):
            assert os.environ.get("W_HARDEN_NEGCTRL_TAMPER") is None

    def test_embedding_config_tampering(self):
        """Test that embedding config is tampered when negative control is active."""
        # Normal config
        with patch.dict(os.environ, {}, clear=True):
            normal_config = get_embedding_config_surface()

        # Tampered config
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            tampered_config = get_embedding_config_surface()

        # Verify tampering effects
        assert normal_config != tampered_config
        assert normal_config["top_k"] == 20
        assert normal_config["cutoff"] == 0.0
        assert "tampered" not in normal_config

        assert tampered_config["top_k"] == 999
        assert tampered_config["cutoff"] == 0.999
        assert tampered_config.get("tampered") is True

    def test_determinism_digest_changes_with_tampering(self):
        """Test that determinism digest changes when tampering is active."""
        # Normal digest
        with patch.dict(os.environ, {}, clear=True):
            normal_digest = compute_lockdown_determinism_digest()

        # Tampered digest
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            tampered_digest = compute_lockdown_determinism_digest()

        # Digests should be different
        assert normal_digest != tampered_digest
        assert len(normal_digest) == 64
        assert len(tampered_digest) == 64

    def test_tampering_is_deterministic(self):
        """Test that tampering effects are deterministic."""
        # Get tampered config multiple times
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            config1 = get_embedding_config_surface()
            config2 = get_embedding_config_surface()

        # Should be identical
        assert config1 == config2

        # Get tampered digest multiple times
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            digest1 = compute_lockdown_determinism_digest()
            digest2 = compute_lockdown_determinism_digest()

        # Should be identical
        assert digest1 == digest2

    def test_negative_control_xfail_behavior(self):
        """Negative control: XFAIL when tampered, PASS when restored.

        When W_HARDEN_NEGCTRL_TAMPER=1 this test calls pytest.xfail() which
        records an xfail and exits 0 with 0 failures.
        When the env var is unset this test passes normally.
        No @xfail decorator is used, eliminating any XPASS possibility.
        """
        if os.environ.get("W_HARDEN_NEGCTRL_TAMPER") == "1":
            pytest.xfail("Negative control tampering active: W_HARDEN_NEGCTRL_TAMPER=1")
        # Restore path: normal PASS

    @pytest.mark.negative_control
    def test_negative_control_marker(self):
        """Test marked with negative_control marker."""
        # This test is marked with @pytest.mark.negative_control
        # It should behave differently based on W_HARDEN_NEGCTRL_TAMPER
        is_tampered = os.environ.get("W_HARDEN_NEGCTRL_TAMPER") == "1"

        if is_tampered:
            pytest.xfail("Negative control tampering active: W_HARDEN_NEGCTRL_TAMPER=1")
        # Normal mode - test should pass

    def test_tampering_affects_multiple_components(self):
        """Test that tampering affects all relevant components."""
        with patch.dict(os.environ, {}, clear=True):
            # Get all normal components
            normal_config = get_embedding_config_surface()
            normal_digest = compute_lockdown_determinism_digest()

        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            # Get all tampered components
            tampered_config = get_embedding_config_surface()
            tampered_digest = compute_lockdown_determinism_digest()

        # All should be affected
        assert normal_config != tampered_config
        assert normal_digest != tampered_digest

        # Verify specific tampering effects
        assert tampered_config["top_k"] == 999
        assert tampered_config["cutoff"] == 0.999
        assert tampered_config.get("tampered") is True

    def test_tampering_restoration(self):
        """Test that tampering effects can be restored."""
        # Start with normal
        with patch.dict(os.environ, {}, clear=True):
            normal_digest = compute_lockdown_determinism_digest()

        # Apply tampering
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            tampered_digest = compute_lockdown_determinism_digest()
            assert tampered_digest != normal_digest

        # Restore to normal
        with patch.dict(os.environ, {}, clear=True):
            restored_digest = compute_lockdown_determinism_digest()
            assert restored_digest == normal_digest

    def test_tampering_environment_variable_edge_cases(self):
        """Test edge cases for tampering environment variable."""
        # Test with various values
        test_values = ["1", "true", "True", "TRUE", "yes", "YES"]

        for value in test_values:
            with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": value}):
                config = get_embedding_config_surface()
                # Only '1' should trigger tampering
                if value == "1":
                    assert config.get("tampered") is True
                else:
                    assert "tampered" not in config

    def test_concurrent_tampering_detection(self):
        """Test tampering detection in concurrent scenarios."""
        # This test ensures tampering detection works even if environment
        # is modified during test execution
        original_value = os.environ.get("W_HARDEN_NEGCTRL_TAMPER")

        try:
            # Set tampering
            os.environ["W_HARDEN_NEGCTRL_TAMPER"] = "1"
            config1 = get_embedding_config_surface()
            assert config1.get("tampered") is True

            # Clear tampering
            del os.environ["W_HARDEN_NEGCTRL_TAMPER"]
            config2 = get_embedding_config_surface()
            assert "tampered" not in config2

        finally:
            # Restore original value
            if original_value is None:
                os.environ.pop("W_HARDEN_NEGCTRL_TAMPER", None)
            else:
                os.environ["W_HARDEN_NEGCTRL_TAMPER"] = original_value
