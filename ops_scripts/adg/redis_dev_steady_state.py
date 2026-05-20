#!/usr/bin/env python3
"""Apply ADG dev Redis steady state on Windows.

- Remove the optional ``redis-memory`` Docker container (port 6379 conflict).
- Verify ADG hot-cache sentinel via ``adg_redis_ingest.py --check``.

Daily ADG work uses Windows Redis on localhost:6379 (``ADG_REDIS_URL``). Keep the
``redis:7-alpine`` image for CI/compose; do not run a second 6379 container unless
you stop the Windows Redis service and re-ingest.

Usage:
    python ops_scripts/adg/redis_dev_steady_state.py
    python ops_scripts/adg/redis_dev_steady_state.py --skip-docker
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTAINER_NAME = "redis-memory"
INGEST = ROOT / "tools" / "adg" / "adg_redis_ingest.py"


def _run(argv: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=check,
        shell=False,
    )


def _remove_redis_memory_container() -> None:
    for action in (["docker", "stop", CONTAINER_NAME], ["docker", "rm", CONTAINER_NAME]):
        proc = _run(action, check=False)
        if proc.returncode != 0 and "No such container" not in (proc.stderr or ""):
            err = (proc.stderr or proc.stdout or "").strip()
            if err:
                print(f"[redis_dev_steady_state] {action[-1]}: {err}")


def _ingest_check() -> int:
    if not INGEST.is_file():
        print(f"ERROR: missing ingest script: {INGEST}", file=sys.stderr)
        return 2
    proc = _run([sys.executable, str(INGEST), "--check"], check=False)
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip(), file=sys.stderr)
    return proc.returncode


def _print_redis_hint() -> None:
    url = os.getenv("ADG_REDIS_URL", "redis://localhost:6379/0")
    print(f"[redis_dev_steady_state] ADG_REDIS_URL={url}")
    try:
        import redis

        client = redis.from_url(url, socket_connect_timeout=3)
        version = client.info("server").get("redis_version", "?")
        print(f"[redis_dev_steady_state] backend redis_version={version}")
        if version.startswith("7."):
            print(
                "[redis_dev_steady_state] OK: Redis 7.x — Docker or native 7 is fine after ingest."
            )
        else:
            print(
                "[redis_dev_steady_state] OK: Windows/native Redis on 6379 is the expected dev path."
            )
            print(
                "[redis_dev_steady_state] Do not start redis-memory on 6379 unless Windows Redis is stopped."
            )
    except Exception as exc:  # guardian: allow-broad-exception -- diagnostic hint only
        print(f"[redis_dev_steady_state] WARN: could not probe Redis: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-docker",
        action="store_true",
        help="Only run adg_redis_ingest --check (no docker stop/rm).",
    )
    args = parser.parse_args()

    if not args.skip_docker:
        _remove_redis_memory_container()

    code = _ingest_check()
    _print_redis_hint()
    if code == 0:
        print("[redis_dev_steady_state] PASS: ADG hot cache ready.")
    else:
        print(
            "[redis_dev_steady_state] FAIL: run: python tools/adg/adg_redis_ingest.py",
            file=sys.stderr,
        )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
