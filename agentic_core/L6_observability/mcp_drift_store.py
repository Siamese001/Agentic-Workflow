"""Layer 6 Observability Integration for MCP Configuration Drift.

Persists MCP configuration snapshots to L6 observability storage
and provides drift alerting integration. This ensures runtime ADG
snapshots are available for historical analysis and compliance.

Storage:
  - Snapshots: artifacts/observability/mcp_snapshots/<timestamp>/
  - Reports: artifacts/observability/mcp_drift_reports/
  - Alerts: Integrated with L6 alerting pipeline
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_evaluation_metric,
    _emit_emits_metric_event,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    emit_determinism_digest,
    emit_replay_key,
)


# Lazy import to avoid L6->L_TOOLS gravity violation
def _get_mcp_drift_recorder():
    from agentic_core.adg.runtime.mcp_drift_recorder import (
        MCPConfigSnapshot,
        MCPDriftEvent,
        MCPDriftRecorder,
        MCPDriftReport,
        MCPDriftSeverity,
        MCPServerState,
    )
    return MCPServerState, MCPConfigSnapshot, MCPDriftEvent, MCPDriftRecorder, MCPDriftReport, MCPDriftSeverity

# Self-bootstrap emitters
emit_replay_key("p0", "mcp_l6_observability")
emit_determinism_digest("p0", "mcp_l6_observability")
_emit_records_telemetry_event("mcp_l6", "l6_obs", "persistence_active")


@dataclass
class MCPL6PersistenceConfig:
    """Configuration for MCP snapshot persistence in L6."""

    snapshots_dir: Path | None = None
    reports_dir: Path | None = None
    base_dir: Path | None = None  # Alternative: set both dirs from base
    max_snapshots: int = 100  # Keep last N snapshots
    max_reports: int = 50     # Keep last N reports
    enable_compression: bool = True

    def __post_init__(self):
        """Resolve directories after initialization."""
        if self.base_dir is not None:
            base = Path(self.base_dir) if isinstance(self.base_dir, str) else self.base_dir
            self.snapshots_dir = base / "mcp_snapshots"
            self.reports_dir = base / "mcp_drift_reports"
        if self.snapshots_dir is None:
            self.snapshots_dir = Path("artifacts/observability/mcp_snapshots")
        if self.reports_dir is None:
            self.reports_dir = Path("artifacts/observability/mcp_drift_reports")


class MCPL6ObservabilityStore:
    """Layer 6 observability store for MCP configuration snapshots.

    Persists runtime ADG snapshots to L6 storage and provides
