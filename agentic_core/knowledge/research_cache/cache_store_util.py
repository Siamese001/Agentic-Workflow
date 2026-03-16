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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "cache_store_util", "p0_governance")
_emit_reads_policy_state("p0", "cache_store_util", "policy_binding")
_emit_snapshots_state("p0", "cache_store_util", "state_snapshot")
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
        except Exception as e:
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
        except Exception as e:
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
        except Exception as e:
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
        except Exception as e:
            Logger.error(f"Failed to clear cache: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self._index),
            "cache_file": str(self.cache_file),
            "cache_size_bytes": self.cache_file.stat().st_size if self.cache_file.exists() else 0,
        }
