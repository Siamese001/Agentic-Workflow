"""
Unit tests for ops_scripts/ci/check_notion_plans_no_duplicates.py.

Plan: notion-plans-status-rca-followups-b8e3f2 (W1.P2d).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_notion_plans_no_duplicates.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "check_notion_plans_no_duplicates", MODULE_PATH
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_notion_plans_no_duplicates"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


def _write_cache(tmp_path: Path, plans: dict) -> Path:
    cache = tmp_path / "plan_registration_cache.json"
    cache.write_text(json.dumps({
        "fetched_at": "2026-05-10T12:00:00Z",
        "fetched_at_epoch": 1.0,
        "plans": plans,
    }), encoding="utf-8")
    return cache


def test_load_cache_clean_returns_singletons(mod, tmp_path, monkeypatch):
    cache = _write_cache(tmp_path, {
        "plan-a-aaaaaa": {"page_id": "p1", "status": "Completed"},
        "plan-b-bbbbbb": {"page_id": "p2", "status": "In Progress"},
    })
    monkeypatch.setattr(mod, "CACHE_PATH", cache)
    snapshot = mod.load_cache_snapshot()
    assert snapshot is not None
    assert all(len(rows) == 1 for rows in snapshot.values())


def test_load_cache_missing_returns_none(mod, tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "CACHE_PATH", tmp_path / "absent.json")
    assert mod.load_cache_snapshot() is None


def test_load_cache_malformed_returns_none(mod, tmp_path, monkeypatch):
    cache = tmp_path / "bad.json"
    cache.write_text("not json", encoding="utf-8")
    monkeypatch.setattr(mod, "CACHE_PATH", cache)
    assert mod.load_cache_snapshot() is None


def test_main_clean_cache_exits_zero(mod, tmp_path, monkeypatch, capsys):
    cache = _write_cache(tmp_path, {
        "plan-a-aaaaaa": {"page_id": "p1", "status": "Completed"},
    })
    monkeypatch.setattr(mod, "CACHE_PATH", cache)
    rc = mod.main([])
    assert rc == 0
    assert "OK" in capsys.readouterr().out


def test_main_missing_cache_exits_two(mod, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(mod, "CACHE_PATH", tmp_path / "absent.json")
    rc = mod.main([])
    assert rc == 2
    err = capsys.readouterr().err
    assert "cache missing" in err


def test_main_bypass_env_passes(mod, monkeypatch, capsys):
    monkeypatch.setenv("NOTION_PLANS_DUP_BYPASS", "1")
    rc = mod.main([])
    assert rc == 0
    assert "BYPASS" in capsys.readouterr().out.upper()


def test_main_with_synthetic_duplicates_via_live_mock(mod, monkeypatch, capsys):
    """Force --live with mocked fetcher to verify duplicate-fail path."""
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    monkeypatch.setattr(
        mod, "fetch_live_plans",
        lambda token: {
            "twin-plan-aaaaaa": [
                {"id": "p1", "status": "In Progress"},
                {"id": "p2", "status": "Not Started"},
            ],
            "lonely-plan-bbbbbb": [{"id": "p3", "status": "Completed"}],
        },
    )
    rc = mod.main(["--live"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "twin-plan-aaaaaa" in out
    assert "p1" in out
    assert "p2" in out


def test_main_json_output(mod, monkeypatch, capsys):
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    monkeypatch.setattr(
        mod, "fetch_live_plans",
        lambda token: {"twin-aaaaaa": [{"id": "p1"}, {"id": "p2"}]},
    )
    rc = mod.main(["--live", "--json"])
    assert rc == 1
    captured = capsys.readouterr().out
    payload = json.loads(captured)
    assert payload["duplicate_count"] == 1
    assert payload["duplicates"][0]["slug"] == "twin-aaaaaa"


def test_main_live_no_token_exits_two(mod, monkeypatch, capsys):
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    rc = mod.main(["--live"])
    assert rc == 2
    assert "requires NOTION_TOKEN" in capsys.readouterr().err
