"""Tests for post_cursor_agent_heartbeat + pre_user_prompt_hook_health_check (W7.1)."""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SCRIPTS = _REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf"


def _load(mod_name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(mod_name, _SCRIPTS / file_name)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def heartbeat_mod(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    mod = _load("post_cursor_agent_heartbeat_t", "post_cursor_agent_heartbeat.py")
    hb_path = tmp_path / "hb.jsonl"
    monkeypatch.setattr(mod, "_HEARTBEAT_PATH", hb_path)
    return mod, hb_path


@pytest.fixture
def health_mod(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    mod = _load("hook_health_check_t", "pre_user_prompt_hook_health_check.py")
    hb_path = tmp_path / "hb.jsonl"
    monkeypatch.setattr(mod, "_HEARTBEAT_PATH", hb_path)
    return mod, hb_path


# ---------------------------------------------------------------------------
# post_cursor_agent_heartbeat
# ---------------------------------------------------------------------------


def test_heartbeat_main_writes_record(heartbeat_mod) -> None:
    mod, hb_path = heartbeat_mod
    rc = mod.main()
    assert rc == 0
    assert hb_path.exists()
    lines = hb_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["hook"] == "post_cursor_agent_heartbeat"
    assert isinstance(record["timestamp_unix"], float)
    assert record["pid"] > 0


def test_heartbeat_appends_on_repeated_calls(heartbeat_mod) -> None:
    mod, hb_path = heartbeat_mod
    mod.main()
    mod.main()
    mod.main()
    lines = hb_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3


def test_heartbeat_truncates_to_max_lines(heartbeat_mod, monkeypatch: pytest.MonkeyPatch) -> None:
    mod, hb_path = heartbeat_mod
    monkeypatch.setattr(mod, "_MAX_LINES", 5)
    for _ in range(20):
        mod._append_and_truncate(hb_path, json.dumps({"x": 1}), max_lines=5)
    lines = hb_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 5


def test_heartbeat_disable_env_var(heartbeat_mod, monkeypatch: pytest.MonkeyPatch) -> None:
    mod, hb_path = heartbeat_mod
    monkeypatch.setenv("POST_CURSOR_AGENT_HEARTBEAT_DISABLE", "1")
    rc = mod.main()
    assert rc == 0
    assert not hb_path.exists()


# ---------------------------------------------------------------------------
# pre_user_prompt_hook_health_check
# ---------------------------------------------------------------------------


def test_health_reports_missing_when_no_file(health_mod) -> None:
    mod, hb_path = health_mod
    result = mod.check_heartbeat_health(path=hb_path)
    assert result["status"] == "missing"
    assert result["last_timestamp"] is None


def test_health_reports_ok_when_fresh(health_mod) -> None:
    mod, hb_path = health_mod
    now = 1_000_000.0
    hb_path.write_text(
        json.dumps({"timestamp_unix": now - 60.0, "hook": "post_cursor_agent_heartbeat"}) + "\n",
        encoding="utf-8",
    )
    result = mod.check_heartbeat_health(path=hb_path, now=now, stale_seconds=3600)
    assert result["status"] == "ok"
    assert result["age_seconds"] == pytest.approx(60.0)


def test_health_reports_stale_when_old(health_mod) -> None:
    mod, hb_path = health_mod
    now = 1_000_000.0
    hb_path.write_text(
        json.dumps({"timestamp_unix": now - 10_000.0, "hook": "post_cursor_agent_heartbeat"}) + "\n",
        encoding="utf-8",
    )
    result = mod.check_heartbeat_health(path=hb_path, now=now, stale_seconds=3600)
    assert result["status"] == "stale"
    assert result["age_seconds"] > 3600


def test_health_handles_empty_file(health_mod) -> None:
    mod, hb_path = health_mod
    hb_path.write_text("", encoding="utf-8")
    result = mod.check_heartbeat_health(path=hb_path)
    assert result["status"] == "missing"


def test_health_handles_malformed_last_line(health_mod) -> None:
    mod, hb_path = health_mod
    hb_path.write_text("{not-json\n", encoding="utf-8")
    result = mod.check_heartbeat_health(path=hb_path)
    assert result["status"] == "missing"


def test_health_uses_latest_line_when_multiple(health_mod) -> None:
    mod, hb_path = health_mod
    now = 1_000_000.0
    lines = [
        json.dumps({"timestamp_unix": now - 99_999.0}),
        json.dumps({"timestamp_unix": now - 100.0}),
    ]
    hb_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = mod.check_heartbeat_health(path=hb_path, now=now, stale_seconds=3600)
    assert result["status"] == "ok"


def test_health_main_returns_zero_regardless(
    health_mod, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    mod, _ = health_mod
    # File absent -> should emit banner but return 0 (fail-soft).
    rc = mod.main()
    assert rc == 0
    err = capsys.readouterr().err
    assert "HOOK-CHAIN HEALTH CHECK" in err


def test_health_disable_env_var_silences(
    health_mod, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    mod, _ = health_mod
    monkeypatch.setenv("POST_CURSOR_AGENT_HEARTBEAT_HEALTH_DISABLE", "1")
    rc = mod.main()
    assert rc == 0
    err = capsys.readouterr().err
    assert "HOOK-CHAIN HEALTH CHECK" not in err


def test_default_threshold_is_thirty_minutes(health_mod) -> None:
    """W10.1 (RCA 2026-04-23): default stale threshold MUST be 30 minutes.

    Guards against regression to the pre-RCA 6h default that hid the
    1h34m HOOK_OUTAGE silence window. Env override still permitted.
    """
    mod, _ = health_mod
    assert mod._DEFAULT_STALE_SECONDS == 30 * 60


def test_health_flags_stale_after_thirty_minutes(health_mod) -> None:
    """W10.1: a 31-minute-old heartbeat MUST be classified ``stale``
    under the default threshold, matching the tightened window."""
    mod, hb_path = health_mod
    now = 1_000_000.0
    # 31 minutes (1860s) — just past the new default (1800s).
    hb_path.write_text(
        json.dumps({"timestamp_unix": now - 1860.0, "hook": "post_cursor_agent_heartbeat"}) + "\n",
        encoding="utf-8",
    )
    result = mod.check_heartbeat_health(path=hb_path, now=now)
    assert result["status"] == "stale"
    assert result["threshold"] == 30 * 60


def test_health_env_override_still_honored(health_mod, monkeypatch: pytest.MonkeyPatch) -> None:
    """W10.1: POST_CURSOR_AGENT_HEARTBEAT_STALE_SECONDS env override still works
    after the default tightening, so operators can relax the threshold
    when justified (e.g. long-running batch sessions)."""
    mod, hb_path = health_mod
    monkeypatch.setenv("POST_CURSOR_AGENT_HEARTBEAT_STALE_SECONDS", "7200")  # 2h
    now = 1_000_000.0
    hb_path.write_text(
        json.dumps({"timestamp_unix": now - 3600.0, "hook": "post_cursor_agent_heartbeat"}) + "\n",
        encoding="utf-8",
    )
    # Age 1h is >30min default but <2h override → ok.
    result = mod.check_heartbeat_health(path=hb_path, now=now)
    assert result["status"] == "ok"
    assert result["threshold"] == 7200


def test_health_writer_reader_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hb_path = tmp_path / "hb.jsonl"
    writer = _load("hb_writer_rt", "post_cursor_agent_heartbeat.py")
    reader = _load("hb_reader_rt", "pre_user_prompt_hook_health_check.py")
    monkeypatch.setattr(writer, "_HEARTBEAT_PATH", hb_path)
    monkeypatch.setattr(reader, "_HEARTBEAT_PATH", hb_path)

    writer.main()
    result = reader.check_heartbeat_health(path=hb_path, now=time.time(), stale_seconds=3600)
    assert result["status"] == "ok"
