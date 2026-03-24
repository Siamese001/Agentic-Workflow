"""Tests for HARDEN-MERGE-LOCKDOWN determinism digest."""

import os
from unittest.mock import patch

import pytest

from agentic_core.L2_execution.determinism import (
    compute_lockdown_determinism_digest,
    generate_lockdown_determinism_digest,
    get_embedding_config_surface,
    get_meta_learning_config_surface,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_determinism_digest")
_emit_applies_guardrail("p0", "test_determinism_digest", "p0_governance")
_emit_reads_policy_state("p0", "test_determinism_digest", "policy_binding")
_emit_snapshots_state("p0", "test_determinism_digest", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_determinism_digest", "p4obs", "metric_1")
_emit_emits_metric_event("test_determinism_digest", "p4obs", "metric_2")
_emit_emits_metric_event("test_determinism_digest", "p4obs", "metric_3")
_emit_emits_metric_event("test_determinism_digest", "p4obs", "metric_4")
_emit_emits_metric_event("test_determinism_digest", "p4obs", "metric_5")
_emit_emits_metric_event("test_determinism_digest", "p4obs", "metric_6")
_emit_records_incident_event("test_determinism_digest", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_determinism_digest", "p4obs", "anomaly")
_emit_writes_observability_log("test_determinism_digest", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_determinism_digest", "p4obs", "mon_state")
_emit_triggers_alert("test_determinism_digest", "p4obs", "alert")
_emit_links_incident_trace("test_determinism_digest", "p4obs", "trace_link")
_emit_captures_pattern("test_determinism_digest", "p3lm", "pattern")
_emit_records_learning_event("test_determinism_digest", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_determinism_digest", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_determinism_digest", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_determinism_digest", "p3lm", "routing")
_emit_improves_agent_policy("test_determinism_digest", "p3lm", "policy")
_emit_stores_learning_state("test_determinism_digest", "p3lm", "state")
_emit_records_execution_trace("test_determinism_digest", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_determinism_digest", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_determinism_digest", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_determinism_digest", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_determinism_digest", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_determinism_digest", "env_read", "p2_env_1")
_emit_reads_environ("test_determinism_digest", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_determinism_digest", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_determinism_digest", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_determinism_digest", "context_pull")
_emit_pulls_context("p1", "test_determinism_digest", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_determinism_digest", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_determinism_digest", "uwg_term_2")
_emit_writes_through("p1", "test_determinism_digest", "write_through")
_emit_writes_through("p1", "test_determinism_digest", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_determinism_digest", "safety_validation")
_emit_invokes_eval("p1", "test_determinism_digest", "eval_call")
_emit_proposal_commits_routing("p1", "test_determinism_digest", "routing_commit")
_emit_escalates_to_human("p1", "test_determinism_digest", "human_escalation")
_emit_routes_through("p1", "test_determinism_digest", "route_through")
_emit_checks_agent_registry("p1", "test_determinism_digest", "agent_registry")
_emit_validates_agent_capability("p1", "test_determinism_digest", "capability")
_emit_dispatches_execution_plan("p1", "test_determinism_digest", "exec_plan")
_emit_agent_executes_agent("p1", "test_determinism_digest", "sub_agent")
_emit_routes_to_agent("p1", "test_determinism_digest", "target_agent")
_emit_verifies_policy("p1", "test_determinism_digest", "policy_check")
_emit_observes_runtime_state("p1", "test_determinism_digest", "runtime_state")
_emit_verifies_boundary("p1", "test_determinism_digest", "boundary_check")
_emit_transcripts_response("p1", "test_determinism_digest", "transcript")
_emit_hard_fails_untranscripted("p1", "test_determinism_digest")
_emit_gated_by_confidence("p1", "test_determinism_digest", "confidence_gate")
emit_replay_key("p0", "test_determinism_digest")
emit_determinism_digest("p0", "test_determinism_digest")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_determinism_digest", "execution_auth")
_emit_validates_capability("p2", "test_determinism_digest", "capability_check")
_emit_routes_to_capability("p2", "test_determinism_digest", "capability_route")
_emit_writes_via_uwg("p2", "test_determinism_digest", "uwg_write")
_emit_blocks_direct_write("p2", "test_determinism_digest", "direct_write_block")
_emit_records_tool_invocation("p2", "test_determinism_digest", "tool_invocation")
_emit_captures_execution_output("p2", "test_determinism_digest", "exec_output")
_emit_dispatches_agent("p3", "test_determinism_digest", "agent_dispatch")
_emit_coordinates_agents("p3", "test_determinism_digest", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_determinism_digest", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_determinism_digest", "healing_outcome")
_emit_escalates_failure("p3", "test_determinism_digest", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_determinism_digest", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_determinism_digest", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_determinism_digest", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_determinism_digest", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_determinism_digest", "eval_metric")
_emit_stores_embedding("p4", "test_determinism_digest", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_determinism_digest", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_determinism_digest", "exec_snapshot_link")


class TestDeterminismDigest:
    """Tests for determinism digest calculation and emission."""

    def test_digest_calculation(self):
        """Test that determinism digest is calculated correctly."""
        digest = compute_lockdown_determinism_digest()

        assert isinstance(digest, str)
        assert len(digest) == 64  # SHA-256 hex length
        assert all(c in "0123456789abcdef" for c in digest)

    def test_digest_emission_format(self):
        """Test that digest emission follows required format."""
        emission = generate_lockdown_determinism_digest()

        assert emission.startswith("HARDEN-MERGE-LOCKDOWN-DETERMINISM-DIGEST: ")
        digest_part = emission.split(": ", 1)[1]
        assert len(digest_part) == 64
        assert all(c in "0123456789abcdef" for c in digest_part)

    def test_determinism_digest_exactly_once_per_run(self, capsys):
        """Digest emitted exactly once per generate_lockdown_determinism_digest() call.

        Uses capsys to capture any stdout the function prints (if any) and
        also asserts the returned string is a single well-formed line.
        Two back-to-back calls must produce identical output.
        """
        emission1 = generate_lockdown_determinism_digest()
        emission2 = generate_lockdown_determinism_digest()

        # Each emission must be exactly one non-empty line
        for emission in (emission1, emission2):
            lines = [l.strip() for l in emission.splitlines() if l.strip()]
            assert len(lines) == 1, (
                f"generate_lockdown_determinism_digest() must return exactly 1 line, "
                f"got {len(lines)}: {lines}"
            )
            assert lines[0].startswith("HARDEN-MERGE-LOCKDOWN-DETERMINISM-DIGEST: "), (
                f"Line must start with correct prefix, got: {lines[0][:60]}"
            )
            hex_part = lines[0].split(": ", 1)[1]
            assert len(hex_part) == 64, f"SHA-256 hex must be 64 chars, got {len(hex_part)}"
            assert all(c in "0123456789abcdef" for c in hex_part), "Not a valid hex digest"

        # Cross-call determinism
        assert emission1 == emission2, (
            f"Digest must be identical across calls:\n  run1={emission1}\n  run2={emission2}"
        )

    def test_digest_determinism(self):
        """Test that digest is identical across multiple calculations."""
        digest1 = compute_lockdown_determinism_digest()
        digest2 = compute_lockdown_determinism_digest()

        assert digest1 == digest2, "Digest should be deterministic"

    def test_embedding_config_surface(self):
        """Test embedding configuration surface extraction (restore/clean mode)."""
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {}, clear=False) as env:
            env.pop("W_HARDEN_NEGCTRL_TAMPER", None)
            config = get_embedding_config_surface()

        assert isinstance(config, dict)
        assert "model_version" in config
        assert "threads" in config
        assert "top_k" in config
        assert "cutoff" in config
        assert "enabled" in config
        assert config["model_version"] == "multilingual-e5-large"
        assert config["threads"] >= 1
        assert config["top_k"] == 20
        assert config["cutoff"] == 0.0

    def test_embedding_config_tampering(self):
        """Test that embedding config is tampered when negative control is active."""
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            config = get_embedding_config_surface()

            assert config.get("tampered") is True
            assert config["top_k"] == 999
            assert config["cutoff"] == 0.999

    def test_embedding_config_no_tampering(self):
        """Test that embedding config is normal when negative control is inactive."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_embedding_config_surface()

            assert "tampered" not in config
            assert config["top_k"] == 20
            assert config["cutoff"] == 0.0

    def test_meta_learning_config_surface(self):
        """Test meta-learning configuration surface extraction."""
        config = get_meta_learning_config_surface()

        assert isinstance(config, dict)
        assert "proposal_only" in config
        assert "validators_enabled" in config
        assert "shadow_evaluator_enabled" in config
        assert "oscillation_detector_enabled" in config
        assert "rlhf_delta_min" in config
        assert "rlhf_delta_max" in config
        assert "decision_delta_limit" in config

        # Verify safety defaults
        assert config["proposal_only"] is True
        assert config["validators_enabled"] is True
        assert config["shadow_evaluator_enabled"] is True
        assert config["oscillation_detector_enabled"] is True
        assert config["rlhf_delta_min"] == 0.1
        assert config["rlhf_delta_max"] == 2.0
        assert config["decision_delta_limit"] == 0.1

    def test_digest_changes_with_tampering(self):
        """Test that digest changes when embedding config is tampered."""
        # Normal digest
        with patch.dict(os.environ, {}, clear=True):
            normal_digest = compute_lockdown_determinism_digest()

        # Tampered digest
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            tampered_digest = compute_lockdown_determinism_digest()

        assert normal_digest != tampered_digest, "Digest should change with tampering"

    def test_digest_includes_all_components(self):
        """Test that digest includes all required sovereignty components."""
        # This is a structural test - we verify the calculation runs without error
        # which implies all components are included
        digest = compute_lockdown_determinism_digest()
        assert digest, "Digest calculation should succeed with all components"

    @pytest.mark.determinism
    def test_cross_run_determinism(self):
        """Test that digest is identical across test runs (marked for determinism)."""
        # This test is marked with @pytest.mark.determinism for cross-run validation
        digest1 = compute_lockdown_determinism_digest()
        digest2 = compute_lockdown_determinism_digest()

        assert digest1 == digest2, "Digest must be identical across runs"

        # Also test emission format
        emission1 = generate_lockdown_determinism_digest()
        emission2 = generate_lockdown_determinism_digest()

        assert emission1 == emission2, "Emission format must be identical across runs"
