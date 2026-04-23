"""Tests for tools/debug/check_orphan_mcp_processes.py."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

import pytest

# The module lives outside the default test import root; add tools/ to path.
REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "tools" / "debug"))

import check_orphan_mcp_processes as mod  # noqa: E402


def _p(pid: int, minutes_ago: int, cmdline: str) -> mod.Proc:
    return mod.Proc(
        pid=pid,
        started=datetime.now() - timedelta(minutes=minutes_ago),
        cmdline=cmdline,
    )


# ---- is_mcp pattern matching ---------------------------------------------


def test_is_mcp_detects_python_server() -> None:
    p = _p(1, 0, "python -u C:/x/tools/mcp/pytest_server.py")
    assert p.is_mcp()


def test_is_mcp_detects_adg_server_module_invocation() -> None:
    p = _p(1, 0, "python -u -m tools.adg.mcp.server")
    assert p.is_mcp()


def test_is_mcp_detects_filesystem_launcher() -> None:
    p = _p(1, 0, "node C:/x/.windsurf/scripts/filesystem_mcp_launcher.js")
    assert p.is_mcp()


def test_is_mcp_detects_notion_npx() -> None:
    p = _p(1, 0, "node ... @notionhq/notion-mcp-server/bin/cli.mjs")
    assert p.is_mcp()


def test_is_mcp_detects_memory_server() -> None:
    p = _p(1, 0, "python -u C:/x/tools/memory/adg_memory_server.py")
    assert p.is_mcp()


def test_is_mcp_false_for_unrelated() -> None:
    assert not _p(1, 0, "python -m pytest tests/").is_mcp()
    assert not _p(1, 0, "node server.js").is_mcp()
    assert not _p(1, 0, "python lsp_server.py").is_mcp()


# ---- find_orphans logic ---------------------------------------------------


def test_no_orphans_when_single_cohort() -> None:
    procs = [
        _p(101, 0, "python tools/mcp/pytest_server.py"),
        _p(102, 0, "python tools/mcp/redis_mcp_server.py"),
        _p(103, 0, "python -m tools.adg.mcp.server"),
    ]
    assert mod.find_orphans(procs, cohort_gap_sec=60, stale_min=5) == []


def test_detects_two_cohorts_older_is_orphan() -> None:
    procs = [
        _p(201, 0, "python tools/mcp/pytest_server.py"),  # new cohort
        _p(202, 0, "python tools/mcp/redis_mcp_server.py"),
        _p(203, 27, "python tools/mcp/pytest_server.py"),  # old cohort
        _p(204, 27, "python tools/mcp/redis_mcp_server.py"),
    ]
    orphans = mod.find_orphans(procs, cohort_gap_sec=60, stale_min=5)
    assert sorted(p.pid for p in orphans) == [203, 204]


def test_stale_min_filter() -> None:
    procs = [
        _p(301, 0, "python tools/mcp/pytest_server.py"),
        _p(302, 2, "python tools/mcp/pytest_server.py"),  # old but <5 min
    ]
    # cohort_gap_sec=60 -> the 2-min-old one is NOT in cohort (gap > 60s),
    # but stale_min=5 filters it out anyway.
    orphans = mod.find_orphans(procs, cohort_gap_sec=60, stale_min=5)
    assert orphans == []


def test_cohort_gap_boundary() -> None:
    procs = [
        _p(401, 0, "python tools/mcp/pytest_server.py"),
        # 30-second gap - should stay in cohort
        mod.Proc(
            pid=402,
            started=datetime.now() - timedelta(seconds=30),
            cmdline="python tools/mcp/redis_mcp_server.py",
        ),
        # 10-minute gap -> different cohort
        _p(403, 10, "python tools/mcp/pytest_server.py"),
    ]
    orphans = mod.find_orphans(procs, cohort_gap_sec=60, stale_min=5)
    assert [p.pid for p in orphans] == [403]


def test_ignores_non_mcp_processes() -> None:
    procs = [
        _p(501, 0, "python tools/mcp/pytest_server.py"),
        _p(502, 120, "python lsp_server.py"),  # not MCP, ignored
        _p(503, 120, "python -m pytest tests"),  # not MCP, ignored
    ]
    assert mod.find_orphans(procs, cohort_gap_sec=60, stale_min=5) == []


def test_single_mcp_process_is_not_orphan() -> None:
    procs = [_p(601, 0, "python tools/mcp/pytest_server.py")]
    assert mod.find_orphans(procs, cohort_gap_sec=60, stale_min=5) == []


# ---- main() CLI ----------------------------------------------------------


def test_main_clean_returns_zero(
    capsys: pytest.CaptureFixture,
) -> None:
    with mock.patch.object(
        mod, "list_processes_windows", return_value=[]
    ), mock.patch.object(
        mod, "list_processes_posix", return_value=[]
    ):
        rc = mod.main([])
    out = capsys.readouterr().out
    assert rc == 0
    assert "clean" in out


def test_main_reports_orphans_returns_one(
    capsys: pytest.CaptureFixture,
) -> None:
    fake = [
        _p(701, 0, "python tools/mcp/pytest_server.py"),
        _p(702, 30, "python tools/mcp/redis_mcp_server.py"),
    ]
    target = (
        "list_processes_windows" if os.name == "nt"
        else "list_processes_posix"
    )
    with mock.patch.object(mod, target, return_value=fake):
        rc = mod.main([])
    out = capsys.readouterr().out
    assert rc == 1
    assert "702" in out
    assert "rerun with --kill" in out


def test_main_kill_calls_kill(
    capsys: pytest.CaptureFixture,
) -> None:
    fake = [
        _p(801, 0, "python tools/mcp/pytest_server.py"),
        _p(802, 30, "python tools/mcp/redis_mcp_server.py"),
    ]
    killed: list[int] = []

    def _fake_kill(pid: int) -> tuple[bool, str]:
        killed.append(pid)
        return True, "ok"

    target = (
        "list_processes_windows" if os.name == "nt"
        else "list_processes_posix"
    )
    with mock.patch.object(
        mod, target, return_value=fake
    ), mock.patch.object(mod, "kill", side_effect=_fake_kill):
        rc = mod.main(["--kill"])
    assert rc == 0
    assert killed == [802]


def test_main_json_output(capsys: pytest.CaptureFixture) -> None:
    fake = [
        _p(901, 0, "python tools/mcp/pytest_server.py"),
        _p(902, 30, "python tools/mcp/redis_mcp_server.py"),
    ]
    target = (
        "list_processes_windows" if os.name == "nt"
        else "list_processes_posix"
    )
    with mock.patch.object(mod, target, return_value=fake):
        rc = mod.main(["--json"])
    assert rc == 1
    import json
    payload = json.loads(capsys.readouterr().out)
    assert payload["orphan_count"] == 1
    assert payload["orphans"][0]["pid"] == 902
