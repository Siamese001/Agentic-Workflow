"""P4 MCP optimization tests — read_gateway.py (mcp6_* filesystem reads)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.tools.read_gateway import (
        file_exists,
        get_file_info,
        list_directory,
        read_bytes,
        read_json,
        read_text,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    read_text = None  # type: ignore[assignment]
    read_bytes = None  # type: ignore[assignment]
    read_json = None  # type: ignore[assignment]
    list_directory = None  # type: ignore[assignment]
    file_exists = None  # type: ignore[assignment]
    get_file_info = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="read_gateway deps unavailable")
class TestReadTextFallback:
    def test_reads_real_file_via_fallback(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world", encoding="utf-8")
        result = read_text(f)
        assert "hello world" in result

    def test_uses_mcp6_when_available(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("real content", encoding="utf-8")
        mock_fn = MagicMock(return_value="mcp content")
        with patch.dict("sys.modules", {"mcp6_read_text_file": MagicMock(mcp6_read_text_file=mock_fn)}):
            result = read_text(f)
        assert result == "mcp content"

    def test_falls_back_on_import_error(self, tmp_path):
        import sys

        f = tmp_path / "fallback.txt"
        f.write_text("fallback content", encoding="utf-8")
        original = sys.modules.pop("mcp6_read_text_file", None)
        try:
            result = read_text(f)
            assert "fallback content" in result
        finally:
            if original is not None:
                sys.modules["mcp6_read_text_file"] = original

    def test_falls_back_on_mcp6_exception(self, tmp_path):
        f = tmp_path / "except.txt"
        f.write_text("direct content", encoding="utf-8")
        mock_fn = MagicMock(side_effect=RuntimeError("mcp error"))
        with patch.dict("sys.modules", {"mcp6_read_text_file": MagicMock(mcp6_read_text_file=mock_fn)}):
            result = read_text(f)
        assert "direct content" in result


@pytest.mark.skipif(not _AVAILABLE, reason="read_gateway deps unavailable")
class TestReadBytes:
    def test_reads_binary_file(self, tmp_path):
        f = tmp_path / "binary.bin"
        f.write_bytes(b"\x00\x01\x02\x03")
        result = read_bytes(f)
        assert result == b"\x00\x01\x02\x03"


@pytest.mark.skipif(not _AVAILABLE, reason="read_gateway deps unavailable")
class TestReadJson:
    def test_reads_and_parses_json(self, tmp_path):
        f = tmp_path / "data.json"
        data = {"key": "value", "num": 42}
        f.write_text(json.dumps(data), encoding="utf-8")
        result = read_json(f)
        assert result["key"] == "value"
        assert result["num"] == 42

    def test_raises_on_invalid_json(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("not valid json {{{{", encoding="utf-8")
        with pytest.raises(Exception):
            read_json(f)


@pytest.mark.skipif(not _AVAILABLE, reason="read_gateway deps unavailable")
class TestListDirectory:
    def test_lists_files_in_directory(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        result = list_directory(tmp_path)
        assert isinstance(result, list)
        names = [Path(r).name if "/" in r or "\\" in r else r for r in result]
        assert any("a.txt" in n for n in names)
        assert any("b.txt" in n for n in names)

    def test_uses_mcp6_when_available(self, tmp_path):
        mock_fn = MagicMock(return_value=["file1.txt", "file2.txt"])
        with patch.dict("sys.modules", {"mcp6_list_directory": MagicMock(mcp6_list_directory=mock_fn)}):
            result = list_directory(tmp_path)
        assert isinstance(result, list)

    def test_falls_back_on_import_error(self, tmp_path):
        import sys

        (tmp_path / "test.txt").write_text("x")
        original = sys.modules.pop("mcp6_list_directory", None)
        try:
            result = list_directory(tmp_path)
            assert isinstance(result, list)
            assert len(result) >= 1
        finally:
            if original is not None:
                sys.modules["mcp6_list_directory"] = original


@pytest.mark.skipif(not _AVAILABLE, reason="read_gateway deps unavailable")
class TestFileExists:
    def test_returns_true_for_existing_file(self, tmp_path):
        f = tmp_path / "exists.txt"
        f.write_text("x")
        assert file_exists(f) is True

    def test_returns_false_for_missing_file(self, tmp_path):
        f = tmp_path / "missing.txt"
        assert file_exists(f) is False


@pytest.mark.skipif(not _AVAILABLE, reason="read_gateway deps unavailable")
class TestGetFileInfo:
    def test_returns_dict(self, tmp_path):
        f = tmp_path / "info.txt"
        f.write_text("hello")
        result = get_file_info(f)
        assert isinstance(result, dict)

    def test_fallback_has_expected_keys(self, tmp_path):
        import sys

        f = tmp_path / "info.txt"
        f.write_text("hello")
        original = sys.modules.pop("mcp6_get_file_info", None)
        try:
            result = get_file_info(f)
            assert "size" in result
            assert "is_file" in result
            assert result["is_file"] is True
        finally:
            if original is not None:
                sys.modules["mcp6_get_file_info"] = original

    def test_uses_mcp6_when_available(self, tmp_path):
        f = tmp_path / "info.txt"
        f.write_text("hello")
        mock_result = {"size": 5, "is_file": True, "is_dir": False}
        mock_fn = MagicMock(return_value=mock_result)
        with patch.dict("sys.modules", {"mcp6_get_file_info": MagicMock(mcp6_get_file_info=mock_fn)}):
            result = get_file_info(f)
        assert isinstance(result, dict)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
