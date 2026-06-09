"""Tests for guard_single_instance() multi-marker support.

Covers the 2026-04-23 bugfix where the adg_sqlite marker
``"tools/adg/mcp/server"`` never matched the actual invocation
``python -u -m tools.adg.mcp.server`` (dot-separated), letting stale
siblings survive window reloads.
"""

from __future__ import annotations

import os
from unittest import mock

import pytest

from tools.mcp import mcp_bootstrap as mod


@pytest.fixture(autouse=True)
def _force_guard_kill_path(monkeypatch: pytest.MonkeyPatch):
    """Keep tests focused on matching semantics, not live heartbeat state."""
    monkeypatch.setenv("MCP_GUARD_FORCE_KILL", "1")
    monkeypatch.setenv("MCP_HEARTBEAT_DISABLE", "1")


class _FakeProc:
    def __init__(self, pid: int, cmdline: list[str], name: str = "python.exe") -> None:
        self.info = {"pid": pid, "name": name, "cmdline": cmdline}
        self.pid = pid
        self.terminated = False
        self.killed = False

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        self.killed = True

    def wait(self, timeout: float = 0.0) -> None:  # noqa: ARG002
        return None


def _install_fake_psutil(monkeypatch: pytest.MonkeyPatch, procs: list[_FakeProc]):
    fake = mock.MagicMock()
    fake.process_iter = mock.MagicMock(return_value=procs)
    fake.Process = mock.MagicMock()
    fake.Process.return_value.parents.return_value = []

    class _Exc(Exception):
        pass

    fake.NoSuchProcess = _Exc
    fake.AccessDenied = _Exc
    fake.ZombieProcess = _Exc
    fake.TimeoutExpired = _Exc
    monkeypatch.setitem(__import__("sys").modules, "psutil", fake)
    return fake


# ---- single-marker backward compatibility --------------------------------


def test_single_str_marker_matches(monkeypatch: pytest.MonkeyPatch) -> None:
    target = _FakeProc(42, ["python", "-u", "C:/x/tools/mcp/vector_db_server.py"])
    other = _FakeProc(43, ["python", "-m", "unrelated"])
    _install_fake_psutil(monkeypatch, [target, other])
    monkeypatch.setattr(os, "getpid", lambda: 1)
    mod.guard_single_instance("vector_db_server.py")
    assert target.terminated
    assert not other.terminated


def test_single_str_marker_no_match(monkeypatch: pytest.MonkeyPatch) -> None:
    p = _FakeProc(42, ["python", "-u", "-m", "tools.adg.mcp.server"])
    _install_fake_psutil(monkeypatch, [p])
    monkeypatch.setattr(os, "getpid", lambda: 1)
    # Original (buggy) slash-separated marker against dot invocation
    mod.guard_single_instance("tools/adg/mcp/server")
    assert not p.terminated


# ---- multi-marker (the fix) ----------------------------------------------


