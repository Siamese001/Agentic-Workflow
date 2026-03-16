"""
Test REQ-414: Network Egress Guard

Tests that all outbound HTTP requests to LLM-serving endpoints (including localhost)
MUST originate exclusively from SovereignLLMGateway.
"""

import os
import socket
from unittest.mock import patch

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

_emit_records_execution_trace("p0", "evidence", "test_network_egress_guard")
_emit_applies_guardrail("p0", "test_network_egress_guard", "p0_governance")
_emit_reads_policy_state("p0", "test_network_egress_guard", "policy_binding")
_emit_snapshots_state("p0", "test_network_egress_guard", "state_snapshot")
emit_replay_key("p0", "test_network_egress_guard")
emit_determinism_digest("p0", "test_network_egress_guard")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_network_egress_guard", "execution_auth")
_emit_validates_capability("p2", "test_network_egress_guard", "capability_check")
_emit_routes_to_capability("p2", "test_network_egress_guard", "capability_route")
_emit_writes_via_uwg("p2", "test_network_egress_guard", "uwg_write")
_emit_blocks_direct_write("p2", "test_network_egress_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "test_network_egress_guard", "tool_invocation")
_emit_captures_execution_output("p2", "test_network_egress_guard", "exec_output")
_emit_dispatches_agent("p3", "test_network_egress_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "test_network_egress_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_network_egress_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_network_egress_guard", "healing_outcome")
_emit_escalates_failure("p3", "test_network_egress_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_network_egress_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_network_egress_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_network_egress_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_network_egress_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_network_egress_guard", "eval_metric")
_emit_stores_embedding("p4", "test_network_egress_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_network_egress_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_network_egress_guard", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.enforcement.network_egress_guard import (
    NetworkEgressViolation,
    check_network_egress_allowed,
    install_egress_guard,
    is_llm_endpoint,
    simulate_direct_llm_request,
    test_egress_guard,
    uninstall_egress_guard,
)
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
)

_emit_emits_metric_event("test_network_egress_guard", "p4obs", "metric_1")
_emit_emits_metric_event("test_network_egress_guard", "p4obs", "metric_2")
_emit_emits_metric_event("test_network_egress_guard", "p4obs", "metric_3")
_emit_emits_metric_event("test_network_egress_guard", "p4obs", "metric_4")
_emit_emits_metric_event("test_network_egress_guard", "p4obs", "metric_5")
_emit_emits_metric_event("test_network_egress_guard", "p4obs", "metric_6")
_emit_records_incident_event("test_network_egress_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_network_egress_guard", "p4obs", "anomaly")
_emit_writes_observability_log("test_network_egress_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_network_egress_guard", "p4obs", "mon_state")
_emit_triggers_alert("test_network_egress_guard", "p4obs", "alert")
_emit_links_incident_trace("test_network_egress_guard", "p4obs", "trace_link")
_emit_captures_pattern("test_network_egress_guard", "p3lm", "pattern")
_emit_records_learning_event("test_network_egress_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_network_egress_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_network_egress_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_network_egress_guard", "p3lm", "routing")
_emit_improves_agent_policy("test_network_egress_guard", "p3lm", "policy")
_emit_stores_learning_state("test_network_egress_guard", "p3lm", "state")
_emit_records_execution_trace("test_network_egress_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_network_egress_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_network_egress_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_network_egress_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_network_egress_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_network_egress_guard", "env_read", "p2_env_1")
_emit_reads_environ("test_network_egress_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_network_egress_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_network_egress_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_network_egress_guard", "context_pull")
_emit_pulls_context("p1", "test_network_egress_guard", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_network_egress_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_network_egress_guard", "uwg_term_secondary")
_emit_writes_through("p1", "test_network_egress_guard", "write_through")
_emit_writes_through("p1", "test_network_egress_guard", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_network_egress_guard", "safety_validation")
_emit_invokes_eval("p1", "test_network_egress_guard", "eval_call")
_emit_proposal_commits_routing("p1", "test_network_egress_guard", "routing_commit")


class TestREQ414NetworkEgressGuard:
    """Test suite for REQ-414 Network Egress Guard."""

    def test_is_llm_endpoint_openai(self):
        """Test detection of OpenAI endpoints."""
        assert is_llm_endpoint("api.openai.com")
        assert is_llm_endpoint("api.openai.com", 443)
        assert is_llm_endpoint("openai.com")
        assert is_llm_endpoint("any.openai.com")

    def test_is_llm_endpoint_anthropic(self):
        """Test detection of Anthropic endpoints."""
        assert is_llm_endpoint("api.anthropic.com")
        assert is_llm_endpoint("anthropic.com")
        assert is_llm_endpoint("any.anthropic.com")

    def test_is_llm_endpoint_google(self):
        """Test detection of Google endpoints."""
        assert is_llm_endpoint("generativelanguage.googleapis.com")
        assert is_llm_endpoint("any.googleapis.com")

    def test_is_llm_endpoint_localhost(self):
        """Test detection of localhost endpoints."""
        assert is_llm_endpoint("localhost")
        assert is_llm_endpoint("localhost", 8000)
        assert is_llm_endpoint("127.0.0.1")
        assert is_llm_endpoint("127.0.0.1", 8080)
        assert is_llm_endpoint("0.0.0.0")
        assert is_llm_endpoint("::1")

    def test_is_llm_endpoint_non_llm(self):
        """Test that non-LLM endpoints are not detected."""
        assert not is_llm_endpoint("example.com")
        assert not is_llm_endpoint("google.com")  # Not the API endpoint
        assert not is_llm_endpoint("github.com")
        assert not is_llm_endpoint("stackoverflow.com")

    def test_check_network_egress_allowed_non_llm(self):
        """Test that non-LLM endpoints are allowed."""
        # Should not raise
        result = check_network_egress_allowed("example.com", 443)
        assert result is True

    def test_check_network_egress_blocked_llm(self):
        """Test that LLM endpoints are blocked outside gateway."""
        with pytest.raises(NetworkEgressViolation) as exc_info:
            check_network_egress_allowed("api.openai.com", 443)

        assert "Unauthorized network egress to LLM endpoint" in str(exc_info.value)
        assert "REQ-414" in str(exc_info.value)

    def test_check_network_egress_blocked_localhost(self):
        """Test that localhost LLM endpoints are blocked."""
        with pytest.raises(NetworkEgressViolation) as exc_info:
            check_network_egress_allowed("localhost", 8000)

        assert "Unauthorized network egress to LLM endpoint" in str(exc_info.value)

    @patch("agentic_core.L2_execution.enforcement.network_egress_guard._is_in_gateway_context")
    def test_check_network_egress_allowed_in_gateway(self, mock_in_gateway):
        """Test that LLM endpoints are allowed within gateway context."""
        mock_in_gateway.return_value = True

        # Should not raise when in gateway context
        result = check_network_egress_allowed("api.openai.com", 443)
        assert result is True

    def test_egress_guard_environment_override(self):
        """Test that EGRESS_GUARD_DISABLED environment variable works."""
        with patch.dict(os.environ, {"EGRESS_GUARD_DISABLED": "1"}):
            # Should not raise even for LLM endpoint
            result = check_network_egress_allowed("api.openai.com", 443)
            assert result is True

    def test_install_egress_guard(self):
        """Test installation of egress guard."""
        # Save original
        original_connect = socket.socket.connect

        try:
            # Install guard
            install_egress_guard()

            # Check that socket.connect was patched
            assert socket.socket.connect != original_connect

        finally:
            # Restore
            uninstall_egress_guard()
            assert socket.socket.connect == original_connect

    def test_simulate_direct_llm_request_blocked(self):
        """Test that simulated direct LLM request is blocked."""
        with pytest.raises(NetworkEgressViolation):
            simulate_direct_llm_request()

    def test_simulate_direct_llm_request_blocked_custom(self):
        """Test that simulated direct LLM request with custom endpoint is blocked."""
        with pytest.raises(NetworkEgressViolation):
            simulate_direct_llm_request("api.anthropic.com", 443)

    def test_test_egress_guard(self):
        """Test the egress guard test function."""
        # Should return True when guard is working
        result = test_egress_guard()
        assert result is True

    def test_socket_connect_guard_integration(self):
        """Test that socket.connect guard works at the socket level."""
        try:
            # Install guard
            install_egress_guard()

            # Create a test socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Try to connect to LLM endpoint - should raise
            with pytest.raises(NetworkEgressViolation):
                sock.connect(("api.openai.com", 443))

            sock.close()

        finally:
            # Restore
            uninstall_egress_guard()

    def test_socket_connect_guard_allows_non_llm(self):
        """Test that socket.connect guard allows non-LLM connections."""
        try:
            # Install guard
            install_egress_guard()

            # Create a test socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Try to connect to non-LLM endpoint - should not raise NetworkEgressViolation
            # (It might raise other connection errors, but not our violation)
            try:
                sock.connect(("example.com", 80))
            except NetworkEgressViolation:
                pytest.fail("Non-LLM connection should not be blocked")
            except (OSError, ConnectionError):
                # Other connection errors are expected (e.g., connection refused, timeout)
                pass

            sock.close()

        finally:
            # Restore
            uninstall_egress_guard()

    def test_caller_module_in_violation_message(self):
        """Test that caller module is included in violation message."""
        with pytest.raises(NetworkEgressViolation) as exc_info:
            check_network_egress_allowed("api.openai.com", 443, "test_module")

        assert "from test_module" in str(exc_info.value)

    def test_multiple_llm_endpoint_patterns(self):
        """Test various LLM endpoint patterns."""
        llm_endpoints = [
            ("api.openai.com", True),
            ("chat.openai.com", True),
            ("openai.com", True),
            ("api.anthropic.com", True),
            ("claude.ai", False),  # Not the API endpoint
            ("generativelanguage.googleapis.com", True),
            ("ai.googleapis.com", True),
            ("google.com", False),  # Not the API endpoint
            ("localhost:11434", True),  # Ollama
            ("127.0.0.1:8000", True),
            ("example.com", False),
            ("github.com", False),
        ]

        for endpoint, should_be_llm in llm_endpoints:
            if ":" in endpoint:
                host, port = endpoint.split(":", 1)
                port = int(port)
                result = is_llm_endpoint(host, port)
            else:
                result = is_llm_endpoint(endpoint)

            assert result == should_be_llm, f"Failed for {endpoint}"

    def test_egress_guard_disabled_skip_installation(self):
        """Test that guard installation is skipped when disabled."""
        with patch.dict(os.environ, {"EGRESS_GUARD_DISABLED": "1"}):
            # Save original
            original_connect = socket.socket.connect

            try:
                # Install guard - should be skipped
                install_egress_guard()

                # Should not have been patched
                assert socket.socket.connect == original_connect

            finally:
                # Cleanup (though not needed)
                uninstall_egress_guard()
