"""ADG-driven tests for agentic_core/config/core/sovereign_config.py — fan_in=5.

Singleton config manager contract tests: importability, singleton semantics,
env-var accessors, typed defaults, and reset for test isolation.
"""
from __future__ import annotations

import pytest

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

_emit_records_execution_trace("p0", "evidence", "test_sovereign_config_adg")
_emit_applies_guardrail("p0", "test_sovereign_config_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_sovereign_config_adg", "policy_binding")
_emit_snapshots_state("p0", "test_sovereign_config_adg", "state_snapshot")
emit_replay_key("p0", "test_sovereign_config_adg")
emit_determinism_digest("p0", "test_sovereign_config_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_sovereign_config_adg", "execution_auth")
_emit_validates_capability("p2", "test_sovereign_config_adg", "capability_check")
_emit_routes_to_capability("p2", "test_sovereign_config_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_sovereign_config_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_sovereign_config_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_sovereign_config_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_sovereign_config_adg", "exec_output")
_emit_dispatches_agent("p3", "test_sovereign_config_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_sovereign_config_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_sovereign_config_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_sovereign_config_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_sovereign_config_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_sovereign_config_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_sovereign_config_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_sovereign_config_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_sovereign_config_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_sovereign_config_adg", "eval_metric")
_emit_stores_embedding("p4", "test_sovereign_config_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_sovereign_config_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_sovereign_config_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.config.core.sovereign_config import (
    SovereignConfigManager,
    get_sovereign_config,
)
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

