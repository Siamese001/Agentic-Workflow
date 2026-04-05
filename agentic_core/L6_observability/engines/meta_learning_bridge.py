"""L6 Meta-Learning Bridge — Wave 4: Meta-learning bus wiring.

Provides L6MetaLearningBridge class that stores runtime ADG snapshots
for meta-learning and links evaluation metrics and telemetry events
to snapshots.

Design:
- Ingests runtime ADG snapshots from L4 State
- Links evaluation results via eval_results field
- Links telemetry events via telemetry_events field
- Provides feed_meta_learning() API for downstream consumption
- Graceful degradation when meta-learning unavailable

Usage:
    from agentic_core.L6_observability import L6MetaLearningBridge

    bridge = L6MetaLearningBridge(storage_path="artifacts/meta_learning")

    # Store snapshot with metadata
    bridge.store_snapshot(
        snapshot=snapshot,
        eval_results={"accuracy": 0.95, "f1": 0.92},
        telemetry_events=[{"type": "metric", "value": 42}],
    )

    # Feed to meta-learning pipeline
    bridge.feed_meta_learning(snapshot_id)
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_feeds_meta_learning,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_updates_meta_learning_state,
    emit_determinism_digest,
    emit_replay_key,
)

# Deferred imports for graceful degradation
try:
    from system_learning.runtime_adg.snapshot import RuntimeADGSnapshot
    SNAPSHOT_AVAILABLE = True
except ImportError:
    SNAPSHOT_AVAILABLE = False
    RuntimeADGSnapshot = None  # type: ignore[misc, assignment]

# Bootstrap ADG edge emission
emit_replay_key("l6_meta_learning_bridge", "L6_OBSERVABILITY")
emit_determinism_digest("l6_meta_learning_bridge", "l6_meta_learning_bridge_digest")
_emit_stores_learning_state("L6_OBSERVABILITY", "l6_meta_learning_bridge", "state_binding")
_emit_updates_meta_learning_state("L6_OBSERVABILITY", "l6_meta_learning_bridge", "update_binding")

logger = logging.getLogger(__name__)


@dataclass
class MetaLearningRecord:
    """A record linking a runtime ADG snapshot to evaluation and telemetry data.

    Attributes:
        snapshot_id: ID of the associated runtime ADG snapshot
        trace_id: Trace ID from the snapshot
        mission: Mission name
        stored_at_utc: Timestamp when record was stored
        eval_results: Evaluation metrics/results linked to snapshot
        telemetry_events: Telemetry events linked to snapshot
        metadata: Additional metadata
    """
    snapshot_id: str
    trace_id: str
    mission: str
    stored_at_utc: int = field(default_factory=lambda: int(time.time() * 1000))
    eval_results: dict[str, Any] = field(default_factory=dict)
    telemetry_events: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "snapshot_id": self.snapshot_id,
            "trace_id": self.trace_id,
            "mission": self.mission,
            "stored_at_utc": self.stored_at_utc,
            "eval_results": self.eval_results,
            "telemetry_events": self.telemetry_events,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MetaLearningRecord:
        """Create from dictionary."""
        return cls(
            snapshot_id=data.get("snapshot_id", ""),
            trace_id=data.get("trace_id", ""),
            mission=data.get("mission", ""),
            stored_at_utc=data.get("stored_at_utc", 0),
            eval_results=data.get("eval_results", {}),
            telemetry_events=data.get("telemetry_events", []),
            metadata=data.get("metadata", {}),
        )


class L6MetaLearningBridge:
    """Bridge between L6 Observability and meta-learning pipeline.

    Wave 4: Meta-learning bus wiring
    - Stores runtime ADG snapshots with evaluation/telemetry linkage
    - Provides feed_meta_learning() for downstream consumption
    - Links evaluation metrics via eval_results field
    - Links telemetry events via telemetry_events field

    Attributes:
        storage_path: Path for local storage of meta-learning records
        _records: In-memory cache of stored records
        _snapshot_to_record: Mapping from snapshot_id to record
    """

    def __init__(
        self,
        storage_path: str = "artifacts/meta_learning",
        enable_persistence: bool = True,
    ):
        """Initialize the meta-learning bridge.

        Args:
            storage_path: Path for local storage
            enable_persistence: Whether to enable local file persistence
        """
        self.storage_path = Path(storage_path)
        self.enable_persistence = enable_persistence
        self._records: dict[str, MetaLearningRecord] = {}
        self._snapshot_to_record: dict[str, str] = {}
        self._telemetry_buffer: list[dict[str, Any]] = []
        self._eval_buffer: list[dict[str, Any]] = []

        # Create storage directory if needed
        if self.enable_persistence:
            self.storage_path.mkdir(parents=True, exist_ok=True)

        logger.info(
            "l6_meta_learning_bridge_initialized",
            extra={
                "storage_path": str(self.storage_path),
                "enable_persistence": enable_persistence,
            },
        )

    def store_snapshot(
        self,
        snapshot: RuntimeADGSnapshot | dict[str, Any],
        eval_results: dict[str, Any] | None = None,
        telemetry_events: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MetaLearningRecord:
        """Store a snapshot with evaluation and telemetry linkage.

        Args:
            snapshot: RuntimeADGSnapshot or dict with snapshot data
            eval_results: Evaluation metrics/results to link
            telemetry_events: Telemetry events to link
            metadata: Additional metadata

        Returns:
            Created MetaLearningRecord
        """
        # Extract data from snapshot
        if isinstance(snapshot, dict):
            snapshot_id = snapshot.get("snapshot_id", "")
            trace_id = snapshot.get("trace_id", "")
            mission = snapshot.get("mission", "")
        else:
            snapshot_id = snapshot.snapshot_id
            trace_id = snapshot.trace_id
            mission = snapshot.mission

        # Create record
        record = MetaLearningRecord(
            snapshot_id=snapshot_id,
            trace_id=trace_id,
            mission=mission,
            eval_results=eval_results or {},
            telemetry_events=telemetry_events or [],
            metadata=metadata or {},
        )

        # Store in memory
        self._records[snapshot_id] = record
        self._snapshot_to_record[snapshot_id] = snapshot_id

        # Emit learning event
        _emit_records_learning_event(
            snapshot_id, "L6_OBSERVABILITY", "snapshot_stored_for_meta_learning"
        )

        # Persist to disk if enabled
        if self.enable_persistence:
            self._persist_record(record)

        logger.info(
            "snapshot_stored_for_meta_learning",
            extra={
                "snapshot_id": snapshot_id[:16] + "...",
                "mission": mission,
                "eval_keys": list(eval_results.keys()) if eval_results else [],
                "telemetry_count": len(telemetry_events) if telemetry_events else 0,
            },
        )

        return record

    def _persist_record(self, record: MetaLearningRecord) -> bool:
        """Persist record to local storage.

        Args:
            record: MetaLearningRecord to persist

        Returns:
            True if successful, False otherwise
        """
        try:
            filename = f"{record.snapshot_id}.json"
            filepath = self.storage_path / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(record.to_dict(), f, indent=2)

            _emit_stores_learning_state(
                "L6_OBSERVABILITY", "l6_meta_learning_bridge", record.snapshot_id
            )

            return True
        except Exception as e:
            logger.warning(
                "record_persist_failed",
                extra={"snapshot_id": record.snapshot_id[:16], "error": str(e)},
            )
            return False

    def load_record(self, snapshot_id: str) -> MetaLearningRecord | None:
        """Load a record by snapshot ID.

        Args:
            snapshot_id: Snapshot ID to look up

        Returns:
            MetaLearningRecord or None if not found
        """
        # Check in-memory cache first
        if snapshot_id in self._records:
            return self._records[snapshot_id]

        # Try to load from disk
        if self.enable_persistence:
            try:
                filepath = self.storage_path / f"{snapshot_id}.json"
                if filepath.exists():
                    with open(filepath, encoding="utf-8") as f:
                        data = json.load(f)
                        record = MetaLearningRecord.from_dict(data)
                        self._records[snapshot_id] = record
                        return record
            except Exception as e:
                logger.warning(
                    "record_load_failed",
                    extra={"snapshot_id": snapshot_id[:16], "error": str(e)},
                )

        return None

    def feed_meta_learning(
        self,
        snapshot_id: str,
        downstream_consumer: str | None = None,
    ) -> dict[str, Any] | None:
        """Feed a snapshot record to the meta-learning pipeline.

        Args:
            snapshot_id: ID of snapshot to feed
            downstream_consumer: Optional consumer identifier

        Returns:
            Record data dict or None if not found
        """
        record = self.load_record(snapshot_id)
        if not record:
            logger.warning(
                "feed_meta_learning_failed",
                extra={"snapshot_id": snapshot_id[:16], "reason": "record_not_found"},
            )
            return None

        # Emit meta-learning feed event
        _emit_feeds_meta_learning(
            snapshot_id, "L6_OBSERVABILITY", downstream_consumer or "meta_learning_pipeline"
        )

        # Update meta-learning state
        _emit_updates_meta_learning_state(
            snapshot_id, "L6_OBSERVABILITY", f"fed_to_{downstream_consumer or 'pipeline'}"
        )

        logger.info(
            "fed_to_meta_learning",
            extra={
                "snapshot_id": snapshot_id[:16] + "...",
                "downstream_consumer": downstream_consumer,
                "eval_count": len(record.eval_results),
                "telemetry_count": len(record.telemetry_events),
            },
        )

        return record.to_dict()

    def add_telemetry_event(
        self,
        snapshot_id: str,
        event: dict[str, Any],
    ) -> bool:
        """Add a telemetry event to an existing record.

        Args:
            snapshot_id: Snapshot ID to add event to
            event: Telemetry event dict

        Returns:
            True if added, False if record not found
        """
        record = self.load_record(snapshot_id)
        if not record:
            return False

        record.telemetry_events.append(event)
        record.stored_at_utc = int(time.time() * 1000)

        # Update in memory
        self._records[snapshot_id] = record

        # Persist updated record
        if self.enable_persistence:
            self._persist_record(record)

        return True

    def add_eval_result(
        self,
        snapshot_id: str,
        key: str,
        value: Any,
    ) -> bool:
        """Add an evaluation result to an existing record.

        Args:
            snapshot_id: Snapshot ID to add result to
            key: Evaluation metric name
            value: Evaluation metric value

        Returns:
            True if added, False if record not found
        """
        record = self.load_record(snapshot_id)
        if not record:
            return False

        record.eval_results[key] = value
        record.stored_at_utc = int(time.time() * 1000)

        # Update in memory
        self._records[snapshot_id] = record

        # Persist updated record
        if self.enable_persistence:
            self._persist_record(record)

        return True

    def get_record_stats(self) -> dict[str, Any]:
        """Get statistics about stored records.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_records": len(self._records),
            "storage_path": str(self.storage_path),
            "enable_persistence": self.enable_persistence,
            "total_eval_results": sum(
                len(r.eval_results) for r in self._records.values()
            ),
            "total_telemetry_events": sum(
                len(r.telemetry_events) for r in self._records.values()
            ),
        }

    def list_records(self) -> list[str]:
        """List all stored snapshot IDs.

        Returns:
            List of snapshot IDs
        """
        return list(self._records.keys())

    def clear(self) -> None:
        """Clear all in-memory records."""
        self._records.clear()
        self._snapshot_to_record.clear()
        logger.info("l6_meta_learning_bridge_cleared")


# Convenience function for getting bridge instance
def get_meta_learning_bridge(
    storage_path: str = "artifacts/meta_learning",
    enable_persistence: bool = True,
) -> L6MetaLearningBridge:
    """Get or create L6MetaLearningBridge instance.

    Args:
        storage_path: Path for local storage
        enable_persistence: Whether to enable persistence

    Returns:
        L6MetaLearningBridge instance
    """
    return L6MetaLearningBridge(
        storage_path=storage_path,
        enable_persistence=enable_persistence,
    )
