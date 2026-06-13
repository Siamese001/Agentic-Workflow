#!/usr/bin/env python3
"""Run an apps_rg (or any) command under a liveness watchdog with a coverage event stream.

WHY THIS EXISTS
A command launched in the *background* by the agent does NOT honor the agent's
``timeout=`` — it runs until it exits, is stopped, or the session ends (proven
2026-06-13: a backgrounded ``while True: pass`` with ``timeout=3000`` was never
auto-killed). A hung apps_rg run would therefore spin forever with no alert. This
supervisor closes that gap:

  * it enforces its OWN ``--hang-timeout`` (no child output AND no new artifact for
    N seconds) and ``--hard-timeout`` on the child process, killing it on breach, and
  * it emits a single, line-buffered event stream covering BOTH progress markers and
    the failure / hang signatures you would actually act on.

So you launch the supervisor — not apps_rg directly — and hang-alerting comes for free:

    # Per-line alerts (agent Monitor tool): each emitted line becomes one notification
    Monitor: python tools/apps_rg/run_with_watchdog.py --hang-timeout 300 \\
             --watch-dir artifacts/apps_rg/runs -- \\
             python -m apps_rg --section executive_summary --target-company ...

    # Stream -> output file + one completion notification (agent run_in_background)
    Bash(run_in_background=true): <same command>

The supervisor's ``--hard-timeout`` is the in-process deadman that fixes the
background gap above. When driving it from the agent, an optional ScheduleWakeup is a
belt-and-suspenders fallback only for the case where the supervisor process itself dies.

Exit codes: the child's own code on clean exit; 124 on hang-timeout or hard-timeout
(matching coreutils ``timeout``); 125 on launch failure.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from queue import Empty, Queue

# Default event filter: apps_rg progress markers + the failure / hang signatures worth an
# alert. Selective on purpose — under the Monitor tool every emitted line is one
# notification, so this is "the lines you'd act on", covering success AND failure.
DEFAULT_EVENT_REGEX = (
    r"progress|step\b|lane|section|x3|disposition|ALLOW|BLOCK|REVIEW|"
    r"Traceback|Error|Exception|FAILED|assert|Killed|OOM|fatal"
)
HANG_EXIT = 124  # coreutils `timeout` convention (hang-timeout OR hard-timeout breach)
LAUNCH_FAIL_EXIT = 125


def _emit(out, msg: str) -> None:
    """Write one watchdog event line and flush (each line == one Monitor notification)."""
    out.write(f"[watchdog] {msg}\n")
    out.flush()


def _newest_mtime(watch_dir: Path) -> float:
    """Newest mtime under ``watch_dir`` — a progress signal for quiet-but-working runs.

    apps_rg lanes can be stdout-silent for minutes during a single LLM call while still
    writing per-lane artifacts; treating a fresh file as liveness prevents false hangs.
    Returns 0.0 when the dir is missing or empty.
    """
    newest = 0.0
    try:
        for root, _dirs, files in os.walk(watch_dir):
            for name in files:
                try:
                    mtime = os.stat(os.path.join(root, name)).st_mtime
                except OSError:
                    continue  # racing deletion / permission flake — skip this file only
                if mtime > newest:
                    newest = mtime
    except OSError:
        return 0.0
    return newest


def _reader(stream, queue: "Queue[str | None]") -> None:
    """Pump child stdout lines onto ``queue``; enqueue ``None`` sentinel at EOF."""
    for line in iter(stream.readline, ""):
        queue.put(line.rstrip("\n"))
    queue.put(None)


def supervise(
    cmd: list[str],
    *,
    hang_timeout: float,
    hard_timeout: float,
    watch_dir: Path | None,
    event_re: re.Pattern[str],
    out=sys.stdout,
) -> int:
    """Run ``cmd`` under the watchdog; stream filtered progress; return an exit code."""
    start = time.monotonic()
    try:
        # shell=False (argv list). No Popen timeout= — the watchdog below (hang_timeout /
        # hard_timeout) is the enforced subprocess deadman, stronger than a blocking
        # timeout= because it also catches a *silent* hang, not just total wall-clock.
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except (OSError, ValueError) as exc:
        _emit(out, f"LAUNCH_FAILED cmd={cmd!r} err={exc}")
        return LAUNCH_FAIL_EXIT

    _emit(
        out,
        f"START pid={proc.pid} hang_timeout={hang_timeout:.0f}s "
        f"hard_timeout={hard_timeout:.0f}s watch_dir={watch_dir or '-'}",
    )

    queue: "Queue[str | None]" = Queue()
    threading.Thread(target=_reader, args=(proc.stdout, queue), daemon=True).start()

    last_progress = time.monotonic()
    last_dir_mtime = _newest_mtime(watch_dir) if watch_dir else 0.0
    next_dir_poll = time.monotonic()
    stream_closed = False

    def _kill(reason: str) -> int:
        _emit(out, f"{reason} elapsed={time.monotonic() - start:.0f}s killing pid={proc.pid}")
        try:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        except OSError:
            pass  # process already gone — nothing to reap
        return HANG_EXIT

    while True:
        # 1) drain child output — every line is a liveness heartbeat; act-on lines stream out
        try:
            item = queue.get(timeout=1.0)
            if item is None:
                stream_closed = True
            else:
                last_progress = time.monotonic()
                if event_re.search(item):
                    _emit(out, item)
        except Empty:
            pass

        now = time.monotonic()

        # 2) artifact-dir liveness (a lane writing files == progress even if stdout is quiet)
        if watch_dir is not None and now >= next_dir_poll:
            next_dir_poll = now + 2.0
            mtime = _newest_mtime(watch_dir)
            if mtime > last_dir_mtime:
                last_dir_mtime = mtime
                last_progress = now

        # 3) child finished AND we've drained its output -> report and exit with its code
        rc = proc.poll()
        if rc is not None and stream_closed:
            _emit(out, f"DONE exit={rc} elapsed={now - start:.0f}s")
            return rc

        # 4) deadmen — silent hang first, then absolute wall-clock ceiling
        if now - last_progress > hang_timeout:
            return _kill(f"HANG_ALERT no_progress_for={now - last_progress:.0f}s")
        if now - start > hard_timeout:
            return _kill(f"HARD_TIMEOUT limit={hard_timeout:.0f}s")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_with_watchdog",
        description="Supervise a command with a liveness watchdog + coverage event stream.",
    )
    parser.add_argument(
        "--hang-timeout", type=float, default=300.0,
        help="kill child if no progress (stdout line or new artifact) for N s (default 300)",
    )
    parser.add_argument(
        "--hard-timeout", type=float, default=5400.0,
        help="kill child after N s total regardless (default 5400 = 90 min)",
    )
    parser.add_argument(
        "--watch-dir", default=None,
        help="extra liveness signal: a new/modified file under this dir counts as progress",
    )
    parser.add_argument(
        "--event-regex", default=None,
        help="override the case-insensitive event filter applied to child stdout",
    )
    parser.add_argument(
        "command", nargs=argparse.REMAINDER,
        help="-- then the command to run, e.g. -- python -m apps_rg --section ...",
    )
    ns = parser.parse_args(argv)

    cmd = list(ns.command)
    if cmd and cmd[0] == "--":  # argparse may or may not strip the separator; handle both
        cmd = cmd[1:]
    if not cmd:
        parser.error("no command given; put it after `--`")
    if ns.hang_timeout <= 0 or ns.hard_timeout <= 0:
        parser.error("--hang-timeout and --hard-timeout must be positive")

    watch_dir = Path(ns.watch_dir) if ns.watch_dir else None
    event_re = re.compile(ns.event_regex or DEFAULT_EVENT_REGEX, re.IGNORECASE)

    return supervise(
        cmd,
        hang_timeout=ns.hang_timeout,
        hard_timeout=ns.hard_timeout,
        watch_dir=watch_dir,
        event_re=event_re,
    )


if __name__ == "__main__":
    raise SystemExit(main())
