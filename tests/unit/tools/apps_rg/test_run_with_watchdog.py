"""Unit tests for tools/apps_rg/run_with_watchdog.py — the background-run hang watchdog.

Each test drives the supervisor against a tiny synthetic child (sys.executable -c ...),
so the suite is fast and needs no apps_rg runtime. The hang test is the load-bearing one:
it proves a silent child is killed promptly by --hang-timeout (the gap a backgrounded
`timeout=` does NOT cover).
"""
from __future__ import annotations

import io
import re
import sys
import time

from tools.apps_rg.run_with_watchdog import (
    DEFAULT_EVENT_REGEX,
    HANG_EXIT,
    LAUNCH_FAIL_EXIT,
    main,
    supervise,
)


def _run(cmd, *, hang_timeout=30.0, hard_timeout=60.0, watch_dir=None, regex=DEFAULT_EVENT_REGEX):
    out = io.StringIO()
    rc = supervise(
        cmd,
        out=out,
        event_re=re.compile(regex, re.IGNORECASE),
        hang_timeout=hang_timeout,
        hard_timeout=hard_timeout,
        watch_dir=watch_dir,
    )
    return rc, out.getvalue()


def test_clean_child_exits_zero_and_streams_progress():
    child = [
        sys.executable,
        "-c",
        "import sys\nfor i in range(3):\n print('progress step', i); sys.stdout.flush()",
    ]
    rc, log = _run(child)
    assert rc == 0
    assert "[watchdog] START" in log
    assert "progress step 0" in log
    assert "[watchdog] DONE exit=0" in log


def test_hang_is_killed_by_hang_timeout():
    # Child sleeps far longer than hang_timeout and emits nothing -> watchdog must kill it
    # well before the child's own 30s sleep would end. This is the background-timeout gap.
    child = [sys.executable, "-c", "import time; time.sleep(30)"]
    t0 = time.monotonic()
    rc, log = _run(child, hang_timeout=1.0, hard_timeout=30.0)
    elapsed = time.monotonic() - t0
    assert rc == HANG_EXIT
    assert "HANG_ALERT" in log
    assert elapsed < 10, f"watchdog took {elapsed:.1f}s to kill a hung child (expected <10s)"


def test_hard_timeout_kills_a_chatty_but_endless_child():
    # Child stays "alive" by printing forever -> hang-timeout never trips, so the absolute
    # hard-timeout is the only thing that can stop it.
    child = [
        sys.executable,
        "-c",
        "import sys, time\nwhile True:\n print('progress tick'); sys.stdout.flush(); time.sleep(0.1)",
    ]
    t0 = time.monotonic()
    rc, log = _run(child, hang_timeout=30.0, hard_timeout=1.0)
    elapsed = time.monotonic() - t0
    assert rc == HANG_EXIT
    assert "HARD_TIMEOUT" in log
    assert elapsed < 10, f"hard-timeout took {elapsed:.1f}s (expected <10s)"


def test_failure_signature_is_surfaced_and_exit_code_preserved():
    child = [
        sys.executable,
        "-c",
        "import sys; print('Traceback (most recent call last):'); sys.exit(2)",
    ]
    rc, log = _run(child)
    assert rc == 2
    assert "Traceback" in log  # failure signature streamed even though it's not "progress"
    assert "[watchdog] DONE exit=2" in log


def test_launch_failure_returns_125():
    rc, log = _run(["definitely-not-a-real-binary-xyz-12345"])
    assert rc == LAUNCH_FAIL_EXIT
    assert "LAUNCH_FAILED" in log


def test_non_event_lines_are_not_streamed():
    # A line matching nothing in the filter must not become an event (keeps Monitor quiet).
    child = [sys.executable, "-c", "print('quiet uninteresting chatter')"]
    rc, log = _run(child)
    assert rc == 0
    assert "quiet uninteresting chatter" not in log


def test_main_parses_double_dash_command():
    rc = main(["--hang-timeout", "10", "--", sys.executable, "-c", "print('progress ok')"])
    assert rc == 0
