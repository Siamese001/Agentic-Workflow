"""ADG-driven tests for apps_shared/scripts/io_operations_validator.py — fan_in=1."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from apps_shared.scripts.io_operations_validator import FileOperations


class TestFileOperations:
    def test_read_json_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            FileOperations.read_json("/nonexistent/path/file.json")

    def test_write_and_read_json_roundtrip(self, tmp_path):
        data = {"key": "value", "count": 42}
        out_path = tmp_path / "test.json"
        FileOperations.write_json(out_path, data)
        loaded = FileOperations.read_json(out_path)
        assert loaded == data

    def test_write_json_creates_file(self, tmp_path):
        out_path = tmp_path / "output.json"
        FileOperations.write_json(out_path, {"a": 1})
        assert out_path.exists()

    def test_read_json_parses_correctly(self, tmp_path):
        data = {"x": [1, 2, 3]}
        out_path = tmp_path / "data.json"
        out_path.write_text(json.dumps(data), encoding="utf-8")
        result = FileOperations.read_json(out_path)
        assert result["x"] == [1, 2, 3]

    def test_has_read_json(self):
        assert hasattr(FileOperations, "read_json")

    def test_has_write_json(self):
        assert hasattr(FileOperations, "write_json")
