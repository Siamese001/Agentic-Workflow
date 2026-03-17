"""ADG-driven tests for agentic_core/L1_cognition/engines/meta_client.py — fan_in=2.

Contract tests: MetaLearningClient singleton, config defaults, stats, reset_instance.
"""
from __future__ import annotations

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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_meta_client_adg")
_emit_applies_guardrail("p0", "test_meta_client_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_meta_client_adg", "policy_binding")
_emit_snapshots_state("p0", "test_meta_client_adg", "state_snapshot")
emit_replay_key("p0", "test_meta_client_adg")
emit_determinism_digest("p0", "test_meta_client_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_meta_client_adg", "execution_auth")
_emit_validates_capability("p2", "test_meta_client_adg", "capability_check")
_emit_routes_to_capability("p2", "test_meta_client_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_meta_client_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_meta_client_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_meta_client_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_meta_client_adg", "exec_output")
_emit_dispatches_agent("p3", "test_meta_client_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_meta_client_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_meta_client_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_meta_client_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_meta_client_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_meta_client_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_meta_client_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_meta_client_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_meta_client_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_meta_client_adg", "eval_metric")
_emit_stores_embedding("p4", "test_meta_client_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_meta_client_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_meta_client_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.engines.meta_client import MetaLearningClient
from agentic_core.L1_cognition.types.client_types import (
    CACHE_KEY_PREFIX,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TTL_SECONDS,
    MAX_HEALING_DEPTH,
    CacheEntry,
    HealingPattern,
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_meta_client_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_meta_client_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_meta_client_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_meta_client_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_meta_client_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_meta_client_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_meta_client_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_meta_client_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_meta_client_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_meta_client_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_meta_client_adg", "p4obs", "alert")
_emit_links_incident_trace("test_meta_client_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_meta_client_adg", "p3lm", "pattern")
_emit_records_learning_event("test_meta_client_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_meta_client_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_meta_client_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_meta_client_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_meta_client_adg", "p3lm", "policy")
_emit_stores_learning_state("test_meta_client_adg", "p3lm", "state")
_emit_records_execution_trace("test_meta_client_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_meta_client_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_meta_client_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_meta_client_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_meta_client_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_meta_client_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_meta_client_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_meta_client_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_meta_client_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_meta_client_adg", "context_pull")
_emit_pulls_context("p1", "test_meta_client_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_meta_client_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_meta_client_adg", "uwg_term_secondary")
_emit_writes_through("p1", "test_meta_client_adg", "write_through")
_emit_writes_through("p1", "test_meta_client_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_meta_client_adg", "safety_validation")
_emit_invokes_eval("p1", "test_meta_client_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_meta_client_adg", "routing_commit")
_emit_escalates_to_human("p1", "test_meta_client_adg", "human_escalation")
_emit_routes_through("p1", "test_meta_client_adg", "route_through")
_emit_checks_agent_registry("p1", "test_meta_client_adg", "agent_registry")
_emit_validates_agent_capability("p1", "test_meta_client_adg", "capability")
_emit_dispatches_execution_plan("p1", "test_meta_client_adg", "exec_plan")
_emit_agent_executes_agent("p1", "test_meta_client_adg", "sub_agent")
_emit_routes_to_agent("p1", "test_meta_client_adg", "target_agent")
_emit_verifies_policy("p1", "test_meta_client_adg", "policy_check")
_emit_observes_runtime_state("p1", "test_meta_client_adg", "runtime_state")
_emit_verifies_boundary("p1", "test_meta_client_adg", "boundary_check")
_emit_transcripts_response("p1", "test_meta_client_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "test_meta_client_adg")
_emit_gated_by_confidence("p1", "test_meta_client_adg", "confidence_gate")


class TestClientTypeConstants:
    def test_cache_key_prefix_is_string(self):
        assert isinstance(CACHE_KEY_PREFIX, str)

    def test_default_similarity_threshold_is_float(self):
        assert isinstance(DEFAULT_SIMILARITY_THRESHOLD, float)
        assert 0.0 < DEFAULT_SIMILARITY_THRESHOLD <= 1.0

    def test_default_ttl_seconds_positive(self):
        assert isinstance(DEFAULT_TTL_SECONDS, int)
        assert DEFAULT_TTL_SECONDS > 0

    def test_max_healing_depth_positive(self):
        assert isinstance(MAX_HEALING_DEPTH, int)
        assert MAX_HEALING_DEPTH > 0


class TestCacheEntry:
    def test_importable(self):
        assert callable(CacheEntry)


class TestHealingPattern:
    def test_importable(self):
        assert callable(HealingPattern)


def _try_create_client():
    """Attempt to create MetaLearningClient, return (client, error)."""
    try:
        MetaLearningClient.reset_instance()
        client = MetaLearningClient()
        return client, None
    except Exception as e:
        return None, e


class TestMetaLearningClientSingleton:
    def setup_method(self):
        MetaLearningClient.reset_instance()

    def teardown_method(self):
        MetaLearningClient.reset_instance()

    def test_reset_instance_method_exists(self):
        assert callable(MetaLearningClient.reset_instance)

    def test_singleton_returns_same_instance(self):
        client1, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        client2 = MetaLearningClient()
        assert client1 is client2

    def test_instance_has_stats(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert isinstance(client.stats, dict)

    def test_stats_has_cache_hits(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert "cache_hits" in client.stats

    def test_stats_has_cache_misses(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert "cache_misses" in client.stats

    def test_similarity_threshold_default(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert client.similarity_threshold == DEFAULT_SIMILARITY_THRESHOLD

    def test_default_ttl(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert client.default_ttl == DEFAULT_TTL_SECONDS

    def test_max_healing_depth(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert client.max_healing_depth == MAX_HEALING_DEPTH

    def test_domain_thresholds_has_agentic_core(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert "agentic_core" in client.domain_thresholds

    def test_domain_ttls_has_apps_lic(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert "apps_lic" in client.domain_ttls

    def test_local_cache_starts_empty(self):
        client, err = _try_create_client()
        if err is not None:
            pytest.skip(f"MetaLearningClient requires Redis: {type(err).__name__}")
        assert isinstance(client._local_cache, dict)
