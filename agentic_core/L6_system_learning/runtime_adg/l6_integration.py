"""Runtime ADG L6 Integration - Meta-learning snapshot storage.

Connects runtime ADG snapshots to L6 meta-learning state for continuous
system learning from execution traces.

Validation Gates:
- Snapshot validation before storage
- Path traversal protection
- Index integrity checks
- Size limits for extracted patterns
"""

from __future__ import annotations

import json
import logging
import tempfile
import time
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from .snapshot import RuntimeADGSnapshot
from tqdm import tqdm

logger = logging.getLogger(__name__)


class L6MetaLearningBridge:
    """Bridge between runtime ADG snapshots and L6 meta-learning state.

        Stores runtime ADG snapshots in L6 territory for meta-learning analysis
    and system evolution based on execution patterns.
    """

    def __init__(self, l6_base_dir: Path | None = None) -> None:
        """Initialize L6 meta-learning bridge.

        Parameters
        ----------
        l6_base_dir:
            Base directory for L6 meta-learning storage. If None, uses default L6 path.
        """
        if l6_base_dir is None:
            project_root = get_validated_project_root()
            l6_base_dir = project_root / "system_learning" / "meta_learning" / "runtime_adg_snapshots"

        self._l6_base_dir = Path(l6_base_dir)
        self._l6_base_dir.mkdir(parents=True, exist_ok=True)

        # Index files for meta-learning
        self._snapshot_index_path = self._l6_base_dir / "snapshot_index.json"
        self._pattern_index_path = self._l6_base_dir / "pattern_index.json"
        self._evolution_log_path = self._l6_base_dir / "evolution_log.jsonl"

        # Maximum sizes for safety
        self._max_pattern_nodes = 10000  # Limit pattern extraction
        self._max_snapshot_size_mb = 50  # Limit snapshot file size

        self._snapshot_index = self._load_index(self._snapshot_index_path)
        self._pattern_index = self._load_index(self._pattern_index_path)

    def _load_index(self, index_path: Path) -> dict[str, Any]:
        """Load index file or return empty dict."""
        if index_path.exists():
            try:
                return json.loads(index_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to load L6 index %s: %s", index_path, exc)
                return {}
        return {}

    def _save_index(self, index_path: Path, data: dict[str, Any]) -> None:
        """Save index file."""
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=index_path.parent,
            prefix=index_path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            tmp_name = handle.name
        Path(tmp_name).replace(index_path)

    def store_snapshot_for_meta_learning(self, snapshot: RuntimeADGSnapshot) -> str:
        """Store runtime ADG snapshot for meta-learning analysis.

        Parameters
        ----------
        snapshot:
            Runtime ADG snapshot to store

        Returns
        -------
        str
            Meta-learning storage ID

        Validation:
            - Snapshot must have valid snapshot_id
            - Node count must be within limits
            - File path sanitized to prevent traversal
        """
        # Validate snapshot
        if not snapshot.snapshot_id or len(snapshot.snapshot_id) != 64:
            raise ValueError(f"Invalid snapshot ID: {snapshot.snapshot_id}")

        if len(snapshot.nodes) > self._max_pattern_nodes:
            raise ValueError(
                f"Snapshot node count {len(snapshot.nodes)} exceeds limit {self._max_pattern_nodes}",
            )

        timestamp = int(time.time())
        meta_learning_id = f"runtime_adg_{timestamp}_{snapshot.snapshot_id[:8]}"

        # Sanitize ID for filesystem safety
        safe_id = "".join(c for c in meta_learning_id if c.isalnum() or c in "_-.")

        # Store snapshot data
        snapshot_file = self._l6_base_dir / f"{safe_id}.json"

        # Validate file path is within base directory (prevent traversal)
        try:
            snapshot_file.resolve().relative_to(self._l6_base_dir.resolve())
        except ValueError:
            raise ValueError(f"Invalid snapshot file path: {snapshot_file}")

        snapshot_data = {
            "meta_learning_id": meta_learning_id,
            "timestamp": timestamp,
            "trace_id": snapshot.trace_id[:256] if snapshot.trace_id else "",  # Limit length
            "mission": snapshot.mission[:256] if snapshot.mission else "",
            "started_at_utc": snapshot.started_at_utc,
            "ended_at_utc": snapshot.ended_at_utc,
            "duration_ms": max(0, snapshot.ended_at_utc - snapshot.started_at_utc),
            "node_count": len(snapshot.nodes),
            "edge_count": len(snapshot.edges),
            "nodes": [
                {
                    "node_id": node.node_id[:128] if node.node_id else "",  # Limit length
                    "name": node.name[:256],
                    "kind": node.kind[:64],
                    "layer": node.layer[:8],
                    "component": node.component[:128],
                    "started_at_utc": node.started_at_utc,
                    "duration_ms": node.duration_ms,
                    "status": node.status[:16] if node.status in ("ok", "error") else "ok",
                    "attributes": json.loads(node.attributes_json) if node.attributes_json else {},
                }
                for node in snapshot.nodes[: self._max_pattern_nodes]  # Limit node serialization
            ],
            "edges": [
                {
                    "src_id": edge.src_id[:128],
                    "dst_id": edge.dst_id[:128],
                    "relation": edge.relation[:64]
                    if edge.relation in ("parent_child", "temporal_sequence")
                    else "unknown",
                }
                for edge in snapshot.edges[: self._max_pattern_nodes * 2]  # Limit edges too
            ],
        }

        # Check serialized size
        serialized = json.dumps(snapshot_data)
        if len(serialized) > self._max_snapshot_size_mb * 1024 * 1024:
            raise ValueError(
                f"Snapshot size {len(serialized) / (1024 * 1024):.1f}MB exceeds limit {self._max_snapshot_size_mb}MB",
            )

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self._l6_base_dir,
            prefix=safe_id + ".",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(serialized)
            tmp_name = handle.name
        Path(tmp_name).replace(snapshot_file)

        # Update snapshot index with size limit
        project_root = get_validated_project_root()
        try:
            # Try to get relative path for portability
            file_path_str = str(snapshot_file.relative_to(project_root))[:512]
        except ValueError:
            # If file is outside project root (e.g., temp directory in tests), use absolute path
            file_path_str = str(snapshot_file.resolve())[:512]

        self._snapshot_index[meta_learning_id] = {
            "trace_id": snapshot.trace_id[:256] if snapshot.trace_id else "",
            "timestamp": timestamp,
            "mission": snapshot.mission[:256] if snapshot.mission else "",
            "node_count": len(snapshot.nodes),
            "edge_count": len(snapshot.edges),
            "duration_ms": max(0, snapshot.ended_at_utc - snapshot.started_at_utc),
            "file_path": file_path_str,
        }

        # Trim index if too large (keep last 1000 entries)
        if len(self._snapshot_index) > 1000:
            oldest_keys = sorted(self._snapshot_index.keys())[: len(self._snapshot_index) - 1000]
            for key in oldest_keys:
                del self._snapshot_index[key]

        self._save_index(self._snapshot_index_path, self._snapshot_index)

        # Extract and store patterns for meta-learning
        self._extract_and_store_patterns(meta_learning_id, snapshot)

        # Log evolution event
        self._log_evolution_event(
            "runtime_adg_stored",
            {
                "meta_learning_id": meta_learning_id,
                "trace_id": snapshot.trace_id[:256] if snapshot.trace_id else "",
                "mission": snapshot.mission[:256] if snapshot.mission else "",
                "node_count": len(snapshot.nodes),
                "edge_count": len(snapshot.edges),
            },
        )

        return meta_learning_id

    def _extract_and_store_patterns(self, meta_learning_id: str, snapshot: RuntimeADGSnapshot) -> None:
        """Extract execution patterns for meta-learning with size limits."""
        # Initialize patterns with size tracking
        patterns = {
            "layer_distribution": {},
            "component_distribution": {},
            "span_type_distribution": {},
            "error_patterns": [],
            "timing_patterns": {
                "slow_operations": [],
                "fast_operations": [],
            },
            "relation_patterns": {},
            "extraction_metadata": {
                "total_nodes": len(snapshot.nodes),
                "timestamp": int(time.time()),
            },
        }

        # Limits for pattern extraction
        max_errors = 100
        max_slow_ops = 100
        max_fast_ops = 100

        # Analyze nodes for patterns
        for node in tqdm(snapshot.nodes, desc="Processing", unit="item"):
            # Layer distribution
            layer = node.layer[:8] if node.layer else "unknown"
            patterns["layer_distribution"][layer] = patterns["layer_distribution"].get(layer, 0) + 1

            # Component distribution
            component = node.component[:128] if node.component else "unknown"
            patterns["component_distribution"][component] = (
                patterns["component_distribution"].get(component, 0) + 1
            )

            # Span type distribution
            span_type = node.kind[:64] if node.kind else "unknown"
            patterns["span_type_distribution"][span_type] = (
                patterns["span_type_distribution"].get(span_type, 0) + 1
            )

            # Error patterns (with limit)
            if node.status == "error" and len(patterns["error_patterns"]) < max_errors:
                patterns["error_patterns"].append(
                    {
                        "node_id": node.node_id[:128] if node.node_id else "",
                        "component": component,
                        "layer": layer,
                    }
                )

            # Timing patterns (with limits)
            if node.duration_ms > 1000 and len(patterns["timing_patterns"]["slow_operations"]) < max_slow_ops:
                patterns["timing_patterns"]["slow_operations"].append(
                    {
                        "node_id": node.node_id[:128] if node.node_id else "",
                        "component": component,
                        "duration_ms": node.duration_ms,
                    }
                )
            elif node.duration_ms < 10 and len(patterns["timing_patterns"]["fast_operations"]) < max_fast_ops:
                patterns["timing_patterns"]["fast_operations"].append(
                    {
                        "node_id": node.node_id[:128] if node.node_id else "",
                        "component": component,
                        "duration_ms": node.duration_ms,
                    }
                )

        # Analyze edges for patterns
        for edge in snapshot.edges:
            relation = edge.relation[:64] if edge.relation else "unknown"
            patterns["relation_patterns"][relation] = patterns["relation_patterns"].get(relation, 0) + 1

        # Store patterns
        self._pattern_index[meta_learning_id] = patterns
        self._save_index(self._pattern_index_path, self._pattern_index)

    def _log_evolution_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Log system evolution event with size validation."""
        # Validate and sanitize event data
        sanitized_data = {}
        for key, value in tqdm(data.items(), desc="Processing", unit="item"):
            if isinstance(value, str):
                sanitized_data[key[:64]] = value[:512]  # Limit string values
            elif isinstance(value, (int, float, bool)):
                sanitized_data[key[:64]] = value
            elif isinstance(value, dict):
                # Recursively sanitize nested dicts (one level only)
                sanitized_data[key[:64]] = {
                    k[:64]: str(v)[:256] if not isinstance(v, (int, float, bool)) else v
                    for k, v in list(value.items())[:20]  # Limit nested keys
                }
            else:
                sanitized_data[key[:64]] = str(value)[:256]

        event = {
            "timestamp": int(time.time()),
            "event_type": str(event_type)[:64],
            "data": sanitized_data,
        }

        try:
            with open(self._evolution_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, separators=(",", ":")) + "\n")
        except OSError as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            logger.warning("l6_integration: failed to write evolution log: %s", exc)

    def get_meta_learning_snapshots(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent snapshots for meta-learning analysis.

        Parameters
        ----------
        limit:
            Maximum number of snapshots to return

        Returns
        -------
        list[dict[str, Any]]
            Recent snapshots with metadata
        """
        # Sort by timestamp descending
        sorted_snapshots = sorted(
            self._snapshot_index.items(),
            key=lambda x: x[1]["timestamp"],
            reverse=True,
        )

        return [{"meta_learning_id": ml_id, **metadata} for ml_id, metadata in sorted_snapshots[:limit]]

    def get_execution_patterns(self, trace_id: str | None = None) -> dict[str, Any]:
        """Get execution patterns for meta-learning.

        Parameters
        ----------
        trace_id:
            Optional trace ID to filter patterns

        Returns
        -------
        dict[str, Any]
            Aggregated execution patterns
        """
        if trace_id:
            # Find meta_learning_id for this trace_id
            ml_id = None
            for mid, metadata in self._snapshot_index.items():
                if metadata["trace_id"] == trace_id:
                    ml_id = mid
                    break

            if ml_id and ml_id in self._pattern_index:
                return self._pattern_index[ml_id]
            else:
                return {}
        else:
            # Aggregate all patterns
            aggregated = {
                "layer_distribution": {},
                "component_distribution": {},
                "span_type_distribution": {},
                "relation_patterns": {},
                "total_snapshots": len(self._pattern_index),
            }

            for patterns in tqdm(self._pattern_index.values(), desc="Processing", unit="item"):
                for layer, count in patterns.get("layer_distribution", {}).items():
                    aggregated["layer_distribution"][layer] = (
                        aggregated["layer_distribution"].get(layer, 0) + count
                    )

                for component, count in patterns.get("component_distribution", {}).items():
                    aggregated["component_distribution"][component] = (
                        aggregated["component_distribution"].get(component, 0) + count
                    )

                for span_type, count in patterns.get("span_type_distribution", {}).items():
                    aggregated["span_type_distribution"][span_type] = (
                        aggregated["span_type_distribution"].get(span_type, 0) + count
                    )

                for relation, count in patterns.get("relation_patterns", {}).items():
                    aggregated["relation_patterns"][relation] = (
                        aggregated["relation_patterns"].get(relation, 0) + count
                    )

            return aggregated

    def query_evolution_log(self, event_type: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """Query evolution log for system learning insights.

        Parameters
        ----------
        event_type:
            Optional event type filter
        limit:
            Maximum number of events to return

        Returns
        -------
        list[dict[str, Any]]
            Evolution events
        """
        if not self._evolution_log_path.exists():
            return []

        events = []
        with open(self._evolution_log_path, encoding="utf-8") as f:
            for line in tqdm(f, desc="Processing", unit="item"):
                try:
                    event = json.loads(line.strip())
                    if event_type is None or event["event_type"] == event_type:
                        events.append(event)
                        if len(events) >= limit:
                            break
                except (json.JSONDecodeError, ValueError):
                    continue

        return events


emit_determinism_digest("runtime_adg_l6_integration", "runtime_adg_l6_integration_digest")
record_execution_trace("runtime_adg_l6_integration", "runtime_adg_l6_integration_trace")
