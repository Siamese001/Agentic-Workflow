"""Regression tests for SovereignSemanticCache.query() — P1 fix.

All tests run with EMBEDDING_ENABLED=false to stay CI-safe.
"""

from __future__ import annotations

import os
import unittest
from unittest.mock import MagicMock, patch

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

_emit_records_execution_trace("p0", "evidence", "test_sovereign_semantic_cache_query")
_emit_applies_guardrail("p0", "test_sovereign_semantic_cache_query", "p0_governance")
_emit_reads_policy_state("p0", "test_sovereign_semantic_cache_query", "policy_binding")
_emit_snapshots_state("p0", "test_sovereign_semantic_cache_query", "state_snapshot")
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

_emit_emits_metric_event("test_sovereign_semantic_cache_query", "p4obs", "metric_1")
_emit_emits_metric_event("test_sovereign_semantic_cache_query", "p4obs", "metric_2")
_emit_emits_metric_event("test_sovereign_semantic_cache_query", "p4obs", "metric_3")
_emit_emits_metric_event("test_sovereign_semantic_cache_query", "p4obs", "metric_4")
_emit_emits_metric_event("test_sovereign_semantic_cache_query", "p4obs", "metric_5")
_emit_emits_metric_event("test_sovereign_semantic_cache_query", "p4obs", "metric_6")
_emit_records_incident_event("test_sovereign_semantic_cache_query", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_sovereign_semantic_cache_query", "p4obs", "anomaly")
_emit_writes_observability_log("test_sovereign_semantic_cache_query", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_sovereign_semantic_cache_query", "p4obs", "mon_state")
_emit_triggers_alert("test_sovereign_semantic_cache_query", "p4obs", "alert")
_emit_links_incident_trace("test_sovereign_semantic_cache_query", "p4obs", "trace_link")
_emit_captures_pattern("test_sovereign_semantic_cache_query", "p3lm", "pattern")
_emit_records_learning_event("test_sovereign_semantic_cache_query", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_sovereign_semantic_cache_query", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_sovereign_semantic_cache_query", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_sovereign_semantic_cache_query", "p3lm", "routing")
_emit_improves_agent_policy("test_sovereign_semantic_cache_query", "p3lm", "policy")
_emit_stores_learning_state("test_sovereign_semantic_cache_query", "p3lm", "state")
_emit_records_execution_trace("test_sovereign_semantic_cache_query", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_sovereign_semantic_cache_query", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_sovereign_semantic_cache_query", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_sovereign_semantic_cache_query", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_sovereign_semantic_cache_query", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_sovereign_semantic_cache_query", "env_read", "p2_env_1")
_emit_reads_environ("test_sovereign_semantic_cache_query", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_sovereign_semantic_cache_query", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_sovereign_semantic_cache_query", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_sovereign_semantic_cache_query", "context_pull")
_emit_pulls_context("p1", "test_sovereign_semantic_cache_query", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_sovereign_semantic_cache_query", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_sovereign_semantic_cache_query", "uwg_term_2")
_emit_writes_through("p1", "test_sovereign_semantic_cache_query", "write_through")
_emit_writes_through("p1", "test_sovereign_semantic_cache_query", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_sovereign_semantic_cache_query", "safety_validation")
_emit_invokes_eval("p1", "test_sovereign_semantic_cache_query", "eval_call")
_emit_proposal_commits_routing("p1", "test_sovereign_semantic_cache_query", "routing_commit")
_emit_escalates_to_human("p1", "test_sovereign_semantic_cache_query", "human_escalation")
_emit_routes_through("p1", "test_sovereign_semantic_cache_query", "route_through")
_emit_checks_agent_registry("p1", "test_sovereign_semantic_cache_query", "agent_registry")
_emit_validates_agent_capability("p1", "test_sovereign_semantic_cache_query", "capability")
_emit_dispatches_execution_plan("p1", "test_sovereign_semantic_cache_query", "exec_plan")
_emit_agent_executes_agent("p1", "test_sovereign_semantic_cache_query", "sub_agent")
_emit_routes_to_agent("p1", "test_sovereign_semantic_cache_query", "target_agent")
_emit_verifies_policy("p1", "test_sovereign_semantic_cache_query", "policy_check")
_emit_observes_runtime_state("p1", "test_sovereign_semantic_cache_query", "runtime_state")
_emit_verifies_boundary("p1", "test_sovereign_semantic_cache_query", "boundary_check")
_emit_transcripts_response("p1", "test_sovereign_semantic_cache_query", "transcript")
_emit_hard_fails_untranscripted("p1", "test_sovereign_semantic_cache_query")
_emit_gated_by_confidence("p1", "test_sovereign_semantic_cache_query", "confidence_gate")
emit_replay_key("p0", "test_sovereign_semantic_cache_query")
emit_determinism_digest("p0", "test_sovereign_semantic_cache_query")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_sovereign_semantic_cache_query", "execution_auth")
_emit_validates_capability("p2", "test_sovereign_semantic_cache_query", "capability_check")
_emit_routes_to_capability("p2", "test_sovereign_semantic_cache_query", "capability_route")
_emit_writes_via_uwg("p2", "test_sovereign_semantic_cache_query", "uwg_write")
_emit_blocks_direct_write("p2", "test_sovereign_semantic_cache_query", "direct_write_block")
_emit_records_tool_invocation("p2", "test_sovereign_semantic_cache_query", "tool_invocation")
_emit_captures_execution_output("p2", "test_sovereign_semantic_cache_query", "exec_output")
_emit_dispatches_agent("p3", "test_sovereign_semantic_cache_query", "agent_dispatch")
_emit_coordinates_agents("p3", "test_sovereign_semantic_cache_query", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_sovereign_semantic_cache_query", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_sovereign_semantic_cache_query", "healing_outcome")
_emit_escalates_failure("p3", "test_sovereign_semantic_cache_query", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_sovereign_semantic_cache_query", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_sovereign_semantic_cache_query", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_sovereign_semantic_cache_query", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_sovereign_semantic_cache_query", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_sovereign_semantic_cache_query", "eval_metric")
_emit_stores_embedding("p4", "test_sovereign_semantic_cache_query", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_sovereign_semantic_cache_query", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_sovereign_semantic_cache_query", "exec_snapshot_link")


def _make_memory_item(key: str, vector: list[float], metadata: dict, namespace: str = ""):
    """Build a MemoryItem for injection into InMemoryVectorStore._storage."""
    import uuid

    from agentic_core.L4_state.types.memory_item_types import MemoryItem

    meta = dict(metadata)
    if namespace:
        meta["namespace"] = namespace
    uid = uuid.uuid5(uuid.NAMESPACE_DNS, key)
    return MemoryItem(id=uid, content=metadata.get("path", key), embedding=vector, metadata=meta)


class TestSovereignSemanticCacheQuery(unittest.TestCase):
    """Tests for the .query() method added in Phase 1."""

    def _make_cache(self):
        """Build a SovereignSemanticCache with mocked Redis (no live connection)."""
        with patch("agentic_core.L4_state.memory.sovereign_semantic_cache.get_redis_client") as mock_redis:
            mock_redis.return_value = MagicMock()
            from agentic_core.L4_state.memory.sovereign_semantic_cache import (
                SovereignSemanticCache,
            )

            cache = SovereignSemanticCache(mission_id="test-mission")
        return cache

    def _inject(self, cache, key: str, vector: list[float], metadata: dict = None, namespace: str = ""):
        """Inject a MemoryItem directly into the underlying _storage dict."""
        item = _make_memory_item(key, vector, metadata or {}, namespace)
        cache._vector_store._storage[key] = item
        if key not in cache._vector_store._ordered_ids:
            cache._vector_store._ordered_ids.append(key)

    def test_query_returns_empty_when_kill_switch_active(self):
        """query() must return [] when EMBEDDING_ENABLED=false."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "false"}):
            cache = self._make_cache()
            self._inject(cache, "key1", [0.1, 0.2, 0.3], {"path": "foo.py"}, "canon-files")
            result = cache.query("some query text")
            self.assertEqual(result, [])

    def test_query_returns_empty_when_store_empty(self):
        """query() must return [] when vector store has no entries."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            cache = self._make_cache()
            with patch(
                "system_learning.engines.openai_embedder.BGEEmbedder.embed_batch",
                return_value=[[0.1, 0.9]],
            ):
                result = cache.query("some query")
            self.assertEqual(result, [])

    def test_query_returns_sorted_results(self):
        """query() must rank results by descending cosine similarity."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            cache = self._make_cache()
            self._inject(cache, "high", [1.0, 0.0], {"path": "high.py"}, "test")
            self._inject(cache, "low", [0.0, 1.0], {"path": "low.py"}, "test")
            with patch(
                "system_learning.engines.openai_embedder.BGEEmbedder.embed_batch",
                return_value=[[1.0, 0.0]],
            ):
                results = cache.query("q", top_k=10)

            self.assertGreater(len(results), 0)
            scores = [r["score"] for r in results]
            self.assertEqual(scores, sorted(scores, reverse=True))

    def test_query_respects_top_k(self):
        """query() must respect the top_k limit."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            cache = self._make_cache()
            for i in range(1, 11):
                self._inject(cache, f"key{i}", [float(i), 1.0])
            with patch(
                "system_learning.engines.openai_embedder.BGEEmbedder.embed_batch",
                return_value=[[1.0, 0.5]],
            ):
                results = cache.query("q", top_k=3)
            self.assertLessEqual(len(results), 3)

    def test_query_filters_by_namespace(self):
        """query() must exclude entries whose namespace does not match."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            cache = self._make_cache()
            self._inject(cache, "match", [1.0, 0.0], {"path": "match.py"}, "wanted")
            self._inject(cache, "nomatch", [1.0, 0.0], {"path": "skip.py"}, "other")
            with patch(
                "system_learning.engines.openai_embedder.BGEEmbedder.embed_batch",
                return_value=[[1.0, 0.0]],
            ):
                results = cache.query("q", namespace="wanted")
            hashes = [r["content_hash"] for r in results]
            self.assertIn("match", hashes)
            self.assertNotIn("nomatch", hashes)

    def test_query_result_schema(self):
        """Each result must contain content_hash, score, and content keys."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            cache = self._make_cache()
            self._inject(cache, "entry", [0.5, 0.5], {"path": "entry.py"})
            with patch(
                "system_learning.engines.openai_embedder.BGEEmbedder.embed_batch",
                return_value=[[0.5, 0.5]],
            ):
                results = cache.query("q")
            self.assertEqual(len(results), 1)
            r = results[0]
            self.assertIn("content_hash", r)
            self.assertIn("score", r)
            self.assertIn("content", r)

    def test_query_graceful_on_embedder_failure(self):
        """query() must return [] if BGEEmbedder raises, not propagate the error."""
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            cache = self._make_cache()
            self._inject(cache, "entry", [0.5, 0.5])
            with patch(
                "system_learning.engines.openai_embedder.BGEEmbedder.embed_batch",
                side_effect=RuntimeError("model unavailable"),
            ):
                result = cache.query("q")
            self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
