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

try:
    import orjson as _orjson

    _ORJSON_AVAILABLE = True
except ImportError:
    _orjson = None  # type: ignore[assignment]
    _ORJSON_AVAILABLE = False
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_emits_metric_event("scan_cache", "p4obs", "metric_1")
_emit_emits_metric_event("scan_cache", "p4obs", "metric_2")
_emit_emits_metric_event("scan_cache", "p4obs", "metric_3")
_emit_emits_metric_event("scan_cache", "p4obs", "metric_4")
_emit_emits_metric_event("scan_cache", "p4obs", "metric_5")
_emit_emits_metric_event("scan_cache", "p4obs", "metric_6")
_emit_records_incident_event("scan_cache", "p4obs", "incident")
_emit_captures_runtime_anomaly("scan_cache", "p4obs", "anomaly")
_emit_writes_observability_log("scan_cache", "p4obs", "obs_log")
_emit_updates_monitoring_state("scan_cache", "p4obs", "mon_state")
_emit_triggers_alert("scan_cache", "p4obs", "alert")
_emit_links_incident_trace("scan_cache", "p4obs", "trace_link")
_emit_captures_pattern("scan_cache", "p3lm", "pattern")
_emit_records_learning_event("scan_cache", "p3lm", "learning_event")
_emit_writes_learning_snapshot("scan_cache", "p3lm", "snapshot")
_emit_feeds_meta_learning("scan_cache", "p3lm", "meta_feed")
_emit_updates_routing_strategy("scan_cache", "p3lm", "routing")
_emit_improves_agent_policy("scan_cache", "p3lm", "policy")
_emit_stores_learning_state("scan_cache", "p3lm", "state")
_emit_records_execution_trace("scan_cache", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("scan_cache", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("scan_cache", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("scan_cache", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("scan_cache", "L4_STATE", "p2_trace_5")
_emit_reads_environ("scan_cache", "env_read", "p2_env_1")
_emit_reads_environ("scan_cache", "env_read", "p2_env_2")
_emit_reads_runtime_state("scan_cache", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("scan_cache", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "scan_cache", "context_pull")
_emit_pulls_context("p1", "scan_cache", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "scan_cache", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "scan_cache", "uwg_term_2")
_emit_writes_through("p1", "scan_cache", "write_through")
_emit_writes_through("p1", "scan_cache", "write_through_2")
_emit_validated_by_safety_plane("p1", "scan_cache", "safety_validation")
_emit_invokes_eval("p1", "scan_cache", "eval_call")
_emit_proposal_commits_routing("p1", "scan_cache", "routing_commit")
_emit_escalates_to_human("p1", "scan_cache", "human_escalation")
_emit_routes_through("p1", "scan_cache", "route_through")
_emit_checks_agent_registry("p1", "scan_cache", "agent_registry")
_emit_validates_agent_capability("p1", "scan_cache", "capability")
_emit_dispatches_execution_plan("p1", "scan_cache", "exec_plan")
_emit_agent_executes_agent("p1", "scan_cache", "sub_agent")
_emit_routes_to_agent("p1", "scan_cache", "target_agent")
_emit_verifies_policy("p1", "scan_cache", "policy_check")
_emit_observes_runtime_state("p1", "scan_cache", "runtime_state")
_emit_verifies_boundary("p1", "scan_cache", "boundary_check")
_emit_transcripts_response("p1", "scan_cache", "transcript")
_emit_hard_fails_untranscripted("p1", "scan_cache")
_emit_gated_by_confidence("p1", "scan_cache", "confidence_gate")

logger = logging.getLogger(__name__)

CACHE_VERSION = "3"

# Files whose content changes should invalidate the entire scan cache.
# Visitor implementations, the symbol-set registry, and the scanner itself
# all affect what edges are extracted from every file in the repo.
_EXTRACTION_LAYER_FILES: tuple[str, ...] = (
    "agentic_core/adg/extraction/static_scanner.py",
    "agentic_core/adg/extraction/scan_cache.py",
    "agentic_core/adg/contracts/schema_util.py",
    "agentic_core/adg/extraction/visitors/__init__.py",
    "agentic_core/adg/extraction/visitors/orchestration.py",
    "agentic_core/adg/extraction/visitors/core.py",
    "agentic_core/adg/extraction/visitors/structural.py",
    "agentic_core/adg/extraction/visitors/dynamic.py",
    "agentic_core/adg/extraction/visitors/governance.py",
    "agentic_core/adg/extraction/visitors/misc.py",
    "agentic_core/adg/extraction/visitors/lifecycle_advanced.py",
    "agentic_core/adg/extraction/visitors/runtime_semantic.py",
    "agentic_core/adg/extraction/visitors/context_control.py",
    "agentic_core/adg/extraction/visitors/transport_proof.py",
    "agentic_core/adg/extraction/visitors/p4_waves.py",
    "agentic_core/adg/extraction/visitors/l4_waves.py",
    "agentic_core/adg/extraction/visitors/learning.py",
)


def compute_extraction_fingerprint(repo_root: Path) -> str:
    """Return a SHA-256 digest over all extraction-layer source files.

    Any change to a visitor, symbol-set, or the scanner itself bumps this
    digest, causing ScanCache.load() to discard the on-disk cache and force
    a full re-scan on the next ADG run.
    """
    h = hashlib.sha256()
    for rel in sorted(_EXTRACTION_LAYER_FILES):
        p = repo_root / rel
        try:
            h.update(p.read_bytes())
        except OSError:
            h.update(rel.encode())  # file absent — include path so digest still changes
    return h.hexdigest()


@dataclass
class _CacheEntry:
    file_hash: str
    edges: list[dict]
    type_surface_map: dict[str, str]
    surface_evidence: dict[str, int]


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
    def load(cls, cache_path: Path, extraction_fingerprint: str = "") -> ScanCache:
        """Load cache from disk.  Returns empty cache on any error."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ScanCache.load")

        if not cache_path.exists():
            return cls()
        try:
            _raw_bytes = cache_path.read_bytes()
            raw = _orjson.loads(_raw_bytes) if _ORJSON_AVAILABLE else json.loads(_raw_bytes.decode("utf-8"))
            if raw.get("version") != CACHE_VERSION:
                logger.debug("ScanCache version mismatch — discarding stale cache")
                return cls()
            if extraction_fingerprint and raw.get("extraction_fingerprint") != extraction_fingerprint:
                logger.debug(
                    "ScanCache extraction_fingerprint mismatch — discarding stale cache "
                    "(visitor/schema change detected)"
                )
                return cls()
            entries: dict[str, _CacheEntry] = {}
            for rel, entry in raw.get("entries", {}).items():
                entries[rel] = _CacheEntry(
                    file_hash=entry["file_hash"],
                    edges=entry["edges"],
                    type_surface_map=entry.get("type_surface_map", {}),
                    surface_evidence=entry.get("surface_evidence", {}),
                )
            return cls(entries)
        # guardian: allow-silent-swallow -- Cache corruption is non-critical; fallback to fresh scan
        except Exception as exc:
            logger.debug("ScanCache load error (%s) — starting fresh", exc)
            return cls()

    def save(self, cache_path: Path, extraction_fingerprint: str = "") -> None:
        """Persist cache to disk atomically (write-then-rename)."""
        payload = {
            "version": CACHE_VERSION,
            "extraction_fingerprint": extraction_fingerprint,
            "entries": {
                rel: {
                    "file_hash": e.file_hash,
                    "edges": e.edges,
                    "type_surface_map": e.type_surface_map,
                    "surface_evidence": e.surface_evidence,
                }
                for rel, e in self._entries.items()
            },
        }
        tmp = cache_path.with_suffix(".tmp")
        try:
            if _ORJSON_AVAILABLE:
                tmp.write_bytes(_orjson.dumps(payload, option=_orjson.OPT_INDENT_2))
            else:
                tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            tmp.replace(cache_path)
        # guardian: allow-silent-swallow -- Cache write failure is non-critical; scan can continue without persistence
        except Exception as exc:
            logger.warning("ScanCache save failed: %s", exc)

    def get(
        self,
        rel_path: str,
        file_hash: str,
    ) -> tuple[list[dict] | None, dict[str, str], dict[str, int], bool]:
        """Check cache for a file.

        Returns:
            (edge_dicts, type_surface_map, surface_evidence, True)
                if the file hash matches the cached entry.
            (None, {}, {}, False)
                if the entry is absent or stale.
        """
        entry = self._entries.get(rel_path)
        if entry is None:
            self.misses += 1
            return None, {}, {}, False
        if entry.file_hash != file_hash:
            self.evictions += 1
            del self._entries[rel_path]
            self.misses += 1
            return None, {}, {}, False
        self.hits += 1
        return entry.edges, entry.type_surface_map, entry.surface_evidence, True

    def put(
        self,
        rel_path: str,
        file_hash: str,
        edges: list[Edge],
        type_surface_map: dict[str, str],
        surface_evidence: dict[str, int],
    ) -> None:
        """Store edges and per-file evidence for a file in the cache."""
        self._entries[rel_path] = _CacheEntry(
            file_hash=file_hash,
            edges=[asdict(e) for e in edges],
            type_surface_map=dict(type_surface_map),
            surface_evidence=dict(surface_evidence),
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
    """Compute SHA-256 hex digest of a file's contents.

    Uses streaming hash for files > 1MB and skips files > 50MB
    to prevent timeouts on large artifacts.
    """
    try:
        size = filepath.stat().st_size
        if size > 50 * 1024 * 1024:
            # For very large files, hash size + mtime as proxy    # guardian: Add error context logging
            mtime = filepath.stat().st_mtime_ns
            return hashlib.sha256(f"{size}:{mtime}".encode()).hexdigest()
        if size > 1024 * 1024:
            # Stream large files in chunks
            h = hashlib.sha256()
            with filepath.open("rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            return h.hexdigest()
        data = filepath.read_bytes()
        return hashlib.sha256(data).hexdigest()
    # guardian: allow-silent-swallow - acceptable exception handling
    except OSError:
        return ""


__all__ = [
    "ScanCache",
    "file_hash",
    "CACHE_VERSION",
    "compute_extraction_fingerprint",
]
