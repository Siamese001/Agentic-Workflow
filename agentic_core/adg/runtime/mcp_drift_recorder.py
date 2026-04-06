"""MCP Configuration Drift Detection for Runtime ADG.

Captures MCP configuration state into runtime ADG snapshots to prevent
critical MCP configuration drift. Integrates with Layer 6 observability
for persistent drift monitoring and alerting.

Architecture:
  Static ADG (mcp_registry.py)  → MCP server declarations
  Runtime ADG (this module)     → Actual MCP configuration state
  Layer 6 Observability         → Snapshot persistence and drift alerts

Data model:
  MCPConfigSnapshot    — A point-in-time capture of MCP configuration
  MCPDriftEvent        — Detected configuration drift event
  MCPDriftRecorder     — Runtime collector for MCP configuration state
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_links_incident_trace,
    _emit_records_incident_event,
    _emit_records_telemetry_event,
    _emit_snapshots_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_writes_observability_log,
    emit_determinism_digest,
    emit_replay_key,
)

# Self-bootstrap emitters for this module
emit_replay_key("p0", "mcp_drift_recorder")
emit_determinism_digest("p0", "mcp_drift_recorder")
_emit_snapshots_state("mcp_drift", "mcp_drift_recorder", "mcp_config_snapshot")
_emit_writes_observability_log("mcp_drift_recorder", "p4obs", "mcp_config_log")
_emit_records_telemetry_event("mcp_drift_recorder", "p4obs", "mcp_telemetry")
_emit_updates_monitoring_state("mcp_drift_recorder", "p4obs", "mcp_monitoring")
_emit_emits_metric_event("mcp_drift_recorder", "p4obs", "mcp_drift_metric")


class MCPDriftSeverity(str, Enum):
    """Severity levels for MCP configuration drift."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MCPDriftType(str, Enum):
    """Types of MCP configuration drift."""

    SERVER_ADDED = "server_added"
    SERVER_REMOVED = "server_removed"
    COMMAND_CHANGED = "command_changed"
    ARGS_CHANGED = "args_changed"
    ENV_CHANGED = "env_changed"
    CAPABILITIES_CHANGED = "capabilities_changed"
    LAYER_REASSIGNED = "layer_reassigned"
    CONFIG_FILE_MISSING = "config_file_missing"
    PARSE_ERROR = "parse_error"


@dataclass(frozen=True)
class MCPServerState:
    """Immutable state of a single MCP server configuration.

    Attributes:
        name: Unique MCP server identifier
        target_layer: Assigned L0-L6 layer
        command: Execution command
        args: Command arguments tuple (hashable)
        env: Environment variables tuple of key=value pairs (hashable)
        capabilities: Sorted tuple of capability strings (hashable)
        disabled: Whether the server is disabled
    """

    name: str
    target_layer: str
    command: str
    args: tuple[str, ...]
    env: tuple[str, ...]  # key=value format for hashability
    capabilities: tuple[str, ...]
    disabled: bool = False

    @property
    def state_hash(self) -> str:
        """Deterministic hash of this server configuration."""
        content = f"{self.name}:{self.target_layer}:{self.command}:{self.args}:{self.env}:{self.capabilities}:{self.disabled}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "target_layer": self.target_layer,
            "command": self.command,
            "args": list(self.args),
            "env": dict(e.split("=", 1) for e in self.env),
            "capabilities": list(self.capabilities),
            "disabled": self.disabled,
            "state_hash": self.state_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MCPServerState:
        """Reconstruct from dictionary (e.g., from JSON)."""
        env_dict = data.get("env", {})
        env_tuple = tuple(f"{k}={v}" for k, v in sorted(env_dict.items()))
        return cls(
            name=data["name"],
            target_layer=data["target_layer"],
            command=data["command"],
            args=tuple(data.get("args", [])),
            env=env_tuple,
            capabilities=tuple(sorted(data.get("capabilities", []))),
            disabled=data.get("disabled", False),
        )


