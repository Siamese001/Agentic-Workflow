"""Unit tests for baseline_io.py (atomic JSON I/O + CI write guard)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from ops_scripts.ci.baseline_io import (
    CIWriteBlockedError,
    read_json,
    write_json_atomic,
)


class TestReadJson:
    """JSON reading."""

    def test_read_valid_json(self, tmp_path):
        f = tmp_path / "test.json"
        f.write_text('{"a": 1}', encoding="utf-8")
        assert read_json(f) == {"a": 1}

    def test_read_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            read_json(tmp_path / "missing.json")

    def test_read_invalid_json(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("not json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            read_json(f)


class TestWriteJsonAtomic:
    """Atomic JSON writing with CI guard."""

    def test_write_creates_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        f = tmp_path / "out.json"
        write_json_atomic(f, {"count": 42})
        assert f.is_file()
        data = json.loads(f.read_text(encoding="utf-8"))
        assert data["count"] == 42

    def test_write_overwrites_existing(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        f = tmp_path / "out.json"
        f.write_text('{"old": true}', encoding="utf-8")
        write_json_atomic(f, {"new": True})
        data = json.loads(f.read_text(encoding="utf-8"))
        assert "new" in data
        assert "old" not in data

    def test_write_is_valid_json(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        f = tmp_path / "out.json"
        write_json_atomic(f, {"entries": [1, 2, 3]})
        # Must parse without error
        json.loads(f.read_text(encoding="utf-8"))

    def test_write_ends_with_newline(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        f = tmp_path / "out.json"
        write_json_atomic(f, {"x": 1})
        assert f.read_text(encoding="utf-8").endswith("\n")


class TestCIWriteGuard:
    """CI write-safety regression tests."""

    def test_blocked_when_ci_true(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CI", "true")
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        monkeypatch.delenv("ALLOW_BASELINE_WRITES_IN_CI", raising=False)
        f = tmp_path / "out.json"
        with pytest.raises(CIWriteBlockedError, match="Refusing to write"):
            write_json_atomic(f, {"x": 1})

    def test_blocked_when_github_actions_true(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        monkeypatch.delenv("ALLOW_BASELINE_WRITES_IN_CI", raising=False)
        f = tmp_path / "out.json"
        with pytest.raises(CIWriteBlockedError, match="Refusing to write"):
            write_json_atomic(f, {"x": 1})

    def test_blocked_when_both_ci_vars_set(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        monkeypatch.delenv("ALLOW_BASELINE_WRITES_IN_CI", raising=False)
        f = tmp_path / "out.json"
        with pytest.raises(CIWriteBlockedError):
            write_json_atomic(f, {"x": 1})

    def test_allowed_when_override_set(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("ALLOW_BASELINE_WRITES_IN_CI", "1")
        f = tmp_path / "out.json"
        write_json_atomic(f, {"x": 1})
        assert f.is_file()

    def test_allowed_when_not_ci(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        monkeypatch.delenv("ALLOW_BASELINE_WRITES_IN_CI", raising=False)
        f = tmp_path / "out.json"
        write_json_atomic(f, {"x": 1})
        assert f.is_file()

    def test_no_file_created_on_block(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CI", "true")
        monkeypatch.delenv("ALLOW_BASELINE_WRITES_IN_CI", raising=False)
        f = tmp_path / "should_not_exist.json"
        with pytest.raises(CIWriteBlockedError):
            write_json_atomic(f, {"x": 1})
        assert not f.exists()
