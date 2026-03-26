"""Runtime ADG L6 Integration - Meta-learning snapshot storage.

Connects runtime ADG snapshots to L6 meta-learning state for continuous
system learning from execution traces.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    get_validated_project_root,
)
from system_learning.runtime_adg.snapshot import RuntimeADGSnapshot


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

        self._snapshot_index = self._load_index(self._snapshot_index_path)
        self._pattern_index = self._load_index(self._pattern_index_path)

    def _load_index(self, index_path: Path) -> dict[str, Any]:
        """Load index file or return empty dict."""
        if index_path.exists():
            try:
                return json.loads(index_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_index(self, index_path: Path, data: dict[str, Any]) -> None:
        """Save index file."""
        index_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

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
        """
        timestamp = int(time.time())
        meta_learning_id = f"runtime_adg_{timestamp}_{snapshot.snapshot_id[:8]}"

        # Store snapshot data
        snapshot_file = self._l6_base_dir / f"{meta_learning_id}.json"
        snapshot_data = {
            "meta_learning_id": meta_learning_id,
            "timestamp": timestamp,
            "trace_id": snapshot.trace_id,
            "mission": snapshot.mission,
            "started_at_utc": snapshot.started_at_utc,
            "ended_at_utc": snapshot.ended_at_utc,
            "duration_ms": snapshot.ended_at_utc - snapshot.started_at_utc,
            "node_count": len(snapshot.nodes),
            "edge_count": len(snapshot.edges),
            "nodes": [
                {
                    "node_id": node.node_id,
                    "name": node.name,
                    "kind": node.kind,
                    "layer": node.layer,
                    "component": node.component,
                    "started_at_utc": node.started_at_utc,
                    "duration_ms": node.duration_ms,
                    "status": node.status,
                    "attributes": json.loads(node.attributes_json) if node.attributes_json else {},
                }
                for node in snapshot.nodes
            ],
            "edges": [
                {
                    "src_id": edge.src_id,
                    "dst_id": edge.dst_id,
                    "relation": edge.relation,
                }
                for edge in snapshot.edges
            ],
        }

        snapshot_file.write_text(json.dumps(snapshot_data, indent=2), encoding="utf-8")

        # Update snapshot index
        project_root = get_validated_project_root()
        self._snapshot_index[meta_learning_id] = {
            "trace_id": snapshot.trace_id,
            "timestamp": timestamp,
            "mission": snapshot.mission,
            "node_count": len(snapshot.nodes),
            "edge_count": len(snapshot.edges),
            "duration_ms": snapshot.ended_at_utc - snapshot.started_at_utc,
            "file_path": str(snapshot_file.relative_to(project_root)),
        }
        self._save_index(self._snapshot_index_path, self._snapshot_index)

        # Extract and store patterns for meta-learning
        self._extract_and_store_patterns(meta_learning_id, snapshot)

        # Log evolution event
        self._log_evolution_event("runtime_adg_stored", {
            "meta_learning_id": meta_learning_id,
            "trace_id": snapshot.trace_id,
            "mission": snapshot.mission,
            "node_count": len(snapshot.nodes),
            "edge_count": len(snapshot.edges),
        })

        return meta_learning_id

    def _extract_and_store_patterns(self, meta_learning_id: str, snapshot: RuntimeADGSnapshot) -> None:
        """Extract execution patterns for meta-learning."""
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
        }

        # Analyze nodes for patterns
        for node in snapshot.nodes:
            # Layer distribution
            layer = node.layer
            patterns["layer_distribution"][layer] = patterns["layer_distribution"].get(layer, 0) + 1

            # Component distribution
            component = node.component
            patterns["component_distribution"][component] = patterns["component_distribution"].get(component, 0) + 1

            # Span type distribution
            span_type = node.kind
            patterns["span_type_distribution"][span_type] = patterns["span_type_distribution"].get(span_type, 0) + 1

            # Error patterns
            if node.status == "error":
                patterns["error_patterns"].append({
                    "node_id": node.node_id,
                    "component": component,
                    "layer": layer,
                })

            # Timing patterns
            if node.duration_ms > 1000:  # > 1 second
                patterns["timing_patterns"]["slow_operations"].append({
                    "node_id": node.node_id,
                    "component": component,
                    "duration_ms": node.duration_ms,
                })
            elif node.duration_ms < 10:  # < 10ms
                patterns["timing_patterns"]["fast_operations"].append({
                    "node_id": node.node_id,
                    "component": component,
                    "duration_ms": node.duration_ms,
                })

        # Analyze edges for patterns
        for edge in snapshot.edges:
            relation = edge.relation
            patterns["relation_patterns"][relation] = patterns["relation_patterns"].get(relation, 0) + 1

        # Store patterns
        self._pattern_index[meta_learning_id] = patterns
        self._save_index(self._pattern_index_path, self._pattern_index)

    def _log_evolution_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Log system evolution event."""
        event = {
            "timestamp": int(time.time()),
            "event_type": event_type,
            "data": data,
        }

        with open(self._evolution_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

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

        return [
            {"meta_learning_id": ml_id, **metadata}
            for ml_id, metadata in sorted_snapshots[:limit]
        ]

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

            for patterns in self._pattern_index.values():
                for layer, count in patterns.get("layer_distribution", {}).items():
                    aggregated["layer_distribution"][layer] = aggregated["layer_distribution"].get(layer, 0) + count

                for component, count in patterns.get("component_distribution", {}).items():
                    aggregated["component_distribution"][component] = aggregated["component_distribution"].get(component, 0) + count

                for span_type, count in patterns.get("span_type_distribution", {}).items():
                    aggregated["span_type_distribution"][span_type] = aggregated["span_type_distribution"].get(span_type, 0) + count

                for relation, count in patterns.get("relation_patterns", {}).items():
                    aggregated["relation_patterns"][relation] = aggregated["relation_patterns"].get(relation, 0) + count

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
        with open(self._evolution_log_path, "r", encoding="utf-8") as f:
            for line in f:
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
