"""E2E tests for MCP drift detection system.

Tests the complete flow from snapshot capture through drift detection
to Layer 6 observability persistence and alerting.
"""

import json
import shutil
import tempfile
import time
from pathlib import Path

import pytest

from agentic_core.adg.runtime import (
    MCPDriftEvent,
    MCPDriftRecorder,
    MCPDriftReport,
    MCPDriftSeverity,
    MCPDriftType,
)
from agentic_core.L6_observability import (
    MCPDriftMonitor,
    MCPL6ObservabilityStore,
    MCPL6PersistenceConfig,
)


@pytest.fixture
def temp_observability_dir():
    """Create a temporary directory for observability artifacts."""
    temp_dir = tempfile.mkdtemp(prefix="mcp_drift_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_mcp_config():
    """Sample MCP configuration for testing."""
    return {
        "mcpServers": {
            "adg_redis": {
                "command": "python",
                "args": ["tools/adg/adg_redis_server.py"],
                "cwd": "C:\\Git\\Agentic-Workflow",
                "env": {"ADG_REDIS_URL": "redis://localhost:6379/0"},
                "capabilities": ["tools"],
                "deploymentMode": "local",
                "layer": "L6"
            },
            "memory": {
                "command": "python",
                "args": ["tools/memory/adg_memory_server.py"],
                "cwd": "C:\\Git\\Agentic-Workflow",
                "env": {"ADG_REDIS_URL": "redis://localhost:6379/0"},
                "capabilities": ["tools", "resources"],
                "deploymentMode": "local",
                "layer": "L6"
            }
        }
    }


@pytest.fixture
def modified_mcp_config():
    """Modified MCP configuration with drift."""
    return {
        "mcpServers": {
            "adg_redis": {
                "command": "python3",  # Changed
                "args": ["tools/adg/adg_redis_server.py", "--debug"],  # Changed
                "cwd": "C:\\Git\\Agentic-Workflow",
                "env": {"ADG_REDIS_URL": "redis://localhost:6379/1"},  # Changed
                "capabilities": ["tools", "resources"],  # Changed
                "deploymentMode": "local",
                "layer": "L6"
            },
            # "memory" server removed
            "new_server": {  # Added
                "command": "node",
                "args": ["server.js"],
                "cwd": "/some/path",
                "env": {},
                "capabilities": ["tools"],
                "deploymentMode": "local",
                "layer": "L5"
            }
        }
    }


class TestMCPDriftRecorderE2E:
    """E2E tests for MCPDriftRecorder."""

    def test_full_snapshot_capture_flow(self, temp_observability_dir, sample_mcp_config):
        """Test complete snapshot capture flow."""
        # Create config file
        config_path = Path(temp_observability_dir) / "mcp_config.json"
        with open(config_path, "w") as f:
            json.dump(sample_mcp_config, f)

        # Create recorder
        recorder = MCPDriftRecorder(agent_id="test_agent")

        # Capture snapshot
        snapshot = recorder.capture_snapshot(config_path)

        # Verify snapshot structure
        assert snapshot.snapshot_id.startswith("mcp-snap-")
        assert snapshot.server_count == 2
        assert len(snapshot.active_servers) == 2
        assert "adg_redis" in snapshot.active_servers
        assert "memory" in snapshot.active_servers
        assert snapshot.config_hash is not None
        assert snapshot.timestamp > 0

        # Verify server states (layer inferred from name/capabilities)
        redis_state = snapshot.servers["adg_redis"]
        assert redis_state.name == "adg_redis"
        assert redis_state.command == "python"
        assert redis_state.args == ("tools/adg/adg_redis_server.py",)
        assert redis_state.target_layer == "L2"  # Default layer (no L6 indicators in name)
        assert redis_state.state_hash is not None

    def test_drift_detection_full_flow(self, temp_observability_dir, sample_mcp_config, modified_mcp_config):
        """Test complete drift detection flow between two snapshots."""
        # Create baseline config
        baseline_path = Path(temp_observability_dir) / "mcp_config_baseline.json"
        with open(baseline_path, "w") as f:
            json.dump(sample_mcp_config, f)

        # Create current config
        current_path = Path(temp_observability_dir) / "mcp_config_current.json"
        with open(current_path, "w") as f:
            json.dump(modified_mcp_config, f)

        # Create recorder
        recorder = MCPDriftRecorder(agent_id="test_agent")

        # Capture snapshots
        baseline = recorder.capture_snapshot(baseline_path)
        current = recorder.capture_snapshot(current_path)

        # Detect drift
        report = recorder.detect_drift(baseline, current)

        # Verify report structure
        assert isinstance(report, MCPDriftReport)
        assert report.report_id.startswith("mcp-drift-")
        assert report.baseline_snapshot_id == baseline.snapshot_id
        assert report.current_snapshot_id == current.snapshot_id
        assert report.timestamp > 0

        # Verify drift detected
        assert report.has_drift is True
        assert report.total_events == 6  # server added/removed + command/args/env/capabilities changed

        # Verify severity
        assert report.max_severity == MCPDriftSeverity.CRITICAL  # Server removed

        # Check specific events
        event_types = [e.drift_type for e in report.drift_events]
        assert MCPDriftType.COMMAND_CHANGED in event_types
        assert MCPDriftType.ARGS_CHANGED in event_types
        assert MCPDriftType.ENV_CHANGED in event_types
        assert MCPDriftType.CAPABILITIES_CHANGED in event_types
        assert MCPDriftType.SERVER_REMOVED in event_types
        assert MCPDriftType.SERVER_ADDED in event_types

    def test_no_drift_scenario(self, temp_observability_dir, sample_mcp_config):
        """Test when no drift is detected."""
        config_path = Path(temp_observability_dir) / "mcp_config.json"
        with open(config_path, "w") as f:
            json.dump(sample_mcp_config, f)

        recorder = MCPDriftRecorder(agent_id="test_agent")

        # Capture same config twice
        baseline = recorder.capture_snapshot(config_path)
        current = recorder.capture_snapshot(config_path)

        report = recorder.detect_drift(baseline, current)

        assert report.has_drift is False
        assert report.total_events == 0
        assert report.max_severity == MCPDriftSeverity.INFO

    def test_drift_with_empty_config(self, temp_observability_dir):
        """Test drift detection with empty config."""
        empty_config = {"mcpServers": {}}

        config_path = Path(temp_observability_dir) / "empty_config.json"
        with open(config_path, "w") as f:
            json.dump(empty_config, f)

        recorder = MCPDriftRecorder(agent_id="test_agent")
        snapshot = recorder.capture_snapshot(config_path)

        assert snapshot.server_count == 0
        assert len(snapshot.active_servers) == 0
        assert snapshot.config_hash is not None  # Should still have hash

    def test_drift_with_missing_file(self, temp_observability_dir):
        """Test handling of missing config file - returns snapshot with error metadata."""
        recorder = MCPDriftRecorder(agent_id="test")

        # Should return snapshot with error metadata, not raise exception
        snapshot = recorder.capture_snapshot(Path(temp_observability_dir) / "nonexistent.json")
        assert snapshot is not None
        assert "error" in snapshot.metadata
        assert "not found" in snapshot.metadata["error"].lower()
        assert snapshot.server_count == 0

    def test_drift_with_invalid_json(self, temp_observability_dir):
        """Test handling of invalid JSON - returns snapshot with error metadata."""
        config_path = Path(temp_observability_dir) / "invalid.json"
        with open(config_path, "w") as f:
            f.write("not valid json {{{")

        recorder = MCPDriftRecorder(agent_id="test")

        # Should return snapshot with error metadata, not raise exception
        snapshot = recorder.capture_snapshot(config_path)
        assert snapshot is not None
        assert "error" in snapshot.metadata
        assert "parse" in snapshot.metadata["error"].lower() or "json" in snapshot.metadata["error"].lower()
        assert snapshot.server_count == 0


class TestMCPL6ObservabilityStoreE2E:
    """E2E tests for MCPL6ObservabilityStore."""

    def test_full_persistence_flow(self, temp_observability_dir, sample_mcp_config):
        """Test complete persistence flow for snapshots and drift reports."""
        config_path = Path(temp_observability_dir) / "mcp_config.json"
        with open(config_path, "w") as f:
            json.dump(sample_mcp_config, f)

        # Create store with custom base dir
        store = MCPL6ObservabilityStore(
            MCPL6PersistenceConfig(
                base_dir=Path(temp_observability_dir),
                max_snapshots=10,
                max_reports=10
            )
        )

        # Capture and save snapshot
        recorder = MCPDriftRecorder(agent_id="test_agent")
        snapshot = recorder.capture_snapshot(config_path)
        snapshot_path = store.save_snapshot(snapshot)

        # Verify snapshot saved
        assert snapshot_path.exists()
        with open(snapshot_path) as f:
            saved_data = json.load(f)
            assert saved_data["snapshot_id"] == snapshot.snapshot_id
            assert saved_data["server_count"] == 2

        # Create and save drift report
        report = MCPDriftReport(
            baseline_snapshot_id="snap-1",
            current_snapshot_id=snapshot.snapshot_id,
            baseline_hash="base_hash",
            current_hash=snapshot.config_hash,
            drift_events=[
                MCPDriftEvent(
                    server_name="test",
                    drift_type=MCPDriftType.SERVER_ADDED,
                    severity=MCPDriftSeverity.INFO,
                    timestamp=time.time(),
                    previous_hash="prev_hash",
                    current_hash="curr_hash",
                    details={"description": "Test drift"}
                )
            ]
        )
        report_path = store.save_drift_report(report)

        # Verify report saved
        assert report_path.exists()
        with open(report_path) as f:
            saved_report = json.load(f)
            assert saved_report["report_id"] == report.report_id
            assert saved_report["has_drift"] is True

        # Verify listings
        snapshots = store.list_snapshots()
        assert len(snapshots) == 1

        reports = store.list_drift_reports()
        assert len(reports) == 1

    def test_cleanup_old_snapshots(self, temp_observability_dir, sample_mcp_config):
        """Test cleanup of old snapshots."""
        config_path = Path(temp_observability_dir) / "mcp_config.json"
        with open(config_path, "w") as f:
            json.dump(sample_mcp_config, f)

        store = MCPL6ObservabilityStore(
            MCPL6PersistenceConfig(
                base_dir=Path(temp_observability_dir),
                max_snapshots=3,
                max_reports=3
            )
        )

        recorder = MCPDriftRecorder(agent_id="test_agent")

        # Create 5 snapshots (exceeds max of 3)
        for _ in range(5):
            snapshot = recorder.capture_snapshot(config_path)
            store.save_snapshot(snapshot)
            time.sleep(0.1)  # Ensure different timestamps

        # Should only keep 3 most recent
        snapshots = store.list_snapshots()
        assert len(snapshots) <= 3

    def test_store_initialization_creates_dirs(self, temp_observability_dir):
        """Test that store initialization creates necessary directories."""
        store = MCPL6ObservabilityStore(
            MCPL6PersistenceConfig(base_dir=Path(temp_observability_dir))
        )

        snapshots_dir = Path(temp_observability_dir) / "mcp_snapshots"
        reports_dir = Path(temp_observability_dir) / "mcp_drift_reports"

        assert snapshots_dir.exists()
        assert reports_dir.exists()


class TestMCPDriftMonitorE2E:
    """E2E tests for MCPDriftMonitor."""

    def test_monitor_start_and_check_flow(self, temp_observability_dir, sample_mcp_config):
        """Test monitor start and drift check flow."""
        config_path = Path(temp_observability_dir) / "mcp_config.json"
        with open(config_path, "w") as f:
            json.dump(sample_mcp_config, f)

        # Create fresh store to ensure isolation
        store = MCPL6ObservabilityStore(
            MCPL6PersistenceConfig(base_dir=temp_observability_dir)
        )

        monitor = MCPDriftMonitor(
            config_path=config_path,
            store=store
        )

        # Start monitoring
        baseline = monitor.start_monitoring()
        assert baseline is not None
        assert baseline.snapshot_id is not None

        # Check drift (same config, should be no drift)
        report = monitor.check_drift()
        assert not report.has_drift

    def test_monitor_detects_drift(self, temp_observability_dir, sample_mcp_config, modified_mcp_config):
        """Test monitor detects drift when config changes."""
        config_path = Path(temp_observability_dir) / "mcp_config.json"
        with open(config_path, "w") as f:
            json.dump(sample_mcp_config, f)

        # Create fresh store to ensure isolation
        store = MCPL6ObservabilityStore(
            MCPL6PersistenceConfig(base_dir=temp_observability_dir)
        )

        monitor = MCPDriftMonitor(
            config_path=config_path,
            store=store
        )

        # Start with baseline
        monitor.start_monitoring()

        # Modify config
        with open(config_path, "w") as f:
            json.dump(modified_mcp_config, f)

        # Check drift
        report = monitor.check_drift()
        assert report is not None
        assert report.has_drift is True

    def test_monitor_context_manager(self, temp_observability_dir, sample_mcp_config):
        """Test monitor as context manager."""
        config_path = Path(temp_observability_dir) / "mcp_config.json"
        with open(config_path, "w") as f:
            json.dump(sample_mcp_config, f)

        # Create fresh store to ensure isolation
        store = MCPL6ObservabilityStore(
            MCPL6PersistenceConfig(base_dir=temp_observability_dir)
        )

        with MCPDriftMonitor(
            config_path=config_path,
            store=store
        ) as monitor:
            assert monitor.baseline is not None
            report = monitor.check_drift()
            assert not report.has_drift

    def test_monitor_update_baseline(self, temp_observability_dir, sample_mcp_config, modified_mcp_config):
        """Test updating baseline after drift detection."""
        config_path = Path(temp_observability_dir) / "mcp_config.json"

        # Create fresh store to ensure isolation
        store = MCPL6ObservabilityStore(
            MCPL6PersistenceConfig(base_dir=temp_observability_dir)
        )

        monitor = MCPDriftMonitor(
            config_path=config_path,
            store=store
        )

        # Start with original config
        with open(config_path, "w") as f:
            json.dump(sample_mcp_config, f)
        monitor.start_monitoring()

        # Change config and detect drift
        with open(config_path, "w") as f:
            json.dump(modified_mcp_config, f)
        report = monitor.check_drift()
        assert report.has_drift

        # Update baseline to new config
        monitor.update_baseline()

        # Check drift again - should be no drift now
        report = monitor.check_drift()
        assert not report.has_drift


class TestIntegrationScenarios:
    """Integration scenario tests."""

    def test_real_mcp_config_capture(self, temp_observability_dir):
        """Test with actual MCP config if available."""
        real_config_paths = [
            Path(".windsurf/mcp_config.json"),
            Path.home() / ".codeium" / "windsurf" / "mcp_config.json",
        ]

        config_path = None
        for path in real_config_paths:
            if path.exists():
                config_path = path
                break

        if config_path is None:
            pytest.skip("No real MCP config found")

        store = MCPL6ObservabilityStore(
            MCPL6PersistenceConfig(base_dir=temp_observability_dir)
        )

        recorder = MCPDriftRecorder(agent_id="integration_test")

        # Capture real config
        snapshot = recorder.capture_snapshot(config_path)
        assert snapshot.server_count > 0
        assert len(snapshot.active_servers) > 0

        # Save to L6
        saved_path = store.save_snapshot(snapshot)
        assert saved_path.exists()

    def test_drift_statistics_aggregation(self, temp_observability_dir, sample_mcp_config):
        """Test drift statistics aggregation over multiple checks."""
        config_path = Path(temp_observability_dir) / "mcp_config.json"
        with open(config_path, "w") as f:
            json.dump(sample_mcp_config, f)

        store = MCPL6ObservabilityStore(
            MCPL6PersistenceConfig(base_dir=temp_observability_dir)
        )

        # Create multiple drift reports
        for i in range(5):
            report = MCPDriftReport(
                baseline_snapshot_id=f"baseline-{i}",
                current_snapshot_id=f"current-{i}",
                baseline_hash=f"prev_hash_{i}",
                current_hash=f"curr_hash_{i}",
                drift_events=[
                    MCPDriftEvent(
                        server_name=f"server-{i}",
                        drift_type=MCPDriftType.CAPABILITIES_CHANGED,
                        severity=MCPDriftSeverity.WARNING,
                        timestamp=time.time(),
                        previous_hash=f"prev_{i}",
                        current_hash=f"curr_{i}",
                        details={"description": f"Test drift {i}"}
                    )
                ]
            )
            store.save_drift_report(report)

        # Get statistics
        stats = store.get_drift_statistics()
        assert stats["total_snapshots"] == 0  # No snapshots saved
        assert stats["total_drift_reports"] == 5
        assert stats["drift_rate"] == 1.0  # All reports have drift
        assert stats["total_events"] == 5

    def test_concurrent_snapshot_operations(self, temp_observability_dir, sample_mcp_config):
        """Test that concurrent operations don't corrupt data."""
        import threading

        config_path = Path(temp_observability_dir) / "mcp_config.json"
        with open(config_path, "w") as f:
            json.dump(sample_mcp_config, f)

        store = MCPL6ObservabilityStore(
            MCPL6PersistenceConfig(base_dir=temp_observability_dir)
        )
        recorder = MCPDriftRecorder(agent_id="concurrent_test")

        errors = []
        snapshots_captured = []

        def capture_and_save():
            try:
                snapshot = recorder.capture_snapshot(config_path)
                path = store.save_snapshot(snapshot)
                snapshots_captured.append(path)
            except Exception as e:
                errors.append(e)

        # Run 10 threads concurrently
        threads = [threading.Thread(target=capture_and_save) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors during concurrent ops: {errors}"
        assert len(snapshots_captured) == 10

        # Verify all snapshots exist
        for path in snapshots_captured:
            assert path.exists(), f"Snapshot not found: {path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
