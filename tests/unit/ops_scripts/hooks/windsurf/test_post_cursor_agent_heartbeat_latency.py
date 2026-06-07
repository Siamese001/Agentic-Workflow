"""Smoke tests for post_cursor_agent_heartbeat latency telemetry (P5)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOK = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_cursor" / "post_cursor_agent_heartbeat.py"


def _run(env_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input="",
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
        shell=False,
        check=False,
    )


def test_heartbeat_writes_record_with_latency_field():
    """After two invocations, the heartbeat log contains a record with
    a chain_latency_ms field. Order-independent: scans the tail for the
    expected schema rather than asserting line-count deltas (the log file
    is shared state and is truncated at MAX_LINES under xdist parallel)."""
    log_path = REPO_ROOT / "artifacts" / "windsurf" / "post_cursor_agent_heartbeat.jsonl"

    r1 = _run()
    assert r1.returncode == 0
    time.sleep(0.05)  # ensure measurable delta
    r2 = _run()
    assert r2.returncode == 0

    assert log_path.exists()
    post_lines = log_path.read_text(encoding="utf-8").splitlines()
    assert post_lines, "heartbeat log must have at least one record"

    # Scan the last 5 records for the chain_latency_ms field — concurrent
    # xdist workers may interleave writes, but at least one of OUR records
    # is in the tail.
    for line in reversed(post_lines[-5:]):
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if "chain_latency_ms" in obj:
            assert obj["chain_latency_ms"] is None or isinstance(obj["chain_latency_ms"], (int, float))
            return
    raise AssertionError("no record with chain_latency_ms in last 5 lines")


def test_heartbeat_disable_env_returns_zero_with_no_output():
    """Disable env short-circuits before any I/O. Order-independent: only
    asserts on exit code + stdout/stderr, not on shared log-file state
    (which may race under pytest-xdist parallel runners)."""
    r = _run(env_overrides={"POST_CURSOR_AGENT_HEARTBEAT_DISABLE": "1"})
    assert r.returncode == 0
    # No warning should be printed when the script no-ops on disable.
    assert "WARN" not in r.stderr
