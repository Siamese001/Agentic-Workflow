"""Live integration tests for the MCP guard enforcement.

These spawn real child processes whose cmdline contains a marker the
guard is configured to match, then invoke ``guard_single_instance()``
in-process and verify the child is actually terminated (via psutil,
not a mock).

Scope: proves the guard fires end-to-end on the real OS and the adoption
installed across the Windsurf MCP fleet (adg_sqlite, vector_db, memory,
redis, otel_mcp, enhanced_http, pytest_mcp) will also fire correctly
when Windsurf spawns duplicate processes.

Kept outside the unit test tree so CI runners that need xdist isolation
can scope-skip this module. Tests are fast (< 5s each) but fork processes.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

psutil = pytest.importorskip("psutil")

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.mcp import mcp_bootstrap  # noqa: E402


def _spawn_decoy(marker_in_cmdline: str) -> subprocess.Popen:
    """Spawn a harmless sleep process whose cmdline contains the marker.

    Passing the marker as a trailing argv (after `-c CODE`) is the only
    safe way to inject it: Python treats argv[1] as a script path, so if
    we put the marker there Python tries to open it as a file and exits
    instantly. Trailing argv becomes sys.argv[1:] of the -c program; it
    still shows up verbatim in psutil's cmdline, which is all the guard
    substring-check needs.
    """
    decoy_body = textwrap.dedent(
        """\
        import sys, time
        for _ in range(300):  # ~30s ceiling
            time.sleep(0.1)
        """
    )
    return subprocess.Popen(
        [sys.executable, "-c", decoy_body, marker_in_cmdline],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _wait_for_pid_gone(pid: int, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not psutil.pid_exists(pid):
            return True
        time.sleep(0.05)
    return False


@pytest.fixture
def decoy_marker():
    """Unique per-test marker — avoids cross-test races on xdist."""
    return f"__test_guard_marker_{os.getpid()}_{time.time_ns()}__"


def test_guard_kills_live_sibling_by_substring(decoy_marker: str) -> None:
    """The core guarantee: a live process whose cmdline contains the marker
    is actually terminated when guard_single_instance() runs."""
    decoy = _spawn_decoy(decoy_marker)
    try:
        time.sleep(0.3)  # let OS publish the proc to psutil
        assert psutil.pid_exists(decoy.pid), "decoy failed to start"
        mcp_bootstrap.guard_single_instance(decoy_marker)
        assert _wait_for_pid_gone(decoy.pid), (
            f"decoy PID {decoy.pid} survived guard_single_instance() — "
            f"guard not effective for marker={decoy_marker!r}"
        )
    finally:
        if psutil.pid_exists(decoy.pid):
            try:
                decoy.kill()
            except OSError:
                pass


def test_guard_multi_marker_matches_dot_form(decoy_marker: str) -> None:
    """The bugfix path: a process with a dot-form marker is matched when
    the guard is configured with a tuple containing that dot form."""
    dot_form = f"{decoy_marker}.dot"
    slash_form = f"{decoy_marker}/slash"
    decoy = _spawn_decoy(dot_form)
    try:
        time.sleep(0.3)
        assert psutil.pid_exists(decoy.pid)
        # Pass both — only the dot marker can actually match.
        mcp_bootstrap.guard_single_instance((slash_form, dot_form))
        assert _wait_for_pid_gone(decoy.pid), "tuple-marker guard failed to match dot-form cmdline"
    finally:
        if psutil.pid_exists(decoy.pid):
            try:
                decoy.kill()
            except OSError:
                pass


def test_guard_does_not_kill_unrelated_sibling(decoy_marker: str) -> None:
    """Negative case: a process whose cmdline doesn't contain the marker
    must NOT be terminated."""
    decoy = _spawn_decoy(decoy_marker)
    try:
        time.sleep(0.3)
        assert psutil.pid_exists(decoy.pid)
        # Wrong marker on purpose.
        mcp_bootstrap.guard_single_instance(f"__completely_unrelated_{time.time_ns()}")
        time.sleep(0.5)
        assert psutil.pid_exists(decoy.pid), (
            "guard incorrectly killed a process whose cmdline did NOT match the configured marker"
        )
    finally:
        if psutil.pid_exists(decoy.pid):
            try:
                decoy.kill()
            except OSError:
                pass


def test_guard_skips_via_env_var(decoy_marker: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Opt-out env var is honored — decoy survives."""
    decoy = _spawn_decoy(decoy_marker)
    try:
        time.sleep(0.3)
        assert psutil.pid_exists(decoy.pid)
        monkeypatch.setenv("TEST_GUARD_SKIP", "1")
        mcp_bootstrap.guard_single_instance(decoy_marker, skip_env="TEST_GUARD_SKIP")
        time.sleep(0.5)
        assert psutil.pid_exists(decoy.pid), "guard fired despite SKIP env var being set to 1"
    finally:
        if psutil.pid_exists(decoy.pid):
            try:
                decoy.kill()
            except OSError:
                pass


def test_adg_server_marker_actually_matches_dotted_invocation(
    decoy_marker: str,
) -> None:
    """Regression test for the 2026-04-23 bugfix.

    Pre-fix: ``tools/adg/mcp/server`` (slash) was the only marker, and
    the server is launched as ``python -m tools.adg.mcp.server`` (dot).
    The substring check never matched, so the guard no-oped.

    Post-fix: markers are passed as a tuple of both forms. This test
    spawns a decoy whose cmdline contains the dot form (as Windsurf
    would actually invoke) and verifies the real adg marker pair kills
    it.
    """
    # Use the exact markers tools/adg/mcp/server.py now passes, suffixed
    # with a nonce so parallel test runs don't collide.
    dot_form = f"tools.adg.mcp.server.{decoy_marker}"
    decoy = _spawn_decoy(dot_form)
    try:
        time.sleep(0.3)
        assert psutil.pid_exists(decoy.pid)
        mcp_bootstrap.guard_single_instance(
            ("tools.adg.mcp.server", "tools/adg/mcp/server"),
        )
        assert _wait_for_pid_gone(decoy.pid), (
            "adg_sqlite marker tuple failed to match the dot-form "
            "invocation — the 2026-04-23 bugfix has regressed"
        )
    finally:
        if psutil.pid_exists(decoy.pid):
            try:
                decoy.kill()
            except OSError:
                pass
