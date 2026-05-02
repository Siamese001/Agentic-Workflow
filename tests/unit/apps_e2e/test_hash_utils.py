"""Unit tests for tools.certification.apps_e2e.hash_utils."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tools.certification.apps_e2e import hash_utils as h


def test_utc_now_iso_ends_with_z() -> None:
    s = h.utc_now_iso()
    assert s.endswith("Z")
    assert "T" in s


def test_sha256_bytes_known_vector() -> None:
    # SHA256("") == e3b0c4...
    assert h.sha256_bytes(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_sha256_file_returns_none_for_missing(tmp_path: Path) -> None:
    assert h.sha256_file(tmp_path / "does_not_exist.json") is None


def test_sha256_file_matches_bytes(tmp_path: Path) -> None:
    p = tmp_path / "x.json"
    p.write_bytes(b"hello world")
    assert h.sha256_file(p) == h.sha256_bytes(b"hello world")


def test_write_json_is_deterministic(tmp_path: Path) -> None:
    payload = {"b": 2, "a": 1}
    p1 = tmp_path / "1.json"
    p2 = tmp_path / "2.json"
    s1, n1 = h.write_json(p1, payload)
    s2, n2 = h.write_json(p2, payload)
    assert s1 == s2
    assert n1 == n2
    # And it's sort_keys=True so 'a' precedes 'b' in the file
    txt = p1.read_text(encoding="utf-8")
    assert txt.index('"a"') < txt.index('"b"')


def test_relative_to_repo_normalizes_separators(tmp_path: Path) -> None:
    rel = h.relative_to_repo(h.REPO_ROOT / "artifacts" / "x.txt")
    assert rel == "artifacts/x.txt"


def test_detect_mock_or_fixture_mode_picks_up_app_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_MOCK", "1")
    monkeypatch.delenv("NARRATIVE_MOCK", raising=False)
    mock, fixture = h.detect_mock_or_fixture_mode("apps_rg")
    assert mock is True
    assert fixture is False


def test_detect_mock_or_fixture_mode_isolates_apps(monkeypatch: pytest.MonkeyPatch) -> None:
    """apps_rg flag does not leak into apps_qna detection."""
    monkeypatch.setenv("APPS_RG_MOCK", "1")
    monkeypatch.delenv("NARRATIVE_MOCK", raising=False)
    mock, _ = h.detect_mock_or_fixture_mode("apps_qna")
    assert mock is False