drift alerting integration.

    Usage:
        store = MCPL6ObservabilityStore()

        # Save snapshot to L6
        store.save_snapshot(snapshot)

        # Save drift report
        store.save_drift_report(report)

        # Load historical snapshots
        snapshots = store.list_snapshots()

        # Get latest for comparison
        latest = store.get_latest_snapshot()
    """

    def __init__(self, config: MCPL6PersistenceConfig | None = None) -> None:
        self._config = config or MCPL6PersistenceConfig()
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create storage directories if needed."""
        self._config.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self._config.reports_dir.mkdir(parents=True, exist_ok=True)

    def save_snapshot(self, snapshot: MCPConfigSnapshot) -> Path:
        """Save MCP configuration snapshot to L6 storage.

        Args:
            snapshot: The configuration snapshot to persist

        Returns:
            Path to saved snapshot file
        """
        import uuid  # noqa: PLC0415

        _trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "MCPL6ObservabilityStore.save_snapshot")

        # Create timestamp-based directory
        timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.localtime(snapshot.timestamp))
        snapshot_dir = self._config.snapshots_dir / timestamp_str
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Save snapshot JSON
        snapshot_file = snapshot_dir / f"{snapshot.snapshot_id}.json"
        with open(snapshot_file, "w", encoding="utf-8") as f:
            f.write(snapshot.to_json())

        # Save metadata index
        index_file = snapshot_dir / "index.json"
        index_data = {
            "snapshot_id": snapshot.snapshot_id,
            "timestamp": snapshot.timestamp,
            "config_hash": snapshot.config_hash,
            "server_count": snapshot.server_count,
            "source_file": snapshot.source_file,
        }
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)

        # Cleanup old snapshots
        self._cleanup_old_snapshots()

        # Emit observability events
        _emit_emits_metric_event("mcp_l6", "l6_obs", "snapshot_saved")
        _emit_captures_evaluation_metric("mcp_l6", "l6_obs", f"servers_{snapshot.server_count}")

        return snapshot_file

    def save_drift_report(self, report: MCPDriftReport) -> Path:
        """Save drift report to L6 storage.

        Args:
            report: The drift report to persist

        Returns:
            Path to saved report file
        """
        import uuid  # noqa: PLC0415

        _trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "MCPL6ObservabilityStore.save_drift_report")

        timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.localtime(report.detected_at))
        report_file = self._config.reports_dir / f"drift_report_{timestamp_str}_{report.current_snapshot_id}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2, default=str)

        # Cleanup old reports
        self._cleanup_old_reports()

        # Emit observability events based on drift severity
        if report.has_drift:
            if report.critical_count > 0:
                _emit_emits_metric_event("mcp_l6", "l6_obs", f"critical_drift_{report.critical_count}")
            if report.warning_count > 0:
                _emit_emits_metric_event("mcp_l6", "l6_obs", f"warning_drift_{report.warning_count}")
        else:
            _emit_emits_metric_event("mcp_l6", "l6_obs", "no_drift")

        return report_file

    def list_snapshots(self) -> list[dict[str, Any]]:
        """List all stored snapshots with metadata.

        Returns:
            List of snapshot metadata dictionaries
        """
        snapshots: list[dict[str, Any]] = []

        for timestamp_dir in sorted(self._config.snapshots_dir.iterdir(), reverse=True):
            if timestamp_dir.is_dir():
                index_file = timestamp_dir / "index.json"
                if index_file.exists():
                    with open(index_file, encoding="utf-8") as f:
                        snapshots.append(json.load(f))

        return snapshots

    def list_drift_reports(self) -> list[Path]:
        """List all stored drift reports.

        Returns:
            List of drift report file paths
        """
        return sorted(self._config.reports_dir.glob("drift_report_*.json"), reverse=True)

    def get_latest_snapshot(self) -> MCPConfigSnapshot | None:
        """Load the most recent snapshot.

        Returns:
            The latest MCPConfigSnapshot or None if no snapshots exist
        """
        snapshots = self.list_snapshots()
        if not snapshots:
            return None

        latest = snapshots[0]
        timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.localtime(latest["timestamp"]))
        snapshot_dir = self._config.snapshots_dir / timestamp_str
        snapshot_file = snapshot_dir / f"{latest['snapshot_id']}.json"

        if snapshot_file.exists():
            with open(snapshot_file, encoding="utf-8") as f:
                data = json.load(f)
            return MCPConfigSnapshot(
                snapshot_id=data["snapshot_id"],
                timestamp=data["timestamp"],
                source_file=data["source_file"],
                servers={
                    name: MCPServerState.from_dict(state)
                    for name, state in data["servers"].items()
                },
                metadata=data.get("metadata", {}),
            )
        return None

    def load_snapshot(self, snapshot_id: str) -> MCPConfigSnapshot | None:
        """Load a specific snapshot by ID.

        Args:
            snapshot_id: The snapshot ID to load

        Returns:
            The MCPConfigSnapshot or None if not found
        """
        for timestamp_dir in self._config.snapshots_dir.iterdir():
            if timestamp_dir.is_dir():
                snapshot_file = timestamp_dir / f"{snapshot_id}.json"
                if snapshot_file.exists():
                    with open(snapshot_file, encoding="utf-8") as f:
                        data = json.load(f)
                    return MCPConfigSnapshot(
                        snapshot_id=data["snapshot_id"],
                        timestamp=data["timestamp"],
                        source_file=data["source_file"],
                        servers={
                            name: MCPServerState.from_dict(state)
                            for name, state in data["servers"].items()
                        },
                        metadata=data.get("metadata", {}),
                    )
        return None

    def _cleanup_old_snapshots(self) -> int:
        """Remove old snapshots beyond max_snapshots limit.

        Returns:
            Number of snapshots removed
        """
        all_dirs = sorted(self._config.snapshots_dir.iterdir())
        if len(all_dirs) <= self._config.max_snapshots:
            return 0

        removed = 0
        for old_dir in all_dirs[:-self._config.max_snapshots]:
            if old_dir.is_dir():
                for file in old_dir.iterdir():
                    file.unlink()
                old_dir.rmdir()
                removed += 1

        return removed

    def _cleanup_old_reports(self) -> int:
        """Remove old drift reports beyond max_reports limit.

        Returns:
            Number of reports removed
        """
        all_reports = sorted(self._config.reports_dir.glob("drift_report_*.json"))
        if len(all_reports) <= self._config.max_reports:
            return 0

        removed = 0
        for old_report in all_reports[:-self._config.max_reports]:
            old_report.unlink()
            removed += 1

        return removed

    def get_drift_statistics(self) -> dict[str, Any]:
        """Get aggregate drift statistics across all reports.

        Returns:
            Dictionary with drift statistics
        """
        reports = self.list_drift_reports()
        total_reports = len(reports)
        reports_with_drift = 0
        total_critical = 0
        total_warnings = 0

        for report_file in reports:
            try:
                with open(report_file, encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("has_drift", False):
                    reports_with_drift += 1
                total_critical += data.get("critical_count", 0)
                total_warnings += data.get("warning_count", 0)
            except (OSError, json.JSONDecodeError):
                continue

        return {
            "total_snapshots": len(self.list_snapshots()),
            "total_drift_reports": total_reports,
            "reports_with_drift": reports_with_drift,
            "total_events": total_critical + total_warnings,
            "total_critical_events": total_critical,
            "total_warning_events": total_warnings,
            "drift_rate": reports_with_drift / total_reports if total_reports > 0 else 0,
        }


class MCPDriftMonitor:
    """Active monitor for MCP configuration drift.

    Continuously monitors MCP configuration and alerts on drift.
Integrates with Layer 6 observability for comprehensive monitoring.

    Usage:
        monitor = MCPDriftMonitor(config_path=".windsurf/mcp_config.json")

        # Start monitoring (captures baseline)
        monitor.start_monitoring()

        # Check for drift (call periodically)
        report = monitor.check_drift()
        if report.has_drift:
            handle_drift(report)

        # Or use as context manager
        with MCPDriftMonitor(config_path) as monitor:
            # Monitoring active
            pass
    """

    def __init__(
        self,
        config_path: str | Path,
        store: MCPL6ObservabilityStore | None = None,
        recorder: MCPDriftRecorder | None = None,
    ) -> None:
        self._config_path = Path(config_path)
        self._store = store or MCPL6ObservabilityStore()
        self._recorder = recorder or MCPDriftRecorder(agent_id="MCPDriftMonitor")
        self._baseline: MCPConfigSnapshot | None = None
        self._started = False

    def start_monitoring(self) -> MCPConfigSnapshot:
        """Start monitoring by capturing baseline snapshot.

        Returns:
            The baseline configuration snapshot
        """
        import uuid  # noqa: PLC0415

        _trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "MCPDriftMonitor.start_monitoring")

        # Try to load previous baseline from store
        self._baseline = self._store.get_latest_snapshot()

        # Capture current state
        current = self._recorder.capture_snapshot(self._config_path)

        # If no baseline exists, use current as baseline
        if self._baseline is None:
            self._baseline = current

        # Save to L6 store
        self._store.save_snapshot(current)

        self._started = True
        _emit_emits_metric_event("mcp_monitor", "l6_obs", "monitoring_started")

        return self._baseline

    def check_drift(self) -> MCPDriftReport | None:
        """Check for configuration drift since baseline.

        Returns:
            MCPDriftReport if monitoring started, None otherwise
        """
        if not self._started:
            return None

        import uuid  # noqa: PLC0415

        _trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "MCPDriftMonitor.check_drift")

        # Capture current state
        current = self._recorder.capture_snapshot(self._config_path)
        self._store.save_snapshot(current)

        # Detect drift against baseline
        report = self._recorder.detect_drift(self._baseline, current)
        self._store.save_drift_report(report)

        return report

    @property
    def baseline(self) -> MCPConfigSnapshot | None:
        """Get the current baseline snapshot."""
        return self._baseline

    def update_baseline(self) -> MCPConfigSnapshot:
        """Update baseline to current configuration.

        Returns:
            The new baseline snapshot
        """
        self._baseline = self._recorder.capture_snapshot(self._config_path)
        self._store.save_snapshot(self._baseline)
        return self._baseline

    def force_baseline_update(self) -> MCPConfigSnapshot:
        """Force update of baseline to current configuration.

        Returns:
            The new baseline snapshot
        """
        self._baseline = self._recorder.capture_snapshot(self._config_path)
        self._store.save_snapshot(self._baseline)
        return self._baseline

    def __enter__(self) -> MCPDriftMonitor:
        """Context manager entry."""
        self.start_monitoring()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if self._started:
            final_report = self.check_drift()
            if final_report and final_report.has_drift:
                _emit_emits_metric_event("mcp_monitor", "l6_obs", f"final_drift_{len(final_report.drift_events)}")


__all__ = [
    "MCPL6ObservabilityStore",
    "MCPL6PersistenceConfig",
    "MCPDriftMonitor",
]
