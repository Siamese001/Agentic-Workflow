"""Tests for F5.1 heartbeat-authoritative liveness check.

Scope: exercise `tools.mcp.mcp_heartbeat.is_heartbeat_authoritative` against
fresh/stale files, live/zombie PIDs, and psutil-missing fallback.

These tests use real files written to a tmp path but stub psutil via a
local class injected into `sys.modules` so no real OS-level kill paths run.
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path
from typing import Any

import pytest

import tools.mcp.mcp_heartbeat as hb


class _FakePsutil:
    """Minimal psutil stand-in covering the attrs F5.1 uses."""

    class NoSuchProcess(Exception):
        pass

    class AccessDenied(Exception):
        pass

    class ZombieProcess(Exception):
        pass

    STATUS_ZOMBIE = "zombie"
    STATUS_STOPPED = "stopped"
    STATUS_DEAD = "dead"
    STATUS_RUNNING = "running"

    def __init__(self, live_pids: dict[int, str]) -> None:
        """live_pids: {pid: status_string}."""
        self._live = dict(live_pids)

    def Process(self, pid: int) -> Any:  # noqa: N802
        if pid not in self._live:
            raise _FakePsutil.NoSuchProcess(pid)
        status = self._live[pid]

        captured_status = status

        class _Proc:
            def is_running(self) -> bool:
                return captured_status != "dead"

            def status(self) -> str:
                return captured_status

        return _Proc()


@pytest.fixture
def isolated_hb_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tmp_path / "mcp_heartbeat"
    monkeypatch.setattr(hb, "_HEARTBEAT_DIR", d)
    return d


@pytest.fixture
def fake_psutil(monkeypatch: pytest.MonkeyPatch):
    def _install(live_pids: dict[int, str]) -> _FakePsutil:
        fake = _FakePsutil(live_pids)
        monkeypatch.setitem(sys.modules, "psutil", fake)
        return fake

    return _install


def _write_hb(dir_path: Path, marker: str, ts: float, pid: int) -> None:
    dir_path.mkdir(parents=True, exist_ok=True)
    logging.info("C3 write receipt: tests/tools/mcp/test_heartbeat_authority.py write side effect recorded")
    path = dir_path / f"{hb._sanitize_marker(marker)}.hb"
    path.write_text(f"{ts:.3f}:{pid}\n", encoding="utf-8")


def test_authoritative_returns_false_when_heartbeat_missing(isolated_hb_dir, fake_psutil):
    fake_psutil({})
    assert hb.is_heartbeat_authoritative("marker-x") is False


def test_authoritative_returns_false_when_heartbeat_stale(isolated_hb_dir, fake_psutil):
    old = time.time() - (hb.HEARTBEAT_STALE_AFTER_SECONDS + 10.0)
    _write_hb(isolated_hb_dir, "marker-x", old, pid=123)
    fake_psutil({123: "running"})  # PID is alive but heartbeat is stale.
    assert hb.is_heartbeat_authoritative("marker-x") is False


def test_authoritative_true_when_fresh_and_running(isolated_hb_dir, fake_psutil):
    _write_hb(isolated_hb_dir, "marker-x", time.time(), pid=123)
    fake_psutil({123: "running"})
    assert hb.is_heartbeat_authoritative("marker-x") is True


def test_authoritative_false_when_fresh_but_zombie(isolated_hb_dir, fake_psutil):
    _write_hb(isolated_hb_dir, "marker-x", time.time(), pid=123)
    fake_psutil({123: "zombie"})
    assert hb.is_heartbeat_authoritative("marker-x") is False


def test_authoritative_false_when_fresh_but_stopped(isolated_hb_dir, fake_psutil):
    _write_hb(isolated_hb_dir, "marker-x", time.time(), pid=123)
    fake_psutil({123: "stopped"})
    assert hb.is_heartbeat_authoritative("marker-x") is False


def test_authoritative_false_when_pid_gone(isolated_hb_dir, fake_psutil):
    _write_hb(isolated_hb_dir, "marker-x", time.time(), pid=999)
    fake_psutil({})  # PID 999 does not exist → NoSuchProcess.
    assert hb.is_heartbeat_authoritative("marker-x") is False


def test_authoritative_falls_back_when_psutil_missing(isolated_hb_dir, monkeypatch):
    _write_hb(isolated_hb_dir, "marker-x", time.time(), pid=123)
    monkeypatch.setitem(sys.modules, "psutil", None)  # ImportError on import.
    # Without psutil we degrade to fresh-only semantics (no regression from
    # pre-F5.1 behavior).
    assert hb.is_heartbeat_authoritative("marker-x") is True


def test_is_heartbeat_fresh_still_works_after_hardening(isolated_hb_dir):
    _write_hb(isolated_hb_dir, "marker-x", time.time(), pid=123)
    assert hb.is_heartbeat_fresh("marker-x") is True
    old = time.time() - (hb.HEARTBEAT_STALE_AFTER_SECONDS + 1.0)
    _write_hb(isolated_hb_dir, "marker-y", old, pid=456)
    assert hb.is_heartbeat_fresh("marker-y") is False
