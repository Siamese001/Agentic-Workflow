"""
conftest.py — defense-in-depth test isolation for tools/notion/* tests.

Two autouse fixtures:

1. ``_isolate_notion_env`` — strips ``NOTION_TOKEN`` / ``NOTION_API_KEY`` from
   the test environment by default. Tests that need a token MUST set it
   explicitly via ``monkeypatch.setenv``. This prevents accidental real
   Notion API calls when CI / dev shells happen to have a token set.

2. ``_redirect_writer_log_path`` — points
   ``tools.notion.wave_lifecycle_writer.LOG_PATH`` at a per-test tmp file
   so unit-test exercises of ``apply_spec`` etc. don't pollute the
   production audit log at ``artifacts/windsurf/wave_lifecycle_notion.jsonl``.

RCA NOTION_PLANS_STATUS_RCA_2026-05-10 §6 (test pollution finding).
Plan: notion-plans-status-rca-followups-b8e3f2 (W3.P1).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(autouse=True)
def _isolate_notion_env(monkeypatch):
    """Strip Notion auth env vars unless a test opts back in."""
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    yield


@pytest.fixture(autouse=True)
def _redirect_writer_log_path(tmp_path, monkeypatch):
    """Redirect wave_lifecycle_writer.LOG_PATH and the new
    _plan_registration_helpers.LOG_PATH at a per-test tmp file.
    """
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from tools.notion import wave_lifecycle_writer as wlw  # noqa: WPS433
        monkeypatch.setattr(wlw, "LOG_PATH", tmp_path / "wave_lifecycle_notion.jsonl")
    except ImportError:
        pass
    try:
        from tools.notion import _plan_registration_helpers as prh  # noqa: WPS433
        monkeypatch.setattr(prh, "LOG_PATH", tmp_path / "plans_db_writes.jsonl")
    except ImportError:
        pass
    yield