def test_tuple_markers_match_dot_form(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p = _FakeProc(42, ["python", "-u", "-m", "tools.adg.mcp.server"])
    _install_fake_psutil(monkeypatch, [p])
    monkeypatch.setattr(os, "getpid", lambda: 1)
    mod.guard_single_instance(
        ("tools.adg.mcp.server", "tools/adg/mcp/server"),
    )
    assert p.terminated


def test_tuple_markers_match_slash_form(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p = _FakeProc(42, ["python", "-u", "C:/x/tools/adg/mcp/server.py"])
    _install_fake_psutil(monkeypatch, [p])
    monkeypatch.setattr(os, "getpid", lambda: 1)
    mod.guard_single_instance(
        ("tools.adg.mcp.server", "tools/adg/mcp/server"),
    )
    assert p.terminated


def test_marker_inside_parent_shell_text_is_not_killed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parent = _FakeProc(
        41,
        [
            "pwsh.exe",
            "-Command",
            "probe text mentions python -m tools.adg.mcp.server",
        ],
        name="pwsh.exe",
    )
    sibling = _FakeProc(42, ["python.exe", "-u", "-m", "tools.adg.mcp.server"])
    _install_fake_psutil(monkeypatch, [parent, sibling])
    monkeypatch.setattr(os, "getpid", lambda: 1)
    mod.guard_single_instance(
        ("tools.adg.mcp.server", "tools/adg/mcp/server"),
    )
    assert not parent.terminated
    assert sibling.terminated


def test_marker_inside_python_ancestor_text_is_not_killed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parent = _FakeProc(
        41,
        [
            "python.exe",
            "-c",
            "subprocess.run([sys.executable, '-m', 'tools.adg.mcp.server'])",
        ],
    )
    sibling = _FakeProc(42, ["python.exe", "-u", "-m", "tools.adg.mcp.server"])
    fake_psutil = _install_fake_psutil(monkeypatch, [parent, sibling])
    fake_psutil.Process.return_value.parents.return_value = [parent]
    monkeypatch.setattr(os, "getpid", lambda: 1)
    mod.guard_single_instance(
        ("tools.adg.mcp.server", "tools/adg/mcp/server"),
    )
    assert not parent.terminated
    assert sibling.terminated


def test_list_markers_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sequence type is tolerant of list as well as tuple."""
    p = _FakeProc(42, ["python", "-m", "tools.adg.mcp.server"])
    _install_fake_psutil(monkeypatch, [p])
    monkeypatch.setattr(os, "getpid", lambda: 1)
    mod.guard_single_instance(
        ["tools.adg.mcp.server", "tools/adg/mcp/server"],
    )
    assert p.terminated


def test_empty_markers_noop(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    p = _FakeProc(42, ["python", "tools/mcp/vector_db_server.py"])
    _install_fake_psutil(monkeypatch, [p])
    monkeypatch.setattr(os, "getpid", lambda: 1)
    with caplog.at_level("WARNING"):
        mod.guard_single_instance(())
    assert not p.terminated
    assert any("GUARD_NOOP" in r.message for r in caplog.records)


def test_markers_filter_empty_strings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p = _FakeProc(42, ["python", "tools.adg.mcp.server"])
    _install_fake_psutil(monkeypatch, [p])
    monkeypatch.setattr(os, "getpid", lambda: 1)
    mod.guard_single_instance(("", "tools.adg.mcp.server", ""))
    assert p.terminated


def test_skip_env_respected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p = _FakeProc(42, ["python", "tools.adg.mcp.server"])
    _install_fake_psutil(monkeypatch, [p])
    monkeypatch.setattr(os, "getpid", lambda: 1)
    monkeypatch.setenv("ADG_SKIP_ZOMBIE_KILL", "1")
    mod.guard_single_instance(
        ("tools.adg.mcp.server", "tools/adg/mcp/server"),
        skip_env="ADG_SKIP_ZOMBIE_KILL",
    )
    assert not p.terminated


def test_own_pid_never_killed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    me = _FakeProc(777, ["python", "tools.adg.mcp.server"])
    sibling = _FakeProc(999, ["python", "tools.adg.mcp.server"])
    _install_fake_psutil(monkeypatch, [me, sibling])
    monkeypatch.setattr(os, "getpid", lambda: 777)
    mod.guard_single_instance("tools.adg.mcp.server")
    assert not me.terminated
    assert sibling.terminated


def test_psutil_missing_returns_silently(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    import sys as _sys

    monkeypatch.delitem(_sys.modules, "psutil", raising=False)

    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def _raising(name, *a, **kw):
        if name == "psutil":
            raise ImportError("simulated")
        return real_import(name, *a, **kw)

    with mock.patch("builtins.__import__", side_effect=_raising):
        with caplog.at_level("WARNING"):
            mod.guard_single_instance("vector_db_server.py")
    assert any("GUARD_UNAVAILABLE" in r.message for r in caplog.records)
