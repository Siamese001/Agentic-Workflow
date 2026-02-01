"""
Phase 3 Optimization Tests - I/O Operations
Tests for deterministic I/O script library.
"""

import pytest
import json
from pathlib import Path
import tempfile
import shutil
from apps_shared.scripts.io_operations import (
    FileOperations,
    DataCollectionOperations,
    MonitoringOperations,
)


class TestFileOperations:
    """Test FileOperations class."""

    def setup_method(self):
        """Create temporary directory for tests."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_read_json_success(self):
        """Test reading JSON file."""
        test_file = self.temp_dir / "test.json"
        test_data = {"key": "value", "number": 42}

        with open(test_file, "w") as f:
            json.dump(test_data, f)

        result = FileOperations.read_json(test_file)

        assert result == test_data

    def test_read_json_file_not_found(self):
        """Test reading non-existent JSON file."""
        with pytest.raises(FileNotFoundError):
            FileOperations.read_json(self.temp_dir / "nonexistent.json")

    def test_write_json_success(self):
        """Test writing JSON file."""
        test_file = self.temp_dir / "output.json"
        test_data = {"key": "value", "list": [1, 2, 3]}

        FileOperations.write_json(test_file, test_data)

        assert test_file.exists()
        with open(test_file) as f:
            loaded = json.load(f)
        assert loaded == test_data

    def test_write_json_creates_directories(self):
        """Test that write_json creates parent directories."""
        test_file = self.temp_dir / "subdir" / "nested" / "test.json"
        test_data = {"created": True}

        FileOperations.write_json(test_file, test_data)

        assert test_file.exists()
        assert test_file.parent.exists()

    def test_read_text_success(self):
        """Test reading text file."""
        test_file = self.temp_dir / "test.txt"
        test_content = "Hello, World!\nLine 2"

        with open(test_file, "w") as f:
            f.write(test_content)

        result = FileOperations.read_text(test_file)

        assert result == test_content

    def test_write_text_success(self):
        """Test writing text file."""
        test_file = self.temp_dir / "output.txt"
        test_content = "Test content\nMultiple lines"

        FileOperations.write_text(test_file, test_content)

        assert test_file.exists()
        with open(test_file) as f:
            content = f.read()
        assert content == test_content

    def test_list_files_non_recursive(self):
        """Test listing files non-recursively."""
        (self.temp_dir / "file1.txt").touch()
        (self.temp_dir / "file2.txt").touch()
        (self.temp_dir / "file3.json").touch()

        files = FileOperations.list_files(self.temp_dir, "*.txt")

        assert len(files) == 2
        assert all(f.suffix == ".txt" for f in files)

    def test_list_files_recursive(self):
        """Test listing files recursively."""
        (self.temp_dir / "file1.txt").touch()
        subdir = self.temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "file2.txt").touch()

        files = FileOperations.list_files(self.temp_dir, "*.txt", recursive=True)

        assert len(files) == 2

    def test_list_files_nonexistent_directory(self):
        """Test listing files in non-existent directory."""
        files = FileOperations.list_files(self.temp_dir / "nonexistent")

        assert files == []

    def test_file_exists_true(self):
        """Test file_exists returns True for existing file."""
        test_file = self.temp_dir / "exists.txt"
        test_file.touch()

        assert FileOperations.file_exists(test_file) is True

    def test_file_exists_false(self):
        """Test file_exists returns False for non-existent file."""
        assert FileOperations.file_exists(self.temp_dir / "nonexistent.txt") is False

    def test_delete_file_success(self):
        """Test deleting existing file."""
        test_file = self.temp_dir / "delete_me.txt"
        test_file.touch()

        result = FileOperations.delete_file(test_file)

        assert result is True
        assert not test_file.exists()

    def test_delete_file_nonexistent(self):
        """Test deleting non-existent file."""
        result = FileOperations.delete_file(self.temp_dir / "nonexistent.txt")

        assert result is False


class TestDataCollectionOperations:
    """Test DataCollectionOperations class."""

    def test_collect_metrics_success(self):
        """Test collecting metrics from data points."""
        data_points = [
            {"score": 10, "time": 100},
            {"score": 20, "time": 200},
            {"score": 30, "time": 300},
        ]

        result = DataCollectionOperations.collect_metrics(data_points, ["score", "time"])

        assert result["score"] == [10, 20, 30]
        assert result["time"] == [100, 200, 300]

    def test_collect_metrics_missing_keys(self):
        """Test collecting metrics with missing keys."""
        data_points = [{"score": 10}, {"time": 200}, {"score": 30, "time": 300}]

        result = DataCollectionOperations.collect_metrics(data_points, ["score", "time"])

        assert result["score"] == [10, 30]
        assert result["time"] == [200, 300]

    def test_aggregate_results_success(self):
        """Test aggregating results by key."""
        results = [
            {"type": "A", "value": 1},
            {"type": "B", "value": 2},
            {"type": "A", "value": 3},
        ]

        aggregated = DataCollectionOperations.aggregate_results(results, "type")

        assert len(aggregated["A"]) == 2
        assert len(aggregated["B"]) == 1
        assert aggregated["A"][0]["value"] == 1
        assert aggregated["A"][1]["value"] == 3

    def test_filter_data_single_filter(self):
        """Test filtering data with single criterion."""
        data = [
            {"status": "active", "score": 10},
            {"status": "inactive", "score": 20},
            {"status": "active", "score": 30},
        ]

        filtered = DataCollectionOperations.filter_data(data, {"status": "active"})

        assert len(filtered) == 2
        assert all(item["status"] == "active" for item in filtered)

    def test_filter_data_multiple_filters(self):
        """Test filtering data with multiple criteria."""
        data = [
            {"status": "active", "type": "A", "score": 10},
            {"status": "active", "type": "B", "score": 20},
            {"status": "inactive", "type": "A", "score": 30},
        ]

        filtered = DataCollectionOperations.filter_data(data, {"status": "active", "type": "A"})

        assert len(filtered) == 1
        assert filtered[0]["score"] == 10


class TestMonitoringOperations:
    """Test MonitoringOperations class."""

    def setup_method(self):
        """Create temporary directory for tests."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_check_system_state_success(self):
        """Test checking system state from file."""
        state_file = self.temp_dir / "state.json"
        state_data = {"status": "running", "uptime": 3600}

        with open(state_file, "w") as f:
            json.dump(state_data, f)

        result = MonitoringOperations.check_system_state(state_file)

        assert result["status"] == "running"
        assert result["uptime"] == 3600

    def test_check_system_state_file_not_found(self):
        """Test checking system state with missing file."""
        result = MonitoringOperations.check_system_state(self.temp_dir / "nonexistent.json")

        assert result["status"] == "unknown"
        assert "error" in result

    def test_record_event_new_log(self):
        """Test recording event to new log file."""
        event_log = self.temp_dir / "events.json"

        MonitoringOperations.record_event(event_log, "test_event", {"data": "value"})

        assert event_log.exists()
        events = FileOperations.read_json(event_log)
        assert len(events) == 1
        assert events[0]["type"] == "test_event"
        assert events[0]["data"]["data"] == "value"

    def test_record_event_append_to_existing(self):
        """Test recording event to existing log."""
        event_log = self.temp_dir / "events.json"

        MonitoringOperations.record_event(event_log, "event1", {"num": 1})
        MonitoringOperations.record_event(event_log, "event2", {"num": 2})

        events = FileOperations.read_json(event_log)
        assert len(events) == 2
        assert events[0]["type"] == "event1"
        assert events[1]["type"] == "event2"

    def test_get_recent_events_success(self):
        """Test getting recent events."""
        event_log = self.temp_dir / "events.json"

        for i in range(15):
            MonitoringOperations.record_event(event_log, f"event{i}", {"num": i})

        recent = MonitoringOperations.get_recent_events(event_log, count=5)

        assert len(recent) == 5
        assert recent[-1]["data"]["num"] == 14

    def test_get_recent_events_with_filter(self):
        """Test getting recent events with type filter."""
        event_log = self.temp_dir / "events.json"

        MonitoringOperations.record_event(event_log, "typeA", {"num": 1})
        MonitoringOperations.record_event(event_log, "typeB", {"num": 2})
        MonitoringOperations.record_event(event_log, "typeA", {"num": 3})

        recent = MonitoringOperations.get_recent_events(event_log, event_type="typeA")

        assert len(recent) == 2
        assert all(e["type"] == "typeA" for e in recent)

    def test_get_recent_events_nonexistent_log(self):
        """Test getting events from non-existent log."""
        recent = MonitoringOperations.get_recent_events(self.temp_dir / "nonexistent.json")

        assert recent == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