@dataclass(frozen=True)
class MCPConfigSnapshot:
    """Point-in-time capture of complete MCP configuration.

    This is the core data structure for runtime ADG integration,
    representing the actual MCP configuration state at snapshot time.

    Attributes:
        snapshot_id: Unique identifier for this snapshot
        timestamp: Unix epoch seconds
        source_file: Path to the MCP config file
        servers: Dictionary of server states by name
        config_hash: Deterministic hash of entire configuration
        metadata: Additional snapshot metadata
    """

    snapshot_id: str
    timestamp: float
    source_file: str
    servers: dict[str, MCPServerState]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def config_hash(self) -> str:
        """Deterministic hash of entire MCP configuration."""
        server_hashes = sorted(f"{name}:{state.state_hash}" for name, state in self.servers.items())
        content = f"{self.source_file}:{server_hashes}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    @property
    def server_count(self) -> int:
        return len(self.servers)

    @property
    def active_servers(self) -> list[str]:
        """List of non-disabled server names."""
        return [name for name, state in self.servers.items() if not state.disabled]

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "source_file": self.source_file,
            "config_hash": self.config_hash,
            "server_count": self.server_count,
            "active_servers": self.active_servers,
            "servers": {name: state.to_dict() for name, state in self.servers.items()},
            "metadata": dict(self.metadata),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True, default=str)


@dataclass(frozen=True)
class MCPDriftEvent:
    """A detected configuration drift event.

    Attributes:
        event_id: Unique drift event identifier
        drift_type: Type of drift detected
        severity: Severity level
        server_name: Affected server (if applicable)
        timestamp: Detection timestamp
        previous_hash: Configuration hash before drift
        current_hash: Configuration hash after drift
        details: Structured drift details
    """

    drift_type: MCPDriftType
    server_name: str | None
    timestamp: float
    previous_hash: str | None
    current_hash: str
    details: dict[str, Any]
    event_id: str = field(default_factory=lambda: f"mcp-drift-{uuid.uuid4().hex[:12]}")
    severity: MCPDriftSeverity = MCPDriftSeverity.WARNING

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "drift_type": self.drift_type.value,
            "severity": self.severity.value,
            "server_name": self.server_name,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash,
            "details": dict(self.details),
        }


@dataclass
class MCPDriftReport:
    """Aggregated drift report comparing two snapshots.

    Attributes:
        baseline_snapshot_id: Reference snapshot ID
        current_snapshot_id: Current snapshot ID
        drift_events: List of detected drift events
        detected_at: Report generation timestamp
    """

    baseline_snapshot_id: str
    current_snapshot_id: str
    baseline_hash: str
    current_hash: str
    drift_events: list[MCPDriftEvent] = field(default_factory=list)
    detected_at: float = field(default_factory=time.time)
    report_id: str = field(default_factory=lambda: f"mcp-drift-{uuid.uuid4().hex[:12]}")

    @property
    def has_drift(self) -> bool:
        return len(self.drift_events) > 0

    @property
    def critical_count(self) -> int:
        return sum(1 for e in self.drift_events if e.severity == MCPDriftSeverity.CRITICAL)

    @property
    def warning_count(self) -> int:
        return sum(1 for e in self.drift_events if e.severity == MCPDriftSeverity.WARNING)

    @property
    def max_severity(self) -> MCPDriftSeverity:
        """Maximum severity among all drift events."""
        if not self.drift_events:
            return MCPDriftSeverity.INFO
        severity_order = [MCPDriftSeverity.INFO, MCPDriftSeverity.WARNING, MCPDriftSeverity.CRITICAL]
        max_idx = max(severity_order.index(e.severity) for e in self.drift_events)
        return severity_order[max_idx]

    @property
    def total_events(self) -> int:
        """Total number of drift events."""
        return len(self.drift_events)

    @property
    def timestamp(self) -> float:
        """Alias for detected_at for compatibility."""
        return self.detected_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "baseline_snapshot_id": self.baseline_snapshot_id,
            "current_snapshot_id": self.current_snapshot_id,
            "baseline_hash": self.baseline_hash,
            "current_hash": self.current_hash,
            "has_drift": self.has_drift,
            "critical_count": self.critical_count,
            "warning_count": self.warning_count,
            "detected_at": self.detected_at,
            "drift_events": [e.to_dict() for e in self.drift_events],
        }


