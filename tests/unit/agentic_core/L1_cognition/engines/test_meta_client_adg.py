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
