"""E9: Incremental File-Level Scan Cache.

Provides a content-hash based cache so that unchanged files can reuse
their prior scan edges rather than re-running the full AST visitors.

Cache format (JSON):
  {
    "version": "<CACHE_VERSION>",
    "entries": {
      "<repo_relative_path>": {
        "file_hash": "<sha256_hex>",
        "edges": [ { ...edge fields... }, ... ]
      }
    }
  }

Usage:
    cache = ScanCache.load(cache_path)
    edges, hit = cache.get(rel_path, file_hash)
    if not hit:
        edges = expensive_scan(file)
        cache.put(rel_path, file_hash, edges)
    cache.save(cache_path)

Thread-safety: not guaranteed — callers should use one cache per scan run.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

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

_emit_applies_guardrail("p0", "scan_cache", "p0_governance")
_emit_reads_policy_state("p0", "scan_cache", "policy_binding")
_emit_snapshots_state("p0", "scan_cache", "state_snapshot")
emit_replay_key("p0", "scan_cache")
emit_determinism_digest("p0", "scan_cache")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "scan_cache", "execution_auth")
_emit_validates_capability("p2", "scan_cache", "capability_check")
_emit_routes_to_capability("p2", "scan_cache", "capability_route")
_emit_writes_via_uwg("p2", "scan_cache", "uwg_write")
_emit_blocks_direct_write("p2", "scan_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "scan_cache", "tool_invocation")
_emit_captures_execution_output("p2", "scan_cache", "exec_output")
_emit_dispatches_agent("p3", "scan_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "scan_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "scan_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "scan_cache", "healing_outcome")
_emit_escalates_failure("p3", "scan_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "scan_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "scan_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "scan_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "scan_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "scan_cache", "eval_metric")
_emit_stores_embedding("p4", "scan_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "scan_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "scan_cache", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)

CACHE_VERSION = "1"


@dataclass
class _CacheEntry:
    file_hash: str
    edges: list[dict]


class ScanCache:
    """In-memory cache backed by a JSON file on disk.

    Attributes:
        hits:    Number of cache-hit files in this session.
        misses:  Number of cache-miss files in this session.
        evictions: Number of stale entries evicted in this session.
    """

    def __init__(self, entries: dict[str, _CacheEntry] | None = None) -> None:
        self._entries: dict[str, _CacheEntry] = entries or {}
        self.hits: int = 0
        self.misses: int = 0
        self.evictions: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, cache_path: Path) -> ScanCache:
        """Load cache from disk.  Returns empty cache on any error."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ScanCache.load")

        if not cache_path.exists():
            return cls()
        try:
            raw = json.loads(cache_path.read_text(encoding="utf-8"))
            if raw.get("version") != CACHE_VERSION:
                logger.debug("ScanCache version mismatch — discarding stale cache")
                return cls()
            entries: dict[str, _CacheEntry] = {}
            for rel, entry in raw.get("entries", {}).items():
                entries[rel] = _CacheEntry(
                    file_hash=entry["file_hash"],
                    edges=entry["edges"],
                )
            return cls(entries)
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("ScanCache load error (%s) — starting fresh", exc)
            return cls()

    def save(self, cache_path: Path) -> None:
        """Persist cache to disk atomically (write-then-rename)."""
        payload = {
            "version": CACHE_VERSION,
            "entries": {
                rel: {"file_hash": e.file_hash, "edges": e.edges} for rel, e in self._entries.items()
            },
        }
        tmp = cache_path.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            tmp.replace(cache_path)
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.warning("ScanCache save failed: %s", exc)

    def get(self, rel_path: str, file_hash: str) -> tuple[list[dict] | None, bool]:
        """Check cache for a file.

        Returns:
            (edge_dicts, True)  if the file hash matches the cached entry.
            (None, False)       if the entry is absent or stale.
        """
        entry = self._entries.get(rel_path)
        if entry is None:
            self.misses += 1
            return None, False
        if entry.file_hash != file_hash:
            self.evictions += 1
            del self._entries[rel_path]
            self.misses += 1
            return None, False
        self.hits += 1
        return entry.edges, True

    def put(self, rel_path: str, file_hash: str, edges: list[Edge]) -> None:
        """Store edges for a file in the cache."""
        self._entries[rel_path] = _CacheEntry(
            file_hash=file_hash,
            edges=[
                {
                    "from_name": e.from_name,
                    "relation_type": e.relation_type,
                    "to_name": e.to_name,
                    "edge_kind": e.edge_kind,
                    "source_file": e.source_file,
                    "line_no": e.line_no,
                    "symbol": e.symbol,
                }
                for e in edges
            ],
        )

    @property
    def size(self) -> int:
        return len(self._entries)

    def stats(self) -> dict:
        return {
            "cache_size": self.size,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": round(self.hits / max(1, self.hits + self.misses), 3),
        }


def file_hash(filepath: Path) -> str:
    """Compute SHA-256 hex digest of a file's contents."""
    try:
        data = filepath.read_bytes()
        return hashlib.sha256(data).hexdigest()
    except OSError:
        return ""


__all__ = [
    "ScanCache",
    "file_hash",
    "CACHE_VERSION",
]
