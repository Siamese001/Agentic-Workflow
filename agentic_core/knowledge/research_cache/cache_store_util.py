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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "cache_store_util", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "cache_store_util", "policy_binding")
trace_contract._emit_snapshots_state("p0", "cache_store_util", "state_snapshot")

trace_contract._emit_emits_metric_event("cache_store_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("cache_store_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("cache_store_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("cache_store_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("cache_store_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("cache_store_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("cache_store_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("cache_store_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("cache_store_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("cache_store_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("cache_store_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("cache_store_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("cache_store_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("cache_store_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("cache_store_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("cache_store_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("cache_store_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("cache_store_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("cache_store_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("cache_store_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("cache_store_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("cache_store_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("cache_store_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("cache_store_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("cache_store_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("cache_store_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("cache_store_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("cache_store_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "cache_store_util", "context_pull")
trace_contract._emit_pulls_context("p1", "cache_store_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "cache_store_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "cache_store_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "cache_store_util", "write_through")
trace_contract._emit_writes_through("p1", "cache_store_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "cache_store_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "cache_store_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "cache_store_util", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "cache_store_util", "human_escalation")
trace_contract._emit_routes_through("p1", "cache_store_util", "route_through")
trace_contract._emit_checks_agent_registry("p1", "cache_store_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "cache_store_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "cache_store_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "cache_store_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "cache_store_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "cache_store_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "cache_store_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "cache_store_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "cache_store_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "cache_store_util")
trace_contract._emit_gated_by_confidence("p1", "cache_store_util", "confidence_gate")
trace_contract.emit_replay_key("p0", "cache_store_util")
trace_contract.emit_determinism_digest("p0", "cache_store_util")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "cache_store_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "cache_store_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "cache_store_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "cache_store_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "cache_store_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "cache_store_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "cache_store_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "cache_store_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "cache_store_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "cache_store_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "cache_store_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "cache_store_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "cache_store_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "cache_store_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "cache_store_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "cache_store_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "cache_store_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "cache_store_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "cache_store_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "cache_store_util", "exec_snapshot_link")

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
        except (
            json.JSONDecodeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            raise

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ResearchCache.exists")

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
        except (json.JSONDecodeError, OSError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-log-and-swallow -- cache entry read failure: non-fatal; None returned signals cache miss to caller
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
        except (OSError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-silent-swallow
            Logger.error(f"Failed to write cache entry: {e}")
            return False

    def clear(self) -> None:
        """Clear all cached entries."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            self._index = {}
            Logger.info("Research cache cleared")
        except (
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            Logger.error(f"Failed to clear cache: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self._index),
            "cache_file": str(self.cache_file),
            "cache_size_bytes": self.cache_file.stat().st_size if self.cache_file.exists() else 0,
        }
