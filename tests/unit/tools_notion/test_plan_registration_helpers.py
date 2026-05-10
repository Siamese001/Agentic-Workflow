"""
Unit tests for tools/notion/_plan_registration_helpers.py.

Covers all decision branches of register_plan_idempotent:
- 0 active rows -> created
- 1 active row -> existed (no write)
- 2+ active rows -> duplicate_blocked (no write)
- no token -> no_token
- transport failure -> api_error
- archived rows do NOT count as active

Plan: notion-plans-status-rca-followups-b8e3f2 (W1.P2a)
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "tools" / "notion" / "_plan_registration_helpers.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "_plan_registration_helpers", MODULE_PATH
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_plan_registration_helpers"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load_module()


@pytest.fixture
def fake_props():
    return {
        "Slug": {"title": [{"text": {"content": "test-plan-aaaaaa"}}]},
        "Status": {"select": {"name": "Not Started"}},
    }


# -------------------------------------------------------------------
# find_active_plan_pages
# -------------------------------------------------------------------


def test_find_active_excludes_archived(mod):
    fake_payload = {
        "results": [
            {"id": "page-1", "in_trash": False},
            {"id": "page-2", "in_trash": True},
            {"id": "page-3", "archived": True},
            {"id": "page-4"},
        ]
    }
    with patch.object(mod, "_post_json", return_value=fake_payload):
        result = mod.find_active_plan_pages("test-plan-aaaaaa", "fake-token")
    ids = [p["id"] for p in result]
    assert ids == ["page-1", "page-4"]


def test_find_active_empty_slug_short_circuits(mod):
    with patch.object(mod, "_post_json") as mock:
        result = mod.find_active_plan_pages("", "fake-token")
    assert result == []
    mock.assert_not_called()


def test_find_active_propagates_api_error(mod):
    with patch.object(mod, "_post_json", side_effect=mod.NotionAPIError("net:boom")):
        with pytest.raises(mod.NotionAPIError):
            mod.find_active_plan_pages("test-plan-aaaaaa", "fake-token")


# -------------------------------------------------------------------
# register_plan_idempotent — happy paths
# -------------------------------------------------------------------


def test_register_creates_when_no_existing(mod, fake_props):
    """0 active rows -> POST a new row."""
    with patch.object(mod, "find_active_plan_pages", return_value=[]):
        with patch.object(
            mod, "_post_json", return_value={"id": "new-page-id"}
        ) as post_mock:
            result = mod.register_plan_idempotent(
                "test-plan-aaaaaa", fake_props, token="fake-token",
            )
    assert result.action == "created"
    assert result.page_id == "new-page-id"
    post_mock.assert_called_once()  # POST happened


def test_register_skips_when_one_existing(mod, fake_props):
    """1 active row -> no write, return existing page_id."""
    with patch.object(
        mod, "find_active_plan_pages",
        return_value=[{"id": "existing-page-id", "in_trash": False}],
    ):
        with patch.object(mod, "_post_json") as post_mock:
            result = mod.register_plan_idempotent(
                "test-plan-aaaaaa", fake_props, token="fake-token",
            )
    assert result.action == "existed"
    assert result.page_id == "existing-page-id"
    post_mock.assert_not_called()


def test_register_blocks_when_duplicates(mod, fake_props):
    """RCA Cause B regression: 2+ active rows -> duplicate_blocked, no write."""
    with patch.object(
        mod, "find_active_plan_pages",
        return_value=[
            {"id": "page-1", "in_trash": False},
            {"id": "page-2", "in_trash": False},
        ],
    ):
        with patch.object(mod, "_post_json") as post_mock:
            result = mod.register_plan_idempotent(
                "test-plan-aaaaaa", fake_props, token="fake-token",
            )
    assert result.action == "duplicate_blocked"
    assert result.page_id == ""
    assert result.duplicates == ("page-1", "page-2")
    assert "refusing to create" in result.detail
    post_mock.assert_not_called()


def test_register_dry_run_never_writes(mod, fake_props):
    with patch.object(mod, "find_active_plan_pages", return_value=[]):
        with patch.object(mod, "_post_json") as post_mock:
            result = mod.register_plan_idempotent(
                "test-plan-aaaaaa", fake_props, token="fake-token", dry_run=True,
            )
    assert result.action == "dry_run"
    assert result.page_id == ""
    post_mock.assert_not_called()


# -------------------------------------------------------------------
# register_plan_idempotent — failure modes
# -------------------------------------------------------------------


def test_register_no_token(mod, fake_props, monkeypatch):
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    result = mod.register_plan_idempotent("test-plan-aaaaaa", fake_props)
    assert result.action == "no_token"
    assert result.page_id == ""


def test_register_api_error_on_query(mod, fake_props):
    with patch.object(
        mod, "find_active_plan_pages",
        side_effect=mod.NotionAPIError("net:timeout"),
    ):
        result = mod.register_plan_idempotent(
            "test-plan-aaaaaa", fake_props, token="fake-token",
        )
    assert result.action == "api_error"
    assert "net:timeout" in result.detail


def test_register_api_error_on_post(mod, fake_props):
    with patch.object(mod, "find_active_plan_pages", return_value=[]):
        with patch.object(
            mod, "_post_json", side_effect=mod.NotionAPIError("http_500:internal"),
        ):
            result = mod.register_plan_idempotent(
                "test-plan-aaaaaa", fake_props, token="fake-token",
            )
    assert result.action == "api_error"
    assert "http_500" in result.detail


# -------------------------------------------------------------------
# Telemetry — every operation logs to plans_db_writes.jsonl
# -------------------------------------------------------------------


def test_register_logs_created(mod, fake_props, tmp_path, monkeypatch):
    log_path = tmp_path / "plans_db_writes.jsonl"
    monkeypatch.setattr(mod, "LOG_PATH", log_path)
    with patch.object(mod, "find_active_plan_pages", return_value=[]):
        with patch.object(mod, "_post_json", return_value={"id": "p1"}):
            mod.register_plan_idempotent(
                "test-plan-aaaaaa", fake_props,
                token="fake-token", writer="my_caller.py",
            )
    contents = log_path.read_text(encoding="utf-8")
    assert '"event": "register_created"' in contents
    assert '"writer": "my_caller.py"' in contents
    assert '"slug": "test-plan-aaaaaa"' in contents


def test_register_logs_duplicate_blocked(mod, fake_props, tmp_path, monkeypatch):
    log_path = tmp_path / "plans_db_writes.jsonl"
    monkeypatch.setattr(mod, "LOG_PATH", log_path)
    with patch.object(
        mod, "find_active_plan_pages",
        return_value=[{"id": "p1"}, {"id": "p2"}],
    ):
        mod.register_plan_idempotent(
            "test-plan-aaaaaa", fake_props,
            token="fake-token", writer="my_caller.py",
        )
    contents = log_path.read_text(encoding="utf-8")
    assert '"event": "register_duplicate_blocked"' in contents
    assert '"page_ids": ["p1", "p2"]' in contents
