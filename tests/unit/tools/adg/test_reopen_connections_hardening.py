"""Tests for ``ADGServerRuntime.reopen_connections`` hardening.

Covers plan ``adg-mcp-reopen-hardening``:

* W2.2 F4 — idempotency short-circuit when snapshot+mtime unchanged.
* W1.2 F2 — bounded timeout wrapper surfaces ``status=error`` on stall
  instead of blocking the caller.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tools.adg.mcp.runtime import ADGServerRuntime


class _FakeSqliteBackend:
    """Stand-in that mimics the ``_sqlite_path`` / ``_last_mtime`` attrs."""

    def __init__(self, path: Path, mtime: float) -> None:
        self._sqlite_path = path
        self._last_mtime = mtime


def _make_runtime_with_service(
    monkeypatch: pytest.MonkeyPatch,
    sqlite_path: Path,
    mtime: float,
    reopen_sleep_s: float = 0.0,
) -> tuple[ADGServerRuntime, MagicMock]:
    """Build a runtime with a stubbed service that records reopen() calls."""
    runtime = ADGServerRuntime()
    service = MagicMock()
    service._sqlite = _FakeSqliteBackend(sqlite_path, mtime)

    def fake_reopen() -> None:
        if reopen_sleep_s:
            time.sleep(reopen_sleep_s)

    service.reopen.side_effect = fake_reopen
    runtime._service = service
    runtime._health = None
    # latest_sqlite() must resolve to the same file + mtime for the noop path.
    monkeypatch.setattr(
        "tools.adg.shared_modules.path_resolver.latest_sqlite",
        lambda: sqlite_path,
    )
    return runtime, service


def test_reopen_noop_when_snapshot_unchanged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """W2.2 F4: same path + mtime → skip service.reopen() entirely."""
    snap = tmp_path / "adg_indexed_20260424_0000.sqlite"
    snap.write_bytes(b"stub")
    logging.info("C3 write receipt: tests/unit/tools/adg/test_reopen_connections_hardening.py write side effect recorded")
    mtime = snap.stat().st_mtime

    runtime, service = _make_runtime_with_service(monkeypatch, snap, mtime)

    result = runtime.reopen_connections()

    assert result["status"] == "ok"
    assert result["data"]["reopened"] is True
    assert result["data"]["noop"] is True
    assert result["data"]["sqlite_path"] == str(snap)
    service.reopen.assert_not_called()


def test_reopen_runs_when_mtime_changes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """W2.2 F4: mtime drift → real reopen (not noop)."""
    snap = tmp_path / "adg_indexed_20260424_0001.sqlite"
    snap.write_bytes(b"stub")
    stale_mtime = snap.stat().st_mtime - 10.0  # pretend backend remembers older mtime

    runtime, service = _make_runtime_with_service(monkeypatch, snap, stale_mtime)

    result = runtime.reopen_connections()

    assert result["status"] == "ok"
    assert result["data"]["reopened"] is True
    assert result["data"]["noop"] is False
    service.reopen.assert_called_once()


def test_reopen_timeout_returns_structured_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """W1.2 F2: slow reopen is bounded by timeout_s and returns status=error."""
    snap = tmp_path / "adg_indexed_20260424_0002.sqlite"
    snap.write_bytes(b"stub")
    stale_mtime = snap.stat().st_mtime - 10.0

    runtime, service = _make_runtime_with_service(monkeypatch, snap, stale_mtime, reopen_sleep_s=2.0)

    result = runtime.reopen_connections(timeout_s=0.1)

    assert result["status"] == "error"
    assert result["data"]["reopened"] is False
    assert result["data"]["reason"] == "timeout"
    assert result["data"]["timeout_s"] == 0.1
    service.reopen.assert_called_once()


def test_log_file_handler_registered_on_named_logger() -> None:
    """W1.1 F1: ``adg_mcp`` logger MUST have a FileHandler pointing at LOG_FILE.

    Guards against reintroduction of the basicConfig-override silent-log
    regression (2026-04-22). Without an explicit FileHandler, FastMCP's
    stdio stderr handlers pre-register and silence file output.
    """
    import logging as _logging
    import os as _os

    from tools.adg.mcp.runtime import LOG, LOG_FILE

    file_handlers = [h for h in LOG.handlers if isinstance(h, _logging.FileHandler)]
    assert file_handlers, "adg_mcp logger must have at least one FileHandler"
    target = _os.path.abspath(LOG_FILE)
    assert any(_os.path.abspath(h.baseFilename) == target for h in file_handlers), (
        f"Expected a FileHandler at {target}; got {[h.baseFilename for h in file_handlers]}"
    )
    # propagate=False keeps our file output from being duplicated to
    # FastMCP stderr sinks.
    assert LOG.propagate is False


def test_log_configuration_is_idempotent_on_reimport() -> None:
    """W1.1 F1: re-invoking ``_configure_adg_logger`` MUST NOT duplicate handlers.

    Subprocess relaunch / hot-reload must not multiply FileHandlers on
    the named logger each time the module is re-imported.
    """
    import logging as _logging

    from tools.adg.mcp.runtime import LOG_FILE, _configure_adg_logger

    before = [h for h in _logging.getLogger("adg_mcp").handlers if isinstance(h, _logging.FileHandler)]
    _configure_adg_logger()
    _configure_adg_logger()
    after = [h for h in _logging.getLogger("adg_mcp").handlers if isinstance(h, _logging.FileHandler)]
    assert len(before) == len(after), f"Handler count changed on re-config: {len(before)} -> {len(after)}"


def test_reopen_noop_when_no_service_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No live service + no stale mtime → falls through to full reopen flow.

    Covers the defensive path where idempotency check is skipped but the
    timeout wrapper still applies on the newly-built service.
    """
    runtime = ADGServerRuntime()
    # Force ``self.service`` (property) to return a stub without tripping
    # ADGService construction.
    stub = MagicMock()
    stub.reopen.return_value = None
    runtime._service = stub

    # With no _sqlite attribute, idempotency check silently falls through.
    stub._sqlite = None

    result = runtime.reopen_connections(timeout_s=5.0)
    assert result["status"] == "ok"
    assert result["data"]["reopened"] is True
    assert result["data"]["noop"] is False
    stub.reopen.assert_called_once()