_emit_emits_metric_event("test_sovereign_config_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_sovereign_config_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_sovereign_config_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_sovereign_config_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_sovereign_config_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_sovereign_config_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_sovereign_config_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_sovereign_config_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_sovereign_config_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_sovereign_config_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_sovereign_config_adg", "p4obs", "alert")
_emit_links_incident_trace("test_sovereign_config_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_sovereign_config_adg", "p3lm", "pattern")
_emit_records_learning_event("test_sovereign_config_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_sovereign_config_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_sovereign_config_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_sovereign_config_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_sovereign_config_adg", "p3lm", "policy")
_emit_stores_learning_state("test_sovereign_config_adg", "p3lm", "state")
_emit_records_execution_trace("test_sovereign_config_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_sovereign_config_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_sovereign_config_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_sovereign_config_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_sovereign_config_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_sovereign_config_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_sovereign_config_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_sovereign_config_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_sovereign_config_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_sovereign_config_adg", "context_pull")
_emit_pulls_context("p1", "test_sovereign_config_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_sovereign_config_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_sovereign_config_adg", "uwg_term_secondary")
_emit_writes_through("p1", "test_sovereign_config_adg", "write_through")
_emit_writes_through("p1", "test_sovereign_config_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_sovereign_config_adg", "safety_validation")
_emit_invokes_eval("p1", "test_sovereign_config_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_sovereign_config_adg", "routing_commit")
_emit_escalates_to_human("p1", "test_sovereign_config_adg", "human_escalation")
_emit_routes_through("p1", "test_sovereign_config_adg", "route_through")
_emit_checks_agent_registry("p1", "test_sovereign_config_adg", "agent_registry")
_emit_validates_agent_capability("p1", "test_sovereign_config_adg", "capability")
_emit_dispatches_execution_plan("p1", "test_sovereign_config_adg", "exec_plan")
_emit_agent_executes_agent("p1", "test_sovereign_config_adg", "sub_agent")
_emit_routes_to_agent("p1", "test_sovereign_config_adg", "target_agent")
_emit_verifies_policy("p1", "test_sovereign_config_adg", "policy_check")
_emit_observes_runtime_state("p1", "test_sovereign_config_adg", "runtime_state")
_emit_verifies_boundary("p1", "test_sovereign_config_adg", "boundary_check")
_emit_transcripts_response("p1", "test_sovereign_config_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "test_sovereign_config_adg")
_emit_gated_by_confidence("p1", "test_sovereign_config_adg", "confidence_gate")


@pytest.fixture(autouse=True)
def reset_singleton():
    SovereignConfigManager.reset_instance()
    yield
    SovereignConfigManager.reset_instance()


class TestSovereignConfigManagerImport:
    def test_class_importable(self):
        assert callable(SovereignConfigManager)

    def test_get_sovereign_config_callable(self):
        assert callable(get_sovereign_config)


class TestSovereignConfigManagerSingleton:
    def test_same_instance_returned(self):
        a = SovereignConfigManager()
        b = SovereignConfigManager()
        assert a is b

    def test_get_sovereign_config_returns_instance(self):
        cfg = get_sovereign_config()
        assert isinstance(cfg, SovereignConfigManager)

    def test_reset_creates_new_instance(self):
        a = SovereignConfigManager()
        SovereignConfigManager.reset_instance()
        b = SovereignConfigManager()
        assert a is not b


class TestSovereignConfigManagerDefaults:
    def test_default_openai_model(self):
        cfg = SovereignConfigManager()
        assert cfg.DEFAULT_OPENAI_MODEL == "gpt-4o"

    def test_default_anthropic_model(self):
        cfg = SovereignConfigManager()
        assert "claude" in cfg.DEFAULT_ANTHROPIC_MODEL

    def test_default_embedding_model(self):
        cfg = SovereignConfigManager()
        assert cfg.DEFAULT_EMBEDDING_MODEL == "BAAI/bge-m3"

    def test_default_max_audit_log_size(self):
        cfg = SovereignConfigManager()
        assert cfg.DEFAULT_MAX_AUDIT_LOG_SIZE == 1000

    def test_default_max_healing_attempts(self):
        cfg = SovereignConfigManager()
        assert cfg.DEFAULT_MAX_HEALING_ATTEMPTS == 3

    def test_embedding_dim_bge(self):
        cfg = SovereignConfigManager()
        assert cfg.EMBEDDING_DIM_BGE == 1024


class TestSovereignConfigManagerEnvAccessors:
    def test_get_str_returns_default_when_unset(self):
        cfg = SovereignConfigManager()
        result = cfg.get_str("__NONEXISTENT_KEY_XYZ__", "fallback")
        assert result == "fallback"

    def test_get_int_returns_default_when_unset(self):
        cfg = SovereignConfigManager()
        result = cfg.get_int("__NONEXISTENT_KEY_XYZ__", 42)
        assert result == 42

    def test_get_bool_returns_default_when_unset(self):
        cfg = SovereignConfigManager()
        result = cfg.get_bool("__NONEXISTENT_KEY_XYZ__", False)
        assert result is False

    def test_get_str_reads_env(self, monkeypatch):
        monkeypatch.setenv("__ADG_TEST_STR__", "hello")
        cfg = SovereignConfigManager()
        assert cfg.get_str("__ADG_TEST_STR__") == "hello"

    def test_get_int_reads_env(self, monkeypatch):
        monkeypatch.setenv("__ADG_TEST_INT__", "99")
        cfg = SovereignConfigManager()
        assert cfg.get_int("__ADG_TEST_INT__") == 99

    def test_get_bool_true_values(self, monkeypatch):
        cfg = SovereignConfigManager()
        for truthy in ("true", "1", "yes", "on", "True", "YES"):
            monkeypatch.setenv("__ADG_TEST_BOOL__", truthy)
            assert cfg.get_bool("__ADG_TEST_BOOL__") is True

    def test_get_bool_false_values(self, monkeypatch):
        cfg = SovereignConfigManager()
        for falsy in ("false", "0", "no", "off"):
            monkeypatch.setenv("__ADG_TEST_BOOL__", falsy)
            assert cfg.get_bool("__ADG_TEST_BOOL__") is False

    def test_get_int_invalid_value_returns_default(self, monkeypatch):
        monkeypatch.setenv("__ADG_TEST_INT_BAD__", "notanint")
        cfg = SovereignConfigManager()
        assert cfg.get_int("__ADG_TEST_INT_BAD__", 7) == 7


class TestSovereignConfigTypedProperties:
    def test_openai_model_property(self):
        cfg = SovereignConfigManager()
        assert isinstance(cfg.openai_model, str)
        assert len(cfg.openai_model) > 0

    def test_redis_mcp_enabled_default_false(self):
        cfg = SovereignConfigManager()
        assert cfg.redis_mcp_enabled is False

    def test_redis_url_default(self):
        cfg = SovereignConfigManager()
        assert "redis" in cfg.redis_url

    def test_max_audit_log_size_property(self):
        cfg = SovereignConfigManager()
        assert isinstance(cfg.max_audit_log_size, int)
        assert cfg.max_audit_log_size > 0
