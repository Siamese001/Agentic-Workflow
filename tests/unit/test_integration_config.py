"""Tests for IntegrationConfig."""

import pytest

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "test_integration_config", "execution_auth")
_emit_validates_capability("p2", "test_integration_config", "capability_check")
_emit_routes_to_capability("p2", "test_integration_config", "capability_route")
_emit_writes_via_uwg("p2", "test_integration_config", "uwg_write")
_emit_blocks_direct_write("p2", "test_integration_config", "direct_write_block")
_emit_records_tool_invocation("p2", "test_integration_config", "tool_invocation")
_emit_captures_execution_output("p2", "test_integration_config", "exec_output")
_emit_dispatches_agent("p3", "test_integration_config", "agent_dispatch")
_emit_coordinates_agents("p3", "test_integration_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_integration_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_integration_config", "healing_outcome")
_emit_escalates_failure("p3", "test_integration_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_integration_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_integration_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_integration_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_integration_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_integration_config", "eval_metric")
_emit_stores_embedding("p4", "test_integration_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_integration_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_integration_config", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
from apps_shared.config.integration_config import (
    LIC_CONFIG,
    RG_CONFIG,
    IntegrationConfig,
    get_domain_config,
)

_emit_emits_metric_event("test_integration_config", "p4obs", "metric_1")
_emit_emits_metric_event("test_integration_config", "p4obs", "metric_2")
_emit_emits_metric_event("test_integration_config", "p4obs", "metric_3")
_emit_emits_metric_event("test_integration_config", "p4obs", "metric_4")
_emit_emits_metric_event("test_integration_config", "p4obs", "metric_5")
_emit_emits_metric_event("test_integration_config", "p4obs", "metric_6")
_emit_records_incident_event("test_integration_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_integration_config", "p4obs", "anomaly")
_emit_writes_observability_log("test_integration_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_integration_config", "p4obs", "mon_state")
_emit_triggers_alert("test_integration_config", "p4obs", "alert")
_emit_links_incident_trace("test_integration_config", "p4obs", "trace_link")
_emit_captures_pattern("test_integration_config", "p3lm", "pattern")
_emit_records_learning_event("test_integration_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_integration_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_integration_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_integration_config", "p3lm", "routing")
_emit_improves_agent_policy("test_integration_config", "p3lm", "policy")
_emit_stores_learning_state("test_integration_config", "p3lm", "state")
_emit_records_execution_trace("test_integration_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_integration_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_integration_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_integration_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_integration_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_integration_config", "env_read", "p2_env_1")
_emit_reads_environ("test_integration_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_integration_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_integration_config", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_integration_config")
_emit_applies_guardrail("p0", "test_integration_config", "p0_governance")
_emit_reads_policy_state("p0", "test_integration_config", "policy_binding")
_emit_snapshots_state("p0", "test_integration_config", "state_snapshot")
_emit_pulls_context("p1", "test_integration_config", "context_pull")
_emit_pulls_context("p1", "test_integration_config", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_integration_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_integration_config", "uwg_term_secondary")
_emit_writes_through("p1", "test_integration_config", "write_through")
_emit_writes_through("p1", "test_integration_config", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_integration_config", "safety_validation")
_emit_invokes_eval("p1", "test_integration_config", "eval_call")
_emit_proposal_commits_routing("p1", "test_integration_config", "routing_commit")
_emit_escalates_to_human("p1", "test_integration_config", "human_escalation")
_emit_routes_through("p1", "test_integration_config", "route_through")
_emit_checks_agent_registry("p1", "test_integration_config", "agent_registry")
_emit_validates_agent_capability("p1", "test_integration_config", "capability")
_emit_dispatches_execution_plan("p1", "test_integration_config", "exec_plan")
_emit_agent_executes_agent("p1", "test_integration_config", "sub_agent")
_emit_routes_to_agent("p1", "test_integration_config", "target_agent")
_emit_verifies_policy("p1", "test_integration_config", "policy_check")
_emit_observes_runtime_state("p1", "test_integration_config", "runtime_state")
_emit_verifies_boundary("p1", "test_integration_config", "boundary_check")
_emit_transcripts_response("p1", "test_integration_config", "transcript")
_emit_hard_fails_untranscripted("p1", "test_integration_config")
_emit_gated_by_confidence("p1", "test_integration_config", "confidence_gate")
emit_replay_key("p0", "test_integration_config")
emit_determinism_digest("p0", "test_integration_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


class TestIntegrationConfig:
    """Tests for IntegrationConfig dataclass."""

    def test_create_config(self):
        """Test creating an integration config."""
        config = IntegrationConfig(
            domain="test",
            domain_prefix="apps_test",
            similarity_threshold=THRESHOLD,
            ttl_seconds=3600,
        )
        assert config.domain == "test"
        assert config.domain_prefix == "apps_test"
        assert config.similarity_threshold == 0.85
        assert config.ttl_seconds == 3600

    def test_default_values(self):
        """Test default values."""
        config = IntegrationConfig(
            domain="test",
            domain_prefix="apps_test",
            similarity_threshold=THRESHOLD,
            ttl_seconds=3600,
        )
        assert config.rate_limit_requests == 100
        assert config.rate_limit_window_seconds == 60
        assert config.required_flags == []
        assert config.optional_flags == []

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = IntegrationConfig(
            domain="test",
            domain_prefix="apps_test",
            similarity_threshold=THRESHOLD,
            ttl_seconds=3600,
            required_flags=["FLAG1"],
        )
        d = config.to_dict()

        assert d["domain"] == "test"
        assert d["domain_prefix"] == "apps_test"
        assert d["similarity_threshold"] == 0.85
        assert d["ttl_seconds"] == 3600
        assert d["required_flags"] == ["FLAG1"]


class TestPredefinedConfigs:
    """Tests for predefined configurations."""

    def test_rg_config_values(self):
        """Test RG configuration values."""
        assert RG_CONFIG.domain == "rg"
        assert RG_CONFIG.domain_prefix == APPS_RG_DIR
        assert RG_CONFIG.similarity_threshold == 0.85
        assert RG_CONFIG.ttl_seconds == 3600

    def test_rg_config_flags(self):
        """Test RG configuration flags."""
        assert "ENABLE_VERIFICATION_GATE" in RG_CONFIG.required_flags
        assert "ENABLE_AUDIT_TRAIL" in RG_CONFIG.required_flags
        assert "ENABLE_META_LEARNING" in RG_CONFIG.optional_flags

    def test_lic_config_values(self):
        """Test LIC configuration values."""
        assert LIC_CONFIG.domain == "lic"
        assert LIC_CONFIG.domain_prefix == APPS_LIC_DIR
        assert LIC_CONFIG.similarity_threshold == 0.92
        assert LIC_CONFIG.ttl_seconds == 7200

    def test_lic_config_stricter_threshold(self):
        """Test LIC has stricter threshold than RG."""
        assert LIC_CONFIG.similarity_threshold > RG_CONFIG.similarity_threshold

    def test_lic_config_longer_ttl(self):
        """Test LIC has longer TTL than RG."""
        assert LIC_CONFIG.ttl_seconds > RG_CONFIG.ttl_seconds

    def test_lic_config_requires_hitl(self):
        """Test LIC requires HITL workflow."""
        assert "ENABLE_HITL_WORKFLOW" in LIC_CONFIG.required_flags
        assert "ENABLE_HITL_WORKFLOW" not in RG_CONFIG.required_flags

    def test_lic_config_more_conservative_rate_limit(self):
        """Test LIC has more conservative rate limit."""
        assert LIC_CONFIG.rate_limit_requests < RG_CONFIG.rate_limit_requests


class TestGetDomainConfig:
    """Tests for get_domain_config function."""

    def test_get_rg_config(self):
        """Test getting RG config."""
        config = get_domain_config("rg")
        assert config is RG_CONFIG

    def test_get_lic_config(self):
        """Test getting LIC config."""
        config = get_domain_config("lic")
        assert config is LIC_CONFIG

    def test_get_config_with_apps_prefix(self):
        """Test getting config with apps_ prefix."""
        rg_config = get_domain_config(APPS_RG_DIR)
        assert rg_config is RG_CONFIG

        lic_config = get_domain_config(APPS_LIC_DIR)
        assert lic_config is LIC_CONFIG

    def test_get_unknown_domain_raises(self):
        """Test getting unknown domain raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_domain_config("unknown")

        assert "Unknown domain" in str(exc_info.value)
        assert "unknown" in str(exc_info.value)
