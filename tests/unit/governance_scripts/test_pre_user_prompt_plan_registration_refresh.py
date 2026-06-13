"""
Unit tests for .claude/governance/scripts/_legacy_windsurf/pre_user_prompt_plan_registration_refresh.py.

Plan: notion-plans-status-rca-followups-b8e3f2 (W2.P2).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
# Canonical path — pre_user_prompt_plan_registration_refresh.py lives in governance/scripts/
MODULE_PATH = (
    REPO_ROOT / ".claude" / "governance" / "scripts" / "pre_user_prompt_plan_registration_refresh.py"
)


def _load():
    # _plan_registration is imported by the module under test.
    sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance" / "scripts"))  # canonical
    spec = importlib.util.spec_from_file_location(
        "pre_user_prompt_plan_registration_refresh", MODULE_PATH
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pre_user_prompt_plan_registration_refresh"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture
def fresh_cache(tmp_path: Path) -> Path:
    """Return path to a cache file written 1 minute ago."""
    cache = tmp_path / "plan_registration_cache.json"
    cache.write_text(json.dumps({
        "fetched_at": "2026-05-10T12:00:00Z",
        "fetched_at_epoch": time.time() - 60,  # 1 min old
        "plans": {"plan-a-aaaaaa": {"page_id": "p1", "status": "Completed"}},
    }), encoding="utf-8")
    return cache


@pytest.fixture
def stale_cache(tmp_path: Path) -> Path:
    cache = tmp_path / "plan_registration_cache.json"
    cache.write_text(json.dumps({
        "fetched_at": "2026-05-09T00:00:00Z",
        "fetched_at_epoch": time.time() - 7200,  # 2h old > 1h TTL
        "plans": {"plan-a-aaaaaa": {"page_id": "p1", "status": "Completed"}},
    }), encoding="utf-8")
    return cache


# -------------------------------------------------------------------
# should_refresh decision matrix
# -------------------------------------------------------------------


def test_should_refresh_when_cache_stale(mod, stale_cache, monkeypatch):
    monkeypatch.setattr(mod, "CACHE_PATH", stale_cache)
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    decision, reason = mod.should_refresh()
    assert decision is True
    assert reason == "cache_stale"


def test_no_refresh_when_cache_fresh(mod, fresh_cache, monkeypatch):
    monkeypatch.setattr(mod, "CACHE_PATH", fresh_cache)
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    decision, reason = mod.should_refresh()
    assert decision is False
    assert reason == "cache_fresh"


def test_should_refresh_when_cache_missing(mod, tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "CACHE_PATH", tmp_path / "absent.json")
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    decision, reason = mod.should_refresh()
    assert decision is True
    assert reason == "cache_missing"


def test_no_refresh_when_no_token(mod, stale_cache, monkeypatch):
    monkeypatch.setattr(mod, "CACHE_PATH", stale_cache)
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    decision, reason = mod.should_refresh()
    assert decision is False
    assert reason == "no_notion_token"


def test_no_refresh_when_bypass_set(mod, stale_cache, monkeypatch):
    monkeypatch.setattr(mod, "CACHE_PATH", stale_cache)
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    monkeypatch.setenv("PLAN_CACHE_REFRESH_BYPASS", "1")
    decision, reason = mod.should_refresh()
    assert decision is False
    assert reason == "bypass_env_set"


# -------------------------------------------------------------------
# spawn_refresh — never blocks, fail-soft
# -------------------------------------------------------------------


def test_spawn_uses_detached_subprocess(mod, monkeypatch):
    """Verify spawn uses Popen with no wait + stdout/stderr suppressed."""
    captured = {}

    class FakePopen:
        def __init__(self, cmd, **kw):
            captured["cmd"] = cmd
            captured["kw"] = kw

    monkeypatch.setattr(mod.subprocess, "Popen", FakePopen)
    ok, msg = mod.spawn_refresh()
    assert ok is True
    assert msg == "spawned"
    assert "--refresh" in captured["cmd"]
    assert captured["kw"]["stdin"] == mod.subprocess.DEVNULL
    assert captured["kw"]["stdout"] == mod.subprocess.DEVNULL
    assert captured["kw"]["stderr"] == mod.subprocess.DEVNULL


def test_spawn_failure_is_soft(mod, monkeypatch):
    """OSError on spawn returns (False, msg) — never raises."""
    def boom(*_a, **_kw):
        raise OSError("simulated")
    monkeypatch.setattr(mod.subprocess, "Popen", boom)
    ok, msg = mod.spawn_refresh()
    assert ok is False
    assert "spawn_failed" in msg


def test_spawn_missing_script(mod, monkeypatch, tmp_path):
    monkeypatch.setattr(mod, "REFRESH_SCRIPT", tmp_path / "absent.py")
    ok, msg = mod.spawn_refresh()
    assert ok is False
    assert "missing" in msg


# -------------------------------------------------------------------
# main — never returns non-zero
# -------------------------------------------------------------------


def test_main_returns_zero_when_fresh(mod, fresh_cache, monkeypatch):
    monkeypatch.setattr(mod, "CACHE_PATH", fresh_cache)
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    with patch.object(mod, "spawn_refresh") as spawn:
        rc = mod.main()
    assert rc == 0
    spawn.assert_not_called()


def test_main_spawns_when_stale(mod, stale_cache, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(mod, "CACHE_PATH", stale_cache)
    monkeypatch.setattr(mod, "LOG_PATH", tmp_path / "refresh.jsonl")
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    with patch.object(mod, "spawn_refresh", return_value=(True, "spawned")):
        rc = mod.main()
    assert rc == 0
    err = capsys.readouterr().err
    assert "spawning background refresh" in err
    log = (tmp_path / "refresh.jsonl").read_text(encoding="utf-8")
    assert '"reason": "cache_stale"' in log


def test_main_returns_zero_even_when_spawn_fails(mod, stale_cache, tmp_path, monkeypatch):
    """Hook MUST never block prompt — even on spawn failure."""
    monkeypatch.setattr(mod, "CACHE_PATH", stale_cache)
    monkeypatch.setattr(mod, "LOG_PATH", tmp_path / "refresh.jsonl")
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    with patch.object(mod, "spawn_refresh", return_value=(False, "spawn_failed:boom")):
        rc = mod.main()
    assert rc == 0  # prompt never blocked


def test_main_no_token_no_spawn(mod, stale_cache, monkeypatch):
    monkeypatch.setattr(mod, "CACHE_PATH", stale_cache)
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    with patch.object(mod, "spawn_refresh") as spawn:
        rc = mod.main()
    assert rc == 0
    spawn.assert_not_called()


def test_cache_age_seconds_returns_none_when_missing(mod, tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "CACHE_PATH", tmp_path / "absent.json")
    assert mod.cache_age_seconds() is None


def test_cache_age_seconds_returns_positive_value(mod, fresh_cache, monkeypatch):
    monkeypatch.setattr(mod, "CACHE_PATH", fresh_cache)
    age = mod.cache_age_seconds()
    assert age is not None
    assert 0 <= age <= 120  # ~1 minute old, with slack
