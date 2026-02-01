"""
Phase 3 Optimization Tests - Script Bridge
Tests for agent-to-script bridge interface.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
from apps_shared.scripts.script_bridge import ScriptBridge, ScriptResult, get_script_bridge


class TestScriptResult:
    """Test ScriptResult dataclass."""

    def test_script_result_creation(self):
        """Test creating ScriptResult."""
        result = ScriptResult(
            success=True, data={"key": "value"}, errors=[], metadata={"source": "test"}
        )

        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.errors == []
        assert result.metadata == {"source": "test"}

    def test_script_result_with_errors(self):
        """Test ScriptResult with errors."""
        result = ScriptResult(success=False, data=None, errors=["Error 1", "Error 2"], metadata={})

        assert result.success is False
        assert len(result.errors) == 2


class TestScriptBridge:
    """Test ScriptBridge functionality."""

    def setup_method(self):
        """Create temporary directory and bridge instance."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.bridge = ScriptBridge()

    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_execute_file_read_json(self):
        """Test executing file read_json operation."""
        test_file = self.temp_dir / "test.json"
        test_data = {"key": "value"}

        with open(test_file, "w") as f:
            json.dump(test_data, f)

        result = self.bridge.execute_script("file", "read_json", file_path=str(test_file))

        assert result.success is True
        assert result.data == test_data
        assert len(result.errors) == 0

    def test_execute_file_write_json(self):
        """Test executing file write_json operation."""
        test_file = self.temp_dir / "output.json"
        test_data = {"written": True}

        result = self.bridge.execute_script(
            "file", "write_json", file_path=str(test_file), data=test_data
        )

        assert result.success is True
        assert test_file.exists()

    def test_execute_file_file_exists(self):
        """Test executing file_exists operation."""
        test_file = self.temp_dir / "exists.txt"
        test_file.touch()

        result = self.bridge.execute_script("file", "file_exists", file_path=str(test_file))

        assert result.success is True
        assert result.data is True

    def test_execute_file_list_files(self):
        """Test executing list_files operation."""
        (self.temp_dir / "file1.txt").touch()
        (self.temp_dir / "file2.txt").touch()

        result = self.bridge.execute_script(
            "file", "list_files", directory=str(self.temp_dir), pattern="*.txt"
        )

        assert result.success is True
        assert len(result.data) == 2

    def test_execute_data_collect_metrics(self):
        """Test executing collect_metrics operation."""
        data_points = [{"score": 10}, {"score": 20}, {"score": 30}]

        result = self.bridge.execute_script(
            "data", "collect_metrics", data_points=data_points, metric_keys=["score"]
        )

        assert result.success is True
        assert result.data["score"] == [10, 20, 30]

    def test_execute_data_aggregate_results(self):
        """Test executing aggregate_results operation."""
        results = [{"type": "A", "val": 1}, {"type": "B", "val": 2}, {"type": "A", "val": 3}]

        result = self.bridge.execute_script(
            "data", "aggregate_results", results=results, group_by="type"
        )

        assert result.success is True
        assert len(result.data["A"]) == 2
        assert len(result.data["B"]) == 1

    def test_execute_data_filter_data(self):
        """Test executing filter_data operation."""
        data = [{"status": "active", "id": 1}, {"status": "inactive", "id": 2}]

        result = self.bridge.execute_script(
            "data", "filter_data", data=data, filters={"status": "active"}
        )

        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["id"] == 1

    def test_execute_monitor_check_system_state(self):
        """Test executing check_system_state operation."""
        state_file = self.temp_dir / "state.json"
        state_data = {"status": "running"}

        with open(state_file, "w") as f:
            json.dump(state_data, f)

        result = self.bridge.execute_script(
            "monitor", "check_system_state", state_file=str(state_file)
        )

        assert result.success is True
        assert result.data["status"] == "running"

    def test_execute_monitor_record_event(self):
        """Test executing record_event operation."""
        event_log = self.temp_dir / "events.json"

        result = self.bridge.execute_script(
            "monitor",
            "record_event",
            event_log=str(event_log),
            event_type="test",
            event_data={"data": "value"},
        )

        assert result.success is True
        assert event_log.exists()

    def test_execute_monitor_get_recent_events(self):
        """Test executing get_recent_events operation."""
        event_log = self.temp_dir / "events.json"

        # Record some events first
        self.bridge.execute_script(
            "monitor",
            "record_event",
            event_log=str(event_log),
            event_type="event1",
            event_data={},
        )
        self.bridge.execute_script(
            "monitor",
            "record_event",
            event_log=str(event_log),
            event_type="event2",
            event_data={},
        )

        result = self.bridge.execute_script(
            "monitor", "get_recent_events", event_log=str(event_log), count=10
        )

        assert result.success is True
        assert len(result.data) == 2

    def test_execute_unknown_script_module(self):
        """Test executing unknown script module."""
        result = self.bridge.execute_script("unknown", "operation")

        assert result.success is False
        assert len(result.errors) > 0
        assert "Unknown script module" in result.errors[0]

    def test_execute_unknown_operation(self):
        """Test executing unknown operation."""
        result = self.bridge.execute_script("file", "unknown_operation")

        assert result.success is False
        assert len(result.errors) > 0

    def test_execute_operation_with_error(self):
        """Test executing operation that raises error."""
        result = self.bridge.execute_script(
            "file", "read_json", file_path="/nonexistent/path/file.json"
        )

        assert result.success is False
        assert len(result.errors) > 0

    def test_read_config_file_convenience(self):
        """Test read_config_file convenience method."""
        config_file = self.temp_dir / "config.json"
        config_data = {"setting": "value"}

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        result = self.bridge.read_config_file(str(config_file))

        assert result.success is True
        assert result.data == config_data

    def test_collect_agent_metrics_convenience(self):
        """Test collect_agent_metrics convenience method."""
        data_points = [{"metric1": 10, "metric2": 20}, {"metric1": 30, "metric2": 40}]

        result = self.bridge.collect_agent_metrics(data_points, ["metric1", "metric2"])

        assert result.success is True
        assert result.data["metric1"] == [10, 30]
        assert result.data["metric2"] == [20, 40]

    def test_monitor_system_convenience(self):
        """Test monitor_system convenience method."""
        state_file = self.temp_dir / "system.json"
        state_data = {"cpu": 50, "memory": 70}

        with open(state_file, "w") as f:
            json.dump(state_data, f)

        result = self.bridge.monitor_system(str(state_file))

        assert result.success is True
        assert result.data["cpu"] == 50


class TestGlobalScriptBridge:
    """Test global script bridge instance."""

    def test_get_script_bridge_singleton(self):
        """Test that get_script_bridge returns singleton."""
        bridge1 = get_script_bridge()
        bridge2 = get_script_bridge()

        assert bridge1 is bridge2

    def test_get_script_bridge_functionality(self):
        """Test that global bridge works correctly."""
        bridge = get_script_bridge()

        result = bridge.execute_script("file", "file_exists", file_path="/nonexistent")

        assert result.success is True
        assert result.data is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