class MCPDriftRecorder:
    """Runtime collector for MCP configuration state.

    Captures MCP configuration into runtime ADG snapshots and detects drift.
    Integrates with Layer 6 observability for persistent monitoring.

    Usage:
        recorder = MCPDriftRecorder()

        # Capture current state
        snapshot = recorder.capture_snapshot("/path/to/mcp_config.json")

        # Detect drift against baseline
        report = recorder.detect_drift(baseline_snapshot, current_snapshot)

        # Access report for alerting
        if report.has_drift:
            for event in report.drift_events:
                handle_drift_event(event)
    """

    def __init__(self, agent_id: str = "MCPDriftRecorder", run_id: str | None = None) -> None:
        self._agent_id = agent_id
        self._run_id = run_id or f"mcp-drift-{int(time.time())}"
        self._snapshots: list[MCPConfigSnapshot] = []
        self._drift_reports: list[MCPDriftReport] = []

    @property
    def snapshots(self) -> list[MCPConfigSnapshot]:
        """All captured snapshots."""
        return self._snapshots.copy()

    @property
    def drift_reports(self) -> list[MCPDriftReport]:
        """All generated drift reports."""
        return self._drift_reports.copy()

    def capture_snapshot(self, config_path: str | Path) -> MCPConfigSnapshot:
        """Capture MCP configuration from JSON file.

        Args:
            config_path: Path to mcp_config.json file

        Returns:
            MCPConfigSnapshot with current configuration state
        """
        config_file = Path(config_path)
        snapshot_id = f"mcp-snap-{uuid.uuid4().hex[:12]}"
        timestamp = time.time()

        # Emit runtime ADG edge: this recorder captures MCP state
        _trace_id = str(uuid.uuid4())
        _emit_records_telemetry_event(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "MCPDriftRecorder.capture_snapshot"
        )

        if not config_file.exists():
            # Return empty snapshot with error metadata
            snapshot = MCPConfigSnapshot(
                snapshot_id=snapshot_id,
                timestamp=timestamp,
                source_file=str(config_file),
                servers={},
                metadata={"error": "Config file not found", "path": str(config_file)},
            )
            self._snapshots.append(snapshot)
            _emit_captures_runtime_anomaly("mcp_drift", "l6_obs", "config_missing")
            return snapshot

        try:
            with open(config_file, encoding="utf-8") as f:
                config_data = json.load(f)
        except (PermissionError, OSError) as e:
            snapshot = MCPConfigSnapshot(
                snapshot_id=snapshot_id,
                timestamp=timestamp,
                source_file=str(config_file),
                servers={},
                metadata={"error": f"Permission denied: {e}", "path": str(config_file)},
            )
            self._snapshots.append(snapshot)
            _emit_captures_runtime_anomaly("mcp_drift", "l6_obs", "permission_denied")
            return snapshot
        except json.JSONDecodeError as e:
            snapshot = MCPConfigSnapshot(
                snapshot_id=snapshot_id,
                timestamp=timestamp,
                source_file=str(config_file),
                servers={},
                metadata={"error": f"JSON parse error: {e}", "path": str(config_file)},
            )
            self._snapshots.append(snapshot)
            _emit_captures_runtime_anomaly("mcp_drift", "l6_obs", "parse_error")
            return snapshot

        # Parse MCP servers from config
        servers: dict[str, MCPServerState] = {}
        mcp_servers = config_data.get("mcpServers", {})

        for server_name, server_config in mcp_servers.items():
            # Determine target layer from capabilities or default to L2
            capabilities = server_config.get("capabilities") or []
            target_layer = self._infer_layer(server_name, capabilities)

            # Parse environment variables
            env_dict = server_config.get("env") or {}
            env_tuple = tuple(f"{k}={v}" for k, v in sorted(env_dict.items()))

            server_state = MCPServerState(
                name=server_name,
                target_layer=target_layer,
                command=server_config.get("command") or "",
                args=tuple(server_config.get("args") or []),
                env=env_tuple,
                capabilities=tuple(sorted(capabilities)),
                disabled=server_config.get("disabled") or False,
            )
            servers[server_name] = server_state

        snapshot = MCPConfigSnapshot(
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            source_file=str(config_file),
            servers=servers,
            metadata={
                "server_count": len(servers),
                "active_count": sum(1 for s in servers.values() if not s.disabled),
            },
        )

        self._snapshots.append(snapshot)

        # Emit observability events
        _emit_snapshots_state(snapshot.snapshot_id, "mcp_drift_recorder", "mcp_config_captured")
        _emit_writes_observability_log("mcp_drift", "l6_obs", f"captured_{snapshot.server_count}_servers")

        return snapshot

    def _infer_layer(self, server_name: str, capabilities: list[str] | None) -> str:
        """Infer target layer from server name and capabilities."""
        layer_indicators = {
            "L0": ["routing", "dispatch", "capacity"],
            "L1": ["reasoning", "thinking", "hypothesis", "cognition"],
            "L2": ["execution", "tool", "search", "fetch", "filesystem"],
            "L3": ["orchestration", "workflow", "agent"],
            "L4": ["state", "cache", "memory", "persistence"],
            "L5": ["safety", "guardrail", "validation", "security"],
            "L6": ["observability", "telemetry", "metric", "dashboard"],
        }

        # Handle None capabilities
        caps = capabilities or []

        # Check server name for layer hints
        name_lower = server_name.lower()
        for layer, indicators in layer_indicators.items():
            if any(ind in name_lower for ind in indicators):
                return layer
            if any(ind in cap.lower() for cap in caps for ind in indicators):
                return layer

        return "L2"  # Default to execution layer

    def detect_drift(self, baseline: MCPConfigSnapshot, current: MCPConfigSnapshot) -> MCPDriftReport:
        """Detect configuration drift between two snapshots.

        Args:
            baseline: Reference configuration snapshot
            current: Current configuration snapshot

        Returns:
            MCPDriftReport with detected drift events
        """
        _trace_id = str(uuid.uuid4())
        _emit_records_telemetry_event(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "MCPDriftRecorder.detect_drift"
        )

        events: list[MCPDriftEvent] = []

        # Detect added servers
        for name in current.servers:
            if name not in baseline.servers:
                events.append(
                    MCPDriftEvent(
                        drift_type=MCPDriftType.SERVER_ADDED,
                        server_name=name,
                        timestamp=time.time(),
                        previous_hash=baseline.config_hash,
                        current_hash=current.config_hash,
                        details={"new_server": current.servers[name].to_dict()},
                        severity=MCPDriftSeverity.INFO,
                    )
                )

        # Detect removed servers
        for name in baseline.servers:
            if name not in current.servers:
                events.append(
                    MCPDriftEvent(
                        drift_type=MCPDriftType.SERVER_REMOVED,
                        server_name=name,
                        timestamp=time.time(),
                        previous_hash=baseline.config_hash,
                        current_hash=current.config_hash,
                        details={"removed_server": baseline.servers[name].to_dict()},
                        severity=MCPDriftSeverity.CRITICAL,
                    )
                )

        # Detect changes in existing servers
        for name in baseline.servers:
            if name in current.servers:
                baseline_state = baseline.servers[name]
                current_state = current.servers[name]

                if baseline_state.state_hash != current_state.state_hash:
                    # Determine what changed
                    details: dict[str, Any] = {"server_name": name}

                    if baseline_state.command != current_state.command:
                        details["command"] = {
                            "from": baseline_state.command,
                            "to": current_state.command,
                        }
                        events.append(
                            MCPDriftEvent(
                                drift_type=MCPDriftType.COMMAND_CHANGED,
                                server_name=name,
                                timestamp=time.time(),
                                previous_hash=baseline.config_hash,
                                current_hash=current.config_hash,
                                details=details,
                                severity=MCPDriftSeverity.CRITICAL,
                            )
                        )

                    if baseline_state.args != current_state.args:
                        details["args"] = {
                            "from": list(baseline_state.args),
                            "to": list(current_state.args),
                        }
                        events.append(
                            MCPDriftEvent(
                                drift_type=MCPDriftType.ARGS_CHANGED,
                                server_name=name,
                                timestamp=time.time(),
                                previous_hash=baseline.config_hash,
                                current_hash=current.config_hash,
                                details=details,
                                severity=MCPDriftSeverity.WARNING,
                            )
                        )

                    if baseline_state.env != current_state.env:
                        details["env"] = {
                            "from": list(baseline_state.env),
                            "to": list(current_state.env),
                        }
                        events.append(
                            MCPDriftEvent(
                                drift_type=MCPDriftType.ENV_CHANGED,
                                server_name=name,
                                timestamp=time.time(),
                                previous_hash=baseline.config_hash,
                                current_hash=current.config_hash,
                                details=details,
                                severity=MCPDriftSeverity.CRITICAL,
                            )
                        )

                    if baseline_state.capabilities != current_state.capabilities:
                        details["capabilities"] = {
                            "from": list(baseline_state.capabilities),
                            "to": list(current_state.capabilities),
                        }
                        events.append(
                            MCPDriftEvent(
                                drift_type=MCPDriftType.CAPABILITIES_CHANGED,
                                server_name=name,
                                timestamp=time.time(),
                                previous_hash=baseline.config_hash,
                                current_hash=current.config_hash,
                                details=details,
                                severity=MCPDriftSeverity.WARNING,
                            )
                        )

                    if baseline_state.target_layer != current_state.target_layer:
                        details["target_layer"] = {
                            "from": baseline_state.target_layer,
                            "to": current_state.target_layer,
                        }
                        events.append(
                            MCPDriftEvent(
                                drift_type=MCPDriftType.LAYER_REASSIGNED,
                                server_name=name,
                                timestamp=time.time(),
                                previous_hash=baseline.config_hash,
                                current_hash=current.config_hash,
                                details=details,
                                severity=MCPDriftSeverity.WARNING,
                            )
                        )

        report = MCPDriftReport(
            baseline_snapshot_id=baseline.snapshot_id,
            current_snapshot_id=current.snapshot_id,
            baseline_hash=baseline.config_hash,
            current_hash=current.config_hash,
            drift_events=events,
        )

        self._drift_reports.append(report)

        # Emit observability events for drift
        if report.has_drift:
            for event in report.drift_events:
                if event.severity == MCPDriftSeverity.CRITICAL:
                    _emit_triggers_alert("mcp_drift", "l6_obs", event.event_id)
                    _emit_records_incident_event("mcp_drift", "l6_obs", event.event_id)
                    _emit_links_incident_trace(event.event_id, "l6_obs", event.server_name or "global")
                elif event.severity == MCPDriftSeverity.WARNING:
                    _emit_captures_runtime_anomaly("mcp_drift", "l6_obs", event.event_id)

            _emit_emits_metric_event("mcp_drift", "l6_obs", f"drift_events_{len(events)}")

        return report

    def get_latest_snapshot(self) -> MCPConfigSnapshot | None:
        """Get the most recent snapshot."""
        return self._snapshots[-1] if self._snapshots else None

    def get_latest_report(self) -> MCPDriftReport | None:
        """Get the most recent drift report."""
        return self._drift_reports[-1] if self._drift_reports else None


__all__ = [
    "MCPServerState",
    "MCPConfigSnapshot",
    "MCPDriftEvent",
    "MCPDriftReport",
    "MCPDriftRecorder",
    "MCPDriftSeverity",
    "MCPDriftType",
]
