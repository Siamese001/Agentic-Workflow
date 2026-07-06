"""Byte-preserving guard wrapper for Codex stdio MCP subprocesses.

The wrapper is intentionally boring: stdin, stdout, and stderr are handled as
bytes, diagnostics never touch stdout, and receipts go to JSONL files. Its job
is to keep noisy stderr away from the MCP stdout protocol while still making
early child exits visible to governance checks.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from typing import Any

DEFAULT_ARTIFACT_DIR = Path("artifacts/mcp")
EARLY_EXIT_CODE = 70
CHUNK_SIZE = 65536


class _StartupProbe:
    """Best-effort detector for startup request/response traffic.

    The guard must not parse or rewrite the stdio stream. This detector only
    scans copied bytes for method names so an early child exit before the
    initialize/tools-list handshake can be classified.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stdin_seen = {"initialize": False, "tools/list": False}
        self._stdout_seen = {"initialize": False, "tools/list": False}

    def observe_stdin(self, chunk: bytes) -> None:
        self._observe(chunk, self._stdin_seen)

    def observe_stdout(self, chunk: bytes) -> None:
        self._observe(chunk, self._stdout_seen)
        if not chunk:
            return
        with self._lock:
            for method, seen in self._stdin_seen.items():
                if seen:
                    self._stdout_seen[method] = True

    def complete(self) -> bool:
        with self._lock:
            return all(self._stdin_seen.values()) and all(self._stdout_seen.values())

    def snapshot(self) -> dict[str, dict[str, bool]]:
        with self._lock:
            return {
                "stdin_seen": dict(self._stdin_seen),
                "stdout_seen": dict(self._stdout_seen),
            }

    def _observe(self, chunk: bytes, state: dict[str, bool]) -> None:
        text = chunk.decode("utf-8", errors="ignore")
        with self._lock:
            for method in state:
                if method in text:
                    state[method] = True


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _receipt_path(server: str, artifact_dir: Path) -> Path:
    return artifact_dir / f"{server}_stdio_guard.jsonl"


def _stderr_path(server: str, artifact_dir: Path) -> Path:
    return artifact_dir / f"{server}.stderr.log"


def _write_receipt(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ts": _utc_now(), **payload}
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True) + "\n")


def _copy_stdin(child: subprocess.Popen[bytes], probe: _StartupProbe) -> None:
    src = sys.stdin.buffer
    dst = child.stdin
    if dst is None:
        return
    try:
        while True:
            chunk = src.read(CHUNK_SIZE)
            if not chunk:
                break
            probe.observe_stdin(chunk)
            dst.write(chunk)
            dst.flush()
    except (BrokenPipeError, OSError):
        return
    finally:
        try:
            dst.close()
        except OSError:
            pass


def _copy_stdout(child: subprocess.Popen[bytes], probe: _StartupProbe) -> None:
    src = child.stdout
    if src is None:
        return
    dst = sys.stdout.buffer
    while True:
        chunk = src.read(CHUNK_SIZE)
        if not chunk:
            break
        probe.observe_stdout(chunk)
        dst.write(chunk)
        dst.flush()


def _copy_stderr(child: subprocess.Popen[bytes], log_path: Path) -> None:
    src = child.stderr
    if src is None:
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab") as fh:
        while True:
            chunk = src.read(CHUNK_SIZE)
            if not chunk:
                break
            fh.write(chunk)
            fh.flush()


def _child_env(server: str, stderr_log_path: Path) -> dict[str, str]:
    env = dict(os.environ)
    env.setdefault("TOKENIZERS_PARALLELISM", "false")
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("MCP_STDERR_LEVEL", "WARNING")
    env["MCP_STDERR_LOG_PATH"] = str(stderr_log_path)
    env["CODEX_STDIO_GUARD_SERVER"] = server
    return env


def run_guard(
    child_argv: Sequence[str],
    *,
    server: str,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> int:
    if not child_argv:
        raise ValueError("child_argv is required")

    artifact_dir = artifact_dir.resolve()
    stderr_log = _stderr_path(server, artifact_dir)
    receipt = _receipt_path(server, artifact_dir)
    probe = _StartupProbe()
    started_at = _utc_now()
    _write_receipt(
        receipt,
        {
            "event": "start",
            "server": server,
            "child_argv": list(child_argv),
            "stderr_log_path": str(stderr_log),
        },
    )

    child = subprocess.Popen(
        list(child_argv),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_child_env(server, stderr_log),
    )
    _write_receipt(receipt, {"event": "child_started", "server": server, "pid": child.pid})

    threads = [
        threading.Thread(target=_copy_stdin, args=(child, probe), daemon=True),
        threading.Thread(target=_copy_stdout, args=(child, probe), daemon=True),
        threading.Thread(target=_copy_stderr, args=(child, stderr_log), daemon=True),
    ]
    for thread in threads:
        thread.start()

    child_returncode = child.wait()
    for thread in threads[1:]:
        thread.join(timeout=5)
    # stdin can remain blocked if the parent keeps stdin open; it is daemonized.
    handshake_complete = probe.complete()
    early_exit = not handshake_complete
    exit_code = child_returncode if not early_exit else (child_returncode or EARLY_EXIT_CODE)
    _write_receipt(
        receipt,
        {
            "event": "child_exit",
            "server": server,
            "pid": child.pid,
            "started_at": started_at,
            "child_returncode": child_returncode,
            "exit_code": exit_code,
            "early_exit_before_initialize_tools_list": early_exit,
            "probe": probe.snapshot(),
        },
    )
    return int(exit_code)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guard a stdio MCP child process.")
    parser.add_argument("--server", required=True, help="stable MCP server id")
    parser.add_argument(
        "--artifact-dir",
        default=str(DEFAULT_ARTIFACT_DIR),
        help="directory for stderr logs and guard receipts",
    )
    parser.add_argument("child", nargs=argparse.REMAINDER, help="child command after --")
    args = parser.parse_args(argv)
    child_argv = list(args.child)
    if child_argv and child_argv[0] == "--":
        child_argv = child_argv[1:]
    try:
        return run_guard(child_argv, server=args.server, artifact_dir=Path(args.artifact_dir))
    except (OSError, ValueError) as exc:
        receipt = _receipt_path(args.server, Path(args.artifact_dir).resolve())
        _write_receipt(
            receipt,
            {
                "event": "guard_error",
                "server": args.server,
                "error": f"{type(exc).__name__}: {exc}",
            },
        )
        print(f"codex_stdio_guard: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
