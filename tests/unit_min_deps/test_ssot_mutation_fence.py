"""Tests for SSOT Mutation Fence Hardening (Wave 2)."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
)
#  # MOVED: from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    ProtectedRootPolicy,
    SourceMutationBlocked,
    enforce_protected_root,
    get_default_protected_root_policy,
)
#  # MOVED: from agentic_core.L2_execution.tools import write_gateway
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_ssot_mutation_fence")
# REMOVED: _emit_applies_guardrail("p0", "test_ssot_mutation_fence", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_ssot_mutation_fence", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_ssot_mutation_fence", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_ssot_mutation_fence", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_ssot_mutation_fence", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_ssot_mutation_fence", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_ssot_mutation_fence", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_ssot_mutation_fence", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_ssot_mutation_fence", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_ssot_mutation_fence", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_ssot_mutation_fence", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_ssot_mutation_fence", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_ssot_mutation_fence", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_ssot_mutation_fence", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_ssot_mutation_fence", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_ssot_mutation_fence", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_ssot_mutation_fence", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_ssot_mutation_fence", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_ssot_mutation_fence", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_ssot_mutation_fence", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_ssot_mutation_fence", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_ssot_mutation_fence", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_ssot_mutation_fence", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_ssot_mutation_fence", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_ssot_mutation_fence", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_ssot_mutation_fence", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_ssot_mutation_fence", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_ssot_mutation_fence", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_ssot_mutation_fence", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_ssot_mutation_fence", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_ssot_mutation_fence", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_ssot_mutation_fence", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ssot_mutation_fence", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ssot_mutation_fence", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_ssot_mutation_fence", "write_through")
# REMOVED: _emit_writes_through("p1", "test_ssot_mutation_fence", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_ssot_mutation_fence", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_ssot_mutation_fence", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_ssot_mutation_fence", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_ssot_mutation_fence", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_ssot_mutation_fence", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_ssot_mutation_fence", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_ssot_mutation_fence", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_ssot_mutation_fence", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_ssot_mutation_fence", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_ssot_mutation_fence", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_ssot_mutation_fence", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_ssot_mutation_fence", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_ssot_mutation_fence", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_ssot_mutation_fence", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_ssot_mutation_fence")
# REMOVED: _emit_gated_by_confidence("p1", "test_ssot_mutation_fence", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_ssot_mutation_fence")
# REMOVED: emit_determinism_digest("p0", "test_ssot_mutation_fence")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_ssot_mutation_fence", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_ssot_mutation_fence", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_ssot_mutation_fence", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_ssot_mutation_fence", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_ssot_mutation_fence", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_ssot_mutation_fence", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_ssot_mutation_fence", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_ssot_mutation_fence", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_ssot_mutation_fence", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_ssot_mutation_fence", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_ssot_mutation_fence", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_ssot_mutation_fence", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_ssot_mutation_fence", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_ssot_mutation_fence", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_ssot_mutation_fence", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_ssot_mutation_fence", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_ssot_mutation_fence", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_ssot_mutation_fence", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_ssot_mutation_fence", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_ssot_mutation_fence", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


@pytest.mark.unit_min_deps
class TestProtectedRootEnforcement:
    """Test protected-root enforcement primitives."""

    def test_enforce_protected_root_blocks_agentic_core(self):
                from agentic_core.L0_routing.config.path_constants import (
                from agentic_core.L0_routing.enforcement.mutation_prohibition import (
                from agentic_core.L2_execution.tools import write_gateway
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L0_routing.enforcement.mutation_prohibition import (
                import agentic_core.L0_routing.scripts.execute_ssot as execute_ssot_module
                from agentic_core.L2_execution.tools import write_gateway
                from agentic_core.L0_routing.enforcement.mutation_prohibition import (
                from agentic_core.L0_routing.enforcement.mutation_prohibition import (
                """Test that writes to agentic_core are blocked."""
                target_path = Path("agentic_core/test_file.py")
                with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
                    enforce_protected_root(target_path, allow_override=False)

            enforce_protected_root(target_path, allow_override=False)

    def test_enforce_protected_root_allows_outside(self):
        """Test that writes outside protected roots are allowed."""
        target_path = Path("docs/evidence/test.md")
        # Should not raise
        enforce_protected_root(target_path, allow_override=False)

    def test_enforce_protected_root_override_allows(self):
        """Test that override allows writes to protected roots."""
        target_path = Path("agentic_core/test_file.py")
        # Should not raise when override is enabled
        enforce_protected_root(target_path, allow_override=True)

    def test_enforce_protected_root_blocks_tests(self):
        """Test that writes to tests directory are blocked (tests is a protected root)."""
        target_path = Path("tests/test_file.py")
        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            enforce_protected_root(target_path, allow_override=False)

    def test_enforce_protected_root_blocks_github(self):
        """Test that writes to .github directory are blocked."""
        target_path = Path(".github/workflows/test.yml")
        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            enforce_protected_root(target_path, allow_override=False)

    def test_exception_includes_matched_root_agentic_core(self):
        """Test that exception message includes the matched immutable root."""
        target_path = Path("agentic_core/test_file.py")
        with pytest.raises(SourceMutationBlocked, match="matched_root=agentic_core"):
            enforce_protected_root(target_path, allow_override=False)

    def test_exception_includes_matched_root_github(self):
        """Test that exception message includes matched root for .github directory."""
        target_path = Path(".github/workflows/test.yml")
        with pytest.raises(SourceMutationBlocked, match=r"matched_root=\.github"):
            enforce_protected_root(target_path, allow_override=False)


@pytest.mark.unit_min_deps
class TestWriteGatewayIntegration:
    """Test write gateway integration with protected-root enforcement."""

    @patch("pathlib.Path.write_text")
    def test_write_gateway_blocks_protected_root(self, mock_write):
        """Test that write_gateway blocks protected root writes."""
        target_path = Path("agentic_core/test_file.py")

        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            write_gateway.write_text(target_path, "test content")

        # Ensure no actual write occurred
        mock_write.assert_not_called()

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.read_bytes", return_value=b"test content")
    @patch("pathlib.Path.write_text")
    def test_write_gateway_allows_outside_protected_root(self, mock_write, mock_read, mock_mkdir):
        """Test that write_gateway allows writes outside protected roots."""
        target_path = Path("docs/evidence/test.md")

        # Should not raise
        write_gateway.write_text(target_path, "test content")

        # Verify write was attempted
        mock_write.assert_called_once_with("test content", encoding="utf-8")

    @patch("pathlib.Path.write_bytes")
    def test_write_bytes_blocks_protected_root(self, mock_write):
        """Test that write_bytes blocks protected root writes."""
        target_path = Path("agentic_core/test_file.bin")

        with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
            write_gateway.write_bytes(target_path, b"test data")

        # Ensure no actual write occurred
        mock_write.assert_not_called()


@pytest.mark.unit_min_deps
class TestBlockEventEmission:
    """Test block event emission to JSONL log."""

    def test_block_emits_jsonl_event(self, tmp_path):
        """Test that a block attempt produces exactly one JSONL line with required fields."""
        target_path = Path("agentic_core/test_file.py")
        log_file = tmp_path / "blocks.jsonl"

        # Monkeypatch the log path
        with patch("agentic_core.L0_routing.enforcement.mutation_prohibition.Path") as mock_path_cls:
            # Make Path() constructor work normally for target_path
            mock_path_cls.side_effect = lambda x: (
                Path(x) if x != "logs/ssot_protected_root_blocks.jsonl" else log_file
            )

            # Also need to patch the open call to use our tmp_path
            original_open = open

            def patched_open(path, *args, **kwargs):
                if "logs/ssot_protected_root_blocks.jsonl" in str(path):
                    return original_open(log_file, *args, **kwargs)
                return original_open(path, *args, **kwargs)

            with patch("builtins.open", side_effect=patched_open):
                with pytest.raises(SourceMutationBlocked):
                    enforce_protected_root(target_path, allow_override=False)

        # Verify JSONL event was written
        assert log_file.exists()
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 1

        # Parse and verify event structure
        event = json.loads(lines[0])
        assert "ts_utc" in event
        assert "target" in event
        assert "matched_root" in event
        assert event["matched_root"] == AGENTIC_CORE_DIR
        assert "caller" in event
        assert event["caller"] == "mutation_prohibition:enforce_protected_root"

    def test_logging_failure_does_not_mask_exception(self):
        """Test that logging failures do not mask SourceMutationBlocked."""
        target_path = Path("agentic_core/test_file.py")

        # Monkeypatch open to raise an exception
        with patch("builtins.open", side_effect=PermissionError("Simulated logging failure")):
            # Should still raise SourceMutationBlocked, not PermissionError
            with pytest.raises(SourceMutationBlocked, match="Protected root mutation blocked"):
                enforce_protected_root(target_path, allow_override=False)

    def test_exception_message_still_includes_diagnostics(self):
        """Test that exception message still includes target and matched_root after adding emission."""
        target_path = Path("agentic_core/test_file.py")

        with pytest.raises(SourceMutationBlocked) as exc_info:
            enforce_protected_root(target_path, allow_override=False)
        e = exc_info.value
        msg = str(e)
        assert "target=" in msg
        assert "matched_root=agentic_core" in msg


@pytest.mark.unit_min_deps
class TestPolicyContract:
    """Test protected-root policy contract and configurability."""

    def test_default_policy_immutable_roots(self):
        """Test that default policy has exactly the canonical immutable roots."""
        policy = get_default_protected_root_policy()
        assert policy.immutable_roots == (AGENTIC_CORE_DIR, TESTS_DIR, ".github", ".windsurfrules")

    def test_default_policy_log_path(self):
        """Test that default policy has the canonical log path."""
        policy = get_default_protected_root_policy()
        assert policy.log_path == "logs/ssot_protected_root_blocks.jsonl"

    def test_policy_override_log_path_writes_to_tmp(self, tmp_path):
        """Test that overriding policy.log_path writes JSONL to tmp_path (no writes to repo logs)."""
        target_path = Path("agentic_core/test_file.py")
        log_file = tmp_path / "test_blocks.jsonl"

        # Create custom policy with tmp_path log
        custom_policy = ProtectedRootPolicy(
            immutable_roots=(AGENTIC_CORE_DIR, TESTS_DIR, ".github"), log_path=str(log_file)
        )

        # Ensure tmp log doesn't exist before test
        assert not log_file.exists()

        # Attempt block with custom policy
        with pytest.raises(SourceMutationBlocked):
            enforce_protected_root(target_path, allow_override=False, policy=custom_policy)

        # Verify JSONL was written to tmp_path
        assert log_file.exists()

        # Verify event structure
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 1  # Exactly one event written
        event = json.loads(lines[0])
        assert event["matched_root"] == AGENTIC_CORE_DIR
        assert "target" in event
        assert "ts_utc" in event
        assert "caller" in event

    def test_policy_override_immutable_roots_changes_matched_root(self, tmp_path):
        """Test that changing policy.immutable_roots changes matched_root in exception and event."""
        target_path = Path("custom_protected/test_file.py")
        log_file = tmp_path / "test_blocks.jsonl"

        # Create custom policy with different immutable roots
        custom_policy = ProtectedRootPolicy(immutable_roots=("custom_protected",), log_path=str(log_file))

        # Attempt block with custom policy
        with pytest.raises(SourceMutationBlocked) as exc_info:
            enforce_protected_root(target_path, allow_override=False, policy=custom_policy)
        e = exc_info.value
        msg = str(e)
        assert "matched_root=custom_protected" in msg

        # Verify event has correct matched_root
        assert log_file.exists()
        lines = log_file.read_text().strip().split("\n")
        event = json.loads(lines[-1])
        assert event["matched_root"] == "custom_protected"

    def test_policy_none_uses_default(self):
        """Test that policy=None uses the default policy."""
        target_path = Path("agentic_core/test_file.py")

        # Should block with default policy
        with pytest.raises(SourceMutationBlocked, match="matched_root=agentic_core"):
            enforce_protected_root(target_path, allow_override=False, policy=None)


@pytest.mark.unit_min_deps
class TestEnvVarIsolation:
    """Test that env vars do not affect protected-root enforcement in SSOT path."""

    def test_env_allow_mutation_does_not_bypass_protected_root(self, monkeypatch):
        """Test that AGENTIC_ALLOW_MUTATION_FOR_TESTS does not bypass protected-root enforcement."""
        target_path = Path("agentic_core/test_file.py")

        # Set env var that should NOT affect protected-root behavior
        monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")

        # Should still block (env var should not affect protected-root enforcement)
        with pytest.raises(SourceMutationBlocked, match="matched_root=agentic_core"):
            enforce_protected_root(target_path, allow_override=False)

    def test_env_deny_mutation_does_not_change_protected_root(self, monkeypatch):
        """Test that AGENTIC_DENY_SOURCE_MUTATION does not change protected-root behavior."""
        target_path = Path("agentic_core/test_file.py")

        # Set env var that should NOT affect protected-root behavior
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        # Should still block (same behavior with or without env var)
        with pytest.raises(SourceMutationBlocked, match="matched_root=agentic_core"):
            enforce_protected_root(target_path, allow_override=False)

    def test_cli_override_works_regardless_of_env(self, monkeypatch):
        """Test that CLI override (allow_override=True) works regardless of env vars."""
        target_path = Path("agentic_core/test_file.py")

        # Set env vars that should NOT interfere
        monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "0")
        monkeypatch.setenv("AGENTIC_DENY_SOURCE_MUTATION", "1")

        # CLI override should allow bypass regardless of env vars
        enforce_protected_root(target_path, allow_override=True)  # Should not raise

    def test_unset_env_vars_do_not_change_behavior(self, monkeypatch):
    """Test unset_env_vars_do_not_change_behavior runtime behavior."""
    # Arrange
    # TODO: Set up test data for unset_env_vars_do_not_change_behavior
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute unset_env_vars_do_not_change_behavior
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
class TestFenceSelfCheck:
    """Test fence self-check mode validates policy + wiring."""

    def test_self_check_ok_path(self):
        """Test that self-check produces status ok JSON when all checks pass."""
        import json
        import subprocess

        result = subprocess.run(
            ["python", "-m", "agentic_core.L0_routing.scripts.execute_ssot_entrypoint", "--fence-self-check"],
            capture_output=True,
            text=True,
        )

        # Should exit 0
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}"

        # Should output valid JSON
        output = json.loads(result.stdout.strip())
        assert output["status"] == "ok"
        assert output["checks"] == 4

    def test_self_check_fails_with_bad_log_path(self, monkeypatch):
        """Test that self-check fails when log_path is under agentic_core."""
#  # MOVED: from agentic_core.L0_routing.enforcement.mutation_prohibition import (
            ProtectedRootPolicy,
        )

        # Monkeypatch get_default_protected_root_policy to return bad log_path
        def bad_policy():
            return ProtectedRootPolicy(
                immutable_roots=(AGENTIC_CORE_DIR, TESTS_DIR, ".github"),
                log_path="agentic_core/bad_log.jsonl",  # Under protected root!
            )

#  # MOVED: import agentic_core.L0_routing.scripts.execute_ssot as execute_ssot_module

        monkeypatch.setattr(
            "agentic_core.L0_routing.enforcement.mutation_prohibition.get_default_protected_root_policy",
            bad_policy,
        )

        # Run self-check
        with pytest.raises(SystemExit) as exc_info:
            execute_ssot_module.run_fence_self_check()

        # Should exit with nonzero
        assert exc_info.value.code != 0

    def test_self_check_validates_write_gateway_wiring(self):
        """Test that self-check validates write_gateway has enforce_protected_root calls."""
        import inspect

#  # MOVED: from agentic_core.L2_execution.tools import write_gateway

        # Verify write_text has allow_override parameter
        sig = inspect.signature(write_gateway.write_text)
        assert "allow_override" in sig.parameters

        # Verify write_text source contains enforce_protected_root
        source = inspect.getsource(write_gateway.write_text)
        assert "enforce_protected_root" in source


@pytest.mark.unit_min_deps
class TestDeterministicReplay:
    """Test deterministic replay verification for protected-root fence behavior."""

    def test_replay_block_event_is_identical_under_fixed_clock(self, tmp_path, monkeypatch):
        """Test that blocked-write telemetry is identical across runs with fixed timestamp."""
#  # MOVED: from agentic_core.L0_routing.enforcement.mutation_prohibition import (
            _emit_block_event,
        )

        target_path = Path("agentic_core/test_file.py").resolve()
        matched_root = AGENTIC_CORE_DIR
        fixed_ts = "2026-02-21T23:00:00+00:00"

        # Run 1: Emit event with fixed timestamp
        log_file_1 = tmp_path / "run1.jsonl"
# REMOVED:         _emit_block_event(target_path, matched_root, str(log_file_1), ts_utc_override=fixed_ts)

        # Run 2: Emit event with same fixed timestamp
        log_file_2 = tmp_path / "run2.jsonl"
# REMOVED:         _emit_block_event(target_path, matched_root, str(log_file_2), ts_utc_override=fixed_ts)

        # Verify JSONL lines are bitwise identical
        content_1 = log_file_1.read_text(encoding="utf-8")
        content_2 = log_file_2.read_text(encoding="utf-8")

        assert content_1 == content_2, "JSONL output should be identical under fixed clock"

        # Verify content is valid JSON with expected fields
        import json

        event = json.loads(content_1.strip())
        assert event["ts_utc"] == fixed_ts
        assert event["matched_root"] == matched_root
        assert "target" in event
        assert "caller" in event

    def test_self_check_output_is_bitwise_identical_across_runs(self):
        """Test that self-check JSON output is bitwise identical across multiple runs."""
        import json
        import subprocess

        # Run self-check twice
        result_1 = subprocess.run(
            ["python", "-m", "agentic_core.L0_routing.scripts.execute_ssot_entrypoint", "--fence-self-check"],
            capture_output=True,
            text=True,
        )

        result_2 = subprocess.run(
            ["python", "-m", "agentic_core.L0_routing.scripts.execute_ssot_entrypoint", "--fence-self-check"],
            capture_output=True,
            text=True,
        )

        # Both should succeed
        assert result_1.returncode == 0
        assert result_2.returncode == 0

        # Outputs should be bitwise identical
        assert result_1.stdout == result_2.stdout, "Self-check output should be deterministic"

        # Verify it's valid JSON
        output = json.loads(result_1.stdout.strip())
        assert output["status"] == "ok"
        assert output["checks"] == 4

    def test_block_event_without_override_uses_real_time(self, tmp_path):
        """Test that block events without override use real UTC time (not deterministic)."""
        import time

#  # MOVED: from agentic_core.L0_routing.enforcement.mutation_prohibition import (
            _emit_block_event,
        )

        target_path = Path("agentic_core/test_file.py").resolve()
        matched_root = AGENTIC_CORE_DIR

        # Run 1
        log_file_1 = tmp_path / "run1.jsonl"
# REMOVED:         _emit_block_event(target_path, matched_root, str(log_file_1))

        # Small delay to ensure different timestamp
        time.sleep(DEFAULT_SLEEP)

        # Run 2
        log_file_2 = tmp_path / "run2.jsonl"
# REMOVED:         _emit_block_event(target_path, matched_root, str(log_file_2))

        # Verify timestamps are different (real time behavior)
        import json

        event_1 = json.loads(log_file_1.read_text().strip())
        event_2 = json.loads(log_file_2.read_text().strip())

        assert event_1["ts_utc"] != event_2["ts_utc"], "Real timestamps should differ across runs"
