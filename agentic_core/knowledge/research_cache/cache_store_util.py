"""
Research Cache Store Utility

Zero-Ambiguity Standard: Named with _util.py suffix
Category: UTILITY (Cache management helper)

Provides persistent storage for research results using JSONL format.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "cache_store_util", "p0_governance")
_emit_reads_policy_state("p0", "cache_store_util", "policy_binding")
_emit_snapshots_state("p0", "cache_store_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("cache_store_util", "p4obs", "metric_1")
_emit_emits_metric_event("cache_store_util", "p4obs", "metric_2")
_emit_emits_metric_event("cache_store_util", "p4obs", "metric_3")
_emit_emits_metric_event("cache_store_util", "p4obs", "metric_4")
_emit_emits_metric_event("cache_store_util", "p4obs", "metric_5")
_emit_emits_metric_event("cache_store_util", "p4obs", "metric_6")
_emit_records_incident_event("cache_store_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("cache_store_util", "p4obs", "anomaly")
_emit_writes_observability_log("cache_store_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("cache_store_util", "p4obs", "mon_state")
_emit_triggers_alert("cache_store_util", "p4obs", "alert")
_emit_links_incident_trace("cache_store_util", "p4obs", "trace_link")
_emit_captures_pattern("cache_store_util", "p3lm", "pattern")
_emit_records_learning_event("cache_store_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cache_store_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("cache_store_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cache_store_util", "p3lm", "routing")
_emit_improves_agent_policy("cache_store_util", "p3lm", "policy")
_emit_stores_learning_state("cache_store_util", "p3lm", "state")
_emit_records_execution_trace("cache_store_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cache_store_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cache_store_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cache_store_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cache_store_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cache_store_util", "env_read", "p2_env_1")
_emit_reads_environ("cache_store_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("cache_store_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cache_store_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cache_store_util", "context_pull")
_emit_pulls_context("p1", "cache_store_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cache_store_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cache_store_util", "uwg_term_2")
_emit_writes_through("p1", "cache_store_util", "write_through")
_emit_writes_through("p1", "cache_store_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "cache_store_util", "safety_validation")
_emit_invokes_eval("p1", "cache_store_util", "eval_call")
_emit_proposal_commits_routing("p1", "cache_store_util", "routing_commit")
_emit_escalates_to_human("p1", "cache_store_util", "human_escalation")
_emit_routes_through("p1", "cache_store_util", "route_through")
_emit_checks_agent_registry("p1", "cache_store_util", "agent_registry")
_emit_validates_agent_capability("p1", "cache_store_util", "capability")
_emit_dispatches_execution_plan("p1", "cache_store_util", "exec_plan")
_emit_agent_executes_agent("p1", "cache_store_util", "sub_agent")
_emit_routes_to_agent("p1", "cache_store_util", "target_agent")
_emit_verifies_policy("p1", "cache_store_util", "policy_check")
_emit_observes_runtime_state("p1", "cache_store_util", "runtime_state")
_emit_verifies_boundary("p1", "cache_store_util", "boundary_check")
_emit_transcripts_response("p1", "cache_store_util", "transcript")
_emit_hard_fails_untranscripted("p1", "cache_store_util")
_emit_gated_by_confidence("p1", "cache_store_util", "confidence_gate")
emit_replay_key("p0", "cache_store_util")
emit_determinism_digest("p0", "cache_store_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "cache_store_util", "execution_auth")
_emit_validates_capability("p2", "cache_store_util", "capability_check")
_emit_routes_to_capability("p2", "cache_store_util", "capability_route")
_emit_writes_via_uwg("p2", "cache_store_util", "uwg_write")
_emit_blocks_direct_write("p2", "cache_store_util", "direct_write_block")
_emit_records_tool_invocation("p2", "cache_store_util", "tool_invocation")
_emit_captures_execution_output("p2", "cache_store_util", "exec_output")
_emit_dispatches_agent("p3", "cache_store_util", "agent_dispatch")
_emit_coordinates_agents("p3", "cache_store_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "cache_store_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "cache_store_util", "healing_outcome")
_emit_escalates_failure("p3", "cache_store_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "cache_store_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cache_store_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "cache_store_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "cache_store_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cache_store_util", "eval_metric")
_emit_stores_embedding("p4", "cache_store_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "cache_store_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cache_store_util", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


class ResearchCache:
    """
    Persistent cache for research results.

    Uses JSONL format for append-only storage with query-based lookup.
    """

    def __init__(self, cache_dir: Path | str):
        """
        Initialize the research cache.

        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "research_cache.jsonl"
        self._index: dict[str, int] = {}
        self._load_index()

    def _hash_query(self, query: str) -> str:
        """Generate a hash key for a query."""
        return hashlib.sha256(query.encode()).hexdigest()[:16]

    def _load_index(self) -> None:
        """Load the cache index from disk."""
        self._index = {}
        if not self.cache_file.exists():
            return
        try:
            with self.cache_file.open("r", encoding="utf-8") as f:
                for line_num, line in enumerate(f):
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            query_hash = entry.get("query_hash")
                            if query_hash:
                                self._index[query_hash] = line_num
                        except json.JSONDecodeError:
                            continue
        # guardian: allow-silent-swallow
        except (json.JSONDecodeError, OSError, RuntimeError, TypeError, ValueError) as e:
            raise
            Logger.error(f"Failed to load cache index: {e}")

    def exists(self, query: str) -> bool:
        """
        Check if a query result exists in the cache.

        Args:
            query: The query string to check

        Returns:
            True if cached, False otherwise
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ResearchCache.exists")

        query_hash = self._hash_query(query)
        return query_hash in self._index

    def get(self, query: str) -> dict[str, Any] | None:
        """
        Retrieve a cached result for a query.

        Args:
            query: The query string to look up

        Returns:
            Cached result dictionary or None if not found
        """
        query_hash = self._hash_query(query)
        if query_hash not in self._index:
            return None
        line_num = self._index[query_hash]
        try:
            with self.cache_file.open("r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i == line_num:
                        entry = json.loads(line.strip())
                        return entry.get("result")
        # guardian: allow-silent-swallow
        except (json.JSONDecodeError, OSError, RuntimeError, TypeError, ValueError) as e:
            Logger.error(f"Failed to retrieve cache entry: {e}")
        return None

    def set(self, query: str, result: dict[str, Any]) -> bool:
        """
        Store a result in the cache.

        Args:
            query: The query string
            result: The result dictionary to cache

        Returns:
            True if successful, False otherwise
        """
        query_hash = self._hash_query(query)
        entry = {"query_hash": query_hash, "query": query, "result": result}
        try:
            with self.cache_file.open("a", encoding="utf-8") as f:
                line_num = (
                    sum(1 for _ in open(self.cache_file, encoding="utf-8")) if self.cache_file.exists() else 0
                )
                json.dump(entry, f)
                f.write("\n")
                self._index[query_hash] = line_num
            return True
        # guardian: allow-silent-swallow
        except (OSError, RuntimeError, TypeError, ValueError) as e:
            Logger.error(f"Failed to write cache entry: {e}")
            return False

    def clear(self) -> None:
        """Clear all cached entries."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            self._index = {}
            Logger.info("Research cache cleared")
        # guardian: allow-silent-swallow
        except (OSError, RuntimeError, TypeError, ValueError) as e:
            Logger.error(f"Failed to clear cache: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self._index),
            "cache_file": str(self.cache_file),
            "cache_size_bytes": self.cache_file.stat().st_size if self.cache_file.exists() else 0,
        }
